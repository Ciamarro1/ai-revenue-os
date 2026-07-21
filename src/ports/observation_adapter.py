from abc import ABC, abstractmethod
from typing import List
from src.core.cognition.models import Observation

class ObservationAdapter(ABC):
    """
    Porta Hexagonal para adaptadores de observação (Sprint 6.3).
    Ingere métricas e as converte em modelos Observation.
    """
    @abstractmethod
    def fetch_observations(self, content_id: str) -> List[Observation]:
        """Recupera métricas e retorna uma lista de observações associadas."""
        pass
