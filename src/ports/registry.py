import threading
from typing import Dict, Type, Any, Union
from src.ports.capabilities import Capabilities

class ProviderRegistry:
    """
    Provider Registry (IoC Container) for AI Revenue OS.
    Maps Ports (or Capability keys/enums) to their corresponding concrete Adapters.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ProviderRegistry, cls).__new__(cls)
                cls._instance._registry = {}
            return cls._instance

    def register(self, key: Union[Type[Any], str, Capabilities], adapter: Any):
        """Registra uma implementação concreta para um determinado Port ou chave de Capability."""
        with self._lock:
            self._registry[key] = adapter

    def resolve(self, key: Union[Type[Any], str, Capabilities]) -> Any:
        """Resolve a implementação registrada para o Port ou Capability especificado."""
        with self._lock:
            if key not in self._registry:
                name = key.value if isinstance(key, Capabilities) else (key if isinstance(key, str) else key.__name__)
                raise ValueError(f"Capability/Port {name} has no registered adapter.")
            return self._registry[key]

    def has_capability(self, key: Union[Type[Any], str, Capabilities]) -> bool:
        """Verifica se há algum adaptador ativo para o Port ou Capability especificado."""
        with self._lock:
            return key in self._registry

    def clear(self):
        """Limpa todos os registros (útil para isolamento de testes unitários)."""
        with self._lock:
            self._registry.clear()
