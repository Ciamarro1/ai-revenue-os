from abc import ABC, abstractmethod
from typing import List, Dict, Any

class MemoryPort(ABC):
    """
    Memory Port interface.
    Decouples the Cognitive Kernel from vector databases (Qdrant, Weaviate, Milvus).
    """
    @abstractmethod
    def store(self, content: str, memory_type: str, metadata: Dict[str, Any]) -> str:
        """Armazena uma memória qualitativa e retorna o ID associado."""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Realiza busca qualitativa por relevância semântica."""
        pass

    @abstractmethod
    def retrieve_context(self, entity: str, limit: int = 3) -> str:
        """Formata e retorna um bloco contextual para injeção em prompts."""
        pass
