from typing import List, Dict, Any, Optional
from src.core.cognition.repository import CognitiveRepository
from src.core.cognition.evidence_engine import EvidenceEngine
from src.core.cognition.models import Evidence

class EvidenceAPI:
    """
    Evidence Facade API.
    Isola o registro e cálculo estatístico de qualidade das evidências coletadas.
    """
    def __init__(self, repo: CognitiveRepository, engine: EvidenceEngine):
        self.repo = repo
        self.engine = engine

    def list_evidence(self) -> List[Evidence]:
        """Retorna todas as evidências registradas."""
        return self.repo.get_evidence()

    def get_by_experiment(self, experiment_id: str) -> List[Evidence]:
        """Retorna evidências de um experimento."""
        return self.repo.get_evidence_by_experiment(experiment_id)

    def register(
        self,
        hypothesis_id: int,
        experiment_id: str,
        claim: str,
        confidence_score: float,
        impact: str,
        narrative: str
    ) -> Evidence:
        """Registra uma nova evidência empírica."""
        evidence = Evidence(
            hypothesis_id=hypothesis_id,
            experiment_id=experiment_id,
            claim=claim,
            confidence_score=confidence_score,
            impact=impact,
            narrative=narrative
        )
        return self.repo.register_evidence(evidence)

    def evaluate(
        self,
        evidence_id: int,
        sample_size: int,
        statistical_confidence: float,
        reliability: float
    ) -> float:
        """Avalia e persiste a qualidade da evidência no SQLite."""
        return self.engine.evaluate_evidence(
            evidence_id=evidence_id,
            sample_size=sample_size,
            statistical_confidence=statistical_confidence,
            reliability=reliability
        )

