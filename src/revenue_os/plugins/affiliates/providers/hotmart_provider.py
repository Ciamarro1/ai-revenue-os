from typing import List
from src.revenue_os.plugins.affiliates.providers.base_affiliate_provider import BaseAffiliateProvider
from src.revenue_os.plugins.affiliates.models import (
    AffiliateProduct,
    OfferDetails,
    CommissionRule,
    DeepLinkRequest,
    DeepLinkResponse
)

class HotmartProvider(BaseAffiliateProvider):
    """
    Adaptador Especializado da Hotmart.
    """

    @property
    def provider_name(self) -> str:
        return "hotmart"

    def discover_products(self, niche: str, limit: int = 10) -> List[AffiliateProduct]:
        if not self._enabled:
            return []

        def _fetch():
            if not self.rate_limiter.acquire():
                raise RuntimeError("Rate limit exceeded for Hotmart API")
            
            catalog = [
                {"id": f"HOT-101-{niche}", "name": f"Formação Master em {niche.title()}", "price": 197.0, "comm": 0.65, "score": 0.92},
                {"id": f"HOT-102-{niche}", "name": f"Curso Prático de {niche.title()} 2026", "price": 97.0, "comm": 0.60, "score": 0.88},
                {"id": f"HOT-103-{niche}", "name": f"Comunidade VIP {niche.title()}", "price": 297.0, "comm": 0.50, "score": 0.85},
            ]
            products = []
            for item in catalog[:limit]:
                p = AffiliateProduct(
                    id=item["id"],
                    marketplace="Hotmart",
                    name=item["name"],
                    category=niche,
                    price_usd=round(item["price"] / 5.0, 2),
                    commission_rate=item["comm"],
                    avg_commission_usd=round((item["price"] * item["comm"]) / 5.0, 2),
                    epc_usd=4.50,
                    score=item["score"],
                    tags=["hotmart", niche, "digital_course"],
                    classification_status="LOCAL_TEST"
                )
                products.append(p)
            return products

        return self.circuit_breaker.execute(lambda: self.retry_engine.execute(_fetch))

    def get_offer_details(self, product_id: str) -> OfferDetails:
        return OfferDetails(
            product_id=product_id,
            marketplace="Hotmart",
            description="Treinamento completo com certificado de conclusão e comunidade exclusiva.",
            guarantee_days=7,
            billing_type="ONE_TIME",
            sales_page_url=f"https://hotmart.com/product/{product_id}",
            support_email="suporte@producer.com",
            producer_name="Produtor Oficial Hotmart"
        )

    def get_commission_rules(self, product_id: str) -> CommissionRule:
        return CommissionRule(
            product_id=product_id,
            marketplace="Hotmart",
            attribution_type="LAST_CLICK",
            commission_percentage=60.0,
            cookie_expiration_days=60,
            currency="BRL",
            supports_recurring=False
        )

    def generate_deep_link(self, request: DeepLinkRequest) -> DeepLinkResponse:
        sub = f"?src={request.sub_id}" if request.sub_id else ""
        tracking_url = f"https://go.hotmart.com/{request.product_id}{sub}"
        return DeepLinkResponse(
            product_id=request.product_id,
            marketplace="Hotmart",
            tracking_url=tracking_url,
            sub_id=request.sub_id
        )
