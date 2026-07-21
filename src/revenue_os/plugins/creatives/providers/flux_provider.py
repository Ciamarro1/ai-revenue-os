import hashlib
from src.revenue_os.plugins.creatives.providers.base_creative_provider import BaseImageProvider
from src.revenue_os.plugins.creatives.storage_manager import CreativeStorageManager
from src.revenue_os.plugins.creatives.models import GeneratedCreativeAsset

class FluxImageProvider(BaseImageProvider):
    """
    Provedor Gerativo FLUX.1-schnell / FLUX.1-dev.
    """

    def __init__(self, storage_manager: CreativeStorageManager = None, enabled: bool = True):
        self.storage = storage_manager or CreativeStorageManager()
        self._enabled = enabled

    @property
    def provider_name(self) -> str:
        return "flux"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def generate_image(self, prompt: str, filename: str = "flux_render.png") -> GeneratedCreativeAsset:
        if not self._enabled:
            raise RuntimeError("FluxImageProvider is disabled.")

        # Geração de conteúdo estático determinístico baseado no prompt
        seed_hash = hashlib.sha256(f"FLUX:{prompt}".encode("utf-8")).digest()
        # Mock de imagem binária (PNG válido simulado)
        mock_png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x04\x00\x00\x00\x04\x00\x08\x06\x00\x00\x00" + seed_hash

        return self.storage.save_asset(
            content_bytes=mock_png_bytes,
            asset_type="image",
            filename=filename,
            provider_name=self.provider_name,
            width=1084,
            height=1084
        )
