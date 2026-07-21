import pytest
from src.reality.oss_catalog.review_gate import OpenSourceReviewGate
from src.reality.oss_catalog.catalog import OSSCatalogService
from src.revenue_os.connectors.marketplace_adapters import (
    HotmartAdapter, ClickBankAdapter, AmazonAdapter, DigistoreAdapter, GumroadAdapter
)
from src.revenue_os.analytics.opportunity_engine import OpportunityEngine
from src.revenue_os.domain.business_asset import BusinessAsset
from src.revenue_os.analytics.opportunity_schemas import RevenueOpportunity
from src.revenue_os.observability.explainability_engine import ExplainabilityEngine
from src.revenue_os.self_optimization import SelfOptimizationEngine

def test_open_source_review_gate(tmp_path):
    log_path = tmp_path / "reviews.json"
    gate = OpenSourceReviewGate(review_log_path=log_path)

    # 1. Feature com solução Open Source madura
    res_oss = gate.review_feature_request(
        feature_name="Landing Page Builder",
        category="landing",
        problem_description="Need fast SSG landing pages"
    )
    assert res_oss["oss_available"] is True
    assert res_oss["action"] == "INTEGRATE_AND_BUILD_ADAPTER"
    assert "Astro" in res_oss["selected_oss"] or "Next" in res_oss["selected_oss"]

    # 2. Feature sem solução Open Source -> Autorizar proprietário
    res_prop = gate.review_feature_request(
        feature_name="Custom Genome Score",
        category="proprietary_genome_brain",
        problem_description="Unique quant fund scoring algorithm"
    )
    assert res_prop["oss_available"] is False
    assert res_prop["action"] == "DEVELOP_PROPRIETARY_DIFFERENTIATOR"

def test_pluggable_marketplace_adapters():
    adapters = [
        HotmartAdapter(),
        ClickBankAdapter(),
        AmazonAdapter(),
        DigistoreAdapter(),
        GumroadAdapter()
    ]

    for adapter in adapters:
        opps = adapter.get_normalized_opportunities("productivity")
        assert len(opps) >= 1
        assert opps[0].marketplace == adapter.marketplace_name
        assert opps[0].opportunity_score > 0

def test_opportunity_engine_aggregation(tmp_path):
    storage = tmp_path / "opps"
    engine = OpportunityEngine(storage_dir=storage)

    top_opps = engine.discover_opportunities("productivity")
    assert len(top_opps) >= 5
    assert top_opps[0].opportunity_score >= top_opps[1].opportunity_score

def test_business_asset_entity():
    opp = RevenueOpportunity(
        id="OPP-100",
        marketplace="Hotmart",
        product_name="Productivity Course",
        category="productivity",
        commission_rate=0.60,
        avg_commission_usd=40.0,
        epc_usd=4.50
    )

    asset = BusinessAsset(
        id="ASSET-777",
        opportunity=opp,
        landing_page_url="https://example.com/landing",
        pins=[{"id": "PIN-1"}, {"id": "PIN-2"}],
        total_impressions=10000,
        total_clicks=500,
        total_conversions=20,
        total_revenue=800.0,
        total_cost=50.0
    )

    assert asset.net_profit == 750.0
    assert asset.roi_ratio == 16.0
    summary = asset.to_summary()
    assert summary["total_pins"] == 2
    assert summary["net_profit_usd"] == 750.0

def test_explainability_decision_dag(tmp_path):
    log_path = tmp_path / "explanations.jsonl"
    engine = ExplainabilityEngine(log_path=log_path)

    dag = engine.generate_decision_dag(
        asset_id="ASSET-777",
        opportunity_id="OPP-100",
        genome_id="GENOME-42",
        experiment_id="EXP-99",
        revenue=800.0
    )

    assert len(dag["nodes"]) == 6
    assert len(dag["edges"]) == 5
    assert dag["status"] == "PROVEN"

def test_self_optimization_architectural_suggestions():
    engine = SelfOptimizationEngine()
    suggestions = engine.suggest_architectural_optimizations([
        {"name": "heavy_render_skill", "latency_sec": 4.5, "failure_rate": 0.05},
        {"name": "playwright_pin_skill", "latency_sec": 2.1, "failure_rate": 0.20}
    ])

    assert len(suggestions) == 2
    assert suggestions[0]["expected_cost_reduction_percent"] == 38.0
    assert suggestions[1]["expected_reliability_increase_percent"] == 25.0
