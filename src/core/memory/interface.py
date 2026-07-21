from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.ports.memory import MemoryPort

class MemoryProvider(MemoryPort):
    """
    Interface abstrata para provedores de armazenamento de memória episódica
    e declarativa (semântica). Permite desacoplar o kernel cognitivo da escolha física da base.
    """
    @abstractmethod
    def store(self, content: str, memory_type: str, metadata: Dict[str, Any]) -> str:
        """
        Armazena uma memória qualitativa e retorna o ID associado.
        """
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Realiza a busca semântica ou por relevância de memórias.
        Retorna lista de dicionários contendo 'content', 'metadata' e 'score'.
        """
        pass

    @abstractmethod
    def retrieve_context(self, entity: str, limit: int = 3) -> str:
        """
        Recupera e formata um bloco textual contendo as memórias mais relevantes
        para alimentar o prompt do agente.
        """
        pass


