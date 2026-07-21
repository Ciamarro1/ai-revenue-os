import pytest
from src.revenue_os.plugins.landing import LandingPluginFactory, LandingDeploymentEngine
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.certification import PluginCertificationEngine

def test_astro_landing_plugin_lifecycle():
    plugin = LandingPluginFactory.create_astro_plugin()
    assert plugin.plugin_name == "astro"
    assert plugin.category == "landing"
    assert plugin.initialize() is True
    
    health = plugin.health_check()
    assert health["status"] == "HEALTHY"
    
    # Build and Deploy
    res = plugin.execute({
        "action": "build_and_deploy",
        "id": "OFFER-1",
        "title": "Astro Product Landing",
        "cdn_provider": "cloudflare_pages"
    })
    assert res["status"] == "SUCCESS"
    assert "pages.dev" in res["landing_url"]
    assert len(res["build_fingerprint"]) > 0
    assert len(res["version"]) > 0

def test_nextjs_landing_plugin_lifecycle():
    plugin = LandingPluginFactory.create_nextjs_plugin()
    assert plugin.plugin_name == "nextjs"
    assert plugin.category == "landing"
    assert plugin.initialize() is True
    
    health = plugin.health_check()
    assert health["status"] == "HEALTHY"
    
    res = plugin.execute({
        "action": "build_and_deploy",
        "id": "OFFER-2",
        "title": "Nextjs Product Landing",
        "cdn_provider": "vercel"
    })
    assert res["status"] == "SUCCESS"
    assert "vercel.app" in res["landing_url"]

def test_deployment_engine_rollback():
    engine = LandingPluginFactory.create_deployment_engine()
    
    # Deploy 1
    b1 = engine.build_landing({"id": "OFFER-100", "title": "Version 1"}, framework="astro")
    d1 = engine.deploy_landing(b1, cdn_name="cloudflare_pages")
    
    # Deploy 2
    b2 = engine.build_landing({"id": "OFFER-100", "title": "Version 2"}, framework="astro")
    d2 = engine.deploy_landing(b2, cdn_name="cloudflare_pages")
    
    assert d2.is_active is True
    
    # Rollback para Deploy 1
    rb = engine.rollback(d1.deployment_id)
    assert rb.status == "SUCCESS"
    assert rb.restored_deployment_id == d1.deployment_id
    assert d1.is_active is True
    assert d2.is_active is False

def test_landing_plugins_certification():
    astro = LandingPluginFactory.create_astro_plugin()
    nextjs = LandingPluginFactory.create_nextjs_plugin()
    
    astro.initialize()
    nextjs.initialize()
    
    runtime = PluginRuntime()
    assert runtime.register_plugin(astro) is True
    assert runtime.register_plugin(nextjs) is True
    
    engine = PluginCertificationEngine()
    cert_astro = engine.certify_plugin(astro, startup_latency_sec=0.10, memory_usage_mb=25.0)
    cert_nextjs = engine.certify_plugin(nextjs, startup_latency_sec=0.12, memory_usage_mb=28.0)
    
    assert cert_astro["is_authorized_for_production"] is True
    assert cert_nextjs["is_authorized_for_production"] is True
