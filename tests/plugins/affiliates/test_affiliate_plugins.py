from src.revenue_os.plugins.affiliates import AffiliatePluginFactory
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.certification import PluginCertificationEngine

def test_hotmart_plugin_lifecycle():
    plugin = AffiliatePluginFactory.create_hotmart_plugin()
    assert plugin.plugin_name == "hotmart_affiliate_plugin"
    assert plugin.category == "marketplaces"
    assert plugin.initialize() is True
    
    health = plugin.health_check()
    assert health["status"] == "HEALTHY"
    
    res = plugin.execute({"action": "discover_products", "niche": "tech", "limit": 2})
    assert res["status"] == "SUCCESS"
    assert len(res["products"]) == 2
    
    link_res = plugin.execute({"action": "generate_deep_link", "product_id": "HOT-101", "sub_id": "test"})
    assert link_res["status"] == "SUCCESS"
    assert "tracking_url" in link_res["deep_link"]
    
    plugin.shutdown()

def test_kiwify_plugin_lifecycle():
    plugin = AffiliatePluginFactory.create_kiwify_plugin()
    assert plugin.plugin_name == "kiwify_affiliate_plugin"
    assert plugin.initialize() is True
    
    res = plugin.execute({"action": "discover_products", "niche": "marketing", "limit": 2})
    assert res["status"] == "SUCCESS"
    assert len(res["products"]) == 2
    
    plugin.shutdown()

def test_eduzz_plugin_lifecycle():
    plugin = AffiliatePluginFactory.create_eduzz_plugin()
    assert plugin.plugin_name == "eduzz_affiliate_plugin"
    assert plugin.initialize() is True
    
    res = plugin.execute({"action": "discover_products", "niche": "finance", "limit": 2})
    assert res["status"] == "SUCCESS"
    assert len(res["products"]) == 2
    
    plugin.shutdown()

def test_amazon_plugin_lifecycle():
    plugin = AffiliatePluginFactory.create_amazon_plugin()
    assert plugin.plugin_name == "amazon_affiliate_plugin"
    assert plugin.initialize() is True
    
    res = plugin.execute({"action": "discover_products", "niche": "gadgets", "limit": 2})
    assert res["status"] == "SUCCESS"
    assert len(res["products"]) == 2
    
    plugin.shutdown()

def test_all_affiliate_plugins_certification():
    plugins = AffiliatePluginFactory.create_all_plugins()
    assert len(plugins) == 4
    
    engine = PluginCertificationEngine()
    runtime = PluginRuntime()
    
    for p in plugins:
        assert runtime.register_plugin(p) is True
        cert = engine.certify_plugin(p, startup_latency_sec=0.15, memory_usage_mb=30.0)
        assert cert["certification_status"] in ["PRODUCTION", "STABLE"]
        assert cert["is_authorized_for_production"] is True
