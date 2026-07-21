import pytest
from src.services.revenue_experiment_cycle import RevenueExperimentPipeline

def test_full_revenue_experiment_cycle():
    pipeline = RevenueExperimentPipeline()
    result = pipeline.run_full_revenue_cycle(niche="productivity")

    assert result["status"] == "cycle_completed"
    assert result["experiment_id"] == "EXP-REV-001"
    assert "topic_candidate" in result
    assert result["net_revenue"] > 0.0
    assert result["genome_score"] > 0.0
    assert result["roi_percentage"] > 100.0
