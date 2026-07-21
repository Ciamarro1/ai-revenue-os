from abc import ABC, abstractmethod
from typing import List, Dict, Any

class SearchPort(ABC):
    """
    Search Port interface.
    Decouples web search integrations (Tavily, Exa, Serper, Brave Search).
    """
    @abstractmethod
    def search_web(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Realiza busca web e retorna resultados contendo URL, título e trecho."""
        pass
