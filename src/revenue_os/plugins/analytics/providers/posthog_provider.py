import os
import requests
from typing import Dict, Any, Optional
from src.revenue_os.plugins.analytics.providers.base_analytics_provider import BaseAnalyticsProvider
from src.revenue_os.plugins.analytics.models import AnalyticsEventPayload, MetricProvenance

class PostHogAnalyticsProvider(BaseAnalyticsProvider):
    """
    Provedor PostHog Analytics.
    """

    def __init__(self, api_key: Optional[str] = None, host: str = "https://app.posthog.com"):
        self.api_key = api_key or os.getenv("POSTHOG_API_KEY")
        self.host = host or os.getenv("POSTHOG_HOST", "https://app.posthog.com")

    @property
    def provider_name(self) -> str:
        return "posthog"

    @property
    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def track_event(self, event: AnalyticsEventPayload) -> Dict[str, Any]:
        if not self.is_enabled:
            provenance = MetricProvenance(provenance_type="WAITING_EXTERNAL_DEPENDENCY")
            return {
                "status": "WAITING_EXTERNAL_DEPENDENCY",
                "provider": self.provider_name,
                "message": "POSTHOG_API_KEY ausente no ambiente.",
                "provenance": provenance.model_dump()
            }

        url = f"{self.host.rstrip('/')}/capture/"
        payload = {
            "api_key": self.api_key,
            "event": event.event_name,
            "distinct_id": event.user_id or "anonymous_user",
            "properties": event.properties
        }

        try:
            res = requests.post(url, json=payload, timeout=5.0)
            provenance = MetricProvenance(provenance_type="REAL_PRODUCTION", signature_verified=True)
            return {
                "status": "SUCCESS" if res.status_code == 200 else "FAILED",
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
