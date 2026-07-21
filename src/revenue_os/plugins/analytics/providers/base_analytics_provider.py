from abc import ABC, abstractmethod
from typing import Dict, Any
from src.revenue_os.plugins.analytics.models import AnalyticsEventPayload

class BaseAnalyticsProvider(ABC):
    """
    Interface Abstrata para Provedores de Telemetria e Analytics.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    def is_enabled(self) -> bool:
        return True

    @abstractmethod
    def track_event(self, event: AnalyticsEventPayload) -> Dict[str, Any]:
        pass
