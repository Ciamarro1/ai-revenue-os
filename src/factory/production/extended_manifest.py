from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import Field
from src.revenue_os.domain.offer_manifest import OfferManifest

class EnrichedOfferManifest(OfferManifest):
    """
    EnrichedOfferManifest (Sprint O3).
    Estende o OfferManifest do Kernel sem violar o lock, adicionando
    todas as 11 novas seções de metadados geradas deterministicamente.
    """
    pain_points: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    image_prompts: List[Dict[str, str]] = Field(default_factory=list)
    video_script: Dict[str, Any] = Field(default_factory=dict)
    pinterest_metadata: Dict[str, Any] = Field(default_factory=dict)
    analytics_metadata: Dict[str, Any] = Field(default_factory=dict)
    landing_metadata: Dict[str, Any] = Field(default_factory=dict)
    inputs_hash: str = ""
    signature_hash: str = ""
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")

    def to_full_production_dict(self) -> Dict[str, Any]:
        """
        Exporta o manifesto completo selado para produção.
        """
        d = self.model_dump()
        d["astro_props"] = self.to_astro_props()
        return d
