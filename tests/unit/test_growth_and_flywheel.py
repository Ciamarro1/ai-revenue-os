import pytest
from src.revenue_os.analytics.knowledge_flywheel import KnowledgeFlywheel
from src.revenue_os.portfolio_manager import PortfolioManager

def test_knowledge_flywheel_insights(tmp_path):
    storage = tmp_path / "flywheel.json"
    flywheel = KnowledgeFlywheel(storage_path=storage)

    insights = flywheel.get_actionable_insights(niche="recipes", platform="pinterest")
    assert len(insights) >= 1
    assert any("domingos" in i["rule"] for i in insights)

    # Ingestão de novo aprendizado
    new_insight = flywheel.ingest_experiment_learning({
        "niche": "finance",
        "platform": "pinterest",
        "hook": "Urgent Savings",
        "ctr": 0.065,
        "revenue": 29.90
    })

    assert new_insight["confidence"] == 0.90
    assert storage.exists()

def test_portfolio_manager_tomorrow_queue_and_allocation():
    manager = PortfolioManager()
    queue = manager.generate_tomorrow_queue(top_n=4)

    assert len(queue) == 4
    assert queue[0]["rank"] == 1
    assert queue[0]["niche"] == "Minimalist Home Office"
    assert queue[0]["expected_roi"] == 4.1

    # Teste de alocação de recursos e Experiment Killer
    experiments = [
        {"id": "EXP-001", "ctr": 0.05, "roi": 3.2, "sample_size": 150},  # SCALE_PAID
        {"id": "EXP-002", "ctr": 0.005, "roi": 0.2, "sample_size": 120}, # KILL
        {"id": "EXP-003", "ctr": 0.035, "roi": 1.2, "sample_size": 80}   # PROMOTE_ORGANIC
    ]

    allocation = manager.allocate_resources(experiments)
    assert allocation["summary"]["scaled_paid"] == 1
    assert allocation["summary"]["terminated"] == 1
    assert allocation["terminated"][0]["action"] == "KILL"
