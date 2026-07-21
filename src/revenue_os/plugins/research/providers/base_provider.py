from abc import ABC, abstractmethod
from typing import List
from src.revenue_os.plugins.research.models import ResearchOpportunity, ProviderHealth

class OpportunityProvider(ABC):
    """
    Interface abstrata para Adaptadores/Provedores de Oportunidade.
    Cada fonte de dados (Hotmart, Amazon, Google Trends, Reddit, HN, RSS, Pinterest)
    implementa esta interface de forma desacoplada.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    def is_enabled(self) -> bool:
        return True

    @abstractmethod
    def fetch_opportunities(self, niche: str, limit: int = 10) -> List[ResearchOpportunity]:
        """
        Coleta e normaliza oportunidades de receita do provedor específico.
        """
        pass

    def health_check(self) -> ProviderHealth:
        """
        Executa verificação básica de saúde operacional do provedor.
        """
        return ProviderHealth(
            provider_name=self.provider_name,
            status="HEALTHY" if self.is_enabled else "DISABLED",
            message="Ready" if self.is_enabled else "Provider disabled by feature flag"
        )
