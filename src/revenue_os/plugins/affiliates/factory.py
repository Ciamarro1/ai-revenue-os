from typing import List
from src.revenue_os.plugins.base_plugin import BasePlugin
from src.revenue_os.plugins.affiliates.config import AffiliatePluginConfig
from src.revenue_os.plugins.affiliates.hotmart_plugin import HotmartAffiliatePlugin
from src.revenue_os.plugins.affiliates.kiwify_plugin import KiwifyAffiliatePlugin
from src.revenue_os.plugins.affiliates.eduzz_plugin import EduzzAffiliatePlugin
from src.revenue_os.plugins.affiliates.amazon_plugin import AmazonAffiliatePlugin
from src.revenue_os.plugins.affiliates.providers import (
    HotmartProvider,
    KiwifyProvider,
    EduzzProvider,
    AmazonProvider
)

class AffiliatePluginFactory:
    """
    Factory Pattern para criação dos Plugins de Afiliados.
    """

    @staticmethod
    def create_hotmart_plugin(config: AffiliatePluginConfig = None) -> HotmartAffiliatePlugin:
        config = config or AffiliatePluginConfig()
        provider = HotmartProvider(enabled=config.enable_hotmart)
        return HotmartAffiliatePlugin(provider=provider)

    @staticmethod
    def create_kiwify_plugin(config: AffiliatePluginConfig = None) -> KiwifyAffiliatePlugin:
        config = config or AffiliatePluginConfig()
        provider = KiwifyProvider(enabled=config.enable_kiwify)
        return KiwifyAffiliatePlugin(provider=provider)

    @staticmethod
    def create_eduzz_plugin(config: AffiliatePluginConfig = None) -> EduzzAffiliatePlugin:
        config = config or AffiliatePluginConfig()
        provider = EduzzProvider(enabled=config.enable_eduzz)
        return EduzzAffiliatePlugin(provider=provider)

    @staticmethod
    def create_amazon_plugin(config: AffiliatePluginConfig = None) -> AmazonAffiliatePlugin:
        config = config or AffiliatePluginConfig()
        provider = AmazonProvider(enabled=config.enable_amazon)
        return AmazonAffiliatePlugin(provider=provider)

    @staticmethod
    def create_all_plugins(config: AffiliatePluginConfig = None) -> List[BasePlugin]:
        config = config or AffiliatePluginConfig()
        plugins = []
        if config.enable_hotmart:
            plugins.append(AffiliatePluginFactory.create_hotmart_plugin(config))
        if config.enable_kiwify:
            plugins.append(AffiliatePluginFactory.create_kiwify_plugin(config))
        if config.enable_eduzz:
            plugins.append(AffiliatePluginFactory.create_eduzz_plugin(config))
        if config.enable_amazon:
            plugins.append(AffiliatePluginFactory.create_amazon_plugin(config))
        return plugins
