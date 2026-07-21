import random
from typing import List, Dict, Any

class PortfolioOptimizer:
    """
    Otimizador de Portfólio de Atenção (Multi-Armed Bandit via Thompson Sampling).
    Distribui peso/orçamento virtual para as variantes baseado em distribuições Beta
    de Cliques de Saída (Sucesso) e Impressões (Tentativas).
    """
    @staticmethod
    def allocate_budgets(variants: List[Dict[str, Any]], total_budget: float) -> Dict[str, float]:
        samples = {}
        
        for var in variants:
            var_id = var.get("variant_id")
            clicks = var.get("conversion_count", 0)
            impressions = var.get("impressions", 0)
            
            # Garante valores positivos para parâmetros da distribuição Beta
            alpha = max(1, clicks) + 1
            beta = max(1, impressions - clicks) + 1
            
            # Thompson Sampling via betavariate (nativa do Python, sem necessidade de NumPy)
            sample = random.betavariate(alpha, beta)
            samples[var_id] = sample
            
        total_score = sum(samples.values())
        if total_score == 0:
            # Caso extremo de falha, distribui igualmente
            share = round(total_budget / len(variants), 2)
            return {var.get("variant_id"): share for var in variants}

        allocations = {}
        for var_id, score in samples.items():
            allocations[var_id] = round((score / total_score) * total_budget, 2)
            
        return allocations
