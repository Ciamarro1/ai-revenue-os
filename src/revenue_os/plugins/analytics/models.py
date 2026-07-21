import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class MetricProvenance(BaseModel):
    """
    Selo de Proveniência da Métrica e Auditabilidade de Origem.
    Classifica rigorosamente se o dado veio de produção real, teste ou simulação.
    """
    provenance_type: str = "LOCAL_TEST"  # REAL_PRODUCTION, SIMULATED_BENCHMARK, LOCAL_TEST, WAITING_EXTERNAL_DEPENDENCY
    trace_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    span_id: str = Field(default_factory=lambda: uuid.uuid4().hex[:16])
    signature: Optional[str] = None
    source_ip: Optional[str] = None
    signature_verified: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")

class AnalyticsEventPayload(BaseModel):
    """
    Payload Canônico de Evento de Telemetria e Analytics.
    """
    event_name: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    provenance: Optional[MetricProvenance] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")

class AffiliateCallbackPayload(BaseModel):
    """
    Payload de Pós-venda e Comissão de Afiliado (Webhooks Hotmart, Kiwify, Eduzz, Amazon).
    """
    platform: str  # hotmart, kiwify, eduzz, amazon
    transaction_id: str
    amount: float
    commission: float
    currency: str = "BRL"
    status: str = "approved"  # approved, refunded, chargedback
    raw_payload: Dict[str, Any] = Field(default_factory=dict)
    provenance: Optional[MetricProvenance] = None

class AnalyticsPluginHealth(BaseModel):
    """
    Health check do plugin de analytics.
    """
    plugin_name: str = "analytics_plugin"
    status: str = "HEALTHY"
    ga4_enabled: bool = False
    posthog_enabled: bool = False
    resend_enabled: bool = False
    webhooks_enabled: bool = True
    message: str = "Operational"

class AnalyticsConfig(BaseModel):
    """
    Configuração Pydantic v2 do Analytics Production Plugin.
    """
    ga4_measurement_id: Optional[str] = None
    ga4_api_secret: Optional[str] = None
    posthog_api_key: Optional[str] = None
    posthog_host: str = "https://app.posthog.com"
    resend_api_key: Optional[str] = None
    webhook_secret: str = "ai_revenue_os_secure_webhook_secret_key"
