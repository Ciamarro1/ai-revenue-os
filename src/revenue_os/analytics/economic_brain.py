import math
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class EconomicBrain:
    """
    Economic Brain do AI Revenue OS (v4.0).
    Otimiza decisões de investimento ponderando receita por confiança preditiva e eficiências de tempo/recursos:
    - Revenue per GPU Hour
    - Revenue per API Dollar
    - Knowledge per Dollar
    - Knowledge per Hour
    """

    def calculate_utility(
        self,
        expected_revenue: float,
        infra_cost: float,
        risk_factor: float,
        observations_count: int = 0,
        confidence_delta: float = 0.10,
        reusability_channels_count: int = 1,
        confidence: float = 0.85,
        gpu_hours: float = 1.0,
        execution_hours: float = 0.5
    ) -> Dict[str, Any]:
        """
        Calcula a utilidade total e métricas de eficiência por tempo, GPU e custos de API.
        """
        # Receita ponderada pela confiança preditiva
        weighted_revenue = round(expected_revenue * max(0.1, min(1.0, confidence)), 2)

        # Risk penalty = Risco * Custo de infraestrutura * 1.5
        risk_penalty = round(risk_factor * max(1.0, infra_cost) * 1.5, 2)

        # Knowledge gain = log10(observations + 1) * confidence_delta * 10.0
        knowledge_gain = round(math.log10(observations_count + 1) * confidence_delta * 10.0, 2)

        # Reusability gain = (canais de distribuição adicionais) * $3.50 de valor reaproveitado
        reusability_gain = round(max(0, reusability_channels_count - 1) * 3.50, 2)

        net_financial_utility = weighted_revenue - infra_cost - risk_penalty
        total_utility = round(net_financial_utility + knowledge_gain + reusability_gain, 2)

        # Métricas de Eficiência Operacional (v4.0)
        revenue_per_gpu_hour = round(weighted_revenue / max(0.1, gpu_hours), 2)
        revenue_per_api_dollar = round(weighted_revenue / max(0.1, infra_cost), 2)
        knowledge_per_dollar = round(knowledge_gain / max(0.1, infra_cost), 2)
        knowledge_per_hour = round(knowledge_gain / max(0.1, execution_hours), 2)

        is_approved = total_utility > 0 or (net_financial_utility >= -5.0 and (knowledge_gain + reusability_gain) >= 3.0)

        return {
            "expected_revenue_raw_usd": expected_revenue,
            "confidence_score": confidence,
            "weighted_revenue_usd": weighted_revenue,
            "infra_cost_usd": infra_cost,
            "risk_penalty_usd": risk_penalty,
            "knowledge_gain_value": knowledge_gain,
            "reusability_gain_value": reusability_gain,
            "total_utility_score": total_utility,
            "efficiency_metrics": {
                "revenue_per_gpu_hour": revenue_per_gpu_hour,
                "revenue_per_api_dollar": revenue_per_api_dollar,
                "knowledge_per_dollar": knowledge_per_dollar,
                "knowledge_per_hour": knowledge_per_hour
            },
            "is_approved_for_execution": is_approved,
            "approval_reason": (
                "Lucratividade ponderada positiva" if net_financial_utility > 0
                else ("Aprovado por Ativo Cognitivo / Reutilizável" if is_approved else "Reprovado por utilidade negativa")
            )
        }
