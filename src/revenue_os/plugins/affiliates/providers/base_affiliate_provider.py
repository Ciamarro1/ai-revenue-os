from abc import ABC, abstractmethod
from typing import List
from src.revenue_os.plugins.affiliates.models import (
    AffiliateProduct,
    OfferDetails,
    CommissionRule,
    DeepLinkRequest,
    DeepLinkResponse,
    AffiliateProviderHealth
)
from src.revenue_os.plugins.affiliates.resilience import (
    TokenBucketRateLimiter,
    ExponentialBackoffRetry,
    CircuitBreaker
)

class BaseAffiliateProvider(ABC):
    """
    Interface Abstrata para Adaptadores de Afiliados.
    Oferece suporte integrado a Rate Limiter, Retry e Circuit Breaker.
    """

    def __init__(self, enabled: bool = True):
        self._enabled = enabled
        self.rate_limiter = TokenBucketRateLimiter(capacity=60.0, refill_rate_per_sec=1.0)
        self.retry_engine = ExponentialBackoffRetry(max_retries=3, backoff_factor=1.2)
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_time_sec=30.0)

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    @abstractmethod
    def discover_products(self, niche: str, limit: int = 10) -> List[AffiliateProduct]:
        pass

    @abstractmethod
    def get_offer_details(self, product_id: str) -> OfferDetails:
        pass

    @abstractmethod
    def get_commission_rules(self, product_id: str) -> CommissionRule:
        pass

    @abstractmethod
    def generate_deep_link(self, request: DeepLinkRequest) -> DeepLinkResponse:
        pass

    def health_check(self) -> AffiliateProviderHealth:
        return AffiliateProviderHealth(
            provider_name=self.provider_name,
            status="HEALTHY" if self._enabled and self.circuit_breaker.state != "OPEN" else "DEGRADED",
            circuit_breaker_state=self.circuit_breaker.state,
            available_tokens=self.rate_limiter.get_available_tokens(),
            error_count=self.circuit_breaker.failure_count,
            message="Operational" if self.circuit_breaker.state == "CLOSED" else f"Circuit Breaker is {self.circuit_breaker.state}"
        )
