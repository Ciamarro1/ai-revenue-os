from src.revenue_os.plugins.analytics import AnalyticsPluginFactory
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.certification import PluginCertificationEngine

def test_analytics_plugin_lifecycle():
    plugin = AnalyticsPluginFactory.create_analytics_plugin()
    assert plugin.plugin_name == "analytics_production_plugin"
    assert plugin.category == "analytics"
    assert plugin.initialize() is True
    
    health = plugin.health_check()
    assert health["status"] == "HEALTHY"
    
    # Rastreamento de Evento
    track_res = plugin.execute({"action": "track_event", "event_name": "lead_capture", "properties": {"campaign": "c1"}})
    assert track_res["status"] == "SUCCESS"
    assert "provenance" in track_res
    
    # Processamento de Callback de Afiliado
    cb_res = plugin.execute({"action": "process_callback", "platform": "kiwify", "raw_payload": {"order_id": "ORD-1"}})
    assert cb_res["status"] == "SUCCESS"
    assert cb_res["callback"]["platform"] == "kiwify"
    
    # Assinatura e Verificação de Webhook
    sign_res = plugin.execute({"action": "sign_webhook", "body": {"data": 123}})
    assert sign_res["status"] == "SUCCESS"
    sig = sign_res["signature"]
    
    verify_res = plugin.execute({"action": "verify_webhook", "body": {"data": 123}, "signature": sig})
    assert verify_res["status"] == "SUCCESS"
    assert verify_res["provenance"]["signature_verified"] is True

def test_analytics_plugin_certification():
    plugin = AnalyticsPluginFactory.create_analytics_plugin()
    plugin.initialize()
    
    runtime = PluginRuntime()
    assert runtime.register_plugin(plugin) is True
    
    engine = PluginCertificationEngine()
    cert = engine.certify_plugin(plugin, startup_latency_sec=0.08, memory_usage_mb=20.0)
    
    assert cert["is_authorized_for_production"] is True
    assert cert["certification_status"] == "PRODUCTION"
