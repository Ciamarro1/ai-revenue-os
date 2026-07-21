from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePlugin(ABC):
    """
    Contrato Único do Plugin Runtime (Sprint 9.7).
    Todo plugin do AI Revenue OS deve implementar esta interface unificada.
    """

    @property
    @abstractmethod
    def plugin_name(self) -> str:
        pass

    @property
    @abstractmethod
    def category(self) -> str:  # e.g., landing, analytics, marketplaces, social, video, image, email, seo
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """
        Inicializa recursos, conexões ou SDKs do plugin.
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Retorna o status de saúde e disponibilidade operacional do plugin.
        """
        pass

    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa a capacidade solicitada.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        Encerra conexões e libera recursos de memória.
        """
        pass
