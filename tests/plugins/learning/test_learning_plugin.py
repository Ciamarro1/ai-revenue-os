from src.revenue_os.plugins.learning import LearningPluginFactory
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.certification import PluginCertificationEngine

def test_learning_plugin_lifecycle():
    plugin = LearningPluginFactory.create_learning_plugin()
    assert plugin.plugin_name == "production_learning_plugin"
    assert plugin.category == "learning"
    assert plugin.initialize() is True
    
    health = plugin.health_check()
    assert health["status"] == "HEALTHY"
    
    # Execução do Ciclo de Aprendizado
    res = plugin.execute({"action": "run_cycle"})
    assert res["status"] == "SUCCESS"
    assert "cycle_result" in res
    
    # Consulta de Hipóteses e Pesos
    hyp_res = plugin.execute({"action": "get_hypotheses"})
    assert hyp_res["status"] == "SUCCESS"
    assert len(hyp_res["hypotheses"]) >= 2
    
    weights_res = plugin.execute({"action": "get_weights"})
    assert weights_res["status"] == "SUCCESS"
    assert len(weights_res["weights"]) >= 2

def test_learning_plugin_certification():
    plugin = LearningPluginFactory.create_learning_plugin()
    plugin.initialize()
    
    runtime = PluginRuntime()
    assert runtime.register_plugin(plugin) is True
    
    engine = PluginCertificationEngine()
    cert = engine.certify_plugin(plugin, startup_latency_sec=0.05, memory_usage_mb=18.0)
    
    assert cert["is_authorized_for_production"] is True
    assert cert["certification_status"] == "PRODUCTION"
