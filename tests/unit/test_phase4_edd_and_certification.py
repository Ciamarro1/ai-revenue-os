import pytest
from src.revenue_os.observability.experiment_ledger import ExperimentLedger
from src.revenue_os.plugins.certification import PluginCertificationEngine
from src.revenue_os.plugins.landing.astro_plugin import AstroLandingPlugin
from src.revenue_os.cognition.dataset_versioning import DatasetVersionManager

def test_experiment_ledger_immutable_recording(tmp_path):
    ledger_path = tmp_path / "experiment_ledger.jsonl"
    ledger = ExperimentLedger(ledger_path=ledger_path)

    rec = ledger.record_experiment({
        "experiment_id": "EXP-9001",
        "genome_id": "GEN-55",
        "offer_id": "OFFER-10",
        "landing_url": "https://example.com/landing",
        "infra_cost_usd": 1.20,
        "revenue_usd": 35.0,
        "roi_ratio": 29.1,
        "ctr": 0.065,
        "conversions": 1
    })

    assert rec.experiment_id == "EXP-9001"
    assert ledger_path.exists()

    history = ledger.get_experiment_history()
    assert len(history) == 1
    assert history[0].roi_ratio == 29.1

def test_plugin_certification_engine():
    engine = PluginCertificationEngine()
    astro_plugin = AstroLandingPlugin()

    cert = engine.certify_plugin(
        plugin=astro_plugin,
        startup_latency_sec=0.30,
        memory_usage_mb=32.0
    )

    assert cert["certification_status"] == "PRODUCTION"
    assert cert["is_authorized_for_production"] is True

def test_dataset_version_manager(tmp_path):
    log_path = tmp_path / "versions.json"
    manager = DatasetVersionManager(version_log_path=log_path)

    ver = manager.create_dataset_version("Pinterest_CTR_Dataset_V1", records_count=15000)

    assert ver["dataset_version_id"] == "DSV-001"
    assert ver["genome_version"] == "GV-DSV-001"
    assert log_path.exists()

    latest = manager.get_latest_version()
    assert latest["dataset_name"] == "Pinterest_CTR_Dataset_V1"
