from typing import List, Dict, Any, Optional
from src.core.events.event_bus import EventBus, Event

class EventAPI:
    """
    Event Facade API.
    Isola a publicação e leitura de histórico de eventos do barramento cognitivo.
    """
    def __init__(self, event_bus: EventBus):
        self.bus = event_bus

    def publish(self, event_type: str, payload: Dict[str, Any]) -> Event:
        """Publica um evento no barramento síncrono e persiste no SQLite."""
        return self.bus.publish(event_type, payload)

    def get_history(self, event_type: Optional[str] = None, limit: int = 50) -> List[Event]:
        """Busca o histórico completo ou filtrado por tipo de evento."""
        return self.bus.get_event_history(event_type, limit)

