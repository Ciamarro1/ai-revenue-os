from typing import Dict, Any, Optional
from src.revenue_os.plugins.base_plugin import BasePlugin
from src.revenue_os.plugins.analytics.models import (
    AnalyticsConfig,
    AnalyticsEventPayload,
    MetricProvenance,
    AnalyticsPluginHealth
)
from src.revenue_os.plugins.analytics.providers.ga4_provider import GA4AnalyticsProvider
from src.revenue_os.plugins.analytics.providers.posthog_provider import PostHogAnalyticsProvider
from src.revenue_os.plugins.analytics.providers.resend_provider import ResendAnalyticsProvider
from src.revenue_os.plugins.analytics.providers.affiliate_callback_processor import AffiliateCallbackProcessor
from src.revenue_os.plugins.analytics.providers.signed_webhook_manager import SignedWebhookManager

class AnalyticsProductionPlugin(BasePlugin):
    """
    AnalyticsProductionPlugin (Sprint O7).
    Plugin oficial de produção de telemetria estendendo o BasePlugin SDK.
    Suporta GA4, PostHog, Resend, Webhooks Assinados e Callbacks de Afiliados com Proveniência EDD.
    """

    def __init__(self, config: Optional[AnalyticsConfig] = None):
        self.config = config or AnalyticsConfig()
        self.ga4 = GA4AnalyticsProvider(self.config.ga4_measurement_id, self.config.ga4_api_secret)
        self.posthog = PostHogAnalyticsProvider(self.config.posthog_api_key, self.config.posthog_host)
        self.resend = ResendAnalyticsProvider(self.config.resend_api_key)
        self.callback_processor = AffiliateCallbackProcessor()
        self.webhook_manager = SignedWebhookManager(self.config.webhook_secret)
        self._initialized = False

    @property
    def plugin_name(self) -> str:
        return "analytics_production_plugin"

    @property
    def category(self) -> str:
        return "analytics"

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        health = AnalyticsPluginHealth(
            plugin_name=self.plugin_name,
            status="HEALTHY" if self._initialized else "UNHEALTHY",
            ga4_enabled=self.ga4.is_enabled,
            posthog_enabled=self.posthog.is_enabled,
            resend_enabled=self.resend.is_enabled,
            webhooks_enabled=True,
            message="Operational" if self._initialized else "Not initialized"
        )
        return health.model_dump()

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "track_event")

        if action == "track_event":
            return self._execute_track_event(payload)

        elif action == "process_callback":
            return self._execute_process_callback(payload)

        elif action == "verify_webhook":
            return self._execute_verify_webhook(payload)

        elif action == "sign_webhook":
            return self._execute_sign_webhook(payload)

        raise ValueError(f"Ação desconhecida '{action}' para AnalyticsProductionPlugin")

    def _execute_track_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        event = AnalyticsEventPayload(
            event_name=payload.get("event_name", "page_view"),
            properties=payload.get("properties", {}),
            user_id=payload.get("user_id"),
            session_id=payload.get("session_id")
        )

        provenance_type = payload.get("provenance_type", "LOCAL_TEST")
        event.provenance = MetricProvenance(provenance_type=provenance_type)

        results = {
            "ga4": self.ga4.track_event(event),
            "posthog": self.posthog.track_event(event),
            "resend": self.resend.track_event(event) if payload.get("send_email") else {"status": "SKIPPED"}
        }

        return {
            "status": "SUCCESS",
            "event_name": event.event_name,
            "provenance": event.provenance.model_dump(),
            "provider_responses": results
        }

    def _execute_process_callback(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        platform = payload.get("platform", "hotmart")
        raw_data = payload.get("raw_payload", {})
        signature = payload.get("signature")

        callback_data = self.callback_processor.process_callback(platform, raw_data, signature)
        return {
            "status": "SUCCESS",
            "callback": callback_data.model_dump()
        }

    def _execute_verify_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = payload.get("body", {})
        sig = payload.get("signature", "")
        provenance = self.webhook_manager.create_signed_provenance(body, sig)
        return {
            "status": "SUCCESS" if provenance.signature_verified else "INVALID_SIGNATURE",
            "provenance": provenance.model_dump()
        }

    def _execute_sign_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = payload.get("body", {})
        signature = self.webhook_manager.sign_payload(body)
        return {
            "status": "SUCCESS",
            "signature": signature
        }

    def shutdown(self) -> None:
        self._initialized = False
