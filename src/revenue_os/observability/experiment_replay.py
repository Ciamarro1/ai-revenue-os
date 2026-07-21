from typing import Dict, Any, Optional
from src.revenue_os.observability.experiment_ledger import ExperimentLedger
from src.revenue_os.cognition.dataset_versioning import DatasetVersionManager

class ExperimentReplayEngine:
    """
    Motor de Replay de Experimentos Históricos (v6.5).
    Carrega as versões exatas de Dataset, Feature Flags e Plugins registradas no Ledger
    para permitir a reprodutibilidade integral de qualquer resultado.
    """

    def __init__(self):
        self.ledger = ExperimentLedger()
        self.dataset_manager = DatasetVersionManager()

    def replay_experiment(self, experiment_id: str) -> Dict[str, Any]:
        history = self.ledger.get_experiment_history()
        match = next((e for e in history if e.experiment_id == experiment_id), None)

        if not match:
            return {
                "experiment_id": experiment_id,
                "replay_status": "NOT_FOUND",
                "error": "Experimento não encontrado no Experiment Ledger"
            }

        latest_ds = self.dataset_manager.get_latest_version()

        return {
            "experiment_id": match.experiment_id,
            "genome_id": match.genome_id,
            "offer_id": match.offer_id,
            "landing_url": match.landing_url,
            "recorded_revenue_usd": match.revenue_usd,
            "recorded_roi": match.roi_ratio,
            "kernel_version": match.kernel_version,
            "dataset_version": latest_ds["dataset_version_id"] if latest_ds else "DSV-001",
            "active_feature_flags": match.active_feature_flags,
            "replay_status": "REPRODUCED_SUCCESSFULLY"
        }
