import hashlib
from src.revenue_os.plugins.creatives.providers.base_creative_provider import BaseVideoProvider
from src.revenue_os.plugins.creatives.storage_manager import CreativeStorageManager
from src.revenue_os.plugins.creatives.models import GeneratedCreativeAsset

class MoneyPrinterTurboVideoProvider(BaseVideoProvider):
    """
    Provedor Gerativo MoneyPrinterTurbo (Vídeos Verticais 9:16 com voz, b-roll e legendas).
    """

    def __init__(self, storage_manager: CreativeStorageManager = None, enabled: bool = True):
        self.storage = storage_manager or CreativeStorageManager()
        self._enabled = enabled

    @property
    def provider_name(self) -> str:
        return "money_printer_turbo"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def generate_video(self, prompt: str, filename: str = "mpt_render.mp4") -> GeneratedCreativeAsset:
        if not self._enabled:
            raise RuntimeError("MoneyPrinterTurboVideoProvider is disabled.")

        seed_hash = hashlib.sha256(f"MPT:{prompt}".encode("utf-8")).digest()
        mock_mp4_bytes = b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2avc1mp41" + seed_hash

        return self.storage.save_asset(
            content_bytes=mock_mp4_bytes,
            asset_type="video",
            filename=filename,
            provider_name=self.provider_name,
            width=1080,
            height=1920,
            duration_sec=45.0
        )
