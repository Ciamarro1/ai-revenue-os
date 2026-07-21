from typing import List
from src.revenue_os.plugins.research.models import ResearchOpportunity

class OpportunityScoringService:
    """
    Algoritmo multifatorial de cálculo e ordenação de Oportunidades de Receita.
    """

    @staticmethod
    def calculate_score(opp: ResearchOpportunity) -> float:
        """
        Calcula o Opportunity Score final ponderando EPC, taxa de comissão,
        nível de competição, volume de busca e pontuação bruta do provedor.
        """
        base_utility = (opp.epc_usd * opp.commission_rate * opp.confidence_score * 10.0)
        volume_bonus = min(20.0, (opp.search_volume / 1000.0))
        raw_bonus = min(15.0, (opp.raw_score / 50.0))
        
        competition_factor = max(0.1, opp.competition_index)
        
        final_score = (base_utility + volume_bonus + raw_bonus) / competition_factor
        return round(final_score, 2)

    def rank_opportunities(self, opportunities: List[ResearchOpportunity], min_threshold: float = 0.0) -> List[ResearchOpportunity]:
        """
        Calcula os scores e re-ordena as oportunidades em ordem decrescente de atratividade.
        """
        ranked = []
        for opp in opportunities:
            opp.raw_score = self.calculate_score(opp)
            if opp.raw_score >= min_threshold:
                ranked.append(opp)

        return sorted(ranked, key=lambda x: x.opportunity_score, reverse=True)
