import os
import logging
from src.factory.schemas import GeneratedAsset

logger = logging.getLogger("factory.quality")


class ImageQualityGate:
    """
    Verifica a integridade física de uma imagem gerada antes da publicação.
    Análogo ao VideoQualityGate, mas para assets estáticos.
    """

    MIN_SIZE_BYTES = 10 * 1024  # 10 KB mínimo

    VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

    @classmethod
    def check_quality(cls, asset: GeneratedAsset) -> bool:
        # 1. Arquivo existe no disco
        if not os.path.exists(asset.path):
            logger.error(f"[ImageQualityGate] Arquivo não encontrado: {asset.path}")
            return False

        # 2. Tamanho mínimo (arquivo não corrompido/vazio)
        size_bytes = os.path.getsize(asset.path)
        if size_bytes < cls.MIN_SIZE_BYTES:
            logger.error(f"[ImageQualityGate] Arquivo muito pequeno ({size_bytes} bytes). Provável corrupção.")
            return False

        # 3. Extensão válida para imagem
        ext = os.path.splitext(asset.path)[1].lower()
        if ext not in cls.VALID_EXTENSIONS:
            logger.error(f"[ImageQualityGate] Extensão inválida para imagem: {ext}")
            return False

        # 4. Conteúdo aprovado obrigatório (título e descrição não podem ser nulos)
        if not asset.approved_title:
            logger.error("[ImageQualityGate] approved_title ausente. O Copywriter deve ter aprovado o conteúdo.")
            return False

        if not asset.approved_description:
            logger.error("[ImageQualityGate] approved_description ausente. O Copywriter deve ter aprovado o conteúdo.")
            return False

        logger.info(f"[ImageQualityGate] Imagem '{asset.path}' aprovada ({size_bytes} bytes).")
        return True
