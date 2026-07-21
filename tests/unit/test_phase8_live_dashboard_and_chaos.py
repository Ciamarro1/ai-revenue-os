import pytest
from src.revenue_os.observability.live_dashboard import LiveOperationsDashboard
from src.revenue_os.observability.experiment_replay import ExperimentReplayEngine
from src.revenue_os.plugins.chaos import PluginChaosTestingEngine
from src.revenue_os.plugins.landing.astro_plugin import AstroLandingPlugin
from src.revenue_os.observability.experiment_ledger import ExperimentLedger

def test_live_operations_dashboard():
    dashboard = LiveOperationsDashboard()
    metrics = dashboard.get_live_dashboard_metrics(
        published_assets_count=14,
        total_revenue_usd=182.0,
        total_infra_cost_usd=132.85
    )

    assert metrics["funnel_metrics"]["published_assets_count"] == 14
    assert metrics["financial_metrics"]["net_profit_usd"] == 49.15
    assert metrics["financial_metrics"]["net_roi_ratio"] == 0.37
    assert metrics["platform_health_indices"]["pmi_score"] >= 80

def test_experiment_replay_engine(tmp_path):
    ledger_file = tmp_path / "ledger.jsonl"
    ledger = ExperimentLedger(ledger_path=ledger_file)
    ledger.record_experiment({
        "experiment_id": "EXP-REPLAY-99",
        "genome_id": "GEN-01",
        "offer_id": "OFFER-01",
        "landing_url": "https://landing.example.com",
        "infra_cost_usd": 5.0,
        "revenue_usd": 25.0,
        "roi_ratio": 4.0,
        "ctr": 0.045,
        "conversions": 1
    })

    replay_engine = ExperimentReplayEngine()
    replay_engine.ledger = ledger

    replay_res = replay_engine.replay_experiment("EXP-REPLAY-99")
    assert replay_res["replay_status"] == "REPRODUCED_SUCCESSFULLY"
    assert replay_res["recorded_revenue_usd"] == 25.0

def test_plugin_chaos_testing():
    chaos = PluginChaosTestingEngine()
    astro = AstroLandingPlugin()

    res = chaos.run_chaos_test(astro, fault_type="API_TIMEOUT")
    assert res["chaos_test_status"] == "PASS_RESILIENT"
    assert res["auto_recovery_successful"] is True
