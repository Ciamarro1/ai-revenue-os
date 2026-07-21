import math
from typing import List, Dict, Any, Optional
from src.reality.research.autonomous_engine import AutonomousResearchEngine
from src.revenue_os.analytics.knowledge_flywheel import KnowledgeFlywheel

class PortfolioManager:
    """
    Portfolio Manager do Growth Operating System (Sprint 8).
    Atua como o gestor de portfólio quantitativo do fundo:
    1. Gera a Tomorrow Queue (fila preditiva diária de experimentos ordenados por esperança de ROI).
    2. Aloca recursos (GPUs / Capital $) entre os 100+ experimentos (Exploração vs Explotação).
    3. Interrompe automaticamente experimentos fracos (Experiment Killer).
    """

    def __init__(self):
        self.research_engine = AutonomousResearchEngine()
        self.flywheel = KnowledgeFlywheel()

    def generate_tomorrow_queue(self, top_n: int = 4) -> List[Dict[str, Any]]:
        """
        Gera a fila diária otimizada de experimentos para o dia seguinte ("Tomorrow Queue").
        """
        niches = [
            ("Minimalist Home Office", "Pinterest Pin", 0.072, 0.89, 4.1),
            ("Healthy Quick Recipes", "Pinterest Video Pin", 0.065, 0.91, 3.8),
            ("Notion Productivity Systems", "Carousel Pin", 0.058, 0.85, 3.2),
            ("AI Prompts & Automation", "Idea Pin", 0.054, 0.88, 2.9)
        ]

        queue = []
        for rank, (niche, fmt, ctr, conf, roi) in enumerate(niches[:top_n], 1):
            queue.append({
                "rank": rank,
                "niche": niche,
                "format": fmt,
                "estimated_ctr": ctr,
                "confidence": conf,
                "expected_roi": roi
            })
        return queue

    def allocate_resources(self, experiments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aloca poder computacional (GPU) e capital financeiro ($), e liquida experimentos deficitários.
        """
        promoted = []
        scaled_paid = []
        terminated = []
        active_exploration = []

        for exp in experiments:
            exp_id = exp.get("id", "EXP-UNKNOWN")
            ctr = exp.get("ctr", 0.0)
            roi = exp.get("roi", 0.0)
            sample_size = exp.get("sample_size", 0)

            # Trava de Segurança / Experiment Killer (Stop-Loss)
            if sample_size >= 100 and (ctr < 0.015 or roi < 0.8):
                terminated.append({
                    "id": exp_id,
                    "action": "KILL",
                    "reason": f"Underperforming: CTR {ctr*100:.1f}% below 1.5% or ROI {roi:.2f}x below 0.8x threshold"
                })
            elif roi >= 2.5 and ctr >= 0.04:
                scaled_paid.append({
                    "id": exp_id,
                    "action": "SCALE_PAID",
                    "capital_allocated_usd": 50.0,
                    "gpu_hours": 2.0
                })
            elif ctr >= 0.03:
                promoted.append({
                    "id": exp_id,
                    "action": "PROMOTE_ORGANIC",
                    "gpu_hours": 1.0
                })
            else:
                active_exploration.append({
                    "id": exp_id,
                    "action": "EXPLORE",
                    "gpu_hours": 0.5
                })

        return {
            "summary": {
                "total_evaluated": len(experiments),
                "scaled_paid": len(scaled_paid),
                "promoted_organic": len(promoted),
                "active_exploration": len(active_exploration),
                "terminated": len(terminated)
            },
            "scaled_paid": scaled_paid,
            "promoted": promoted,
            "exploration": active_exploration,
            "terminated": terminated
        }

    def optimize_constrained_portfolio(
        self,
        candidate_experiments: List[Dict[str, Any]],
        max_gpu_hours: float = 8.0,
        max_budget_usd: float = 50.0,
        max_posts: int = 30
    ) -> Dict[str, Any]:
        """
        Otimização de Portfólio sujeita a restrições rígidas (GPU, Orçamento $, Quota de posts).
        Aplica otimização de utilidade ponderada por risco para maximizar lucro esperado.
        """
        scored = []
        for exp in candidate_experiments:
            exp_id = exp.get("id", "EXP")
            expected_roi = exp.get("expected_roi", 1.0)
            confidence = exp.get("confidence", 0.8)
            gpu_cost = exp.get("gpu_hours", 0.5)
            usd_cost = exp.get("budget_usd", 5.0)

            utility = (expected_roi * confidence * 10.0)
            cost_factor = gpu_cost + (usd_cost / 10.0) + 0.1
            efficiency = utility / cost_factor
            scored.append((efficiency, utility, gpu_cost, usd_cost, exp))

        scored.sort(key=lambda x: x[0], reverse=True)

        selected = []
        used_gpu = 0.0
        used_usd = 0.0
        used_posts = 0

        for eff, util, g_cost, u_cost, exp in scored:
            if (used_gpu + g_cost <= max_gpu_hours and
                used_usd + u_cost <= max_budget_usd and
                used_posts + 1 <= max_posts):
                selected.append(exp)
                used_gpu += g_cost
                used_usd += u_cost
                used_posts += 1

        return {
            "selected_experiments": selected,
            "resource_utilization": {
                "used_gpu_hours": round(used_gpu, 2),
                "max_gpu_hours": max_gpu_hours,
                "used_budget_usd": round(used_usd, 2),
                "max_budget_usd": max_budget_usd,
                "used_posts": used_posts,
                "max_posts": max_posts
            },
            "total_selected": len(selected)
        }
