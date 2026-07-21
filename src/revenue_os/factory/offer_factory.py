from typing import Optional, Dict, Any
from src.revenue_os.analytics.opportunity_schemas import RevenueOpportunity
from src.revenue_os.analytics.genome_library import Genome
from src.revenue_os.domain.offer_manifest import OfferManifest

class OfferFactory:
    """
    Lean Offer Factory (Sprint 10).
    Foco estrito e enxuto: Consome uma RevenueOpportunity e um Genome
    e devolve o manifesto estruturado OfferManifest sem acoplamento a renderizadores visuais.
    """

    def create_offer_manifest(self, opportunity: RevenueOpportunity, genome: Optional[Genome] = None) -> OfferManifest:
        """
        Deriva o manifesto estruturado com base na oportunidade de receita e nos atributos do genoma.
        """
        hook_style = genome.hook if genome else "Gancho de Alto Impacto"
        product_name = opportunity.product_name

        headline = f"{hook_style}: {product_name}"
        val_prop = f"Solução completa no nicho {opportunity.category} com {opportunity.commission_rate*100:.0f}% de desconto exclusivo."

        sections = [
            {"type": "hero", "headline": headline, "subheadline": val_prop},
            {"type": "features", "title": "O que você aprenderá", "items": ["Método passo a passo", "Modelos prontos", "Acesso vitalício"]},
            {"type": "faq", "title": "Perguntas Frequentes", "items": [{"q": "Como recebo o acesso?", "a": "Imediatamente no seu e-mail pós-confirmação."}]}
        ]

        faqs = [{"q": "Há garantia?", "a": "Sim, garantia incondicional de 7 dias."}]

        seo = {
            "title": f"{product_name} — Oferta Oficial",
            "description": f"Adquira o {product_name} com suporte e bônus exclusivos.",
            "keywords": f"{opportunity.category}, {product_name}, curso, guia"
        }

        return OfferManifest(
            id=f"MANIFEST-{opportunity.id}",
            opportunity_id=opportunity.id or "OPP-DEFAULT",
            product_name=product_name,
            title=product_name,
            headline=headline,
            value_proposition=val_prop,
            sections=sections,
            cta_text="Garantir Oferta Agora",
            cta_url=opportunity.affiliate_url,
            faqs=faqs,
            seo_metadata=seo,
            schema_org_json={"@context": "https://schema.org", "@type": "Product", "name": product_name}
        )
