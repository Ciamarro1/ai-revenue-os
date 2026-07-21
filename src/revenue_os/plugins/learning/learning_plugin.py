from typing import Dict, Any, Optional
from src.revenue_os.plugins.base_plugin import BasePlugin
from src.revenue_os.plugins.learning.models import LearningConfig
from src.revenue_os.plugins.learning.engine import ProductionLearningEngine
from src.revenue_os.plugins.learning.scheduler import LearningScheduler

class ProductionLearningPlugin(BasePlugin):
    """
    ProductionLearningPlugin (Sprint O8).
    Plugin oficial de aprendizado contínuo e calibração de produção estendendo o BasePlugin SDK.
    Garante que SOMENTE evidências REAL_PRODUCTION alterem os pesos do EconomicBrain.
    """

    def __init__(self, config: Optional[LearningConfig] = None):
        self.config = config or LearningConfig()
        self.engine = ProductionLearningEngine(self.config)
        self.scheduler = LearningScheduler(self.engine)
        self._initialized = False

    @property
    def plugin_name(self) -> str:
        return "production_learning_plugin"

    @property
    def category(self) -> str:
        return "learning"

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self._initialized else "UNHEALTHY",
            "plugin_name": self.plugin_name,
            "category": self.category,
            "promotion_threshold": self.config.promotion_threshold,
            "rejection_threshold": self.config.rejection_threshold,
            "scheduler_status": self.scheduler.get_status()
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action", "run_cycle")

        if action == "run_cycle" or action == "recalibrate":
            custom_entries = payload.get("entries")
            res = self.engine.run_cycle(custom_entries)
            return {"status": "SUCCESS", "cycle_result": res.model_dump()}

        elif action == "get_hypotheses":
            return {"status": "SUCCESS", "hypotheses": self.engine.get_hypotheses()}

        elif action == "get_weights":
            return {"status": "SUCCESS", "weights": self.engine.get_weights()}

        raise ValueError(f"Ação desconhecida '{action}' para ProductionLearningPlugin")

    def shutdown(self) -> None:
        self._initialized = False
