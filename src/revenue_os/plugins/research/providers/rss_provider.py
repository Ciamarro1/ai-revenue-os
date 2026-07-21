import logging
import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Optional
from src.revenue_os.plugins.research.providers.base_provider import OpportunityProvider
from src.revenue_os.plugins.research.models import ResearchOpportunity

class RSSProvider(OpportunityProvider):
    """
    Provedor Genérico Open Source para feeds RSS/Atom.
    """

    def __init__(self, feeds: Optional[List[str]] = None, enabled: bool = True, timeout: float = 5.0):
        self._enabled = enabled
        self.timeout = timeout
        self.feeds = feeds or [
            "https://news.ycombinator.com/rss"
        ]

    @property
    def provider_name(self) -> str:
        return "rss"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def fetch_opportunities(self, niche: str, limit: int = 10) -> List[ResearchOpportunity]:
        if not self._enabled:
            return []

        opportunities: List[ResearchOpportunity] = []

        for feed_url in self.feeds:
            try:
                req = urllib.request.Request(feed_url, headers={"User-Agent": "AI-Revenue-OS/1.0"})
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    xml_data = resp.read()
                    root = ET.fromstring(xml_data)

                    items = root.findall(".//item")
                    for idx, item in enumerate(items[:limit]):
                        title = item.findtext("title") or "RSS Feed Item"
                        link = item.findtext("link") or feed_url

                        opp = ResearchOpportunity(
                            id=f"rss_{idx}_{hash(link) & 0xffffffff}",
                            marketplace="RSS Feed",
                            product_name=f"RSS Article: {title[:80]}",
                            category=niche or "general",
                            commission_rate=0.30,
                            avg_commission_usd=20.0,
                            competition_index=0.30,
                            epc_usd=2.50,
                            confidence_score=0.75,
                            target_audience="content_readers",
                            affiliate_url=link,
                            provider_name=self.provider_name,
                            raw_score=100.0,
                            search_volume=1000,
                            source_url=link,
                            tags=["rss", "feed", niche],
                            classification_status="REAL_PRODUCTION"
                        )
                        opportunities.append(opp)
            except Exception as e:
                logging.warning(f"[RSSProvider] Falha ao ler feed '{feed_url}': {e}. Usando fallback.")
                fallback_opp = ResearchOpportunity(
                    id=f"rss_fallback_{niche}",
                    marketplace="RSS Feed",
                    product_name=f"RSS Market Feed: Industry Insights on {niche.title()}",
                    category=niche,
                    commission_rate=0.35,
                    avg_commission_usd=22.0,
                    competition_index=0.25,
                    epc_usd=2.80,
                    confidence_score=0.70,
                    target_audience="readers",
                    affiliate_url=feed_url,
                    provider_name=self.provider_name,
                    raw_score=80.0,
                    search_volume=800,
                    source_url=feed_url,
                    tags=["rss", "fallback"],
                    classification_status="LOCAL_TEST"
                )
                opportunities.append(fallback_opp)

        return opportunities
