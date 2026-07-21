from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import json
import os

class ExperimentRecord(BaseModel):
    experiment_id: str
    status: str = Field(default="SHADOW_MODE")
    objective: str
    variants: List[str]
    start_date: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    end_date: Optional[str] = None
    owner: str = "Revenue Strategist"
    baseline: str = "Equal Allocation"

class ExperimentRegistry:
    """
    Catálogo Oficial de Experimentos.
    Acompanhamento de longo prazo e auditoria de estado das campanhas (VP-001 Fase 3).
    """
    def __init__(self, db_path: str = "experiment_catalog.jsonl"):
        self.db_path = db_path
        
    def register(self, record: ExperimentRecord):
        with open(self.db_path, "a", encoding="utf-8") as f:
            f.write(record.model_dump_json() + "\n")
            
    def close_experiment(self, experiment_id: str):
        # Numa implementação real de BD, daríamos UPDATE no registro.
        # Aqui, apenas adicionamos uma entrada de fechamento no append-only log.
        closing_entry = {
            "experiment_id": experiment_id,
            "status": "CLOSED",
            "end_date": datetime.utcnow().isoformat()
        }
        with open(self.db_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(closing_entry) + "\n")
