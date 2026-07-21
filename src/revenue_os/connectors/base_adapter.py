from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.revenue_os.analytics.opportunity_schemas import RevenueOpportunity

class BaseMarketplaceAdapter(ABC):
    """
    Classe abstrata base para Adaptadores de Marketplace (Sprint 9.5 Integration Layer).
    Cada marketplace implementa exclusivamente a extração e mapeamento dos seus dados nativos.
    """

    @property
    @abstractmethod
    def marketplace_name(self) -> str:
        pass

    @abstractmethod
    def fetch_raw_opportunities(self, niche: str) -> List[Dict[str, Any]]:
        """
        Coleta os payloads brutos do marketplace.
        """
        pass

    def get_normalized_opportunities(self, niche: str) -> List[RevenueOpportunity]:
        """
        Executa o pipeline estandardizado: Connector -> Adapter -> Normalizer -> Validator.
        """
        raw_items = self.fetch_raw_opportunities(niche)
        normalized = []
        for raw in raw_items:
            opp = self.normalize(raw, niche)
            if self.validate(opp):
                normalized.append(opp)
        return normalized

    @abstractmethod
    def normalize(self, raw_data: Dict[str, Any], niche: str) -> RevenueOpportunity:
        """
        Normaliza os dados nativos do marketplace para o schema padrão RevenueOpportunity.
        """
        pass

    def validate(self, opp: RevenueOpportunity) -> bool:
        """
        Valida se a oportunidade atende aos requisitos mínimos de qualidade e integridade.
        """
        return opp.commission_rate > 0.05 and opp.epc_usd > 0.50 and opp.confidence_score >= 0.50
