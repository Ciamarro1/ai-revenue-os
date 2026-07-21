from typing import List
from src.revenue_os.plugins.affiliates.providers.base_affiliate_provider import BaseAffiliateProvider
from src.revenue_os.plugins.affiliates.models import (
    AffiliateProduct,
    OfferDetails,
    CommissionRule,
    DeepLinkRequest,
    DeepLinkResponse
)

class KiwifyProvider(BaseAffiliateProvider):
    """
    Adaptador Especializado da Kiwify.
    """

    @property
    def provider_name(self) -> str:
        return "kiwify"

    def discover_products(self, niche: str, limit: int = 10) -> List[AffiliateProduct]:
        if not self._enabled:
            return []

        def _fetch():
            if not self.rate_limiter.acquire():
                raise RuntimeError("Rate limit exceeded for Kiwify API")

            catalog = [
                {"id": f"KIW-201-{niche}", "name": f"Método {niche.title()} Sem Segredos", "price": 147.0, "comm": 0.70, "score": 0.94},
                {"id": f"KIW-202-{niche}", "name": f"Desafio 30 Dias {niche.title()}", "price": 47.0, "comm": 0.80, "score": 0.89},
            ]
            products = []
            for item in catalog[:limit]:
                p = AffiliateProduct(
                    id=item["id"],
                    marketplace="Kiwify",
                    name=item["name"],
                    category=niche,
                    price_usd=round(item["price"] / 5.0, 2),
                    commission_rate=item["comm"],
                    avg_commission_usd=round((item["price"] * item["comm"]) / 5.0, 2),
                    epc_usd=5.20,
                    score=item["score"],
                    tags=["kiwify", niche, "digital_product"],
                    classification_status="LOCAL_TEST"
                )
                products.append(p)
            return products

        return self.circuit_breaker.execute(lambda: self.retry_engine.execute(_fetch))

    def get_offer_details(self, product_id: str) -> OfferDetails:
        return OfferDetails(
            product_id=product_id,
            marketplace="Kiwify",
            description="Infoproduto de alta conversão com checkout transparente Kiwify.",
            guarantee_days=7,
            billing_type="ONE_TIME",
            sales_page_url=f"https://pay.kiwify.com.br/{product_id}",
            support_email="suporte@kiwifyproducer.com",
            producer_name="Produtor Kiwify"
        )

    def get_commission_rules(self, product_id: str) -> CommissionRule:
        return CommissionRule(
            product_id=product_id,
            marketplace="Kiwify",
            attribution_type="LAST_CLICK",
            commission_percentage=70.0,
            cookie_expiration_days=90,
            currency="BRL",
            supports_recurring=False
        )

    def generate_deep_link(self, request: DeepLinkRequest) -> DeepLinkResponse:
        sub = f"&afsrc={request.sub_id}" if request.sub_id else ""
        tracking_url = f"https://pay.kiwify.com.br/{request.product_id}?af={request.affiliate_id}{sub}"
        return DeepLinkResponse(
            product_id=request.product_id,
            marketplace="Kiwify",
            tracking_url=tracking_url,
            sub_id=request.sub_id
        )
