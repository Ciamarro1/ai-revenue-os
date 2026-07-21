from typing import List, Dict, Any
from src.revenue_os.observability.reality_snapshot import RealitySnapshotTracker
from src.revenue_os.analytics.calibration_engine import CalibrationEngine
import time

class HistoricalReplaySimulator:
    """
    Motor da Fase 2 (VP-001).
    Ingere Datasets do passado e os projeta no Simulador de Calibração,
    sem gastar 1 único centavo real nas APIs.
    """
    def __init__(self):
        self.snapshot = RealitySnapshotTracker(log_path="replay_snapshots.jsonl")
        self.calibration = CalibrationEngine()
        
    def inject_historical_dataset(self, dataset: List[Dict[str, Any]]):
        """
        Recebe um array de campanhas antigas e testa o drift preditivo do sistema.
        Ex Dataset: [{"cycle": 1, "predicted": 4.8, "real": 3.7, "context": "productivity"}]
        """
        print(f"Iniciando Historical Replay de {len(dataset)} ciclos...")
        
        for record in dataset:
            # 1. Mede a falha de predição
            drift = self.calibration.calculate_predictive_bias(
                metric_name="CTR",
                predicted=record["predicted"],
                reality=record["real"],
                context_key=record["context"]
            )
            
            # 2. Imortaliza no Snapshot
            self.snapshot.take_snapshot(
                cycle_id=record["cycle"],
                predicted_reward=record["predicted"],
                real_reward=record["real"],
                decision="HOLD", # Decisão mockada em Replay
                profit=0.0
            )
            
            print(f"Cycle {record['cycle']}: {drift['trend']} | Fator de Correção: {drift['correction_multiplier']}")
            time.sleep(0.01) # Simula async
            
        print("Replay Concluído. O Calibration Engine foi treinado.")
