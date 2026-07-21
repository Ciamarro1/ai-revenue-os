"""
QualityCascadeResolver
======================
Resolve o melhor provedor disponível por CATEGORIA de recurso (voz, vídeo, imagem, LLM).

Para cada categoria, existe uma cadeia de prioridade ordenada por qualidade.
O resolver testa cada provedor em ordem e retorna o primeiro que responder com sucesso.
Se todos falharem, retorna o fallback final garantido (sem chamada de API).

Categorias suportadas:
  - VOICE      : ElevenLabs (eleven_v3 + emoções) → SiliconFlow TTS → Edge TTS pt-BR
  - VIDEO      : Portrait: Pexels → Pixabay → Coverr | Landscape: Coverr → Pexels → Pixabay
  - IMAGE      : NVIDIA FLUX.1-dev (padrão atual)
  - LLM        : OpenRouter/Gemini → Groq → Gemini nativo → Volcengine → Moonshot
  - MPT_LLM    : Groq → Moonshot → Gemini → Volcengine → OpenRouter (para uso interno do MPT)
"""

import requests
import tomllib
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Mapa de intensidade emocional para style do ElevenLabs (0.0 – 1.0)
# Quanto maior o style, mais expressivo e menos estável o discurso.
# ─────────────────────────────────────────────────────────────────────────────
EMOTION_STYLE_MAP = {
    "excitement":  0.95,
    "urgency":     0.90,
    "surprise":    0.85,
    "fear":        0.80,
    "curiosity":   0.65,
    "discovery":   0.60,
    "aspiration":  0.55,
    "status":      0.50,
    "belonging":   0.45,
    "neutral":     0.20,
}


