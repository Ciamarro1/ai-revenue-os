from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class HypothesisState(BaseModel):
    """
    Estado de uma Hipótese no HypothesisRegistry durante o loop de aprendizado.
    """
    hypothesis_id: str
    statement: str
    prior_confidence: float = 0.50
    current_confidence: float = 0.50
    status: str = "CANDIDATE"  # CANDIDATE, PROMOTED_LAW, REJECTED
    sample_size: int = 0
    last_evidence_provenance: Optional[str] = None
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")

class EconomicBrainWeight(BaseModel):
    """
    Peso de decisão recalibrado no EconomicBrain.
    """
    param_name: str
    current_weight: float
    previous_weight: float
    delta: float
    sample_size: int = 0
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")

class LearningCycleResult(BaseModel):
    """
    Resultado de uma iteração completa do Production Learning Loop.
    """
    cycle_id: str
    total_ledger_entries: int
    real_production_entries: int
    ignored_benchmark_entries: int
    hypotheses_evaluated: int
    promoted_count: int
    rejected_count: int
    weights_recalibrated: int
    dataset_version: str
    evaluated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")

class LearningConfig(BaseModel):
    """
    Configuração Pydantic v2 do Production Learning Loop.
    """
    promotion_threshold: float = 0.85
    rejection_threshold: float = 0.15
    learning_rate: float = 0.10
    ledger_file_path: str = "experiment_ledger.jsonl"
    dataset_version_prefix: str = "DS-V"
