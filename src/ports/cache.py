from abc import ABC, abstractmethod
from typing import Any, Optional

class CachePort(ABC):
    """
    Cache Port interface.
    Decouples transient caching systems (Redis, SQLite Cache, in-memory Cache).
    """
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Recupera um valor armazenado no cache pelo identificador da chave."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Armazena um valor no cache com tempo de expiração opcional."""
        pass

    @abstractmethod
    def delete(self, key: str):
        """Remove o item do cache correspondente à chave."""
        pass
