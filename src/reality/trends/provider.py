import random
from typing import Dict, Any
from src.reality.base import TrendProvider

class MockTrendProvider(TrendProvider):
    """
    Provedor simulador de tendências operando na camada Reality.
    Utilizado como fallback e para o ciclo de testes em sandbox.
    """
    provider_name = "mock_trends"
    confidence_score = 0.80  # Confiança alta mas não absoluta (é um mock de qualidade)

    def __init__(self):
        self.topics = [
            {"topic": "setup de mesa minimalista", "category": "lifestyle", "metric_target": "retention_3s", "growth_rate": 0.32},
            {"topic": "investimento em dividendos para iniciantes", "category": "finance", "metric_target": "ctr", "growth_rate": 0.45},
            {"topic": "dicas de produtividade no trabalho", "category": "lifestyle", "metric_target": "retention_3s", "growth_rate": 0.28},
            {"topic": "como economizar 30% da renda", "category": "finance", "metric_target": "ctr", "growth_rate": 0.52},
            {"topic": "ideias de lanches saudaveis rapidos", "category": "lifestyle", "metric_target": "retention_3s", "growth_rate": 0.37}
        ]

    def health(self) -> Dict[str, Any]:
        return {"healthy": True, "provider": self.provider_name}

    def discover_trend(self) -> Dict[str, Any]:
        trend = random.choice(self.topics).copy()
        # Adiciona um hook padrão sugerido baseado na tendência
        if trend["category"] == "finance":
            trend["suggested_hook"] = f"Por que a maioria das pessoas falha ao tentar {trend['topic']}?"
        else:
            trend["suggested_hook"] = f"3 pequenos segredos sobre {trend['topic']} que ninguém te conta."
        return trend
