import pytest
from src.revenue_os.plugins.research import ResearchPlugin, ResearchPluginFactory, ResearchPluginConfig
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.certification import PluginCertificationEngine

def test_research_plugin_lifecycle():
    plugin = ResearchPluginFactory.create_plugin()
    assert plugin.plugin_name == "research_plugin"
    assert plugin.category == "research"
    
    assert plugin.initialize() is True
    
    health = plugin.health_check()
    assert health["status"] == "HEALTHY"
    assert health["active_providers_count"] == 7
    
    # Execução
    res = plugin.execute({"niche": "python", "limit": 3})
    assert res["status"] == "SUCCESS"
    assert res["niche"] == "python"
    assert len(res["opportunities"]) > 0
    assert len(res["providers_used"]) > 0
    
    plugin.shutdown()
    assert plugin.health_check()["status"] == "UNHEALTHY"

def test_research_plugin_runtime_integration():
    plugin = ResearchPluginFactory.create_plugin()
    runtime = PluginRuntime()
    
    registered = runtime.register_plugin(plugin)
    assert registered is True
    
    fetched = runtime.get_plugin("research_plugin")
    assert fetched is not None
    assert fetched.plugin_name == "research_plugin"

def test_research_plugin_certification():
    plugin = ResearchPluginFactory.create_plugin()
    plugin.initialize()
    
    engine = PluginCertificationEngine()
    cert = engine.certify_plugin(plugin, startup_latency_sec=0.20, memory_usage_mb=35.0)
    
    assert cert["plugin_name"] == "research_plugin"
    assert cert["certification_status"] in ["PRODUCTION", "STABLE"]
    assert cert["is_authorized_for_production"] is True

def test_research_plugin_cache_behavior():
    config = ResearchPluginConfig(cache_enabled=True, cache_ttl_seconds=300)
    plugin = ResearchPluginFactory.create_plugin(config)
    plugin.initialize()
    
    # Primeira chamada: de provedores
    res1 = plugin.execute({"niche": "ai", "limit": 2})
    assert res1["from_cache"] is False
    
    # Segunda chamada: deve vir do cache
    res2 = plugin.execute({"niche": "ai", "limit": 2})
    assert res2["from_cache"] is True
    
    # Chamada com force_refresh
    res3 = plugin.execute({"niche": "ai", "limit": 2, "force_refresh": True})
    assert res3["from_cache"] is False
