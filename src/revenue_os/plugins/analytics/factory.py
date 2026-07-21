from typing import Optional
from src.revenue_os.plugins.analytics.models import AnalyticsConfig
from src.revenue_os.plugins.analytics.analytics_plugin import AnalyticsProductionPlugin

class AnalyticsPluginFactory:
    """
    Factory Pattern para criação unificada do Analytics Production Plugin.
    """

    @staticmethod
    def create_analytics_plugin(config: Optional[AnalyticsConfig] = None) -> AnalyticsProductionPlugin:
        config = config or AnalyticsConfig()
        return AnalyticsProductionPlugin(config=config)
