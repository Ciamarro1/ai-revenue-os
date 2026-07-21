from pydantic import BaseModel, Field

class ResearchPluginConfig(BaseModel):
    """
    Configuração do ResearchPlugin com Pydantic v2.
    Permite controle refinado de Feature Flags, Cache, Timeouts e limites.
    """
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    dedup_enabled: bool = True
    max_results_per_provider: int = 10
    request_timeout_seconds: float = 5.0
    min_score_threshold: float = 0.50

    # Feature Flags por Provedor
    enable_google_trends: bool = True
    enable_reddit: bool = True
    enable_hackernews: bool = True
    enable_rss: bool = True
    enable_hotmart: bool = True
    enable_amazon: bool = True
    enable_pinterest: bool = True

    # Feeds genéricos configuráveis para RSS
    rss_custom_feeds: list[str] = Field(default_factory=lambda: [
        "https://news.ycombinator.com/rss",
        "https://feeds.feedburner.com/TechCrunch/"
    ])
