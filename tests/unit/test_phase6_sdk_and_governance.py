import pytest
from src.revenue_os.sdk import BasePlugin, DomainEvent, BusinessAsset, OfferManifest, PluginCertificationEngine
from src.revenue_os.sdk.plugin_sdk import PluginContext, PluginLogger
from src.revenue_os.observability.reliability_metrics import ReliabilityMetricsEngine
from src.revenue_os.observability.benchmarking import BenchmarkingEngine

def test_plugin_sdk_exports():
    assert BasePlugin is not None
    assert DomainEvent is not None
    assert BusinessAsset is not None
    assert OfferManifest is not None
    assert PluginCertificationEngine is not None

def test_plugin_context_and_logger():
    ctx = PluginContext(experiment_id="EXP-101", payload={"key": "val"})
    assert ctx.experiment_id == "EXP-101"

    log_msg = PluginLogger.info("AstroPlugin", "Render successful")
    assert "[PLUGIN_INFO][AstroPlugin]" in log_msg

def test_reliability_metrics_engine():
    engine = ReliabilityMetricsEngine()
    rri = engine.calculate_rri(recent_rois=[2.5, 2.8, 3.1, 2.7])
    assert rri["rri_score"] > 70.0
    assert rri["reliability_level"] in ["HIGHLY_RELIABLE", "MODERATE"]

    kqi = engine.calculate_kqi(confirmed_rules_count=18, rejected_rules_count=2)
    assert kqi["kqi_score"] >= 80.0
    assert kqi["quality_level"] == "HIGH_QUALITY"

def test_benchmarking_engine():
    bench = BenchmarkingEngine()
    week_1 = {"ctr": 0.021, "roi": 1.8, "conversion_rate": 0.02, "kqi_score": 75.0}
    week_2 = {"ctr": 0.026, "roi": 2.4, "conversion_rate": 0.03, "kqi_score": 82.0}

    res = bench.compare_weeks(week_1, week_2)
    assert res["is_outperforming_previous_week"] is True
    assert res["ctr_delta"] == 0.005
    assert res["roi_delta"] == 0.6
