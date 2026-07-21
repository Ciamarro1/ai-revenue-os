"""
Qdrant Collection Manager.

Gerencia o ciclo de vida das coleções vetoriais no Qdrant,
garantindo que a coleção `ai_revenue_memories` exista com as dimensões corretas.
"""
import logging
from typing import Optional

from src.adapters.qdrant.client import QdrantConnector, _QDRANT_AVAILABLE

if _QDRANT_AVAILABLE:
    from qdrant_client.models import Distance, VectorParams

logger = logging.getLogger(__name__)

# Nome da coleção padrão do AI Revenue OS
COLLECTION_NAME = "ai_revenue_memories"


class CollectionManager:
    """
    Garante a existência e configuração correta das coleções vetoriais
    no servidor Qdrant.
    """
    def __init__(self, connector: QdrantConnector, vector_size: int = 384):
        self.connector = connector
        self.vector_size = vector_size

    def ensure_collection(self) -> bool:
        """
        Cria a coleção padrão se ela ainda não existir.
        Retorna True se a coleção está pronta para uso.
        """
        if not self.connector.is_connected:
            return False
        try:
            collections = self.connector.client.get_collections().collections
            existing_names = [c.name for c in collections]

            if COLLECTION_NAME not in existing_names:
                self.connector.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(
                    f"Coleção '{COLLECTION_NAME}' criada "
                    f"(dim={self.vector_size}, distance=COSINE)."
                )
            else:
                logger.info(f"Coleção '{COLLECTION_NAME}' já existe.")
            return True
        except Exception as e:
            logger.warning(f"Erro ao garantir coleção Qdrant: {e}")
            return False

    def get_collection_info(self) -> Optional[dict]:
        """Retorna informações sobre a coleção, ou None se indisponível."""
        if not self.connector.is_connected:
            return None
        try:
            info = self.connector.client.get_collection(COLLECTION_NAME)
            return {
                "name": COLLECTION_NAME,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "status": str(info.status),
            }
        except Exception:
            return None


