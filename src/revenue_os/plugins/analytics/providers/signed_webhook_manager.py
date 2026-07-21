import hmac
import hashlib
import json
from typing import Dict, Any
from src.revenue_os.plugins.analytics.models import MetricProvenance

class SignedWebhookManager:
    """
    Gerenciador de Webhooks Assinados com HMAC-SHA256.
    Garante autenticidade e não-repúdio de eventos e callbacks recebidos de parceiros.
    """

    def __init__(self, secret_key: str = "ai_revenue_os_secure_webhook_secret_key"):
        self.secret_key = secret_key.encode("utf-8")

    def sign_payload(self, payload: Dict[str, Any]) -> str:
        """
        Calcula a assinatura HMAC-SHA256 de um dicionário de payload.
        """
        raw_body = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hmac.new(self.secret_key, raw_body, hashlib.sha256).hexdigest()

    def verify_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """
        Verifica se a assinatura HMAC-SHA256 bate com o payload.
        """
        if not signature:
            return False
        expected_sig = self.sign_payload(payload)
        return hmac.compare_digest(expected_sig.lower(), signature.lower())

    def create_signed_provenance(self, payload: Dict[str, Any], signature: str) -> MetricProvenance:
        is_valid = self.verify_signature(payload, signature)
        return MetricProvenance(
            provenance_type="REAL_PRODUCTION" if is_valid else "LOCAL_TEST",
            signature=signature,
            signature_verified=is_valid
        )
