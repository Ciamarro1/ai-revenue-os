import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class ExperimentRecord(BaseModel):
    """
    Registro Imutável no Livro Contábil de Experimentos (Experiment Ledger).
    Garante reprodutibilidade total de qualquer resultado empírico obtido.
    """
    experiment_id: str
    parent_experiment_id: Optional[str] = None
    genome_id: str
    offer_id: str
    landing_url: str
    channel: str = "pinterest"
    marketplace: str = "hotmart"
    infra_cost_usd: float
    revenue_usd: float
    roi_ratio: float
    ctr: float
    conversions: int
    kernel_version: str = "v4.5"
    active_feature_flags: Dict[str, Any] = Field(default_factory=dict)
    model_name: str = "gemini-2.5-flash"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")

class ExperimentLedger:
    """
    Livro Contábil Imutável de Experimentos (Sprint L1 + EDD).
    Registra de forma permanente e auditável todos os parâmetros e resultados de cada experimento concluído.
    """

    def __init__(self, ledger_path: Optional[Path] = None):
        if ledger_path is None:
            self.ledger_path = Path(__file__).parent.parent.parent.parent / "knowledge" / "experiment_ledger.jsonl"
        else:
            self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def record_experiment(self, record_data: Dict[str, Any]) -> ExperimentRecord:
        record = ExperimentRecord(**record_data)
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.model_dump(), ensure_ascii=False) + "\n")
        return record

    def get_experiment_history(self) -> List[ExperimentRecord]:
        history = []
        if not self.ledger_path.exists():
            return history

        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        history.append(ExperimentRecord(**data))
                    except Exception:
                        continue
        return history
