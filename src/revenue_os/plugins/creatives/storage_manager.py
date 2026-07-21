import os
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from src.revenue_os.plugins.creatives.models import GeneratedCreativeAsset

class CreativeStorageManager:
    """
    Gerenciador de Armazenamento Físico de Ativos da Fábrica Criativa.
    Responsável por salvar imagens e vídeos, calcular fingerprints SHA-256 e etiquetar versionamento.
    """

    def __init__(self, base_dir: str = "storage/creatives"):
        self.base_dir = Path(base_dir)
        self.images_dir = self.base_dir / "images"
        self.videos_dir = self.base_dir / "videos"
        self._ensure_directories()

    def _ensure_directories(self):
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.videos_dir.mkdir(parents=True, exist_ok=True)

    def compute_sha256(self, content_bytes: bytes) -> str:
        return hashlib.sha256(content_bytes).hexdigest()

    def save_asset(
        self,
        content_bytes: bytes,
        asset_type: str,
        filename: str,
        provider_name: str,
        width: int = 1080,
        height: int = 1920,
        duration_sec: float = 0.0
    ) -> GeneratedCreativeAsset:
        """
        Salva o conteúdo em disco, calcula o SHA-256 e gera o manifesto do ativo.
        """
        self._ensure_directories()
        target_dir = self.videos_dir if asset_type == "video" else self.images_dir
        file_path = target_dir / filename

        with open(file_path, "wb") as f:
            f.write(content_bytes)

        content_hash = self.compute_sha256(content_bytes)
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        version = f"v1.0.0-{asset_type[:3]}-{timestamp_str}"
        asset_id = f"AST-{asset_type[:3].upper()}-{content_hash[:8]}"

        mime_type = "video/mp4" if asset_type == "video" else "image/png"

        return GeneratedCreativeAsset(
            asset_id=asset_id,
            asset_type=asset_type,
            provider_name=provider_name,
            file_path=str(file_path),
            content_hash=content_hash,
            version=version,
            width=width,
            height=height,
            duration_sec=duration_sec,
            mime_type=mime_type,
            classification_status="LOCAL_TEST"
        )
