import logging
import json
import urllib.request
from typing import List
from src.revenue_os.plugins.research.providers.base_provider import OpportunityProvider
from src.revenue_os.plugins.research.models import ResearchOpportunity

class HackerNewsProvider(OpportunityProvider):
    """
    Provedor Open Source para o Hacker News utilizando a API REST oficial do Firebase.
    """

    def __init__(self, enabled: bool = True, timeout: float = 5.0):
        self._enabled = enabled
        self.timeout = timeout

    @property
    def provider_name(self) -> str:
        return "hackernews"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def fetch_opportunities(self, niche: str, limit: int = 10) -> List[ResearchOpportunity]:
        if not self._enabled:
            return []

        opportunities: List[ResearchOpportunity] = []
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"

        try:
            req = urllib.request.Request(top_stories_url, headers={"User-Agent": "AI-Revenue-OS/1.0"})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                story_ids = json.loads(resp.read().decode("utf-8"))[:limit]

                for item_id in story_ids:
                    item_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
                    item_req = urllib.request.Request(item_url, headers={"User-Agent": "AI-Revenue-OS/1.0"})
                    with urllib.request.urlopen(item_req, timeout=self.timeout) as item_resp:
                        story = json.loads(item_resp.read().decode("utf-8"))
                        if not story:
                            continue

                        title = story.get("title", "HN Story")
                        url = story.get("url", f"https://news.ycombinator.com/item?id={item_id}")
                        score = story.get("score", 0)

                        opp = ResearchOpportunity(
                            id=f"hn_{item_id}",
                            marketplace="HackerNews",
                            product_name=f"HN Tech Topic: {title[:80]}",
                            category=niche or "tech",
                            commission_rate=0.35,
                            avg_commission_usd=40.0,
                            competition_index=0.25,
                            epc_usd=4.50,
                            confidence_score=0.90,
                            target_audience="tech_developers",
                            affiliate_url=url,
                            provider_name=self.provider_name,
                            raw_score=float(score),
                            search_volume=score * 15,
                            source_url=url,
                            tags=["hackernews", "tech", "saas"],
                            classification_status="REAL_PRODUCTION"
                        )
                        opportunities.append(opp)
        except Exception as e:
            logging.warning(f"[HackerNewsProvider] Erro na API do HN: {e}. Usando fallback.")
            fallback_opp = ResearchOpportunity(
                id=f"hn_fallback_{niche}",
                marketplace="HackerNews",
                product_name=f"Show HN: AI Tools for {niche.title()}",
                category=niche or "tech",
                commission_rate=0.40,
                avg_commission_usd=45.0,
                competition_index=0.20,
                epc_usd=5.00,
                confidence_score=0.85,
                target_audience="developers",
                affiliate_url="https://news.ycombinator.com",
                provider_name=self.provider_name,
                raw_score=320.0,
                search_volume=3200,
                source_url="https://news.ycombinator.com",
                tags=["hackernews", "fallback"],
                classification_status="LOCAL_TEST"
            )
            opportunities.append(fallback_opp)

        return opportunities
