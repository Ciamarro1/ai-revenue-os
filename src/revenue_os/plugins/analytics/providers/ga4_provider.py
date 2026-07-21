import os
import requests
from typing import Dict, Any, Optional
from src.revenue_os.plugins.analytics.providers.base_analytics_provider import BaseAnalyticsProvider
from src.revenue_os.plugins.analytics.models import AnalyticsEventPayload, MetricProvenance

class GA4AnalyticsProvider(BaseAnalyticsProvider):
    """
    Provedor GA4 (Google Analytics 4 Measurement Protocol).
    """

    def __init__(self, measurement_id: Optional[str] = None, api_secret: Optional[str] = None):
        self.measurement_id = measurement_id or os.getenv("GA4_MEASUREMENT_ID")
        self.api_secret = api_secret or os.getenv("GA4_API_SECRET")

    @property
    def provider_name(self) -> str:
        return "ga4"

    @property
    def is_enabled(self) -> bool:
        return bool(self.measurement_id and self.api_secret)

    def track_event(self, event: AnalyticsEventPayload) -> Dict[str, Any]:
        if not self.is_enabled:
            provenance = MetricProvenance(provenance_type="WAITING_EXTERNAL_DEPENDENCY")
            return {
                "status": "WAITING_EXTERNAL_DEPENDENCY",
                "provider": self.provider_name,
                "message": "GA4_MEASUREMENT_ID ou GA4_API_SECRET ausente no ambiente.",
                "provenance": provenance.model_dump()
            }

        url = f"https://www.google-analytics.com/mp/collect?measurement_id={self.measurement_id}&api_secret={self.api_secret}"
        payload = {
            "client_id": event.user_id or "anonymous_user",
            "events": [{
                "name": event.event_name,
                "params": event.properties
            }]
        }

        try:
            res = requests.post(url, json=payload, timeout=5.0)
            provenance = MetricProvenance(provenance_type="REAL_PRODUCTION", signature_verified=True)
            return {
                "status": "SUCCESS" if res.status_code in [200, 204] else "FAILED",
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
