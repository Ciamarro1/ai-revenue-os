from src.revenue_os.analytics.schemas import RealWorldMetrics

class EconomicsRewardCalculator:
    """
    Calcula a recompensa Q (Reward) baseada nas métricas orgânicas reais
    do Pinterest para alimentar a GenomeLibrary de forma determinística.
    """
    def calculate(self, metrics: RealWorldMetrics, cost: float) -> float:
        # Se deu lucro real
        profit = metrics.profit_usd - cost
        if profit > 0:
            return min(1.0, 0.6 + (profit / 100.0))
            
        # Se gerou tráfego e engajamento forte mesmo sem conversão
        if metrics.ctr_percent > 3.0 and metrics.impressions > 1000:
            return 0.50
            
        # Fracasso orgânico
        return max(0.0, (metrics.ctr_percent / 10.0))
