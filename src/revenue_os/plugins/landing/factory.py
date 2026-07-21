from typing import Optional
from src.revenue_os.plugins.landing.models import LandingDeploymentConfig
from src.revenue_os.plugins.landing.deployment_engine import LandingDeploymentEngine
from src.revenue_os.plugins.landing.astro_plugin import AstroLandingPlugin
from src.revenue_os.plugins.landing.nextjs_plugin import NextjsLandingPlugin

class LandingPluginFactory:
    """
    Factory Pattern para criação dos Plugins e Engine de Landing Pages.
    """

    @staticmethod
    def create_deployment_engine(config: Optional[LandingDeploymentConfig] = None) -> LandingDeploymentEngine:
        return LandingDeploymentEngine(config=config)

    @staticmethod
    def create_astro_plugin(config: Optional[LandingDeploymentConfig] = None) -> AstroLandingPlugin:
        engine = LandingPluginFactory.create_deployment_engine(config)
        return AstroLandingPlugin(deployment_engine=engine)

    @staticmethod
    def create_nextjs_plugin(config: Optional[LandingDeploymentConfig] = None) -> NextjsLandingPlugin:
        engine = LandingPluginFactory.create_deployment_engine(config)
        return NextjsLandingPlugin(deployment_engine=engine)
