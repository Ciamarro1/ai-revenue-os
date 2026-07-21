from typing import List, Optional
from src.core.cognition.repository import CognitiveRepository
from src.core.cognition.belief_manager import BeliefManager
from src.core.cognition.models import Belief, Observation, Evidence

class BeliefAPI:
    """
    Belief Facade API.
    Isola a leitura e atualização síncrona da confiança de crenças do sistema.
    """
    def __init__(self, repo: CognitiveRepository, manager: BeliefManager):
        self.repo = repo
        self.manager = manager

    def list_beliefs(self) -> List[Belief]:
        """Retorna todas as crenças estratégicas."""
        return self.repo.get_beliefs()

    def get_belief(self, belief_id: int) -> Optional[Belief]:
        """Recupera uma crença específica pelo ID."""
        beliefs = self.repo.get_beliefs()
        return next((b for b in beliefs if b.id == belief_id), None)

    def evolve(
        self,
        belief_id: int,
        evidence_confidence: float,
        impact: str,
        reason: str,
        learning_rate: float = 0.10,
        quality_score: float = 1.0
    ) -> float:
        """Executa a evolução Bayesiana-like da confiança de uma crença."""
        return self.manager.evolve_belief(
            belief_id=belief_id,
            evidence_confidence=evidence_confidence,
            impact=impact,
            reason=reason,
            learning_rate=learning_rate,
            quality_score=quality_score
        )

    def process_observation(
        self,
        observation: Observation,
        related_belief_id: int,
        baseline_value: float = 1.0,
        tolerance_percent: float = 10.0,
        experiment_id: Optional[str] = None
    ) -> Evidence:
        """Processa observação, gera evidência e revisa a crença relacionada."""
        from src.core.cognition.belief_service import BeliefService
        service = BeliefService(self.repo, self.manager)
        return service.process_observation(
            observation=observation,
            related_belief_id=related_belief_id,
            baseline_value=baseline_value,
            tolerance_percent=tolerance_percent,
            experiment_id=experiment_id
        )

