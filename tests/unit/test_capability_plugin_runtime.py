import pytest
from src.reality.oss_catalog.catalog import OSSEntry
from src.reality.oss_catalog.governance import OSSEvaluationScorecard
from src.revenue_os.connectors.capability_registry import CapabilityRegistry, CapabilityConfig
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.landing.astro_plugin import AstroLandingPlugin
from src.revenue_os.domain.offer_manifest import OfferManifest

def test_oss_evaluation_scorecard():
    scorecard = OSSEvaluationScorecard()
    entry = OSSEntry(
        name="Astro / Next.js",
        category="landing",
        license="MIT",
        maturity="High",
        language="TypeScript",
        integration_ease="Seamless",
        use_case="Geração de SSG landing pages",
        official_url="https://astro.build",
        stars=45000,
        last_commit_days_ago=2,
        maintenance_score=0.95
    )

    res = scorecard.evaluate_entry(entry)
    assert res.overall_score >= 80.0
    assert res.recommendation == "RECOMMENDED_PRIMARY"

def test_capability_registry():
    registry = CapabilityRegistry()
    
    primary = registry.get_provider("landing_generation")
    fallbacks = registry.get_fallbacks("landing_generation")

    assert primary == "astro"
    assert "nextjs" in fallbacks

def test_plugin_runtime_and_execution():
    registry = CapabilityRegistry()
    runtime = PluginRuntime(capability_registry=registry)

    astro_plugin = AstroLandingPlugin()
    registered = runtime.register_plugin(astro_plugin)
    assert registered is True

    res = runtime.execute_capability("landing_generation", {"title": "Notion Template Pro", "headline": "Organize sua vida"})
    assert res["status"] == "SUCCESS"
    assert res["executed_by_provider"] == "astro"
    assert "built_with" in res

def test_offer_manifest_intermediate_artifact():
    manifest = OfferManifest(
        id="MANIFEST-001",
        opportunity_id="OPP-101",
        product_name="Productivity System",
        title="Formação Master em Produtividade",
        headline="Duplique sua eficiência em 30 dias",
        value_proposition="Sistema comprovado de gestão de tempo",
        cta_text="Garantir Acesso",
        cta_url="https://checkout.hotmart.com/x",
        faqs=[{"q": "Tenho acesso vitalício?", "a": "Sim, acesso vitalício."}],
        seo_metadata={"title": "SEO Title", "description": "SEO Description"}
    )

    props = manifest.to_astro_props()
    assert props["title"] == "Formação Master em Produtividade"
    assert props["cta"]["url"] == "https://checkout.hotmart.com/x"
    assert len(props["faqs"]) == 1
