from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from src.revenue_os.connectors.capability_registry import CapabilityRegistry
from src.revenue_os.events.event_backbone import EventBackbone

class ExecutionPlanStep(BaseModel if 'BaseModel' in globals() else object):
    pass

class PlanningEngine:
    """
    Planning Engine do AI Revenue OS.
    Camada intermediária entre o Economic Brain e o Capability Registry / Plugin Runtime.
    Recebe objetivos de receita de alto nível e projeta o plano de trabalho DAG em etapas sequenciais.
    """

    def __init__(self, capability_registry: Optional[CapabilityRegistry] = None, event_backbone: Optional[EventBackbone] = None):
        self.capability_registry = capability_registry or CapabilityRegistry()
        self.event_backbone = event_backbone or EventBackbone()

    def create_execution_plan(self, target_daily_revenue_usd: float = 100.0, niche: str = "productivity") -> Dict[str, Any]:
        """
        Gera um plano de execução completo derivado das capacidades registradas.
        """
        steps = [
            {
                "step_order": 1,
                "phase": "RESEARCH",
                "capability": "market_research",
                "provider": "autonomous_engine",
                "action": f"Varredura multi-fonte para a categoria '{niche}'"
            },
            {
                "step_order": 2,
                "phase": "OPPORTUNITY_SELECTION",
                "capability": "marketplace_connectors",
                "provider": self.capability_registry.get_provider("marketplace_connectors"),
                "action": "Pesquisa e seleção da oferta com maior EPC"
            },
            {
                "step_order": 3,
                "phase": "OFFER_GENERATION",
                "capability": "offer_factory",
                "provider": "offer_manifest_generator",
                "action": "Geração do manifesto estruturado OfferManifest"
            },
            {
                "step_order": 4,
                "phase": "LANDING_BUILD",
                "capability": "landing_generation",
                "provider": self.capability_registry.get_provider("landing_generation"),
                "action": "Compilação de Landing Page via SSG/MDX"
            },
            {
                "step_order": 5,
                "phase": "DISTRIBUTION",
                "capability": "browser_automation",
                "provider": self.capability_registry.get_provider("browser_automation"),
                "action": "Publicação e distribuição de mídias verticais"
            },
            {
                "step_order": 6,
                "phase": "ANALYTICS_AND_FLYWHEEL",
                "capability": "analytics_dashboard",
                "provider": self.capability_registry.get_provider("analytics_dashboard"),
                "action": "Medição de conversão e atualização da Knowledge Flywheel"
            }
        ]

        return {
            "plan_id": f"PLAN-{niche.upper()}-100USD",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "target_daily_revenue_usd": target_daily_revenue_usd,
            "niche": niche,
            "total_steps": len(steps),
            "execution_dag_steps": steps
        }
