from typing import List
from src.revenue_os.plugins.affiliates.providers.base_affiliate_provider import BaseAffiliateProvider
from src.revenue_os.plugins.affiliates.models import (
    AffiliateProduct,
    OfferDetails,
    CommissionRule,
    DeepLinkRequest,
    DeepLinkResponse
)

class EduzzProvider(BaseAffiliateProvider):
    """
    Adaptador Especializado da Eduzz (Nutror / Orbit).
    """

    @property
    def provider_name(self) -> str:
        return "eduzz"

    def discover_products(self, niche: str, limit: int = 10) -> List[AffiliateProduct]:
        if not self._enabled:
            return []

        def _fetch():
            if not self.rate_limiter.acquire():
                raise RuntimeError("Rate limit exceeded for Eduzz API")

            catalog = [
                {"id": f"EDU-301-{niche}", "name": f"Academia {niche.title()} Pro", "price": 497.0, "comm": 0.50, "score": 0.90},
                {"id": f"EDU-302-{niche}", "name": f"Imersão {niche.title()} Ao Vivo", "price": 997.0, "comm": 0.40, "score": 0.86},
            ]
            products = []
            for item in catalog[:limit]:
                p = AffiliateProduct(
                    id=item["id"],
                    marketplace="Eduzz",
                    name=item["name"],
                    category=niche,
                    price_usd=round(item["price"] / 5.0, 2),
                    commission_rate=item["comm"],
                    avg_commission_usd=round((item["price"] * item["comm"]) / 5.0, 2),
                    epc_usd=6.10,
                    score=item["score"],
                    tags=["eduzz", niche, "high_ticket"],
                    classification_status="LOCAL_TEST"
                )
                products.append(p)
            return products

        return self.circuit_breaker.execute(lambda: self.retry_engine.execute(_fetch))

    def get_offer_details(self, product_id: str) -> OfferDetails:
        return OfferDetails(
            product_id=product_id,
            marketplace="Eduzz",
            description="Curso de alto valor agregado hospedado na plataforma Nutror.",
            guarantee_days=15,
            billing_type="RECURRING",
            sales_page_url=f"https://eduzz.com/p/{product_id}",
            support_email="suporte@eduzzproducer.com",
            producer_name="Produtor Eduzz"
        )

    def get_commission_rules(self, product_id: str) -> CommissionRule:
        return CommissionRule(
            product_id=product_id,
            marketplace="Eduzz",
            attribution_type="LAST_CLICK",
            commission_percentage=50.0,
            cookie_expiration_days=45,
            currency="BRL",
            supports_recurring=True
        )

    def generate_deep_link(self, request: DeepLinkRequest) -> DeepLinkResponse:
        sub = f"&utm_content={request.sub_id}" if request.sub_id else ""
        tracking_url = f"https://sun.eduzz.com/{request.product_id}?a={request.affiliate_id}{sub}"
        return DeepLinkResponse(
            product_id=request.product_id,
            marketplace="Eduzz",
            tracking_url=tracking_url,
            sub_id=request.sub_id
        )
