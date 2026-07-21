"""
Vector Memory Provider — Qdrant-backed semantic memory with SQLite fallback.

Dual-write architecture:
  - Sempre persiste no SQLite local (durabilidade garantida, busca por Jaccard).
  - Quando Qdrant está disponível, também indexa embeddings vetoriais
    para busca coseno de alta qualidade.
  - Se Qdrant falha ou está offline, degrada graciosamente para SQLite.
"""
import json
import logging
import uuid
from typing import List, Dict, Any, Optional

from src.core.memory.interface import MemoryProvider
from src.core.memory.sqlite_memory import SQLiteMemoryProvider
from src.adapters.qdrant.client import QdrantConnector, _QDRANT_AVAILABLE
from src.adapters.qdrant.embedding import EmbeddingPipeline
from src.adapters.qdrant.collection_manager import CollectionManager, COLLECTION_NAME

if _QDRANT_AVAILABLE:
    from qdrant_client.models import PointStruct

logger = logging.getLogger(__name__)


class VectorMemoryProvider(MemoryProvider):
    """
    Provedor de memória vetorial com dual-write (Qdrant + SQLite).

    Arquitetura:
      store()  → SQLite (sempre) + Qdrant (quando disponível)
      search() → Qdrant (quando disponível) | SQLite (fallback)

    O SQLite garante durabilidade e disponibilidade offline.
    O Qdrant fornece busca semântica de alta qualidade via coseno.
    """
    def __init__(
        self,
        db: Any,
        fallback_provider: Optional[SQLiteMemoryProvider] = None,
        qdrant_host: Optional[str] = None,
        qdrant_port: Optional[int] = None,
    ):
        self.db = db
        self.fallback = fallback_provider or SQLiteMemoryProvider(db)
        self.connector = QdrantConnector(host=qdrant_host, port=qdrant_port)
        self.embedder = EmbeddingPipeline()
        self.collection_mgr = CollectionManager(
            self.connector, vector_size=self.embedder.vector_size
        )
        self.qdrant_ready = False
        self._init_qdrant()

    def _init_qdrant(self):
        """Tenta conectar ao Qdrant e garantir a coleção."""
        if self.connector.connect():
            if self.collection_mgr.ensure_collection():
                self.qdrant_ready = True
                logger.info(
                    f"VectorMemoryProvider: Qdrant ativo "
                    f"(backend={self.embedder.backend})"
                )

    # -- Propriedade de compatibilidade com testes legados --
    @property
    def qdrant_client(self):
        """Retorna o client Qdrant bruto, ou None se offline."""
        return self.connector.client if self.qdrant_ready else None

    def store(self, content: str, memory_type: str, metadata: Dict[str, Any]) -> str:
        """
        Persiste a memória com dual-write:
          1. Sempre grava no SQLite local (fonte de verdade durável).
          2. Se Qdrant disponível, também indexa o embedding vetorial.
        """
        # 1. SQLite — sempre
        sqlite_id = self.fallback.store(content, memory_type, metadata)

        # 2. Qdrant — quando disponível
        if self.qdrant_ready:
            try:
                vector = self.embedder.embed(content)
                point_id = str(uuid.uuid4())
                point = PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "content": content,
                        "memory_type": memory_type,
                        "metadata": metadata,
                        "sqlite_id": sqlite_id,
                    },
                )
                self.connector.client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=[point],
                )
            except Exception as e:
                logger.warning(f"Qdrant upsert falhou, SQLite preservado: {e}")

        return sqlite_id

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Busca memórias relevantes.
        Prioriza Qdrant (cosine similarity) quando disponível,
        senão usa SQLite (Jaccard token similarity).
        """
        if self.qdrant_ready:
            try:
                query_vector = self.embedder.embed(query)
                hits = self.connector.client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=query_vector,
                    limit=limit,
                )
                results = []
                for hit in hits:
                    results.append({
                        "id": str(hit.payload.get("sqlite_id", hit.id)),
                        "memory_type": hit.payload.get("memory_type", "unknown"),
                        "content": hit.payload.get("content", ""),
                        "metadata": hit.payload.get("metadata", {}),
                        "score": hit.score,
                    })
                return results
            except Exception as e:
                logger.warning(f"Qdrant search falhou, usando SQLite: {e}")

        # Fallback — SQLite Jaccard
        return self.fallback.search(query, limit)

    def retrieve_context(self, entity: str, limit: int = 3) -> str:
        """
        Recupera e formata contexto de memórias para injeção no prompt.
        Usa o provedor ativo (Qdrant ou SQLite).
        """
        memories = self.search(entity, limit=limit)
        if not memories:
            return "Nenhuma experiência episódica ou aprendizado anterior relevante recuperado."

        blocks = []
        for idx, m in enumerate(memories, 1):
            meta = m.get("metadata", {})
            meta_str = ", ".join(f"{k}: {v}" for k, v in meta.items())
            score_info = f", Score: {m['score']:.2f}" if "score" in m else ""
            blocks.append(
                f"[{idx}] {m['content']} "
                f"(Tipo: {m['memory_type']}, Metadados: {{{meta_str}}}{score_info})"
            )

        return "\n".join(blocks)



