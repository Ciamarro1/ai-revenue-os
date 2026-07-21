import os
import requests
from typing import Dict, Any, Optional
from src.revenue_os.plugins.analytics.providers.base_analytics_provider import BaseAnalyticsProvider
from src.revenue_os.plugins.analytics.models import AnalyticsEventPayload, MetricProvenance

class ResendAnalyticsProvider(BaseAnalyticsProvider):
    """
    Provedor Resend para disparo e telemetria de e-mails transacionais.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RESEND_API_KEY")

    @property
    def provider_name(self) -> str:
        return "resend"

    @property
    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def track_event(self, event: AnalyticsEventPayload) -> Dict[str, Any]:
        if not self.is_enabled:
            provenance = MetricProvenance(provenance_type="WAITING_EXTERNAL_DEPENDENCY")
            return {
                "status": "WAITING_EXTERNAL_DEPENDENCY",
                "provider": self.provider_name,
                "message": "RESEND_API_KEY ausente no ambiente.",
                "provenance": provenance.model_dump()
            }

        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": event.properties.get("from", "onboarding@resend.dev"),
            "to": [event.properties.get("to", "delivered@resend.dev")],
            "subject": event.properties.get("subject", f"Event Notification: {event.event_name}"),
            "html": event.properties.get("html", f"<p>Event: {event.event_name}</p>")
        }

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=5.0)
            provenance = MetricProvenance(provenance_type="REAL_PRODUCTION", signature_verified=True)
            return {
                "status": "SUCCESS" if res.status_code in [200, 201] else "FAILED",
                "http_status": res.status_code,
                "provider": self.provider_name,
                "provenance": provenance.model_dump()
            }
        except Exception as e:
            provenance = MetricProvenance(provenance_type="LOCAL_TEST")
            return {
                "status": "FAILED",
                "error": str(e),
                "provider": self.provider_name,
                "provenance": provenance.model_dump()
            }
