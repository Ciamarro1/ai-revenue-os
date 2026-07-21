from typing import Optional, List
from pydantic import BaseModel, Field

class RevenueOpportunity(BaseModel):
    """
    Schema formal de Oportunidade de Receita (Sprint 9).
    Mapeia produtos e ofertas de afiliados pesquisados antes da geração de experimentos.
    """
    id: Optional[str] = None
    marketplace: str  # Hotmart, ClickBank, Amazon, Digistore24, Monetizze, Impact
    product_name: str
    category: str
    commission_rate: float = 0.50  # 50%
    avg_commission_usd: float = 35.0
    competition_index: float = 0.40
    epc_usd: float = 4.20  # Earnings Per Click
    confidence_score: float = 0.85
    target_audience: str = "general"
    affiliate_url: str = "https://example.com/aff"

    @property
    def opportunity_score(self) -> float:
        """
        Calcula a atratividade da oportunidade considerando EPC, comissão, confiança e competição.
        """
        raw_utility = self.epc_usd * self.commission_rate * self.confidence_score * 10.0
        competition_factor = max(0.1, self.competition_index)
        return round(raw_utility / competition_factor, 2)
