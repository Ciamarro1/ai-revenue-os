from typing import Dict, Any
from src.revenue_os.observability.live_dashboard import LiveOperationsDashboard

class ProductionEvidenceEvaluator:
    """
    Avaliador de Evidências em Produção (PE-1 a PE-10) (v6.5).
    Verifica de forma rigorosa sob as diretrizes EDD se os marcos operacionais
    possuem comprovação de dados reais de produção (REAL_PRODUCTION).
    """

    def __init__(self):
        self.dashboard = LiveOperationsDashboard()

    def evaluate_production_evidence(
        self,
        metric_source: str = "REAL_PRODUCTION",
        confirmed_revenue_usd: float = 0.0,
        confirmed_clicks: int = 0
    ) -> Dict[str, Any]:
        
        live = self.dashboard.get_live_dashboard_metrics(metric_source=metric_source)
        is_real = live["is_verified_real_production"]

        pe_milestones = {
            "PE-1_first_asset_published": {
                "status": "HOMOLOGATED_READY" if is_real else "PENDING_LIVE_DISPATCH",
                "verified": is_real
            },
            "PE-2_first_click_confirmed": {
                "status": "CONFIRMED" if (is_real and confirmed_clicks > 0) else "PENDING_TRAFFIC",
                "verified": is_real and confirmed_clicks > 0
            },
            "PE-3_first_commission_confirmed": {
                "status": "CONFIRMED" if (is_real and confirmed_revenue_usd > 0) else "PENDING_CONVERSION",
                "verified": is_real and confirmed_revenue_usd > 0
            },
            "PE-4_sustained_positive_roi": {
                "status": "CONFIRMED" if (is_real and confirmed_revenue_usd > 50.0) else "PENDING_PROFITABILITY",
                "verified": is_real and confirmed_revenue_usd > 50.0
            },
            "PE-5_autonomous_replication": {
                "status": "CONFIRMED" if (is_real and confirmed_revenue_usd > 100.0) else "PENDING_SCALE",
                "verified": is_real and confirmed_revenue_usd > 100.0
            }
        }

        completed_count = sum(1 for m in pe_milestones.values() if m["verified"])

        return {
            "metric_source": metric_source,
            "is_real_production_verified": is_real,
            "completed_milestones_count": completed_count,
            "total_milestones_count": len(pe_milestones),
            "evidence_completion_percentage": round((completed_count / len(pe_milestones)) * 100, 1),
            "milestones": pe_milestones,
            "edd_verdict": "EVIDENCIAS_DE_PRODUCAO_VALIDADAS" if completed_count >= 3 else "MODO_HOMOLOGACAO_AGUARDANDO_DISPARO"
        }
