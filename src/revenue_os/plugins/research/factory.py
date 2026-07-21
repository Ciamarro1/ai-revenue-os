from src.revenue_os.plugins.research.config import ResearchPluginConfig
from src.revenue_os.plugins.research.services.provider_registry import ProviderRegistry
from src.revenue_os.plugins.research.services.cache_service import ResearchCacheService
from src.revenue_os.plugins.research.services.dedup_service import DeduplicationService
from src.revenue_os.plugins.research.services.scoring_service import OpportunityScoringService
from src.revenue_os.plugins.research.providers import (
    GoogleTrendsProvider,
    RedditProvider,
    HackerNewsProvider,
    RSSProvider,
    HotmartProvider,
    AmazonProvider,
    PinterestTrendsProvider
)

class ResearchPluginFactory:
    """
    Factory Pattern para criação e configuração completa do ResearchPlugin.
    """

    @staticmethod
    def create_plugin(config: ResearchPluginConfig = None):
        from src.revenue_os.plugins.research.research_plugin import ResearchPlugin

        config = config or ResearchPluginConfig()
        registry = ProviderRegistry()

        # Registro dos 7 Provedores conforme Feature Flags
        if config.enable_google_trends:
            registry.register(GoogleTrendsProvider(enabled=True, timeout=config.request_timeout_seconds))
        if config.enable_reddit:
            registry.register(RedditProvider(enabled=True, timeout=config.request_timeout_seconds))
        if config.enable_hackernews:
            registry.register(HackerNewsProvider(enabled=True, timeout=config.request_timeout_seconds))
        if config.enable_rss:
            registry.register(RSSProvider(feeds=config.rss_custom_feeds, enabled=True, timeout=config.request_timeout_seconds))
        if config.enable_hotmart:
            registry.register(HotmartProvider(enabled=True))
        if config.enable_amazon:
            registry.register(AmazonProvider(enabled=True))
        if config.enable_pinterest:
            registry.register(PinterestTrendsProvider(enabled=True))

        cache_service = ResearchCacheService(default_ttl_seconds=config.cache_ttl_seconds)
        dedup_service = DeduplicationService()
        scoring_service = OpportunityScoringService()

        return ResearchPlugin(
            config=config,
            provider_registry=registry,
            cache_service=cache_service,
            dedup_service=dedup_service,
            scoring_service=scoring_service
        )
