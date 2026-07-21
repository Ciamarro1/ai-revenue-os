class RewardModel:
    """
    Modelo de Recompensa Composta (Composite Reward Model).
    Combina métricas orgânicas (CTR, Retenção) e financeiras (Lucro) para guiar o aprendizado.
    """
    def __init__(self, w_revenue: float = 0.5, w_ctr: float = 0.3, w_retention: float = 0.2):
        self.w_revenue = w_revenue
        self.w_ctr = w_ctr
        self.w_retention = w_retention

    def calculate_reward(self, revenue_usd: float, ctr_percent: float, retention_3s_percent: float) -> float:
        # Pondera o retorno financeiro com os sinais precoces de retenção orgânica.
        # Normaliza contra benchmarks operacionais:
        # - Lucro de $50 por vídeo = pontuação 1.0
        # - CTR de 5.0% = pontuação 1.0
        # - Retenção inicial de 60% = pontuação 1.0
        norm_rev = min(1.0, revenue_usd / 50.0)
        norm_ctr = min(1.0, ctr_percent / 5.0)
        norm_ret = min(1.0, retention_3s_percent / 60.0)

        composite = (
            (self.w_revenue * norm_rev) + 
            (self.w_ctr * norm_ctr) + 
            (self.w_retention * norm_ret)
        )
        # Retorna o score final em escala percentual (0 a 100)
        return round(composite * 100, 2)
