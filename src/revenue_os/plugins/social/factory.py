from typing import Optional
from src.revenue_os.plugins.social.models import PinterestConfig
from src.revenue_os.plugins.social.pinterest_plugin import PinterestPlugin

class SocialPluginFactory:
    """
    Factory Pattern para criação unificada de plugins de mídias sociais.
    """

    @staticmethod
    def create_pinterest_plugin(config: Optional[PinterestConfig] = None) -> PinterestPlugin:
        config = config or PinterestConfig()
        return PinterestPlugin(config=config)
