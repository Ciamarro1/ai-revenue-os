from typing import List
from src.revenue_os.plugins.research.providers.base_provider import OpportunityProvider
from src.revenue_os.plugins.research.models import ResearchOpportunity

class AmazonProvider(OpportunityProvider):
    """
    Adaptador de Mercado para Produtos Best Sellers da Amazon.
    """

    def __init__(self, enabled: bool = True):
        self._enabled = enabled

    @property
    def provider_name(self) -> str:
        return "amazon"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def fetch_opportunities(self, niche: str, limit: int = 10) -> List[ResearchOpportunity]:
        if not self._enabled:
            return []

        catalog = [
            {"title": f"Kit Pro {niche.title()} Essentials", "comm": 0.10, "price": 149.0, "rating": 4.8},
            {"title": f"Smart Gadget {niche.title()} Edition", "comm": 0.08, "price": 89.0, "rating": 4.6},
            {"title": f"Livro Best Seller: O Futuro de {niche.title()}", "comm": 0.15, "price": 24.0, "rating": 4.9},
        ]

        opportunities: List[ResearchOpportunity] = []
        for idx, item in enumerate(catalog[:limit]):
            opp = ResearchOpportunity(
                id=f"amazon_{idx}_{niche}",
                marketplace="Amazon",
                product_name=item["title"],
                category=niche,
                commission_rate=item["comm"],
                avg_commission_usd=round(item["price"] * item["comm"], 2),
                competition_index=0.45,
                epc_usd=2.10,
                confidence_score=0.92,
                target_audience="e-commerce_shoppers",
                affiliate_url=f"https://amazon.com/dp/B000{idx}?tag=airevenueos-20",
                provider_name=self.provider_name,
                raw_score=item["rating"] * 20.0,
                search_volume=8000,
                source_url="https://amazon.com",
                tags=["amazon", "physical_products", niche],
                classification_status="LOCAL_TEST"
            )
            opportunities.append(opp)

        return opportunities
