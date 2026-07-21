from typing import List
from src.revenue_os.plugins.research.providers.base_provider import OpportunityProvider
from src.revenue_os.plugins.research.models import ResearchOpportunity

class HotmartProvider(OpportunityProvider):
    """
    Adaptador de Mercado para a Vitrine de Afiliados Hotmart.
    """

    def __init__(self, enabled: bool = True):
        self._enabled = enabled

    @property
    def provider_name(self) -> str:
        return "hotmart"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def fetch_opportunities(self, niche: str, limit: int = 10) -> List[ResearchOpportunity]:
        if not self._enabled:
            return []

        # Como a API privada da Hotmart requer token OAuth de parceiro (WAITING_EXTERNAL_DEPENDENCY),
        # fornecemos catálogo estruturado EDD classificado como LOCAL_TEST.
        catalog = [
            {"title": f"Curso Completo de {niche.title()}", "comm": 0.60, "price": 97.0, "temp": 150.0},
            {"title": f"Mentoria Premium em {niche.title()}", "comm": 0.50, "price": 297.0, "temp": 120.0},
            {"title": f"Ebook Guia Prático de {niche.title()}", "comm": 0.70, "price": 47.0, "temp": 90.0},
        ]

        opportunities: List[ResearchOpportunity] = []
        for idx, item in enumerate(catalog[:limit]):
            opp = ResearchOpportunity(
                id=f"hotmart_{idx}_{niche}",
                marketplace="Hotmart",
                product_name=item["title"],
                category=niche,
                commission_rate=item["comm"],
                avg_commission_usd=round(item["price"] * item["comm"], 2),
                competition_index=0.35,
                epc_usd=4.80,
                confidence_score=0.88,
                target_audience="digital_buyers",
                affiliate_url=f"https://hotmart.com/product/{idx}",
                provider_name=self.provider_name,
                raw_score=item["temp"],
                search_volume=int(item["temp"] * 100),
                source_url="https://hotmart.com",
                tags=["hotmart", "affiliate", niche],
                classification_status="LOCAL_TEST"
            )
            opportunities.append(opp)

        return opportunities
