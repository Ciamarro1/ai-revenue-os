from abc import ABC, abstractmethod
from typing import Dict, Any, List

class FeatureStorePort(ABC):
    """
    Feature Store Port interface.
    Decouples feature store backends (Feast, SQLite features cache).
    """
    @abstractmethod
    def get_features(self, entity_id: str, feature_names: List[str]) -> Dict[str, Any]:
        """Recupera features de uma entidade específica."""
        pass

    @abstractmethod
    def store_features(self, entity_id: str, features: Dict[str, Any]):
        """Persiste um conjunto de features para uma entidade."""
        pass
