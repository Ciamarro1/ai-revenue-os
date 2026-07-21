from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class AffiliateProduct(BaseModel):
    """
    Modelo de Produto de Afiliado (Sprint O2).
    """
    id: str
    marketplace: str  # Hotmart, Kiwify, Eduzz, Amazon
    name: str
    category: str = "general"
    price_usd: float = 0.0
    commission_rate: float = 0.50
    avg_commission_usd: float = 0.0
    epc_usd: float = 1.00
    score: float = 0.80
    tags: List[str] = Field(default_factory=list)
    classification_status: str = "LOCAL_TEST"  # REAL_PRODUCTION, SIMULATED_BENCHMARK, LOCAL_TEST, WAITING_EXTERNAL_DEPENDENCY

class OfferDetails(BaseModel):
    """
    Detalhes formais de uma oferta de afiliado.
    """
    product_id: str
    marketplace: str
    description: str = ""
    guarantee_days: int = 7
    billing_type: str = "ONE_TIME"  # ONE_TIME, RECURRING, SUBSCRIPTION
    sales_page_url: str = ""
    support_email: str = "support@example.com"
    producer_name: str = "Official Producer"
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)

class CommissionRule(BaseModel):
    """
    Regras formais de atribuição de comissão.
    """
    product_id: str
    marketplace: str
    attribution_type: str = "LAST_CLICK"  # LAST_CLICK, FIRST_CLICK, MULTI_TOUCH
    commission_percentage: float = 50.0
    cookie_expiration_days: int = 60
    currency: str = "USD"
    supports_recurring: bool = False

class DeepLinkRequest(BaseModel):
    """
    Solicitação de geração de link de afiliado rastreado.
    """
    product_id: str
    affiliate_id: str = "default_aff"
    sub_id: Optional[str] = None
    campaign_id: Optional[str] = None
    custom_params: Dict[str, str] = Field(default_factory=dict)

class DeepLinkResponse(BaseModel):
    """
    Resposta contendo o link de afiliado devidamente gerado e rastreado.
    """
    product_id: str
    marketplace: str
    tracking_url: str
    sub_id: Optional[str] = None
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")

class AffiliateProviderHealth(BaseModel):
    """
    Modelo de saúde e métricas de resiliência do provedor de afiliados.
    """
    provider_name: str
    status: str = "HEALTHY"
    circuit_breaker_state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    available_tokens: float = 100.0
    error_count: int = 0
    message: str = "Operational"
