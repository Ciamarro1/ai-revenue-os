import hashlib
from src.revenue_os.plugins.creatives.providers.base_creative_provider import BaseImageProvider
from src.revenue_os.plugins.creatives.storage_manager import CreativeStorageManager
from src.revenue_os.plugins.creatives.models import GeneratedCreativeAsset

class ComfyUIImageProvider(BaseImageProvider):
    """
    Provedor Gerativo ComfyUI para workflows de imagem.
    """

    def __init__(self, storage_manager: CreativeStorageManager = None, enabled: bool = True):
        self.storage = storage_manager or CreativeStorageManager()
        self._enabled = enabled

    @property
    def provider_name(self) -> str:
        return "comfyui"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def generate_image(self, prompt: str, filename: str = "comfyui_render.png") -> GeneratedCreativeAsset:
        if not self._enabled:
            raise RuntimeError("ComfyUIImageProvider is disabled.")

        seed_hash = hashlib.sha256(f"COMFYUI:{prompt}".encode("utf-8")).digest()
        mock_png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x04\x00\x00\x00\x04\x00\x08\x06\x00\x00\x00" + seed_hash

        return self.storage.save_asset(
            content_bytes=mock_png_bytes,
            asset_type="image",
            filename=filename,
            provider_name=self.provider_name,
            width=1080,
            height=1920
        )
