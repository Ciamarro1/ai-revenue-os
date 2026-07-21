from abc import ABC, abstractmethod
from typing import Optional

class SecretPort(ABC):
    """
    Secret Port interface.
    Decouples credentials management (env files, AWS Secrets Manager, Vault, Bitwarden).
    """
    @abstractmethod
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Recupera o valor associado a uma chave de segredo."""
        pass

    @abstractmethod
    def set_secret(self, key: str, value: str):
        """Persiste ou sobrescreve uma credencial de forma segura."""
        pass
