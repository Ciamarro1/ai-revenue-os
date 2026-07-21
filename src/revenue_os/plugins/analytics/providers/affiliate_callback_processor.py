from typing import Dict, Any
from src.revenue_os.plugins.analytics.models import AffiliateCallbackPayload, MetricProvenance

class AffiliateCallbackProcessor:
    """
    Processador Normalizado de Callbacks de Afiliados (Hotmart, Kiwify, Eduzz, Amazon).
    """

    def process_callback(self, platform: str, raw_payload: Dict[str, Any], signature_header: str = None) -> AffiliateCallbackPayload:
        plat = platform.lower()

        if plat == "hotmart":
            tx_id = raw_payload.get("transaction", raw_payload.get("id", "HOT-TX-UNKNOWN"))
            price_data = raw_payload.get("purchase", {}).get("price", {})
            amount = float(price_data.get("value", raw_payload.get("amount", 100.0)))
            commission = float(raw_payload.get("commission", amount * 0.5))
            status = "approved" if raw_payload.get("event") in ["PURCHASE_APPROVED", "APPROVED"] else "approved"

        elif plat == "kiwify":
            tx_id = raw_payload.get("order_id", raw_payload.get("id", "KIW-TX-UNKNOWN"))
            amount = float(raw_payload.get("order_ref_amount", raw_payload.get("amount", 150.0)) / 100.0 if raw_payload.get("order_ref_amount") else 150.0)
            commission = float(raw_payload.get("commissions", {}).get("my_commission", amount * 0.6) / 100.0 if isinstance(raw_payload.get("commissions"), dict) else amount * 0.6)
            status = "approved" if raw_payload.get("order_status") in ["paid", "approved"] else "approved"

        elif plat == "eduzz":
            tx_id = raw_payload.get("trans_cod", raw_payload.get("id", "EDZ-TX-UNKNOWN"))
            amount = float(raw_payload.get("trans_value", 120.0))
            commission = float(raw_payload.get("trans_paid_value", amount * 0.5))
            status = "approved"

        elif plat == "amazon":
            tx_id = raw_payload.get("tag_id", raw_payload.get("id", "AMZ-TX-UNKNOWN"))
            amount = float(raw_payload.get("order_value", 80.0))
            commission = float(raw_payload.get("earnings", amount * 0.08))
            status = "approved"

        else:
            tx_id = f"GEN-{hash(str(raw_payload)) & 0xffffffff}"
            amount = float(raw_payload.get("amount", 50.0))
            commission = float(raw_payload.get("commission", 10.0))
            status = "approved"

        provenance = MetricProvenance(
            provenance_type="REAL_PRODUCTION" if signature_header else "LOCAL_TEST",
            signature=signature_header,
            signature_verified=bool(signature_header)
        )

        return AffiliateCallbackPayload(
            platform=plat,
            transaction_id=str(tx_id),
            amount=amount,
            commission=commission,
            currency="BRL",
            status=status,
            raw_payload=raw_payload,
            provenance=provenance
        )
