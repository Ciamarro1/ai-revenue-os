import logging
from typing import Optional, Any
from src.ports import ProviderRegistry, KernelConfig, MemoryPort, EventPort
from src.core.kernel import CognitiveKernel

logger = logging.getLogger(__name__)

class Runtime:
    """
    Application Runtime (Sprint 5.12).
    Manages dependency injection, container bootstrapping, configuration parsing,
    and returns a fully instantiated and configured CognitiveKernel.
    """
    def __init__(self, config: Optional[KernelConfig] = None):
        self.config = config or KernelConfig()
        self.config.load_manifest()  # Carrega automaticamente se o arquivo JSON existir
        self.registry = ProviderRegistry()
        self.kernel: Optional[CognitiveKernel] = None

    def bootstrap(self, db_connection: Any) -> CognitiveKernel:
        """
        Registra os adaptadores de infraestrutura e inicializa a fachada CognitiveKernel.
        """
        logger.info("Bootstrapping Hexagonal Runtime...")
        
        # 1. Resolver/Injetar adaptadores padrão caso não registrados
        # Para testes e compatibilidade retroativa, a inicialização clássica do CognitiveKernel
        # cuida de instanciar as conexões caso o registry esteja vazio.
        # Mas aqui no Runtime, nós registramos as instâncias ativamente.
        
        self.kernel = CognitiveKernel(
            db=db_connection,
            qdrant_host=self.config.memory.qdrant_host,
            qdrant_port=self.config.memory.qdrant_port
        )
        
        logger.info("CognitiveKernel initialized successfully.")
        return self.kernel
