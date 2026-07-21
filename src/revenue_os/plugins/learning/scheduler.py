import time
import logging
from typing import Optional, Dict, Any
from src.revenue_os.plugins.learning.engine import ProductionLearningEngine
from src.revenue_os.plugins.learning.models import LearningCycleResult

class LearningScheduler:
    """
    Agendador de Ciclos de Aprendizado e Recalibração de Produção.
    """

    def __init__(self, engine: Optional[ProductionLearningEngine] = None):
        self.engine = engine or ProductionLearningEngine()
        self.last_run_time: Optional[float] = None
        self.last_result: Optional[LearningCycleResult] = None

    def trigger_cycle(self) -> LearningCycleResult:
        """
        Executa um ciclo completo de aprendizado sob o filtro estrito de proveniência EDD.
        """
        logging.info("[LearningScheduler] Iniciando ciclo de aprendizado de produção...")
        result = self.engine.run_cycle()
        self.last_run_time = time.time()
        self.last_result = result
        logging.info(f"[LearningScheduler] Ciclo {result.cycle_id} concluído. Versão do Dataset: {result.dataset_version}")
        return result

    def get_status(self) -> Dict[str, Any]:
        return {
            "last_run_time": self.last_run_time,
            "last_cycle_id": self.last_result.cycle_id if self.last_result else None,
            "dataset_version": self.last_result.dataset_version if self.last_result else None
        }
