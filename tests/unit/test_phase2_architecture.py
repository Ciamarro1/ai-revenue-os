import pytest
from src.reality.oss_catalog.catalog import OSSCatalogService
from src.revenue_os.analytics.opportunity_engine import OpportunityEngine
from src.revenue_os.observability.explainability_engine import ExplainabilityEngine
from src.revenue_os.self_optimization import SelfOptimizationEngine

def test_oss_catalog_service(tmp_path):
    catalog_path = tmp_path / "oss_catalog.json"
    service = OSSCatalogService(catalog_path=catalog_path)

    results = service.search_solution(category="landing")
    assert len(results) >= 1
    assert "Astro" in results[0].name or "Next" in results[0].name
    assert catalog_path.exists()

def test_opportunity_engine(tmp_path):
    storage = tmp_path / "opps"
    engine = OpportunityEngine(storage_dir=storage)

    opps = engine.discover_opportunities("productivity")
    assert len(opps) >= 3
    assert opps[0].opportunity_score > 0
    assert opps[0].marketplace in ["Hotmart", "ClickBank", "Amazon"]

def test_explainability_engine(tmp_path):
    log_path = tmp_path / "explanations.jsonl"
    engine = ExplainabilityEngine(log_path=log_path)

    rec = engine.explain_niche_selection(
        niche="Minimalist Home Office",
        expected_ctr_gain=0.18,
        competition_reduction=-0.42,
        commission_gain=0.27,
        confidence=0.91,
        projected_roi=3.8
    )

    assert rec["action"] == "SELECT_NICHE"
    assert "CTR esperado +18.0%" in rec["explanation"]
    assert log_path.exists()

def test_self_optimization_engine():
    engine = SelfOptimizationEngine(current_exploration_ratio=0.30)
    audit = engine.run_health_and_optimization_audit(
        skill_telemetry=[
            {"name": "slow_rendering_skill", "avg_latency_sec": 12.5, "success_rate": 0.80}
        ],
        average_roi=3.5
    )

    assert audit["health_status"] == "WARNING"
    assert audit["current_ratios"]["exploration"] < 0.30
    assert len(audit["detected_bottlenecks"]) == 1
    assert len(audit["optimization_recommendations"]) >= 1
