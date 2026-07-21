"""
Qdrant Vector Database — Connection Adapter.

Gerencia a conexão com o servidor Qdrant local (via Docker)
com health-check, timeout configurável e configuração por variáveis de ambiente.
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Flags de disponibilidade — definidos na importação
_QDRANT_AVAILABLE = False
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    _QDRANT_AVAILABLE = True
except ImportError:
    QdrantClient = None
    Distance = None
    VectorParams = None
    PointStruct = None


def is_qdrant_available() -> bool:
    """Retorna True se a biblioteca qdrant-client está instalada."""
    return _QDRANT_AVAILABLE


class QdrantConnector:
    """
    Adapter de conexão para o Qdrant Vector Database.

    Configuração via variáveis de ambiente:
      - QDRANT_HOST (default: localhost)
      - QDRANT_PORT (default: 6333)
      - QDRANT_TIMEOUT (default: 2.0)
    """
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        timeout: Optional[float] = None,
    ):
        self.host = host or os.getenv("QDRANT_HOST", "localhost")
        self.port = port or int(os.getenv("QDRANT_PORT", "6333"))
        self.timeout = timeout or float(os.getenv("QDRANT_TIMEOUT", "2.0"))
        self.client: Optional["QdrantClient"] = None
        self._connected = False

    def connect(self) -> bool:
        """
        Tenta estabelecer conexão com o servidor Qdrant.
        Retorna True se o servidor está saudável.
        """
        if not _QDRANT_AVAILABLE:
            logger.info("qdrant-client não instalado — usando fallback SQLite.")
            return False
        try:
            self.client = QdrantClient(
                host=self.host,
                port=self.port,
                timeout=self.timeout,
            )
            # Health check real: tenta listar coleções
            self.client.get_collections()
            self._connected = True
            logger.info(f"Qdrant conectado em {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.warning(f"Qdrant indisponível ({e}) — usando fallback SQLite.")
            self.client = None
            self._connected = False
            return False

    @property
    def is_connected(self) -> bool:
        return self._connected and self.client is not None

    def disconnect(self):
        """Encerra a conexão com o Qdrant."""
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass
        self.client = None
        self._connected = False
