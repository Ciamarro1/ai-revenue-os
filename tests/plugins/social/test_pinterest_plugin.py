from src.revenue_os.plugins.social import SocialPluginFactory, PinterestConfig
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.certification import PluginCertificationEngine

def test_pinterest_plugin_lifecycle_shadow():
    plugin = SocialPluginFactory.create_pinterest_plugin(PinterestConfig(mode="shadow"))
    assert plugin.plugin_name == "pinterest_plugin"
    assert plugin.category == "social"
    assert plugin.initialize() is True
    
    health = plugin.health_check()
    assert health["status"] == "HEALTHY"
    assert health["mode"] == "shadow"
    
    # Execution em Modo Shadow
    res = plugin.execute({
        "action": "publish",
        "title": "Shadow Pin",
        "description": "Shadow Description",
        "link": "https://pages.airevenueos.com"
    })
    assert res["status"] == "SUCCESS"
    assert res["result"]["status"] == "shadow_mode"
    assert res["result"]["classification_status"] == "LOCAL_TEST"

def test_pinterest_plugin_waiting_external_dependency():
    # Modo Live sem sessão e sem token -> Deve retornar WAITING_EXTERNAL_DEPENDENCY
    plugin = SocialPluginFactory.create_pinterest_plugin(PinterestConfig(mode="live", session_file_path="non_existent.json"))
    plugin.initialize()
    
    res = plugin.execute({
        "action": "publish",
        "title": "Live Pin",
        "description": "Desc",
        "link": "https://pages.airevenueos.com"
    })
    assert res["status"] == "WAITING_EXTERNAL_DEPENDENCY"
    assert res["result"]["classification_status"] == "WAITING_EXTERNAL_DEPENDENCY"

def test_pinterest_plugin_queue_processing():
    plugin = SocialPluginFactory.create_pinterest_plugin(PinterestConfig(mode="shadow"))
    plugin.initialize()
    
    # Enfileiramento
    enq_res = plugin.execute({"action": "enqueue", "title": "Queued Pin"})
    assert enq_res["status"] == "SUCCESS"
    assert enq_res["job"]["status"] == "QUEUED"
    
    # Processamento da Fila
    proc_res = plugin.execute({"action": "process_queue"})
    assert proc_res["status"] == "SUCCESS"
    assert proc_res["job"]["status"] == "COMPLETED"

def test_pinterest_plugin_certification():
    plugin = SocialPluginFactory.create_pinterest_plugin(PinterestConfig(mode="shadow"))
    plugin.initialize()
    
    runtime = PluginRuntime()
    assert runtime.register_plugin(plugin) is True
    
    engine = PluginCertificationEngine()
    cert = engine.certify_plugin(plugin, startup_latency_sec=0.10, memory_usage_mb=32.0)
    
    assert cert["is_authorized_for_production"] is True
    assert cert["certification_status"] == "PRODUCTION"
