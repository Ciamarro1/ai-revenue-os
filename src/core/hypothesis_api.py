from typing import List, Optional
from src.core.cognition.models import Hypothesis
from src.core.cognition.hypothesis_repository import HypothesisRepository
from src.core.cognition.hypothesis_service import HypothesisService

class HypothesisAPI:
    """
    Hypothesis Facade API (Sprint 6.2).
    Isola o gerenciamento, avaliação e evolução de hipóteses do ecossistema.
    """
    def __init__(self, repo: HypothesisRepository, service: HypothesisService):
        self.repo = repo
        self.service = service

    def create(self, statement: str, initial_confidence: float = 0.50) -> Hypothesis:
        """Cria e registra uma nova hipótese."""
        return self.service.create_hypothesis(statement, initial_confidence)

    def get(self, hypothesis_id: int) -> Optional[Hypothesis]:
        """Recupera uma hipótese específica."""
        return self.repo.get_hypothesis(hypothesis_id)

    def list(self) -> List[Hypothesis]:
        """Lista todas as hipóteses registradas."""
        return self.repo.get_hypotheses()

    def evaluate(self, hypothesis_id: int, evidence_id: int, is_supporting: bool, learning_rate: float = 0.15) -> float:
        """Avalia uma hipótese contra uma nova evidência empírica usando cálculo Bayesiano."""
        return self.service.evaluate_evidence(hypothesis_id, evidence_id, is_supporting, learning_rate)

    def promote(self, hypothesis_id: int) -> str:
        """Promove uma hipótese validada para um experimento ativo."""
        return self.service.promote_to_experiment(hypothesis_id)
