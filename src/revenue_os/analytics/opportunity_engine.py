import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.revenue_os.analytics.opportunity_schemas import RevenueOpportunity
from src.revenue_os.connectors.base_adapter import BaseMarketplaceAdapter
from src.revenue_os.connectors.marketplace_adapters import (
    HotmartAdapter, ClickBankAdapter, AmazonAdapter, DigistoreAdapter, GumroadAdapter
)

class OpportunityEngine:
    """
    Opportunity Engine do AI Revenue OS (Sprint 9 + Sprint 9.5 Integration Layer).
    Pesquisa e ranqueia oportunidades de receita agregando adaptadores plugáveis de marketplace:
    Hotmart, ClickBank, Amazon, Digistore24, Gumroad.
    """

    def __init__(self, storage_dir: Optional[Path] = None, adapters: Optional[List[BaseMarketplaceAdapter]] = None):
        if storage_dir is None:
            self.storage_dir = Path(__file__).parent.parent.parent.parent / "knowledge" / "revenue_opportunities"
        else:
            self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        if adapters is None:
            self.adapters = [
                HotmartAdapter(),
                ClickBankAdapter(),
                AmazonAdapter(),
                DigistoreAdapter(),
                GumroadAdapter()
            ]
        else:
            self.adapters = adapters

    def discover_opportunities(self, category: str = "productivity") -> List[RevenueOpportunity]:
        """
        Coleta oportunidades através de todos os adaptadores registrados, normaliza e ordena por OpportunityScore.
        """
        all_opportunities = []
        for adapter in self.adapters:
            try:
                opps = adapter.get_normalized_opportunities(category)
                all_opportunities.extend(opps)
            except Exception:
                continue

        ranked = sorted(all_opportunities, key=lambda o: o.opportunity_score, reverse=True)
        self._save_opportunities(ranked)
        return ranked

    def _save_opportunities(self, opportunities: List[RevenueOpportunity]) -> None:
        for opp in opportunities:
            filename = f"{opp.id}_{opp.marketplace.lower()}.json"
            filepath = self.storage_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(opp.model_dump(), f, indent=2, ensure_ascii=False)

    def get_top_opportunity(self, category: Optional[str] = None) -> Optional[RevenueOpportunity]:
        opps = self.discover_opportunities(category=category or "productivity")
        return opps[0] if opps else None
