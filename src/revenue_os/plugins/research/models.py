from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from src.revenue_os.analytics.opportunity_schemas import RevenueOpportunity

class ResearchOpportunity(RevenueOpportunity):
    """
    Schema estendido de Oportunidade de Pesquisa (Sprint O1).
    Herda de RevenueOpportunity do Kernel garantindo 100% de compatibilidade,
    adicionando atributos de rastreabilidade, proveniência e classificação EDD.
    """
    provider_name: str = "unknown"
    raw_score: float = 0.0
    search_volume: int = 0
    source_url: str = ""
    tags: List[str] = Field(default_factory=list)
    extracted_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")
    dedup_hash: str = ""
    classification_status: str = "LOCAL_TEST"  # REAL_PRODUCTION, SIMULATED_BENCHMARK, LOCAL_TEST, WAITING_EXTERNAL_DEPENDENCY

class ProviderHealth(BaseModel):
    """
    Modelo de saúde operacional individual para adaptadores de pesquisa.
    """
    provider_name: str
    status: str = "HEALTHY"  # HEALTHY, DEGRADED, UNHEALTHY, DISABLED
    latency_ms: float = 0.0
    last_check: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")
    error_count: int = 0
    message: str = "Operational"

class OpportunitySearchResult(BaseModel):
    """
    Envelope de resultado retornado pela execução do ResearchPlugin.
    """
    niche: str
    total_found: int = 0
    returned_count: int = 0
    dedup_removed: int = 0
    from_cache: bool = False
    execution_time_ms: float = 0.0
    opportunities: List[ResearchOpportunity] = Field(default_factory=list)
    providers_used: List[str] = Field(default_factory=list)
    provider_healths: Dict[str, ProviderHealth] = Field(default_factory=dict)
