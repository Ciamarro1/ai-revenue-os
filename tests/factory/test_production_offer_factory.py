from src.revenue_os.analytics.opportunity_schemas import RevenueOpportunity
from src.factory.production import ProductionOfferFactory, EnrichedOfferManifest

def test_production_offer_factory_generation():
    factory = ProductionOfferFactory()
    opp = RevenueOpportunity(
        id="OPP-101",
        marketplace="Hotmart",
        product_name="Formação Master AI 2026",
        category="technology",
        commission_rate=0.60,
        epc_usd=4.50,
        affiliate_url="https://checkout.hotmart.com/TEST"
    )
    
    manifest = factory.create_enriched_manifest(opp)
    
    assert isinstance(manifest, EnrichedOfferManifest)
    assert manifest.opportunity_id == "OPP-101"
    assert manifest.product_name == "Formação Master AI 2026"
    assert len(manifest.headline) > 0
    assert len(manifest.benefits) > 0
    assert len(manifest.pain_points) > 0
    assert len(manifest.cta_text) > 0
    assert "title" in manifest.seo_metadata
    assert len(manifest.keywords) > 0
    assert len(manifest.image_prompts) == 3
    assert "voiceover_script" in manifest.video_script
    assert "hero_section" in manifest.landing_metadata
    assert "pin_title" in manifest.pinterest_metadata
    assert "utm_params" in manifest.analytics_metadata
    assert len(manifest.inputs_hash) > 0
    assert len(manifest.signature_hash) > 0

def test_production_offer_factory_determinism():
    factory = ProductionOfferFactory()
    opp = RevenueOpportunity(
        id="OPP-101",
        marketplace="Kiwify",
        product_name="Método Produtividade",
        category="productivity",
        commission_rate=0.70,
        epc_usd=5.20
    )
    
    m1 = factory.create_enriched_manifest(opp)
    m2 = factory.create_enriched_manifest(opp)
    
    # Verificação de determinismo matemático absoluto
    assert m1.headline == m2.headline
    assert m1.value_proposition == m2.value_proposition
    assert m1.benefits == m2.benefits
    assert m1.pain_points == m2.pain_points
    assert m1.cta_text == m2.cta_text
    assert m1.image_prompts == m2.image_prompts
    assert m1.video_script == m2.video_script
    assert m1.inputs_hash == m2.inputs_hash
    assert m1.signature_hash == m2.signature_hash

def test_production_offer_factory_exports():
    factory = ProductionOfferFactory()
    opp = RevenueOpportunity(
        id="OPP-202",
        marketplace="Amazon",
        product_name="Smart Desk Gear",
        category="hardware"
    )
    
    manifest = factory.create_enriched_manifest(opp)
    
    astro_props = manifest.to_astro_props()
    assert "headline" in astro_props
    assert "cta" in astro_props
    assert "sections" in astro_props
    
    full_dict = manifest.to_full_production_dict()
    assert "astro_props" in full_dict
    assert "signature_hash" in full_dict
