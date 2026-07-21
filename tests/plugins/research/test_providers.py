from src.revenue_os.plugins.research.providers import (
    GoogleTrendsProvider,
    RedditProvider,
    HackerNewsProvider,
    RSSProvider,
    HotmartProvider,
    AmazonProvider,
    PinterestTrendsProvider
)

def test_google_trends_provider():
    provider = GoogleTrendsProvider(enabled=True, timeout=2.0)
    assert provider.provider_name == "google_trends"
    assert provider.is_enabled is True
    
    opps = provider.fetch_opportunities(niche="tech", limit=2)
    assert len(opps) > 0
    assert opps[0].marketplace == "Google Trends"
    assert opps[0].classification_status in ["REAL_PRODUCTION", "LOCAL_TEST"]

def test_reddit_provider():
    provider = RedditProvider(enabled=True, timeout=2.0)
    assert provider.provider_name == "reddit"
    
    opps = provider.fetch_opportunities(niche="python", limit=2)
    assert len(opps) > 0
    assert opps[0].marketplace == "Reddit"

def test_hackernews_provider():
    provider = HackerNewsProvider(enabled=True, timeout=2.0)
    assert provider.provider_name == "hackernews"
    
    opps = provider.fetch_opportunities(niche="saas", limit=2)
    assert len(opps) > 0
    assert opps[0].marketplace == "HackerNews"

def test_rss_provider():
    provider = RSSProvider(enabled=True, timeout=2.0)
    assert provider.provider_name == "rss"
    
    opps = provider.fetch_opportunities(niche="tech", limit=2)
    assert len(opps) > 0

def test_hotmart_provider():
    provider = HotmartProvider(enabled=True)
    assert provider.provider_name == "hotmart"
    
    opps = provider.fetch_opportunities(niche="marketing", limit=2)
    assert len(opps) == 2
    assert opps[0].marketplace == "Hotmart"
    assert opps[0].classification_status == "LOCAL_TEST"

def test_amazon_provider():
    provider = AmazonProvider(enabled=True)
    assert provider.provider_name == "amazon"
    
    opps = provider.fetch_opportunities(niche="fitness", limit=2)
    assert len(opps) == 2
    assert opps[0].marketplace == "Amazon"
    assert opps[0].classification_status == "LOCAL_TEST"

def test_pinterest_trends_provider():
    provider = PinterestTrendsProvider(enabled=True)
    assert provider.provider_name == "pinterest_trends"
    
    opps = provider.fetch_opportunities(niche="decor", limit=2)
    assert len(opps) == 2
    assert opps[0].marketplace == "Pinterest Trends"
    assert opps[0].classification_status == "LOCAL_TEST"
