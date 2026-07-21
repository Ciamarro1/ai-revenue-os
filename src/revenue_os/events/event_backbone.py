import logging
from typing import Dict, List, Callable, Any, Optional
from src.revenue_os.events.domain_events import DomainEvent

class EventBackbone:
    """
    Barramento de Eventos de Domínio (Sprint 9.8 Event Backbone).
    Implementa Pub/Sub desacoplado desacoplando os módulos da aplicação.
    Cada plugin ou engine pode assinar tópicos de eventos sem conhecer os emissores.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[DomainEvent], None]]] = {}
        self._event_history: List[DomainEvent] = []

    def subscribe(self, event_type: str, listener: Callable[[DomainEvent], None]) -> None:
        """
        Registra uma função ou ouvinte para um tipo específico de evento.
        """
        key = event_type.lower()
        if key not in self._subscribers:
            self._subscribers[key] = []
        self._subscribers[key].append(listener)

    def publish(self, event: DomainEvent) -> int:
        """
        Publica um evento de domínio para todos os ouvintes inscritos.
        """
        self._event_history.append(event)
        key = event.event_type.lower()
        listeners = self._subscribers.get(key, [])
        
        # Também notifica inscritos no wildcard '*'
        wildcard_listeners = self._subscribers.get("*", [])

        notified_count = 0
        for listener in listeners + wildcard_listeners:
            try:
                listener(event)
                notified_count += 1
            except Exception as e:
                logging.error(f"Erro ao processar evento '{event.event_type}' no ouvinte {listener}: {e}")

        return notified_count

    def get_history(self, event_type: Optional[str] = None) -> List[DomainEvent]:
        if event_type is None:
            return self._event_history
        return [e for e in self._event_history if e.event_type.lower() == event_type.lower()]
