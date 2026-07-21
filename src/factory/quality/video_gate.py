import os
import logging
from src.factory.schemas import GeneratedAsset

logger = logging.getLogger("factory.quality")

class VideoQualityGate:
    """Verifica a integridade do vídeo gerado antes de ser aprovado para publicação."""
    
    @classmethod
    def check_quality(cls, asset: GeneratedAsset) -> bool:
        if not os.path.exists(asset.path):
            logger.error(f"❌ [VideoQualityGate] Arquivo não encontrado: {asset.path}")
            return False
            
        size_bytes = os.path.getsize(asset.path)
        if size_bytes < 1024 * 10: # 10 KB mínimo
            logger.error(f"❌ [VideoQualityGate] Arquivo muito pequeno (corrompido?): {size_bytes} bytes")
            return False
            
        if asset.duration < 5.0:
            logger.error(f"❌ [VideoQualityGate] Vídeo muito curto: {asset.duration}s (Mínimo: 5.0s)")
            return False
            
        logger.info("✅ [VideoQualityGate] Vídeo passou nas verificações de integridade física.")
        return True
