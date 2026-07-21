from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class EventPort(ABC):
    """
    Event Port interface.
    Decouples the Cognitive Kernel event messaging (SQLite, NATS, Kafka, Redis Streams).
    """
    @abstractmethod
    def publish(self, event_type: str, payload: Dict[str, Any]) -> Any:
        """Publica um evento cognitivo e o persiste para logs históricos."""
        pass

    @abstractmethod
    def get_event_history(self, event_type: Optional[str] = None, limit: int = 50) -> List[Any]:
        """Busca o histórico de eventos gravados."""
        pass
