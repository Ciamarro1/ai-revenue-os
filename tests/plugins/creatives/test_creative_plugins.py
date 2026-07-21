from src.revenue_os.plugins.creatives import CreativePluginFactory
from src.revenue_os.plugins.plugin_runtime import PluginRuntime
from src.revenue_os.plugins.certification import PluginCertificationEngine

def test_image_generation_plugin_lifecycle():
    plugin = CreativePluginFactory.create_image_plugin()
    assert plugin.plugin_name == "image_generation_plugin"
    assert plugin.category == "image"
    assert plugin.initialize() is True
    
    health = plugin.health_check()
    assert health["status"] == "HEALTHY"
    
    # Direct Generation
    res = plugin.execute({"action": "generate", "prompt": "Futuristic Workspace", "filename": "test_img.png"})
    assert res["status"] == "SUCCESS"
    assert "content_hash" in res["asset"]
    
    # Enqueue and process
    enq_res = plugin.execute({"action": "enqueue", "prompt": "Queued Image"})
    assert enq_res["status"] == "SUCCESS"
    
    proc_res = plugin.execute({"action": "process_queue"})
    assert proc_res["status"] == "SUCCESS"

def test_video_generation_plugin_lifecycle():
    plugin = CreativePluginFactory.create_video_plugin()
    assert plugin.plugin_name == "video_generation_plugin"
    assert plugin.category == "video"
    assert plugin.initialize() is True
    
    res = plugin.execute({"action": "generate", "prompt": "Vertical Promo Script", "filename": "test_vid.mp4"})
    assert res["status"] == "SUCCESS"
    assert res["asset"]["asset_type"] == "video"

def test_creative_benchmark_engine():
    engine = CreativePluginFactory.create_benchmark_engine()
    
    res = engine.run_benchmark(lambda: sum(range(100)), num_iterations=5)
    assert res.total_jobs == 5
    assert res.successful_jobs == 5
    assert res.success_rate_pct == 100.0
    assert res.throughput_jobs_per_sec > 0

def test_creative_plugins_certification():
    img_plugin = CreativePluginFactory.create_image_plugin()
    vid_plugin = CreativePluginFactory.create_video_plugin()
    
    img_plugin.initialize()
    vid_plugin.initialize()
    
    runtime = PluginRuntime()
    assert runtime.register_plugin(img_plugin) is True
    assert runtime.register_plugin(vid_plugin) is True
    
    engine = PluginCertificationEngine()
    cert_img = engine.certify_plugin(img_plugin, startup_latency_sec=0.10, memory_usage_mb=30.0)
    cert_vid = engine.certify_plugin(vid_plugin, startup_latency_sec=0.15, memory_usage_mb=35.0)
    
    assert cert_img["is_authorized_for_production"] is True
    assert cert_vid["is_authorized_for_production"] is True
