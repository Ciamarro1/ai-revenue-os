from typing import Any, Dict, List
from src.core.memory.interface import MemoryProvider

class MemoryRetriever:
    """
    Memory Retrieval Layer (Sprint 5).
    Orquestra a busca qualitativa de memórias episódicas e aprendizados
    para construir blocos contextuais ricos e injetar nos prompts de agentes.
    """
    def __init__(self, provider: MemoryProvider):
        self.provider = provider

    def get_agent_context(self, current_niche: str, query: str, limit: int = 3) -> str:
        """
        Gera o contexto injetável consolidando o nicho atual e termos de busca.
        """
        combined_query = f"{current_niche} {query}"
        context_data = self.provider.retrieve_context(combined_query, limit=limit)
        
        return f"""=== MEMÓRIAS OPERACIONAIS E APRENDIZADOS ANTERIORES ===
{context_data}
======================================================
"""

