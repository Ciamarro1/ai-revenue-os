import time
from src.revenue_os.plugins.research.models import ResearchOpportunity
from src.revenue_os.plugins.research.services import (
    ProviderRegistry,
    DeduplicationService,
    ResearchCacheService,
    OpportunityScoringService
)
from src.revenue_os.plugins.research.providers import HotmartProvider, AmazonProvider

def test_provider_registry():
    registry = ProviderRegistry()
    h_provider = HotmartProvider(enabled=True)
    a_provider = AmazonProvider(enabled=False)
    
    registry.register(h_provider)
    registry.register(a_provider)
    
    assert len(registry.list_all()) == 2
    assert len(registry.list_active()) == 1
    assert registry.get("hotmart") == h_provider
    
    registry.unregister("hotmart")
    assert len(registry.list_all()) == 1

def test_deduplication_service():
    dedup = DeduplicationService()
    
    opp1 = ResearchOpportunity(
        marketplace="Hotmart", product_name="Curso Python", category="tech", affiliate_url="https://example.com/p1"
    )
    opp2 = ResearchOpportunity(
        marketplace="Hotmart", product_name="Curso Python", category="tech", affiliate_url="https://example.com/p1"
    )
    opp3 = ResearchOpportunity(
        marketplace="Amazon", product_name="Livro Python", category="tech", affiliate_url="https://example.com/p2"
    )
    
    deduped, removed = dedup.deduplicate([opp1, opp2, opp3])
    assert len(deduped) == 2
    assert removed == 1

def test_cache_service():
    cache = ResearchCacheService(default_ttl_seconds=1)
    
    from src.revenue_os.plugins.research.models import OpportunitySearchResult
    mock_result = OpportunitySearchResult(niche="test", returned_count=1)
    
    cache.set("test", 5, mock_result)
    cached = cache.get("test", 5)
    assert cached is not None
    assert cached.from_cache is True
    
    # Aguardar TTL expirar
    time.sleep(1.1)
    assert cache.get("test", 5) is None

def test_scoring_service():
    scoring = OpportunityScoringService()
    
    opp_high = ResearchOpportunity(
        marketplace="M1", product_name="P1", category="c", epc_usd=10.0, commission_rate=0.80, confidence_score=0.90, competition_index=0.20, search_volume=15000, raw_score=100.0
    )
    opp_low = ResearchOpportunity(
        marketplace="M2", product_name="P2", category="c", epc_usd=1.0, commission_rate=0.10, confidence_score=0.50, competition_index=0.80, search_volume=500, raw_score=10.0
    )
    
    ranked = scoring.rank_opportunities([opp_low, opp_high])
    assert ranked[0].product_name == "P1"
    assert ranked[0].opportunity_score > ranked[1].opportunity_score
