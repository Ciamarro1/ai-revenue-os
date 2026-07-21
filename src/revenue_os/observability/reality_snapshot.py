import json
import os
from typing import Dict, Any

class RealitySnapshotTracker:
    """
    Gravação da Série Temporal (VP-001).
    Consolida as 100 rodadas obrigatórias capturando a margem de erro entre 
    o laboratório matemático e o mundo real (API Pinterest).
    """
    def __init__(self, log_path: str = "reality_snapshots.jsonl"):
        self.log_path = log_path
        
    def take_snapshot(self, cycle_id: int, predicted_reward: float, real_reward: float, decision: str, profit: float):
        entry = {
            "cycle": cycle_id,
            "predicted_reward": round(predicted_reward, 3),
            "real_reward": round(real_reward, 3),
            "calibration_error": round(abs(predicted_reward - real_reward), 3),
            "allocator_decision": decision,
            "profit": round(profit, 2)
        }
        
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            
    def get_historical_calibration_error(self) -> float:
        """
        Recupera o erro médio histórico para que o Calibration Engine injete a correção de viés.
        """
        if not os.path.exists(self.log_path):
            return 0.0
            
        with open(self.log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        if not lines:
            return 0.0
            
        total_error = sum(json.loads(line)["calibration_error"] for line in lines)
        return total_error / len(lines)
