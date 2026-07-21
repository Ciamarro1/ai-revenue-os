import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class OfferManifest(BaseModel):
    """
    Artefato Intermediário da Offer Factory (Sprint 10 + Princípio Open Source First).
    O AI Revenue OS gera este manifesto estruturado com toda a inteligência da oferta.
    Os adaptadores Open Source (Astro, Next.js, Hugo) transformam este manifesto em projetos finais sem reconstruir CMS/builders.
    """
    id: str
    opportunity_id: str
    product_name: str
    title: str
    headline: str
    value_proposition: str
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    cta_text: str = "Garantir Oferta com 60% de Desconto"
    cta_url: str = "https://checkout.example.com"
    faqs: List[Dict[str, str]] = Field(default_factory=list)
    seo_metadata: Dict[str, str] = Field(default_factory=dict)
    schema_org_json: Dict[str, Any] = Field(default_factory=dict)

    def to_astro_props(self) -> Dict[str, Any]:
        """
        Converte o manifesto intermediário em propriedades limpas para o Astro SSG Adapter.
        """
        return {
            "title": self.title,
            "headline": self.headline,
            "valueProposition": self.value_proposition,
            "cta": {"text": self.cta_text, "url": self.cta_url},
            "sections": self.sections,
            "faqs": self.faqs,
            "seo": self.seo_metadata,
            "schemaOrg": self.schema_org_json
        }