# ─────────────────────────────────────────────────────────────────────────────
# Classe Principal
# ─────────────────────────────────────────────────────────────────────────────
class QualityCascadeResolver:
    """
    Resolve o melhor provedor disponível por categoria, com fallback automático.

    Uso:
        resolver = QualityCascadeResolver(mpt_config_path="/path/to/config.toml",
                                           nvidia_api_key="nvapi-...")
        voice, style  = resolver.resolve_voice(emotion="curiosity")
        source        = resolver.resolve_video_source(aspect="9:16")
        llm_provider  = resolver.resolve_mpt_llm_provider()
    """

    def __init__(self, mpt_config_path: str = None, nvidia_api_key: str = None):
        self._cfg = {}
        self._nvidia_api_key = nvidia_api_key or ""
        if mpt_config_path and Path(mpt_config_path).exists():
            with open(mpt_config_path, "rb") as f:
                self._cfg = tomllib.load(f)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _app(self) -> dict:
        return self._cfg.get("app", {})

    def _get(self, section: str, key: str, default="") -> str:
        return self._cfg.get(section, {}).get(key, default)

    def _http_ok(self, url: str, headers: dict = None, params: dict = None,
                 timeout: int = 6) -> bool:
        """Retorna True se a requisição retornar HTTP 200."""
        try:
            r = requests.get(url, headers=headers or {}, params=params or {},
                             timeout=timeout)
            return r.status_code == 200
        except Exception:
            return False

    # ── CATEGORIA: VOICE ─────────────────────────────────────────────────────

    def resolve_voice(self, emotion: str = "neutral") -> tuple[str, float]:
        """
        Cascata de qualidade para voz/TTS:
          Tier 1 – ElevenLabs (eleven_v3, emoções expressivas)
                   ATENÇÃO: apenas vozes próprias da conta (category != premade).
                   Vozes da biblioteca pública exigem plano pago via API.
          Tier 2 – SiliconFlow TTS
          Tier 3 – Edge TTS pt-BR (fallback garantido, sem API)

        Retorna (voice_name, style_score).
        voice_name inclui o sufixo ;style=X quando for ElevenLabs.
        """
        style = EMOTION_STYLE_MAP.get(emotion, 0.40)

        # ── Tier 0: Voz preferida configurada explicitamente ─────────────────
        # Se preferred_voice_id estiver definido no config.toml, usa direto.
        # Evita varrer o catálogo e garante que a voz correta seja sempre usada.
        el_key = self._get("elevenlabs", "api_key")
        preferred_id   = self._get("elevenlabs", "preferred_voice_id")
        preferred_name = self._get("elevenlabs", "preferred_voice_name", "Custom Voice")
        if el_key and preferred_id:
            try:
                r = requests.get(
                    f"https://api.elevenlabs.io/v1/voices/{preferred_id}",
                    headers={"xi-api-key": el_key},
                    timeout=6,
                )
                if r.status_code == 200:
                    voice_data = r.json()
                    actual_name = voice_data.get("name", preferred_name)
                    voice_str = (
                        f"elevenlabs:{preferred_id}:{actual_name}"
                        f";style={style}"
                    )
                    print(
                        f"🎤 [Voice | Tier 0] ElevenLabs voz preferida: '{actual_name}' "
                        f"(ID={preferred_id}, style={style:.2f}, emotion='{emotion}')"
                    )
                    return voice_str, style
                else:
                    print(
                        f"⚠️ [Voice | Tier 0] Voz preferida {preferred_id} retornou "
                        f"{r.status_code}. Continuando cascata."
                    )
            except Exception as e:
                print(f"⚠️ [Voice | Tier 0] Voz preferida falhou: {e}. Continuando cascata.")

        # ── Tier 1: ElevenLabs ───────────────────────────────────────────────
        if el_key and len(el_key) > 10:
            try:
                r = requests.get(
                    "https://api.elevenlabs.io/v2/voices",
                    headers={"xi-api-key": el_key},
                    params={"page_size": 50},
                    timeout=8,
                )
                if r.status_code == 200:
                    voices = r.json().get("voices", [])

                    # FILTRO CRÍTICO: apenas vozes da própria conta.
                    # category="premade" = biblioteca pública → requer plano pago via API.
                    # category="cloned" / "generated" / "professional" / "instant" → conta própria.
                    owned = [
                        v for v in voices
                        if v.get("voice_id")
                        and v.get("status") != "disabled"
                        and v.get("category", "premade") != "premade"
                    ]

                    if owned:
                        # Prioriza fine-tuned dentro das vozes próprias
                        fine_tuned = [
                            v for v in owned
                            if v.get("fine_tuning", {}).get("finetuning_state") == "fine_tuned"
                        ]
                        chosen = (fine_tuned or owned)[0]
                        voice_str = (
                            f"elevenlabs:{chosen['voice_id']}:{chosen['name']}"
                            f";style={style}"
                        )
                        print(
                            f"🎤 [Voice | Tier 1] ElevenLabs: '{chosen['name']}' "
                            f"(category={chosen.get('category')}, "
                            f"style={style:.2f}, emotion='{emotion}')"
                        )
                        return voice_str, style
                    else:
                        print(
                            "⚠️ [Voice | Tier 1] ElevenLabs: sem vozes próprias na conta. "
                            "Crie ou clone uma voz em elevenlabs.io para usar via API gratuita."
                        )
                else:
                    print(f"⚠️ [Voice | Tier 1] ElevenLabs retornou {r.status_code}.")
            except Exception as e:
                print(f"⚠️ [Voice | Tier 1] ElevenLabs falhou: {e}")

        # ── Tier 2: SiliconFlow TTS ───────────────────────────────────────────
        sf_key = self._get("siliconflow", "api_key")
        if sf_key and len(sf_key) > 10:
            try:
                r = requests.get(
                    "https://api.siliconflow.com/v1/models",
                    headers={"Authorization": f"Bearer {sf_key}"},
                    timeout=6,
                )
                if r.status_code == 200:
                    voice_str = "siliconflow:FunAudioLLM/CosyVoice2-0.5B:alex"
                    print(f"🎤 [Voice | Tier 2] SiliconFlow TTS: {voice_str}")
                    return voice_str, style
                print(f"⚠️ [Voice | Tier 2] SiliconFlow retornou {r.status_code}.")
            except Exception as e:
                print(f"⚠️ [Voice | Tier 2] SiliconFlow falhou: {e}")

        # ── Tier 3: Edge TTS (fallback gratuito, sempre disponível) ──────────
        print("🎤 [Voice | Tier 3] Fallback: Edge TTS pt-BR-AntonioNeural")
        return "pt-BR-AntonioNeural", style

    # ── CATEGORIA: VIDEO SOURCE ───────────────────────────────────────────────

    def resolve_video_source(self, aspect: str = "9:16") -> str:
        """
        Cascata de qualidade para vídeos de B-Roll — sensível ao aspect ratio:

          Para 9:16 (portrait / short-form):
            Tier 1 – Pexels  (catálogo portrait nativo HD/4K)
            Tier 2 – Pixabay (catálogo portrait HD)
            Tier 3 – Coverr  (quase sem conteúdo portrait ~1% → letterbox)

          Para 16:9 (landscape / cinematic):
            Tier 1 – Coverr  (HD/4K, licença limpa, acervo landscape excelente)
            Tier 2 – Pexels  (HD/4K, acervo massivo)
            Tier 3 – Pixabay (HD, acervo diverso)

        Nota: O próprio código do MPT documenta que Coverr é 99% landscape.
        Usá-lo para portrait gera resize + letterbox e degrada a qualidade visual.
        """
        app = self._app()
        coverr_keys = app.get("coverr_api_keys", [])
        pexels_keys  = app.get("pexels_api_keys",  [])
        pixabay_keys = app.get("pixabay_api_keys", [])

        coverr = (
            "coverr",
            "https://api.coverr.co/videos",
            {"query": "nature", "page_size": 1},
            {"Authorization": f"Bearer {coverr_keys[0]}"},
        ) if coverr_keys else None

        pexels = (
            "pexels",
            "https://api.pexels.com/videos/search",
            {"query": "nature", "per_page": 1},
            {"Authorization": pexels_keys[0]},
        ) if pexels_keys else None

        pixabay = (
            "pixabay",
            "https://pixabay.com/api/videos/",
            {"q": "nature", "per_page": 1, "key": pixabay_keys[0]},
            {},
        ) if pixabay_keys else None

        is_portrait = aspect == "9:16"
        if is_portrait:
            ordered = [p for p in [pexels, pixabay, coverr] if p]
            print("🎬 [Video Resolver] Modo portrait (9:16): Pexels → Pixabay → Coverr")
        else:
            ordered = [p for p in [coverr, pexels, pixabay] if p]
            print("🎬 [Video Resolver] Modo landscape (16:9): Coverr → Pexels → Pixabay")

        for tier, (name, url, params, headers) in enumerate(ordered, start=1):
            if self._http_ok(url, headers=headers, params=params):
                quality = "HD/4K portrait" if is_portrait else "HD/4K landscape"
                print(f"🎬 [Video | Tier {tier}] Fonte selecionada: {name} ({quality})")
                return name
            print(f"⚠️ [Video | Tier {tier}] {name} indisponível. Tentando próximo.")

        print("⚠️ [Video] Todos os provedores falharam. Usando pexels como último recurso.")
        return "pexels"

    # ── CATEGORIA: MPT LLM INTERNO ────────────────────────────────────────────

    def resolve_mpt_llm_provider(self) -> str:
        """
        Resolve o melhor provedor de LLM para uso INTERNO do MPT (geração de search terms).
        Retorna o nome do provedor no formato aceito pelo config.toml do MPT.

        Cascade (prioriza gratuitos e rápidos primeiro):
          Tier 1 – Groq    (llama-3.3-70b, ultra-rápido, free tier generoso)
          Tier 2 – Moonshot / Kimi
          Tier 3 – Gemini nativo
          Tier 4 – Volcengine (Doubao)
          Fallback – OpenRouter (pode ter créditos insuficientes)
        """
        groq_key = self._get("app", "groq_api_key")
        if groq_key:
            if self._http_ok(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {groq_key}"},
            ):
                print("🧠 [MPT LLM | Tier 1] Groq selecionado (llama-3.3-70b)")
                return "groq"
            print("⚠️ [MPT LLM | Tier 1] Groq indisponível.")

        moon_key = self._get("app", "moonshot_api_key")
        moon_url = self._get("app", "moonshot_base_url", "https://api.moonshot.cn/v1")
        if moon_key:
            if self._http_ok(
                moon_url.rstrip("/") + "/models",
                headers={"Authorization": f"Bearer {moon_key}"},
            ):
                print("🧠 [MPT LLM | Tier 2] Moonshot/Kimi selecionado")
                return "moonshot"
            print("⚠️ [MPT LLM | Tier 2] Moonshot indisponível.")

        gemini_key = self._get("app", "gemini_api_key")
        if gemini_key:
            if self._http_ok(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}",
            ):
                print("🧠 [MPT LLM | Tier 3] Gemini nativo selecionado")
                return "gemini"
            print("⚠️ [MPT LLM | Tier 3] Gemini indisponível.")

        volc_key = self._get("app", "volcengine_api_key")
        volc_url = self._get("app", "volcengine_base_url", "")
        if volc_key and volc_url:
            if self._http_ok(
                volc_url.rstrip("/") + "/models",
                headers={"Authorization": f"Bearer {volc_key}"},
            ):
                print("🧠 [MPT LLM | Tier 4] Volcengine selecionado")
                return "volcengine"
            print("⚠️ [MPT LLM | Tier 4] Volcengine indisponível.")

        print("🧠 [MPT LLM | Fallback] OpenRouter")
        return "openai"

    # ── CATEGORIA: IMAGE ──────────────────────────────────────────────────────

    def resolve_image_provider(self) -> str:
        """
        Cascata para geração de imagens:
          Tier 1 – NVIDIA FLUX.1-dev (alta fidelidade, fotorrealismo)
          Fallback – nvidia_flux1_dev (sempre disponível se a chave existir)
        """
        if self._nvidia_api_key and "nvapi-" in self._nvidia_api_key:
            try:
                r = requests.get(
                    "https://ai.api.nvidia.com/v1/genai/health",
                    headers={"Authorization": f"Bearer {self._nvidia_api_key}"},
                    timeout=5,
                )
                if r.status_code in (200, 404):
                    print("🖼️ [Image | Tier 1] NVIDIA FLUX.1-dev selecionado")
                    return "nvidia_flux1_dev"
            except Exception:
                pass

        print("🖼️ [Image | Tier 1] NVIDIA FLUX.1-dev (padrão)")
        return "nvidia_flux1_dev"

    # ── CATEGORIA: LLM (Copywriter externo ao MPT) ────────────────────────────

    def resolve_llm(self) -> dict:
        """
        Cascata para LLMs usados pelo ExperimentRunner (copywriting / roteiro).
          Tier 1 – OpenRouter (Gemini 2.5 Flash)
          Tier 2 – Groq (Llama 3.3 70B)
          Tier 3 – Gemini nativo
          Tier 4 – Volcengine (Doubao)
          Tier 5 – Moonshot / Kimi
          Fallback – GEMINI_API_KEY do ambiente

        Retorna dict {provider, api_key, base_url, model}.
        """
        import os

        candidates = []

        openai_key   = self._get("app", "openai_api_key")
        openai_url   = self._get("app", "openai_base_url")
        openai_model = self._get("app", "openai_model_name", "google/gemini-2.5-flash")
        if openai_key:
            candidates.append({
                "tier": 1, "name": "OpenRouter (Gemini 2.5 Flash)",
                "provider": "openai_compat", "api_key": openai_key,
                "base_url": openai_url or "https://openrouter.ai/api/v1",
                "model": openai_model,
                "health_url": "https://openrouter.ai/api/v1/models",
                "health_headers": {"Authorization": f"Bearer {openai_key}"},
            })

        groq_key   = self._get("app", "groq_api_key")
        groq_model = self._get("app", "groq_model_name", "llama-3.3-70b-versatile")
        if groq_key:
            candidates.append({
                "tier": 2, "name": "Groq (Llama 3.3 70B)",
                "provider": "openai_compat", "api_key": groq_key,
                "base_url": "https://api.groq.com/openai/v1",
                "model": groq_model,
                "health_url": "https://api.groq.com/openai/v1/models",
                "health_headers": {"Authorization": f"Bearer {groq_key}"},
            })

        gemini_key   = self._get("app", "gemini_api_key")
        gemini_model = self._get("app", "gemini_model_name", "gemini-flash-latest")
        if gemini_key:
            candidates.append({
                "tier": 3, "name": "Gemini Nativo",
                "provider": "gemini", "api_key": gemini_key,
                "base_url": "", "model": gemini_model,
                "health_url": f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}",
                "health_headers": {},
            })

        volc_key   = self._get("app", "volcengine_api_key")
        volc_url   = self._get("app", "volcengine_base_url")
        volc_model = self._get("app", "volcengine_model_name")
        if volc_key:
            candidates.append({
                "tier": 4, "name": "Volcengine (Doubao)",
                "provider": "openai_compat", "api_key": volc_key,
                "base_url": volc_url, "model": volc_model,
                "health_url": volc_url.rstrip("/") + "/models",
                "health_headers": {"Authorization": f"Bearer {volc_key}"},
            })

        moon_key   = self._get("app", "moonshot_api_key")
        moon_url   = self._get("app", "moonshot_base_url", "https://api.moonshot.cn/v1")
        moon_model = self._get("app", "moonshot_model_name", "kimi-k2.7-code")
        if moon_key:
            candidates.append({
                "tier": 5, "name": "Moonshot / Kimi",
                "provider": "openai_compat", "api_key": moon_key,
                "base_url": moon_url, "model": moon_model,
                "health_url": moon_url.rstrip("/") + "/models",
                "health_headers": {"Authorization": f"Bearer {moon_key}"},
            })

        for c in candidates:
            if self._http_ok(c["health_url"], headers=c["health_headers"], timeout=6):
                print(f"🧠 [LLM | Tier {c['tier']}] {c['name']} ({c['model']})")
                return {k: v for k, v in c.items()
                        if k not in ("health_url", "health_headers", "tier", "name")}
            print(f"⚠️ [LLM] {c['name']} indisponível. Tentando próximo.")

        env_key = os.getenv("GEMINI_API_KEY", "")
        print("🧠 [LLM | Fallback] GEMINI_API_KEY do ambiente")
        return {"provider": "gemini", "api_key": env_key, "base_url": "", "model": "gemini-2.5-flash"}
