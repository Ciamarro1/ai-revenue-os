"""
Embedding Pipeline.

Converte texto em vetores numéricos para indexação no Qdrant.
Usa `sentence-transformers` quando disponível, com fallback para
um vetorizador hash leve que funciona sem GPU ou dependências pesadas.
"""
import hashlib
import logging
from typing import List, Optional
from src.ports.embedding import EmbeddingPort

logger = logging.getLogger(__name__)

# Tenta carregar sentence-transformers (dependência opcional do grupo [vector])
_SBERT_AVAILABLE = False
_sbert_model = None

try:
    from sentence_transformers import SentenceTransformer
    _SBERT_AVAILABLE = True
except ImportError:
    SentenceTransformer = None

# Dimensão padrão usada pelo modelo 'all-MiniLM-L6-v2'
DEFAULT_VECTOR_SIZE = 384


def _get_sbert_model():
    """Lazy-loading do modelo de embeddings."""
    global _sbert_model
    if _sbert_model is None and _SBERT_AVAILABLE:
        _sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _sbert_model


class EmbeddingPipeline(EmbeddingPort):
    """
    Pipeline de embeddings text-to-vector com fallback gracioso.

    Estratégia:
      1. Se sentence-transformers está instalado → embedding denso real (384-dim).
      2. Senão → hash-based vectorizer leve (384-dim), usado apenas para
         desenvolvimento local e testes sem GPU.
    """
    def __init__(self, vector_size: int = DEFAULT_VECTOR_SIZE):
        self.vector_size = vector_size
        self._use_sbert = _SBERT_AVAILABLE

    @property
    def backend(self) -> str:
        """Retorna o nome do backend de embedding ativo."""
        return "sentence-transformers" if self._use_sbert else "hash-fallback"

    def embed(self, text: str) -> List[float]:
        """Converte um texto em vetor numérico."""
        if self._use_sbert:
            return self._embed_sbert(text)
        return self._embed_hash(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Converte múltiplos textos em vetores numéricos."""
        if self._use_sbert:
            return self._embed_sbert_batch(texts)
        return [self._embed_hash(t) for t in texts]

    def _embed_sbert(self, text: str) -> List[float]:
        """Embedding via sentence-transformers (denso, cosine-ready)."""
        model = _get_sbert_model()
        vector = model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def _embed_sbert_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch embedding via sentence-transformers."""
        model = _get_sbert_model()
        vectors = model.encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vectors]

    def _embed_hash(self, text: str) -> List[float]:
        """
        Fallback: vetorização baseada em hash determinístico.
        Gera um vetor pseudo-aleatório reprodutível a partir do texto.
        Útil para testes e ambientes sem GPU.
        """
        # Normaliza o texto
        normalized = text.strip().lower()
        # Gera hash SHA-256 e expande para preencher o vetor
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        
        vector = []
        # Expande o hash para atingir vector_size dimensões
        rounds = (self.vector_size // 32) + 1
        for i in range(rounds):
            sub_hash = hashlib.sha256(f"{digest}:{i}".encode("utf-8")).hexdigest()
            for j in range(0, len(sub_hash), 2):
                if len(vector) >= self.vector_size:
                    break
                # Converte 2 hex chars em float [-1, 1]
                byte_val = int(sub_hash[j:j+2], 16)
                vector.append((byte_val / 127.5) - 1.0)
        
        # Normalização L2
        magnitude = sum(v * v for v in vector) ** 0.5
        if magnitude > 0:
            vector = [v / magnitude for v in vector]
        
        return vector[:self.vector_size]


