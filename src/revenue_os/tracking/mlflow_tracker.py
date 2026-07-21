import os
import mlflow
import threading
from pathlib import Path

class MLflowTracker:
    """
    Camada de Observabilidade Experimental sobre o AI Revenue OS.
    Utiliza MLflow para criar um dashboard científico sem interferir no banco original SQLite.
    """
    _local_lock = threading.Lock()
    
    def __init__(self, db_path: str = "knowledge/mlflow.db", tracking_uri: str = None):
        # Resolve o path absoluto para garantir que sempre fique no lugar certo
        project_root = Path(__file__).parent.parent.parent.parent
        db_full_path = project_root / db_path
        db_full_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.tracking_uri = tracking_uri or f"sqlite:///{db_full_path}"
        mlflow.set_tracking_uri(self.tracking_uri)
        
        self.experiment_name = "AI_Revenue_OS_Experiments"
        mlflow.set_experiment(self.experiment_name)
        
        self.active_run = None
        
    def start_run(self, experiment_id: str, run_name: str = None):
        """Inicia uma sessão de tracking para um experimento."""
        with self._local_lock:
            # End previous run if any
            if mlflow.active_run():
                mlflow.end_run()
                
            run_name = run_name or experiment_id
            self.active_run = mlflow.start_run(run_name=run_name)
            # Log o ID original do nosso sistema como tag para facilitar busca
            mlflow.set_tag("revenue_os_experiment_id", experiment_id)
            return self.active_run

    def log_parameters(self, params: dict):
        """Registra parâmetros da hipótese (hook, topic, etc)."""
        if self.active_run:
            mlflow.log_params(params)

    def log_metrics(self, metrics: dict):
        """Registra resultados do mundo real (ctr, retention, etc)."""
        if self.active_run:
            # MLflow metrics only accept numbers
            numeric_metrics = {k: v for k, v in metrics.items() if isinstance(v, (int, float))}
            mlflow.log_metrics(numeric_metrics)

    def log_artifacts(self, local_dir: str):
        """Faz o upload dos arquivos gerados (json, vídeos) para o dashboard."""
        if self.active_run and os.path.exists(local_dir):
            mlflow.log_artifacts(local_dir)

    def log_timing(self, operation_name: str, duration_seconds: float):
        """Registra timing de uma operação como métrica no MLflow."""
        if self.active_run:
            try:
                mlflow.log_metrics({f"timing_{operation_name}_seconds": round(duration_seconds, 3)})
            except Exception:
                pass

    def end_run(self, status: str = "FINISHED"):
        """Finaliza a sessão do MLflow."""
        with self._local_lock:
            if mlflow.active_run():
                mlflow.end_run(status=status)
            self.active_run = None
