import json
from datetime import datetime
from typing import List, Dict, Any
import os

class DecisionLedger:
    """
    O Livro Caixa de Decisões.
    Permite total rastreabilidade (auditoria) sobre onde e porquê o motor alocou fundos.
    Obrigatório para Fase B (Robustness).
    """
    def __init__(self, log_path: str = "decisions.jsonl"):
        self.log_path = log_path

    def record_decision(self, experiment_id: str, decision: str, reasons: List[str], metadata: Dict[str, Any] = None):
        """Grava uma decisão imutável de caixa no arquivo .jsonl"""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "decision": decision,
            "experiment": experiment_id,
            "reason": reasons,
            "metadata": metadata or {}
        }
        
        # Append-only (imutabilidade simulada localmente)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            
    def read_history(self, tail_lines: int = 50) -> List[Dict[str, Any]]:
        """Leitura retroativa para auditoria humana ou Calibração de Agente."""
        if not os.path.exists(self.log_path):
            return []
            
        with open(self.log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        history = [json.loads(l) for l in lines[-tail_lines:]]
        return history
