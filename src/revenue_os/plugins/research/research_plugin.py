import time
import logging
from typing import Dict, Any, List, Optional
from src.revenue_os.plugins.base_plugin import BasePlugin
from src.revenue_os.plugins.research.config import ResearchPluginConfig
from src.revenue_os.plugins.research.models import OpportunitySearchResult, ResearchOpportunity, ProviderHealth
from src.revenue_os.plugins.research.services.provider_registry import ProviderRegistry
from src.revenue_os.plugins.research.services.cache_service import ResearchCacheService
from src.revenue_os.plugins.research.services.dedup_service import DeduplicationService
from src.revenue_os.plugins.research.services.scoring_service import OpportunityScoringService

class ResearchPlugin(BasePlugin):
    """
    ResearchPlugin (Sprint O1).
    Plugin oficial para descoberta de oportunidades de receita de mercado
    utilizando múltiplos adaptadores Open Source desacoplados.
    """

    def __init__(
        self,
        config: Optional[ResearchPluginConfig] = None,
        provider_registry: Optional[ProviderRegistry] = None,
        cache_service: Optional[ResearchCacheService] = None,
        dedup_service: Optional[DeduplicationService] = None,
        scoring_service: Optional[OpportunityScoringService] = None
    ):
        self.config = config or ResearchPluginConfig()
        self.registry = provider_registry or ProviderRegistry()
        self.cache = cache_service or ResearchCacheService(default_ttl_seconds=self.config.cache_ttl_seconds)
        self.dedup = dedup_service or DeduplicationService()
        self.scoring = scoring_service or OpportunityScoringService()
        self._initialized = False

    @property
    def plugin_name(self) -> str:
        return "research_plugin"

    @property
    def category(self) -> str:
        return "research"

    def initialize(self) -> bool:
        """
        Inicializa o plugin e seus provedores associados.
        """
        self._initialized = True
        logging.info(f"[{self.plugin_name}] Inicializado com {len(self.registry.list_active())} provedores ativos.")
        return True

    def health_check(self) -> Dict[str, Any]:
        """
        Retorna o status de saúde consolidado do ResearchPlugin e de seus adaptadores.
        """
        active_providers = self.registry.list_active()
        provider_healths = {p.provider_name: p.health_check().model_dump() for p in active_providers}

        is_healthy = self._initialized and len(active_providers) > 0

        return {
            "status": "HEALTHY" if is_healthy else "UNHEALTHY",
            "plugin_name": self.plugin_name,
            "category": self.category,
            "active_providers_count": len(active_providers),
            "provider_healths": provider_healths
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa a busca de oportunidades de pesquisa.
        
        Payload esperado:
          - niche (str): Nicho de mercado a ser pesquisado (ex: "python", "ai", "finance")
          - limit (int): Limite máximo de oportunidades por provedor (opcional, padrão 10)
          - force_refresh (bool): Ignorar cache (opcional, padrão False)
        """
        start_time = time.time()
        niche = payload.get("niche", "general")
        limit = payload.get("limit", self.config.max_results_per_provider)
        force_refresh = payload.get("force_refresh", False)

        # 1. Checar Cache
        if self.config.cache_enabled and not force_refresh:
            cached_result = self.cache.get(niche, limit)
            if cached_result:
                res_dict = cached_result.model_dump()
                res_dict["status"] = "SUCCESS"
                return res_dict

        # 2. Coletar Oportunidades dos Provedores Ativos
        raw_opportunities: List[ResearchOpportunity] = []
        providers_used: List[str] = []
        provider_healths: Dict[str, ProviderHealth] = {}

        for provider in self.registry.list_active():
            try:
                opps = provider.fetch_opportunities(niche=niche, limit=limit)
                raw_opportunities.extend(opps)
                providers_used.append(provider.provider_name)
                provider_healths[provider.provider_name] = provider.health_check()
            except Exception as e:
                logging.error(f"[{self.plugin_name}] Falha no provedor '{provider.provider_name}': {e}")
                provider_healths[provider.provider_name] = ProviderHealth(
                    provider_name=provider.provider_name,
                    status="UNHEALTHY",
                    error_count=1,
                    message=str(e)
                )

        total_found = len(raw_opportunities)

        # 3. Deduplicação
        dedup_removed = 0
        if self.config.dedup_enabled:
            raw_opportunities, dedup_removed = self.dedup.deduplicate(raw_opportunities)

        # 4. Pontuação e Ranking
        ranked_opportunities = self.scoring.rank_opportunities(
            raw_opportunities,
            min_threshold=self.config.min_score_threshold
        )

        exec_time_ms = round((time.time() - start_time) * 1000, 2)

        result_envelope = OpportunitySearchResult(
            niche=niche,
            total_found=total_found,
            returned_count=len(ranked_opportunities),
            dedup_removed=dedup_removed,
            from_cache=False,
            execution_time_ms=exec_time_ms,
            opportunities=ranked_opportunities,
            providers_used=providers_used,
            provider_healths=provider_healths
        )

        # 5. Guardar em Cache
        if self.config.cache_enabled:
            self.cache.set(niche, limit, result_envelope)

        response = result_envelope.model_dump()
        response["status"] = "SUCCESS"
        return response

    def shutdown(self) -> None:
        """
        Encerra recursos de memória e cache do plugin.
        """
        self.cache.clear()
        self._initialized = False
        logging.info(f"[{self.plugin_name}] Encerrado com sucesso.")
