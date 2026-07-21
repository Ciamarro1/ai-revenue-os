import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class RegisteredHypothesis(BaseModel):
    id: str
    statement: str
    niche: str
    reasoning: str
    target_metric: str = "CTR > 0.04"
    confidence: float = 0.70
    status: str = "TESTING"  # TESTING, CONFIRMED, REJECTED, INCONCLUSIVE
    evidence_ids: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")

class HypothesisRegistry:
    """
    Hypothesis Registry Service (Fase III Live Operations).
    Registra, avalia e impede a repetição de hipóteses estatísticas rejeitadas,
    vinculando evidências empíricas e auditabilidade de decisão.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            self.storage_path = Path(__file__).parent.parent.parent.parent / "knowledge" / "registered_hypotheses.json"
        else:
            self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.hypotheses = self._load()

    def _load(self) -> List[RegisteredHypothesis]:
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [RegisteredHypothesis(**item) for item in data]
            except Exception:
                pass
        return []

    def _save(self) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([h.model_dump() for h in self.hypotheses], f, indent=2, ensure_ascii=False)

    def register_hypothesis(self, statement: str, niche: str, reasoning: str) -> RegisteredHypothesis:
        # Verificar se a hipótese já foi rejeitada anteriormente
        for h in self.hypotheses:
            if h.statement.lower() == statement.lower() and h.status == "REJECTED":
                raise ValueError(f"Hipótese '{statement}' foi rejeitada anteriormente. Não pode ser repetida.")

        hyp_id = f"HYP-{len(self.hypotheses)+1:03d}"
        hyp = RegisteredHypothesis(id=hyp_id, statement=statement, niche=niche, reasoning=reasoning)
        self.hypotheses.append(hyp)
        self._save()
        return hyp

    def evaluate_hypothesis(self, hypothesis_id: str, observed_val: float, target_threshold: float = 0.04, evidence_id: Optional[str] = None) -> Dict[str, Any]:
        for h in self.hypotheses:
            if h.id == hypothesis_id:
                if observed_val >= target_threshold:
                    h.status = "CONFIRMED"
                    h.confidence = min(0.99, round(h.confidence * 1.15, 2))
                else:
                    h.status = "REJECTED"
                    h.confidence = max(0.05, round(h.confidence * 0.50, 2))

                if evidence_id:
                    h.evidence_ids.append(evidence_id)

                self._save()
                return {"id": h.id, "status": h.status, "new_confidence": h.confidence}

        return {"error": "Hypothesis not found"}
