from typing import List, Optional
from src.core.cognition.planning_repository import PlanningRepository
from src.core.cognition.planning_service import PlanningService
from src.core.cognition.models import Objective, Plan, PlanStep
from src.services.decision_queue import DecisionQueue

class PlanningAPI:
    """
    Planning Facade API (Sprint 6.5).
    Isola a consulta, formulação de objetivos e geração de planos tácticos.
    """
    def __init__(self, repository: PlanningRepository, service: PlanningService):
        self.repository = repository
        self.service = service

    def create_objective(self, description: str, target_metric: str) -> Objective:
        """Cadastra um novo objetivo estratégico de negócio."""
        objective = Objective(description=description, target_metric=target_metric, status="Active")
        return self.repository.save_objective(objective)

    def generate_plans(self, objective_id: int) -> List[Plan]:
        """Gera e prioriza planos empíricos associados a um objetivo."""
        return self.service.generate_plans(objective_id)

    def get_plan_steps(self, plan_id: int) -> List[PlanStep]:
        """Lista os passos operacionais de um plano."""
        return self.repository.get_plan_steps(plan_id)

    def enqueue_step(self, step_id: int, queue: DecisionQueue) -> str:
        """Enfileira um passo de plano na Decision Queue gerando um experimento."""
        return self.service.enqueue_plan_step(step_id, queue)

    def get_objectives(self) -> List[Objective]:
        """Lista todos os objetivos estratégicos."""
        return self.repository.get_objectives()

    def get_plans(self) -> List[Plan]:
        """Lista todos os planos gerados."""
        return self.repository.get_plans()
