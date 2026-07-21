from abc import ABC, abstractmethod
from typing import List

class EmbeddingPort(ABC):
    """
    Embedding Port interface.
    Decouples text-to-vector pipeline backends (FastEmbed, SentenceTransformers, OpenAI, etc.).
    """
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Converte um texto em vetor de números (floats)."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Converte múltiplos textos em vetores."""
        pass
