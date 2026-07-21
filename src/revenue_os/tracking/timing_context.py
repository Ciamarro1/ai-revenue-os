import time
import logging

logger = logging.getLogger("revenue_os.timing")


class TimingContext:
    """
    Context manager para medir e logar tempos de operações.
    Integra com MLflow quando tracker disponível.
    
    Uso:
        with TimingContext("research", mlflow_tracker) as tc:
            do_work()
        print(f"Levou {tc.elapsed:.2f}s")
    """
    
    def __init__(self, operation_name: str, mlflow_tracker=None):
        self.name = operation_name
        self.tracker = mlflow_tracker
        self.start: float = 0.0
        self.elapsed: float = 0.0
    
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.start
        logger.info(f"{self.name}: {self.elapsed:.2f}s")
        
        if self.tracker:
            try:
                self.tracker.log_metrics({
                    f"timing_{self.name}_seconds": round(self.elapsed, 3)
                })
            except Exception as e:
                logger.warning(f"Erro ao logar timing no MLflow: {e}")
        
        return False  # Don't suppress exceptions
