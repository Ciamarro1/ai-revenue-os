from typing import Optional
from src.revenue_os.plugins.learning.models import LearningConfig
from src.revenue_os.plugins.learning.learning_plugin import ProductionLearningPlugin

class LearningPluginFactory:
    """
    Factory Pattern para criação unificada do Production Learning Plugin.
    """

    @staticmethod
    def create_learning_plugin(config: Optional[LearningConfig] = None) -> ProductionLearningPlugin:
        config = config or LearningConfig()
        return ProductionLearningPlugin(config=config)
