import math
import random
from typing import Dict, Any, List
from datetime import datetime, timezone

from src.revenue_os.analytics.genome_library import Genome, GenomeLibrary
from src.revenue_os.analytics.knowledge_flywheel import KnowledgeFlywheel
from src.revenue_os.portfolio_manager import PortfolioManager

class RealitySimulator:
    """
    Reality Simulator do AI Revenue OS.
    Simula a publicação em escala de milhares de mídias (ex: 10.000 Pins ao longo de 180 dias)
    para medir a velocidade de aprendizado do sistema, receita acumulada, custos e ROI
    antes de investir capital financeiro real.
    """

    def __init__(self, base_ctr: float = 0.025, base_conversion: float = 0.03, avg_ticket_usd: float = 15.0):
        self.base_ctr = base_ctr
        self.base_conversion = base_conversion
        self.avg_ticket_usd = avg_ticket_usd
        self.genome_lib = GenomeLibrary()
        self.flywheel = KnowledgeFlywheel()
        self.portfolio_manager = PortfolioManager()

    def simulate_long_term_run(self, total_posts: int = 10000, days: int = 180, cost_per_post_usd: float = 0.05) -> Dict[str, Any]:
        """
        Simula a execução contínua de D dias e P posts, medindo o crescimento da curva de aprendizado.
        """
        posts_per_day = total_posts // max(1, days)
        cumulative_impressions = 0
        cumulative_clicks = 0
        cumulative_saves = 0
        cumulative_conversions = 0
        cumulative_revenue = 0.0
        cumulative_cost = total_posts * cost_per_post_usd

        # Simulação do aprendizado em flywheel (curva logarítmica de melhoria de CTR)
        daily_snapshots = []

        current_ctr = self.base_ctr
        current_conv = self.base_conversion

        for day in range(1, days + 1):
            # A cada 10 dias, o aprendizado da Flywheel incrementa o CTR e a conversão por refinamento de Genomas
            if day % 10 == 0:
                current_ctr = min(0.085, current_ctr * 1.04)
                current_conv = min(0.075, current_conv * 1.03)

            day_impressions = posts_per_day * random.randint(800, 1500)
            day_clicks = int(day_impressions * current_ctr)
            day_saves = int(day_impressions * (current_ctr * 0.8))
            day_conversions = int(day_clicks * current_conv)
            day_revenue = round(day_conversions * self.avg_ticket_usd, 2)

            cumulative_impressions += day_impressions
            cumulative_clicks += day_clicks
            cumulative_saves += day_saves
            cumulative_conversions += day_conversions
            cumulative_revenue += day_revenue

            if day % 30 == 0 or day == days:
                daily_snapshots.append({
                    "day": day,
                    "cumulative_posts": day * posts_per_day,
                    "current_ctr_percent": round(current_ctr * 100, 2),
                    "cumulative_revenue_usd": round(cumulative_revenue, 2),
                    "net_profit_usd": round(cumulative_revenue - (day * posts_per_day * cost_per_post_usd), 2)
                })

        net_profit = round(cumulative_revenue - cumulative_cost, 2)
        roi_ratio = round(cumulative_revenue / max(1.0, cumulative_cost), 2)

        return {
            "simulation_parameters": {
                "total_posts": total_posts,
                "days": days,
                "posts_per_day": posts_per_day,
                "cost_per_post_usd": cost_per_post_usd,
                "total_infra_cost_usd": cumulative_cost
            },
            "cumulative_results": {
                "impressions": cumulative_impressions,
                "clicks": cumulative_clicks,
                "saves": cumulative_saves,
                "conversions": cumulative_conversions,
                "gross_revenue_usd": round(cumulative_revenue, 2),
                "net_profit_usd": net_profit,
                "roi_ratio": f"{roi_ratio}x",
                "final_learned_ctr": f"{round(current_ctr * 100, 2)}%"
            },
            "snapshots_every_30_days": daily_snapshots
        }
