import json
from pathlib import Path
from typing import Dict, Any

class ExperimentTracker:
    """
    Rastreador de Experimentos (Telemetria) - EXP-007.
    Registra a "caixa preta" do pipeline completo em formato JSONL (O(1) append).
    """
    def __init__(self, storage_dir: str = "knowledge"):
        self.db_path = Path(__file__).parent.parent.parent / storage_dir / "experiments.jsonl"
        self._ensure_db()
        
    def _ensure_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.db_path.exists():
            # Toca o arquivo
            self.db_path.touch()

    def log_experiment(self, payload: Dict[str, Any]):
        """
        Faz o append do registro do experimento como uma linha JSON (JSON Lines).
        """
        with open(self.db_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
            
        print(f"📊 [Tracker] Experimento '{payload.get('experiment_id')}' gravado com sucesso no JSONL.")
