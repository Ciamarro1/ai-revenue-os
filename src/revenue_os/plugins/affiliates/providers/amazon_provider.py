from typing import List
from src.revenue_os.plugins.affiliates.providers.base_affiliate_provider import BaseAffiliateProvider
from src.revenue_os.plugins.affiliates.models import (
    AffiliateProduct,
    OfferDetails,
    CommissionRule,
    DeepLinkRequest,
    DeepLinkResponse
)

class AmazonProvider(BaseAffiliateProvider):
    """
    Adaptador Especializado do Amazon Associates Program.
    """

    @property
    def provider_name(self) -> str:
        return "amazon"

    def discover_products(self, niche: str, limit: int = 10) -> List[AffiliateProduct]:
        if not self._enabled:
            return []

        def _fetch():
            if not self.rate_limiter.acquire():
                raise RuntimeError("Rate limit exceeded for Amazon Associates API")

            catalog = [
                {"id": f"B08N5{niche[:3].upper()}1", "name": f"Pro {niche.title()} Hardware Gear", "price": 199.99, "comm": 0.10, "score": 0.96},
                {"id": f"B09X7{niche[:3].upper()}2", "name": f"Wireless {niche.title()} Smart Accessory", "price": 49.99, "comm": 0.08, "score": 0.91},
            ]
            products = []
            for item in catalog[:limit]:
                p = AffiliateProduct(
                    id=item["id"],
                    marketplace="Amazon",
                    name=item["name"],
                    category=niche,
                    price_usd=item["price"],
                    commission_rate=item["comm"],
                    avg_commission_usd=round(item["price"] * item["comm"], 2),
                    epc_usd=3.20,
                    score=item["score"],
                    tags=["amazon", niche, "physical_gear"],
                    classification_status="LOCAL_TEST"
                )
                products.append(p)
            return products

        return self.circuit_breaker.execute(lambda: self.retry_engine.execute(_fetch))

    def get_offer_details(self, product_id: str) -> OfferDetails:
        return OfferDetails(
            product_id=product_id,
            marketplace="Amazon",
            description="Produto físico com envio Prime e garantia oficial Amazon.",
            guarantee_days=30,
            billing_type="ONE_TIME",
            sales_page_url=f"https://amazon.com/dp/{product_id}",
            support_email="cs@amazon.com",
            producer_name="Amazon Official Store"
        )

    def get_commission_rules(self, product_id: str) -> CommissionRule:
        return CommissionRule(
            product_id=product_id,
            marketplace="Amazon",
            attribution_type="LAST_CLICK",
            commission_percentage=10.0,
            cookie_expiration_days=1,
            currency="USD",
            supports_recurring=False
        )

    def generate_deep_link(self, request: DeepLinkRequest) -> DeepLinkResponse:
        tag = request.affiliate_id if request.affiliate_id != "default_aff" else "airevenueos-20"
        sub = f"&ascsubtag={request.sub_id}" if request.sub_id else ""
        tracking_url = f"https://amazon.com/dp/{request.product_id}?tag={tag}{sub}"
        return DeepLinkResponse(
            product_id=request.product_id,
            marketplace="Amazon",
            tracking_url=tracking_url,
            sub_id=request.sub_id
        )
