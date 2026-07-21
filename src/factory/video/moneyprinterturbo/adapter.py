import os
import json
import uuid
import time
import subprocess
import hashlib
from pathlib import Path
from typing import Optional

from src.factory.base import VideoGenerator
from src.factory.schemas import CreativeBrief, GeneratedAsset
from src.services.circuit_breaker import CircuitBreakerMixin
from src.services.exceptions import RetryableError, FatalError
from src.factory.video.moneyprinterturbo.quality_cascade import QualityCascadeResolver


class MoneyPrinterTurboProvider(VideoGenerator, CircuitBreakerMixin):
    """
    Adapter definitivo (Stateless) para transformar o MoneyPrinterTurbo num renderizador puro.
    Obedece estritamente ao contrato VideoGenerator da Factory Layer.
    
    Usa QualityCascadeResolver para selecionar dinamicamente o melhor provedor
    disponível por categoria (voz, vídeo, imagem, LLM) com fallback automático.
    """
    provider_name = "moneyprinterturbo"
    confidence_score = 0.90

    def __init__(self, mpt_dir: Path):
        CircuitBreakerMixin.__init__(self, self.provider_name)
        self.mpt_dir = Path(mpt_dir).resolve()
        self.python_exe = self.mpt_dir / "mpt_env" / "Scripts" / "python.exe"
        self.cli_py = self.mpt_dir / "cli.py"

        # Inicializa o resolver de qualidade por categoria
        mpt_config = str(self.mpt_dir / "config.toml")
        nvidia_key = os.getenv("NVIDIA_API_KEY", "")
        self.cascade = QualityCascadeResolver(
            mpt_config_path=mpt_config,
            nvidia_api_key=nvidia_key,
        )

        if not self.python_exe.exists():
            print(f"⚠️ [MPT Adapter] Python EXE não encontrado em: {self.python_exe}.")
        if not self.cli_py.exists():
            print(f"⚠️ [MPT Adapter] Script cli.py não encontrado em: {self.cli_py}.")

    def _generate_hash(self, brief: CreativeBrief) -> str:
        """Gera um hash robusto para os inputs do render (usado para cache)."""
        payload = (
            f"{brief.hypothesis_id}|{brief.hook}|{'#'.join(brief.search_terms)}"
            f"|{brief.format}|{brief.duration}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def health(self) -> dict:
        return {
            "healthy": self.python_exe.exists(),
            "provider": self.provider_name,
            "python_exe": str(self.python_exe),
        }

    def generate(self, brief: CreativeBrief) -> GeneratedAsset:
        """
        Executa o pipeline do MPT traduzindo o CreativeBrief.
        Resolve dinamicamente os melhores provedores por categoria antes de renderizar.
        """
        self.cb_check()

        start_time = time.time()
        timeout = 900

        # ── Parâmetros base do brief ──────────────────────────────────────────
        subject = brief.subject or brief.hook
        script = brief.script or brief.hook
        search_terms = brief.search_terms
        aspect = "9:16" if brief.format == "short_video" else "16:9"
        language = "pt-BR"

        # ── Cascata de Qualidade por Categoria ────────────────────────────────
        print("🔍 [MPT Adapter] Resolvendo melhores provedores por categoria...")
        voice, emotion_style = self.cascade.resolve_voice(brief.emotion)
        video_source = self.cascade.resolve_video_source(aspect=aspect)  # aspect-aware!
        mpt_llm_provider = self.cascade.resolve_mpt_llm_provider()       # LLM interno do MPT
        # LLM do Copywriter e Imagem são resolvidos pelo ExperimentRunner antes desta etapa

        # ── Cache de renders ──────────────────────────────────────────────────
        render_hash = self._generate_hash(brief)
        cache_dir = Path(__file__).parent.parent.parent.parent / "cache" / "renders" / render_hash
        cache_file = cache_dir / "render_result.json"

        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            cached_path = data.get("path", str(self.mpt_dir / "dummy.mp4"))
            # Ajusta caminhos para o diretório de execução atual caso tenham mudado (Documents vs Downloads)
            project_root = str(self.mpt_dir.parent)
            if "projeto" in cached_path:
                parts = cached_path.split("projeto", 1)
                cached_path = project_root + parts[1]
            
            if os.path.exists(cached_path):
                print(f"🎬 [MPT Adapter] CACHE HIT! Retornando render pré-calculado: {render_hash}")
                task_dir = data.get("task_dir", "")
                if "projeto" in task_dir:
                    task_dir = project_root + task_dir.split("projeto", 1)[1]
                subtitles_path = data.get("subtitles_path", "")
                if subtitles_path and "projeto" in subtitles_path:
                    subtitles_path = project_root + subtitles_path.split("projeto", 1)[1]
                audio_path = data.get("audio_path", "")
                if audio_path and "projeto" in audio_path:
                    audio_path = project_root + audio_path.split("projeto", 1)[1]

                return GeneratedAsset(
                    path=cached_path,
                    duration=data.get("duration", brief.duration),
                    resolution=data.get("resolution", "1080x1920"),
                    provider=self.provider_name,
                    confidence=self.confidence_score,
                    task_dir=task_dir,
                    subtitles_path=subtitles_path,
                    audio_path=audio_path,
                )

        # ── Renderização Real ─────────────────────────────────────────────────
        task_id = str(uuid.uuid4())
        task_dir = self.mpt_dir / "storage" / "tasks" / task_id
        terms_str = ",".join(search_terms) if search_terms else ""

        # O voice_name para o CLI não carrega o sufixo ;style= (passado internamente pelo voice.py)
        voice_name_clean = voice.split(";")[0]

        print(f"🎬 [MPT Adapter] Iniciando Render Task: {task_id} para {brief.hypothesis_id}")

        cmd = [
            str(self.python_exe), str(self.cli_py),
            "--task-id",       task_id,
            "--video-subject", subject,
            "--video-script",  script,
            "--video-aspect",  aspect,
            "--video-language", language,
            "--voice-name",    voice_name_clean,
            "--video-source",  video_source,
        ]
        if terms_str:
            cmd.extend(["--video-terms", terms_str])

        env = os.environ.copy()
        env["PYTHONUTF8"] = "1"
        # Sobrescreve o provedor de LLM interno do MPT via env para usar o melhor disponível
        env["MPT_LLM_PROVIDER"] = mpt_llm_provider
        path_key = "PATH" if "PATH" in env else "Path"
        if path_key not in env:
            env[path_key] = ""
        if "ImageMagick" not in env[path_key]:
            env[path_key] += ";C:\\Program Files\\ImageMagick-7.1.2-Q16-HDRI"

        stdout_log = ""
        stderr_log = ""
        success = False

        # ── Injeta o melhor provedor de LLM no config.toml do MPT ────────────
        # O MPT lê o provedor do config.toml; sobrescrevemos em runtime.
        mpt_config_path = self.mpt_dir / "config.toml"
        original_config_content = None
        try:
            if mpt_config_path.exists():
                original_config_content = mpt_config_path.read_text(encoding="utf-8")
                import re
                patched = re.sub(
                    r'^llm_provider\s*=\s*"[^"]*"',
                    f'llm_provider = "{mpt_llm_provider}"',
                    original_config_content,
                    flags=re.MULTILINE,
                )
                mpt_config_path.write_text(patched, encoding="utf-8")
                print(f"🧠 [MPT Config] llm_provider sobrescrito para: {mpt_llm_provider}")
        except Exception as cfg_err:
            print(f"⚠️ [MPT Config] Não foi possível sobrescrever llm_provider: {cfg_err}")

        try:
            if not self.python_exe.exists():
                print("⚠️ [MPT Adapter] MPT não instalado. Criando vídeo placeholder.")
                task_dir.mkdir(parents=True, exist_ok=True)
                video_path = task_dir / "final.mp4"
                with open(video_path, "wb") as f:
                    f.write(b"mock_video_content" * 1000)
                success = True
            else:
                try:
                    result = subprocess.run(
                        cmd,
                        cwd=str(self.mpt_dir),
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        env=env,
                    )
                    stdout_log = result.stdout
                    stderr_log = result.stderr
                    success = result.returncode == 0
                except Exception as e:
                    stderr_log = f"ERROR: Falha fatal: {str(e)}"
                    success = False
        finally:
            # Restaura o config.toml original independente do resultado
            if original_config_content is not None:
                try:
                    mpt_config_path.write_text(original_config_content, encoding="utf-8")
                except Exception:
                    pass

        if not task_dir.exists():
            task_dir.mkdir(parents=True, exist_ok=True)

        video_path = task_dir / "final-1.mp4"
        if not video_path.exists():
            video_path = task_dir / "final.mp4"

        subtitles_path = task_dir / "subtitle.srt"
        audio_path = task_dir / "audio.mp3"

        if not success or not video_path.exists():
            self.cb_record_failure()
            raise RetryableError("FACTORY_RENDER_FAIL", f"Geração falhou no MPT. Log:\n{stderr_log}")

        # ── Extrai duração física real via python-av ──────────────────────────
        actual_duration = brief.duration
        try:
            import av
            container = av.open(str(video_path))
            actual_duration = int(float(container.duration) / av.time_base)
            container.close()
            print(f"🎬 [MPT Adapter] Duração real do vídeo extraída: {actual_duration}s")
        except Exception as av_err:
            print(f"⚠️ [MPT Adapter] Erro ao extrair duração via av: {av_err}. Usando default: {brief.duration}s")

        self.cb_record_success()
        asset = GeneratedAsset(
            path=str(video_path),
            duration=actual_duration,
            resolution="1080x1920" if aspect == "9:16" else "1920x1080",
            provider=self.provider_name,
            confidence=self.confidence_score,
            task_dir=str(task_dir),
            subtitles_path=str(subtitles_path) if subtitles_path.exists() else None,
            audio_path=str(audio_path) if audio_path.exists() else None,
        )

        # ── Salva no cache ────────────────────────────────────────────────────
        cache_dir.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(asset.model_dump(), f, indent=2, ensure_ascii=False)

        return asset
