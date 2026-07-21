from typing import List
from src.revenue_os.plugins.research.providers.base_provider import OpportunityProvider
from src.revenue_os.plugins.research.models import ResearchOpportunity

class PinterestTrendsProvider(OpportunityProvider):
    """
    Adaptador de Tendências e Pesquisas Virais do Pinterest.
    """

    def __init__(self, enabled: bool = True):
        self._enabled = enabled

    @property
    def provider_name(self) -> str:
        return "pinterest_trends"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def fetch_opportunities(self, niche: str, limit: int = 10) -> List[ResearchOpportunity]:
        if not self._enabled:
            return []

        catalog = [
            {"title": f"Idéias Criativas de {niche.title()} em Alta", "saves": 12500, "cvr": 0.04},
            {"title": f"Infográfico: Passo a Passo {niche.title()}", "saves": 8900, "cvr": 0.05},
            {"title": f"Estética & Design {niche.title()} 2026", "saves": 15400, "cvr": 0.03},
        ]

        opportunities: List[ResearchOpportunity] = []
        for idx, item in enumerate(catalog[:limit]):
            opp = ResearchOpportunity(
                id=f"pin_{idx}_{niche}",
                marketplace="Pinterest Trends",
                product_name=item["title"],
                category=niche,
                commission_rate=0.50,
                avg_commission_usd=32.0,
                competition_index=0.30,
                epc_usd=3.80,
                confidence_score=0.85,
                target_audience="visual_pinners",
                affiliate_url=f"https://pinterest.com/search/pins/?q={niche}",
                provider_name=self.provider_name,
                raw_score=float(item["saves"]),
                search_volume=item["saves"],
                source_url="https://pinterest.com/trends",
                tags=["pinterest", "visual_trends", niche],
                classification_status="LOCAL_TEST"
            )
            opportunities.append(opp)

        return opportunities
