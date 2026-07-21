import logging
from typing import Dict, Any
from src.ports import ProviderRegistry, MemoryPort, EventPort

logger = logging.getLogger(__name__)

class Lifecycle:
    """
    Lifecycle Manager (Sprint 5.12).
    Coordinates start-up checks, runtime provider connectivity audits,
    and shutdown cleanups.
    """
    def __init__(self):
        self.registry = ProviderRegistry()

    def health_check(self) -> Dict[str, Any]:
        """
        Executa auditorias de conectividade em todos os adaptadores registrados.
        """
        logger.info("Executing operational health checks...")
        status = {
            "status": "healthy",
            "capabilities": {}
        }

        # 1. Verificar barramento de eventos (EventPort)
        if self.registry.has_capability(EventPort):
            try:
                self.registry.resolve(EventPort).get_event_history(limit=1)
                status["capabilities"]["event_bus"] = "connected"
            except Exception as e:
                status["capabilities"]["event_bus"] = f"degraded: {str(e)}"
                status["status"] = "degraded"
        else:
            status["capabilities"]["event_bus"] = "missing"
            status["status"] = "degraded"

        # 2. Verificar memória (MemoryPort)
        if self.registry.has_capability(MemoryPort):
            try:
                # Faz um search simples para testar a saúde do backend de memória
                self.registry.resolve(MemoryPort).search("health check test", limit=1)
                status["capabilities"]["memory"] = "connected"
            except Exception as e:
                status["capabilities"]["memory"] = f"degraded: {str(e)}"
                status["status"] = "degraded"
        else:
            status["capabilities"]["memory"] = "missing"
            status["status"] = "degraded"

        return status

    def shutdown(self):
        """
        Desconecta e limpa recursos persistentes de todos os provedores ativos.
        """
        logger.info("Initiating runtime shutdown...")
        # Limpar registros do container IoC
        self.registry.clear()
        logger.info("Shutdown completed.")
