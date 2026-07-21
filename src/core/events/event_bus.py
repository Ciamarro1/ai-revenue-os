from datetime import datetime, timezone
import json
import threading
from typing import Callable, Dict, Any, List, Optional
from src.ports.event import EventPort

class Event:
    """Representa um evento cognitivo trafegado pelo barramento."""
    def __init__(self, event_type: str, payload: Dict[str, Any], timestamp: Optional[str] = None):
        self.event_type = event_type
        self.payload = payload
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp
        }


class EventBus(EventPort):
    """
    Cognitive Event Bus (Sprint 5.7).
    Barramento de eventos síncrono com persistência histórica
    em SQLite para auditoria de traces de decisões de agentes.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventBus, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, db: Optional[Any] = None):
        with self._lock:
            if db:
                self.db = db
            if getattr(self, "_initialized", False):
                return
            if not db:
                self.db = None
            self.handlers: Dict[str, List[Callable[[Event], None]]] = {}
            self.global_handlers: List[Callable[[Event], None]] = []
            self._initialized = True

    def subscribe(self, event_type: str, handler: Callable[[Event], None]):
        """Inscreve um callback para um tipo de evento específico."""
        with self._lock:
            if event_type not in self.handlers:
                self.handlers[event_type] = []
            self.handlers[event_type].append(handler)

    def subscribe_global(self, handler: Callable[[Event], None]):
        """Inscreve um callback global que recebe todos os eventos."""
        with self._lock:
            self.global_handlers.append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[Event], None]):
        """Cancela a inscrição de um callback."""
        with self._lock:
            if event_type in self.handlers:
                try:
                    self.handlers[event_type].remove(handler)
                except ValueError:
                    pass

    def publish(self, event_type: str, payload: Dict[str, Any]) -> Event:
        """
        Publica um evento, grava no SQLite para persistência histórica
        e despacha para todos os subscribers de forma síncrona.
        """
        event = Event(event_type, payload)
        
        # 1. Gravar no SQLite (se o banco estiver configurado)
        if self.db:
            try:
                with self.db._get_conn() as conn:
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO cognitive_events (event_type, payload_json, timestamp)
                        VALUES (?, ?, ?)
                    """, (event.event_type, json.dumps(event.payload), event.timestamp))
                    conn.commit()
            except Exception:
                pass

        # 2. Copiar os handlers sob lock para evitar deadlock na chamada
        handlers_to_call = []
        with self._lock:
            if event_type in self.handlers:
                handlers_to_call.extend(self.handlers[event_type])
            handlers_to_call.extend(self.global_handlers)

        # 3. Chamar handlers
        for handler in handlers_to_call:
            try:
                handler(event)
            except Exception:
                pass

        return event

    def get_event_history(self, event_type: Optional[str] = None, limit: int = 50) -> List[Event]:
        """Recupera o histórico de eventos armazenados no SQLite."""
        if not self.db:
            return []
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                if event_type:
                    c.execute("""
                        SELECT event_type, payload_json, timestamp 
                        FROM cognitive_events 
                        WHERE event_type = ? 
                        ORDER BY id DESC LIMIT ?
                    """, (event_type, limit))
                else:
                    c.execute("""
                        SELECT event_type, payload_json, timestamp 
                        FROM cognitive_events 
                        ORDER BY id DESC LIMIT ?
                    """, (limit,))
                rows = c.fetchall()
            return [Event(row[0], json.loads(row[1]), row[2]) for row in rows]
        except Exception:
            return []

    def clear_listeners(self):
        """Limpa todos os listeners registrados (útil para testes unitários)."""
        with self._lock:
            self.handlers.clear()
            self.global_handlers.clear()
            self.db = None


