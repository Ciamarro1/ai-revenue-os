import os
import re
from typing import Dict, Any, Optional

class SecretsManager:
    """
    Secrets Manager & Governança de Configuração de Segurança (Sprint P1).
    Isola tokens, chaves de API e credenciais de marketplaces evitando vazamentos em logs ou repositórios.
    """

    def __init__(self, environment: Optional[str] = None):
        self.environment = environment or os.getenv("APP_ENV", "development").lower()

    def get_secret(self, secret_key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Recupera com segurança um segredo de ambiente.
        """
        val = os.getenv(secret_key, default)
        return val

    def mask_secret(self, secret_value: Optional[str]) -> str:
        """
        Mascara segredos para exibição segura em logs e auditorias.
        Ex: 'sk-proj-123456789' -> 'sk-p...6789'
        """
        if not secret_value or len(secret_value) < 8:
            return "********"
        return f"{secret_value[:4]}...{secret_value[-4:]}"

    def audit_security_governance(self) -> Dict[str, Any]:
        """
        Executa auditoria de segredos e separação de ambientes.
        """
        required_keys = ["OPENAI_API_KEY", "PINTEREST_ACCESS_TOKEN", "HOTMART_API_SECRET", "DATABASE_URL"]
        missing = [k for k in required_keys if not os.getenv(k)]

        return {
            "environment": self.environment,
            "is_production": self.environment == "production",
            "configured_keys_count": len(required_keys) - len(missing),
            "missing_keys": missing,
            "security_status": "SECURE" if not missing else "DEGRADED_MISSING_KEYS"
        }
