import os
import uuid
import base64
import hashlib
import logging
import requests
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from src.factory.base import ImageGenerator
from src.factory.schemas import CreativeBrief, GeneratedAsset
from src.services.circuit_breaker import CircuitBreakerMixin
from src.services.exceptions import RetryableError, FatalError

load_dotenv()
logger = logging.getLogger("factory.nvidia")


class NvidiaImageProvider(ImageGenerator, CircuitBreakerMixin):
    """
    Adapter para a API de Geração de Imagens da NVIDIA (FLUX.1-dev).
    Obedece estritamente ao contrato ImageGenerator da Factory Layer.
    O conteúdo textual (prompt, título, descrição, CTA) chega pronto do Core
    (Copywriter + Critic) via CreativeBrief. Este provider apenas executa a geração.
    """
    provider_name = "nvidia_flux1_dev"
    confidence_score = 0.92

    # Dimensões otimizadas para Pinterest (ratio 1:1 quadrado estável)
    PINTEREST_WIDTH = 1024
    PINTEREST_HEIGHT = 1024

    def __init__(self, api_key: str = None, output_dir: str = "output"):
        CircuitBreakerMixin.__init__(self, self.provider_name)
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.api_url = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-dev"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def health(self) -> dict:
        if not self.api_key or "nvapi-" not in self.api_key:
            return {"healthy": False, "provider": self.provider_name, "error": "NVIDIA_API_KEY ausente ou inválida"}
        return {"healthy": True, "provider": self.provider_name, "model": "flux.1-dev"}

    def generate(self, brief: CreativeBrief) -> GeneratedAsset:
        """
        Gera uma imagem estática a partir de um CreativeBrief aprovado pelo Core.
        O prompt visual é derivado automaticamente dos campos semânticos do brief.
        """
        self.cb_check()

        if not self.api_key or "nvapi-" not in self.api_key:
            raise FatalError("NVIDIA_API_CONFIG", "NVIDIA_API_KEY não configurada. Configure NVIDIA_API_KEY no .env")

        # Monta o prompt visual a partir do conteúdo aprovado pelo Copywriter
        visual_prompt = self._build_visual_prompt(brief)
        render_hash = hashlib.sha256(visual_prompt.encode()).hexdigest()

        # Cache hit check (por output_dir para evitar colusão entre ambientes)
        cache_dir = self.output_dir / ".cache" / render_hash
        cache_file = cache_dir / "render_result.json"
        if cache_file.exists():
            import json
            logger.info(f"[NvidiaImageProvider] CACHE HIT: {render_hash[:12]}")
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            asset = GeneratedAsset(**data)
            # Reinjetar conteúdo aprovado no asset recuperado do cache
            asset.approved_title = brief.hook[:120]
            asset.approved_description = brief.script if brief.script else brief.hook
            asset.approved_cta = "Saiba mais no link da bio."
            asset.destination_link = "https://github.com/Ciamarro1/ai-revenue-os"
            return asset

        # Geração via API NVIDIA
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "prompt": visual_prompt,
            "width": self.PINTEREST_WIDTH,
            "height": self.PINTEREST_HEIGHT,
            "steps": 30,
            "seed": 0
        }

        logger.info(f"[NvidiaImageProvider] Gerando imagem para brief: {brief.hypothesis_id}")
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=120)
        except Exception as e:
            self.cb_record_failure()
            raise RetryableError("NVIDIA_NETWORK_FAIL", f"Falha de rede ao acessar NVIDIA API: {e}")

        if response.status_code == 429:
            self.cb_record_failure()
            raise RetryableError("NVIDIA_RATE_LIMIT", "Rate limit atingido na NVIDIA API. Aguarde e tente novamente.")

        if response.status_code != 200:
            self.cb_record_failure()
            raise RetryableError("NVIDIA_API_ERROR", f"Erro na NVIDIA API (HTTP {response.status_code}): {response.text}")

        data = response.json()
        artifacts = data.get("artifacts", [])
        if not artifacts or not artifacts[0].get("base64"):
            self.cb_record_failure()
            raise RetryableError("NVIDIA_EMPTY_RESPONSE", "A API retornou resposta sem artefatos de imagem.")

        # Salvar imagem
        image_bytes = base64.b64decode(artifacts[0]["base64"])
        output_path = self.output_dir / f"img_{uuid.uuid4().hex[:8]}.jpg"
        with open(output_path, "wb") as f:
            f.write(image_bytes)

        self.cb_record_success()
        logger.info(f"[NvidiaImageProvider] Imagem gerada: {output_path}")

        asset = GeneratedAsset(
            path=str(output_path),
            duration=0,  # Imagens não têm duração
            resolution=f"{self.PINTEREST_WIDTH}x{self.PINTEREST_HEIGHT}",
            provider=self.provider_name,
            confidence=self.confidence_score,
            # Conteúdo aprovado pelo Core
            approved_title=brief.hook[:120],
            approved_description=brief.script if brief.script else brief.hook,
            approved_cta="Saiba mais no link da bio.",
            destination_link="https://github.com/Ciamarro1/ai-revenue-os"
        )

        # Salvar no cache
        import json
        cache_dir.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(asset.model_dump(), f, indent=2, ensure_ascii=False)

        return asset

    def _build_visual_prompt(self, brief: CreativeBrief) -> str:
        """
        Traduz o CreativeBrief aprovado pelo Copywriter em um prompt visual rico para o FLUX.
        O conteúdo textual já foi validado pelo Critic — aqui apenas geramos a representação visual.
        """
        emotion_map = {
            "curiosity": "mysterious, thought-provoking, intriguing atmosphere",
            "fear": "urgent, dramatic, high-stakes atmosphere",
            "trust": "clean, professional, trustworthy, calm atmosphere",
            "desire": "aspirational, luxury, beautiful, desirable atmosphere",
            "excitement": "energetic, vibrant, dynamic, exciting atmosphere",
        }
        emotion_style = emotion_map.get(brief.emotion, "professional, modern atmosphere")

        return (
            f"High quality Pinterest pin image, vertical format 2:3, "
            f"visually representing the concept of '{brief.subject}'. "
            f"{emotion_style}. "
            f"Audience: {brief.audience}. "
            f"Visual hook: {brief.hook[:100]}. "
            f"Style: photorealistic, sharp, premium social media content, "
            f"no text overlay, no watermarks, studio lighting, "
            f"suitable for {brief.platform} marketing."
        )
