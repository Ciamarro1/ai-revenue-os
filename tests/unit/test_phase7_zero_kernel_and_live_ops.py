import pytest
from pathlib import Path
from src.revenue_os.factory.live_pipeline_validator import LivePipelineValidator

def test_zero_kernel_modification_policy_doc_exists():
    doc = Path("docs/architecture/zero_kernel_modification.md")
    assert doc.exists()

def test_live_pipeline_validator_pm1():
    validator = LivePipelineValidator()
    res = validator.validate_pm1_pipeline()

    assert res["milestone"] == "PM-1"
    assert res["is_pipeline_ready"] is True
    assert res["status"] == "READY_FOR_LIVE_DISPATCH"
    assert res["checks"]["astro_plugin_certified"] is True
    assert res["checks"]["pmi_maturity_score"] >= 80
