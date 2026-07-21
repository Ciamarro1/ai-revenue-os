import hashlib
import json
from typing import Optional, Dict, Any
from src.revenue_os.analytics.opportunity_schemas import RevenueOpportunity
from src.revenue_os.analytics.genome_library import Genome
from src.factory.production.extended_manifest import EnrichedOfferManifest
from src.factory.production.generators import DeterministicOfferGenerators

class ProductionOfferFactory:
    """
    Production Offer Factory (Sprint O3).
    Gera manifestos de oferta 100% determinísticos, reproduzíveis e selados criptograficamente.
    """

    def create_enriched_manifest(
        self,
        opportunity: RevenueOpportunity,
        genome: Optional[Genome] = None
    ) -> EnrichedOfferManifest:
        """
        Deriva o EnrichedOfferManifest completo combinando os 11 geradores determinísticos.
        """
        identifier = f"{opportunity.id or 'OPP'}_{opportunity.product_name.lower().strip()}"
        niche = opportunity.category or "general"
        product_name = opportunity.product_name

        # 1. Headlines & Subheadlines
        headline, val_prop = DeterministicOfferGenerators.generate_headlines(niche, product_name, identifier)

        # 2. Benefícios
        benefits = DeterministicOfferGenerators.generate_benefits(niche, product_name, identifier)

        # 3. Dores (Pain Points)
        pain_points = DeterministicOfferGenerators.generate_pain_points(niche, identifier)

        # 4. CTA
        cta_text, urgency_text = DeterministicOfferGenerators.generate_cta(identifier)

        # 5. SEO Metadata
        seo_meta = DeterministicOfferGenerators.generate_seo_metadata(niche, product_name, identifier)

        # 6. Keywords
        keywords = DeterministicOfferGenerators.generate_keywords(niche, product_name, identifier)

        # 7. Image Prompts
        image_prompts = DeterministicOfferGenerators.generate_image_prompts(niche, product_name, identifier)

        # 8. Video Prompts
        video_script = DeterministicOfferGenerators.generate_video_prompts(niche, product_name, identifier)

        # 9. Landing Metadata
        landing_meta = DeterministicOfferGenerators.generate_landing_metadata(
            niche, product_name, headline, val_prop, benefits, pain_points, identifier
        )

        # 10. Pinterest Metadata
        pinterest_meta = DeterministicOfferGenerators.generate_pinterest_metadata(niche, product_name, identifier)

        # 11. Analytics Metadata
        analytics_meta = DeterministicOfferGenerators.generate_analytics_metadata(
            opportunity.id or "OPP-0", opportunity.marketplace, niche, identifier
        )

        # Seções para compatibilidade com renderizadores Astro / Next.js
        sections = [
            {"type": "hero", "headline": headline, "subheadline": val_prop, "cta_urgency": urgency_text},
            {"type": "pain_points", "title": "Você Enfrenta Estes Problemas?", "items": pain_points},
            {"type": "benefits", "title": "O Que Você Irá Conquistar", "items": benefits},
            {"type": "pricing", "title": "Condição Especial de Lançamento", "items": landing_meta["pricing_section"]}
        ]

        faqs = [
            {"q": "Como funciona o acesso?", "a": "O acesso é imediato e enviado para o seu e-mail logo após a confirmação da inscrição."},
            {"q": "Qual é a garantia?", "a": "Oferecemos garantia incondicional de 7 dias com reembolso total caso você não fique satisfeito."}
        ]

        schema_org = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": product_name,
            "description": seo_meta["description"],
            "offers": {
                "@type": "Offer",
                "price": "97.00",
                "priceCurrency": "BRL",
                "availability": "https://schema.org/InStock"
            }
        }

        # Cálculo de Hash Determinístico de Inputs e Assinatura Criptográfica
        raw_input_payload = f"{identifier}|{niche}|{opportunity.epc_usd}|{opportunity.commission_rate}"
        inputs_hash = hashlib.sha256(raw_input_payload.encode("utf-8")).hexdigest()
        
        signature_payload = f"{inputs_hash}|{headline}|{cta_text}|{len(benefits)}"
        signature_hash = hashlib.sha256(signature_payload.encode("utf-8")).hexdigest()

        return EnrichedOfferManifest(
            id=f"OFFER-{identifier}",
            opportunity_id=opportunity.id or "OPP-DEFAULT",
            product_name=product_name,
            title=f"{product_name} — Oferta Exclusiva",
            headline=headline,
            value_proposition=val_prop,
            sections=sections,
            cta_text=cta_text,
            cta_url=opportunity.affiliate_url or "https://example.com/checkout",
            faqs=faqs,
            seo_metadata=seo_meta,
            schema_org_json=schema_org,
            pain_points=pain_points,
            benefits=benefits,
            keywords=keywords,
            image_prompts=image_prompts,
            video_script=video_script,
            pinterest_metadata=pinterest_meta,
            analytics_metadata=analytics_meta,
            landing_metadata=landing_meta,
            inputs_hash=inputs_hash,
            signature_hash=signature_hash
        )
