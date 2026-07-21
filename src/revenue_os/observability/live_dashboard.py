from typing import Dict, Any, List
from src.revenue_os.observability.platform_maturity import PlatformMaturityEngine
from src.revenue_os.observability.reliability_metrics import ReliabilityMetricsEngine

class LiveOperationsDashboard:
    """
    Dashboard de Operações em Tempo Real (v6.5).
    Distingue estritamente a origem dos dados: REAL_PRODUCTION vs SIMULATED_BENCHMARK (Diretriz EDD).
    """

    def __init__(self):
        self.pmi_engine = PlatformMaturityEngine()
        self.reliability_engine = ReliabilityMetricsEngine()

    def get_live_dashboard_metrics(
        self,
        metric_source: str = "SIMULATED_BENCHMARK",  # "REAL_PRODUCTION" ou "SIMULATED_BENCHMARK"
        published_assets_count: int = 14,
        active_landings_count: int = 14,
        published_pins_count: int = 280,
        average_ctr: float = 0.029,
        total_clicks: int = 1340,
        total_conversions: int = 11,
        total_revenue_usd: float = 182.0,
        total_infra_cost_usd: float = 132.85,
        recent_rois: List[float] = [1.37, 1.42, 1.35]
    ) -> Dict[str, Any]:
        
        net_profit_usd = round(total_revenue_usd - total_infra_cost_usd, 2)
        net_roi_ratio = round(net_profit_usd / max(1.0, total_infra_cost_usd), 2)

        rri = self.reliability_engine.calculate_rri(recent_rois=recent_rois)
        kqi = self.reliability_engine.calculate_kqi(confirmed_rules_count=18, rejected_rules_count=2)
        pmi = self.pmi_engine.calculate_pmi()

        is_real_production = (metric_source == "REAL_PRODUCTION")

        return {
            "metric_source": metric_source,
            "is_verified_real_production": is_real_production,
            "funnel_metrics": {
                "published_assets_count": published_assets_count,
                "active_landings_count": active_landings_count,
                "published_pins_count": published_pins_count,
                "average_ctr_percentage": round(average_ctr * 100, 2),
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "conversion_rate_percentage": round((total_conversions / max(1, total_clicks)) * 100, 2)
            },
            "financial_metrics": {
                "total_revenue_usd": total_revenue_usd,
                "total_infra_cost_usd": total_infra_cost_usd,
                "net_profit_usd": net_profit_usd,
                "net_roi_ratio": net_roi_ratio
            },
            "platform_health_indices": {
                "pmi_score": pmi["pmi_score"],
                "rri_score": rri["rri_score"],
                "kqi_score": kqi["kqi_score"]
            },
            "edd_validation": {
                "pm_milestones_proven": is_real_production,
                "status": "VALIDATED_PRODUCTION_EVIDENCE" if is_real_production else "SIMULATED_BENCHMARK_PROMPT"
            }
        }
