import pytest
from src.revenue_os.analytics.economic_brain import EconomicBrain
from src.reality.oss_catalog.catalog import OSSCatalogService

def test_economic_brain_time_and_resource_efficiency():
    brain = EconomicBrain()
    res = brain.calculate_utility(
        expected_revenue=100.0,
        infra_cost=10.0,
        risk_factor=0.10,
        confidence=0.90,
        gpu_hours=2.0,
        execution_hours=1.0,
        observations_count=50
    )

    eff = res["efficiency_metrics"]
    assert eff["revenue_per_gpu_hour"] == 45.0  # (100 * 0.9) / 2.0 = 45.0
    assert eff["revenue_per_api_dollar"] == 9.0  # 90.0 / 10.0 = 9.0
    assert eff["knowledge_per_dollar"] > 0
    assert eff["knowledge_per_hour"] > 0

def test_oss_capability_matrix_coverage():
    service = OSSCatalogService()
    entries = service.entries
    categories = {e.category.lower() for e in entries}

    assert "landing" in categories
    assert "automation" in categories
    assert "video" in categories
    assert "analytics" in categories
    assert "rag" in categories
