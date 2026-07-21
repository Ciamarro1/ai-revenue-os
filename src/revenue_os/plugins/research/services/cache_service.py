import time
from typing import Dict, Any, Optional
from src.revenue_os.plugins.research.models import OpportunitySearchResult

class ResearchCacheService:
    """
    Serviço de Cache em Memória com TTL (Time To Live).
    """

    def __init__(self, default_ttl_seconds: int = 3600):
        self.default_ttl = default_ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _generate_key(self, niche: str, limit: int) -> str:
        return f"{niche.lower().strip()}:{limit}"

    def get(self, niche: str, limit: int) -> Optional[OpportunitySearchResult]:
        key = self._generate_key(niche, limit)
        item = self._cache.get(key)

        if not item:
            return None

        if time.time() > item["expires_at"]:
            del self._cache[key]
            return None

        res: OpportunitySearchResult = item["data"]
        res.from_cache = True
        return res

    def set(self, niche: str, limit: int, result: OpportunitySearchResult, ttl_seconds: Optional[int] = None) -> None:
        key = self._generate_key(niche, limit)
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self._cache[key] = {
            "data": result,
            "expires_at": time.time() + ttl
        }

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)
