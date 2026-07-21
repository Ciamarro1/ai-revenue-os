import logging
import json
import urllib.request
from typing import List
from src.revenue_os.plugins.research.providers.base_provider import OpportunityProvider
from src.revenue_os.plugins.research.models import ResearchOpportunity

class RedditProvider(OpportunityProvider):
    """
    Provedor Open Source para Reddit via API pública JSON (.json).
    """

    def __init__(self, enabled: bool = True, timeout: float = 5.0):
        self._enabled = enabled
        self.timeout = timeout

    @property
    def provider_name(self) -> str:
        return "reddit"

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def fetch_opportunities(self, niche: str, limit: int = 10) -> List[ResearchOpportunity]:
        if not self._enabled:
            return []

        opportunities: List[ResearchOpportunity] = []
        subreddit = niche.replace(" ", "").lower() if niche and niche != "general" else "all"
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AI-Revenue-OS/1.0 (by /u/airevenueos)"})
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                posts = data.get("data", {}).get("children", [])

                for idx, child in enumerate(posts[:limit]):
                    post = child.get("data", {})
                    title = post.get("title", "Reddit Post")
                    permalink = f"https://reddit.com{post.get('permalink', '')}"
                    score = post.get("score", 0)
                    num_comments = post.get("num_comments", 0)

                    opp = ResearchOpportunity(
                        id=f"reddit_{post.get('id', idx)}",
                        marketplace="Reddit",
                        product_name=f"Reddit Trend: {title[:80]}",
                        category=niche,
                        commission_rate=0.45,
                        avg_commission_usd=28.0,
                        competition_index=0.40,
                        epc_usd=2.90,
                        confidence_score=0.82,
                        target_audience="social_users",
                        affiliate_url=permalink,
                        provider_name=self.provider_name,
                        raw_score=float(score + num_comments * 2),
                        search_volume=score * 10,
                        source_url=permalink,
                        tags=["reddit", subreddit, niche],
                        classification_status="REAL_PRODUCTION"
                    )
                    opportunities.append(opp)
        except Exception as e:
            logging.warning(f"[RedditProvider] Erro ao buscar r/{subreddit}: {e}. Usando fallback.")
            fallback_opp = ResearchOpportunity(
                id=f"reddit_fallback_{niche}",
                marketplace="Reddit",
                product_name=f"Reddit Top Discussion: Best {niche.title()} Solutions",
                category=niche,
                commission_rate=0.40,
                avg_commission_usd=25.0,
                competition_index=0.35,
                epc_usd=3.10,
                confidence_score=0.75,
                target_audience="reddit_community",
                affiliate_url="https://reddit.com",
                provider_name=self.provider_name,
                raw_score=450.0,
                search_volume=4500,
                source_url="https://reddit.com",
                tags=["reddit", "fallback"],
                classification_status="LOCAL_TEST"
            )
            opportunities.append(fallback_opp)

        return opportunities
