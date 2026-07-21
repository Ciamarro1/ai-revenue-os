"""
LlamaIndex Retriever — Semantic Retrieval Wrapper.

Executa buscas semânticas contra a coleção Qdrant.
Quando LlamaIndex está indisponível, delega diretamente ao Qdrant client.
"""
import logging
from typing import Any, List, Dict, Optional

from src.adapters.qdrant.client import QdrantConnector, _QDRANT_AVAILABLE
from src.adapters.qdrant.embedding import EmbeddingPipeline
from src.adapters.qdrant.collection_manager import COLLECTION_NAME

if _QDRANT_AVAILABLE:
    from qdrant_client.models import Filter

logger = logging.getLogger(__name__)


class SemanticRetriever:
    """
    Retriever semântico que consulta o Qdrant usando embeddings de query.

    Fluxo:
      Query string → EmbeddingPipeline → Qdrant cosine search → ranked results
    """
    def __init__(
        self,
        connector: QdrantConnector,
        embedding_pipeline: Optional[EmbeddingPipeline] = None,
    ):
        self.connector = connector
        self.embedder = embedding_pipeline or EmbeddingPipeline()

    def retrieve(
        self, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Busca os `top_k` documentos mais similares semanticamente à query.

        Retorna lista de dicts com:
          - content (str)
          - metadata (dict)
          - score (float): similaridade coseno [0, 1]
        """
        if not self.connector.is_connected:
            return []

        try:
            query_vector = self.embedder.embed(query)
            results = self.connector.client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vector,
                limit=top_k,
            )
            return [
                {
                    "content": hit.payload.get("content", ""),
                    "metadata": hit.payload.get("metadata", {}),
                    "score": hit.score,
                    "id": str(hit.id),
                }
                for hit in results
            ]
        except Exception as e:
            logger.warning(f"Erro na busca semântica Qdrant: {e}")
            return []


