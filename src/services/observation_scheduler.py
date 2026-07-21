import time
from typing import List, Optional
from src.core.kernel import CognitiveKernel
from src.ports.observation_adapter import ObservationAdapter

class ObservationScheduler:
    """
    Scheduler de Observação (Sprint 6.3).
    Ingere métricas de provedores externos via ObservationAdapters,
    gerando novas observações na base cognitiva do Kernel.
    """
    def __init__(self, kernel: CognitiveKernel, adapters: List[ObservationAdapter]):
        self.kernel = kernel
        self.adapters = adapters

    def poll_metrics(self, content_id: str, related_belief_id: int, experiment_id: Optional[str] = None) -> int:
        """
        Busca métricas externas para um content_id e insere observações.
        Retorna a quantidade de novas observações geradas.
        """
        count = 0
        for adapter in self.adapters:
            try:
                obs_list = adapter.fetch_observations(content_id)
                for obs in obs_list:
                    self.kernel.beliefs.process_observation(
                        observation=obs,
                        related_belief_id=related_belief_id,
                        experiment_id=experiment_id
                    )
                    count += 1
            except Exception as e:
                print(f"⚠️ [ObservationScheduler] Erro ao obter observações para {content_id}: {e}")
        return count
