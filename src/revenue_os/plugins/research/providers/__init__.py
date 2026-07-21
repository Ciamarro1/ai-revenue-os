from src.revenue_os.plugins.research.providers.base_provider import OpportunityProvider
from src.revenue_os.plugins.research.providers.google_trends_provider import GoogleTrendsProvider
from src.revenue_os.plugins.research.providers.reddit_provider import RedditProvider
from src.revenue_os.plugins.research.providers.hackernews_provider import HackerNewsProvider
from src.revenue_os.plugins.research.providers.rss_provider import RSSProvider
from src.revenue_os.plugins.research.providers.hotmart_provider import HotmartProvider
from src.revenue_os.plugins.research.providers.amazon_provider import AmazonProvider
from src.revenue_os.plugins.research.providers.pinterest_trends_provider import PinterestTrendsProvider

__all__ = [
    "OpportunityProvider",
    "GoogleTrendsProvider",
    "RedditProvider",
    "HackerNewsProvider",
    "RSSProvider",
    "HotmartProvider",
    "AmazonProvider",
    "PinterestTrendsProvider",
]
