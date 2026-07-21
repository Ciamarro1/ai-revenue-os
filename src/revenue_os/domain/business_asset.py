import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from src.revenue_os.analytics.opportunity_schemas import RevenueOpportunity
from src.revenue_os.analytics.genome_library import Genome

class BusinessAsset(BaseModel):
    """
    Entidade Principal do Domínio do AI Revenue OS.
    Representa o Ativo de Negócio unificado contendo toda a cadeia de produção e performance:
    Opportunity ➔ Genome ➔ Landing ➔ Pin ➔ Video ➔ Blog ➔ Email ➔ Analytics ➔ Revenue ➔ Knowledge.
    """
    id: str
    opportunity: RevenueOpportunity
    genome: Optional[Genome] = None
    landing_page_url: Optional[str] = None
    pins: List[Dict[str, Any]] = Field(default_factory=list)
    videos: List[Dict[str, Any]] = Field(default_factory=list)
    blog_posts: List[Dict[str, Any]] = Field(default_factory=list)
    emails: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Métricas consolidadas de performance financeira e de distribuição
    total_impressions: int = 0
    total_clicks: int = 0
    total_conversions: int = 0
    total_revenue: float = 0.0
    total_cost: float = 0.0
    status: str = "Active"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")

    @property
    def net_profit(self) -> float:
        return round(self.total_revenue - self.total_cost, 2)

    @property
    def roi_ratio(self) -> float:
        return round(self.total_revenue / max(1.0, self.total_cost), 2)

    @property
    def ctr(self) -> float:
        return round(self.total_clicks / max(1, self.total_impressions), 4)

    def to_summary(self) -> Dict[str, Any]:
        return {
            "asset_id": self.id,
            "product_name": self.opportunity.product_name,
            "marketplace": self.opportunity.marketplace,
            "landing_page_url": self.landing_page_url,
            "total_pins": len(self.pins),
            "total_videos": len(self.videos),
            "net_profit_usd": self.net_profit,
            "roi_ratio": f"{self.roi_ratio}x",
            "status": self.status
        }
