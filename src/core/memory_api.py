from typing import List, Dict, Any
from src.core.memory.interface import MemoryProvider
from src.core.memory.retrieval import MemoryRetriever

class MemoryAPI:
    """
    Memory Facade API.
    Isola o armazenamento qualitativo e o RAG semântico contextual para prompts de agentes.
    """
    def __init__(self, provider: MemoryProvider, retriever: MemoryRetriever):
        self.provider = provider
        self.retriever = retriever

    def store(self, content: str, memory_type: str, metadata: Dict[str, Any]) -> str:
        """Armazena uma nova memória de longo prazo (SQLite + Qdrant)."""
        return self.provider.store(content, memory_type, metadata)

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Realiza busca semântica/qualitativa por relevância."""
        return self.provider.search(query, limit)

    def get_context(self, current_niche: str, query: str, limit: int = 3) -> str:
        """Gera o bloco contextual formatado pronto para injeção no prompt do agente."""
        return self.retriever.get_agent_context(current_niche, query, limit)

