import pytest
from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.revenue_engine import RevenueEngine
from src.revenue_os.analytics.schemas import ExperimentContract, Hypothesis, Variant, Economics


@pytest.fixture
def temp_db():
    db = ExperimentDatabase(":memory:")
    # Seed an experiment so we can query and update it
    exp = ExperimentContract(
        experiment_id="EXP-TEST-001",
        hypothesis=Hypothesis(statement="test hypothesis", metric_target="revenue"),
        variant=Variant(id="A", description="test description"),
        economics=Economics(generation_cost_usd=1.0, revenue_usd=0.0),
        creative_hash="hash123",
        platform="pinterest"
    )
    db.insert_experiment(exp)
    return db


@pytest.fixture
def engine(temp_db):
    return RevenueEngine(db=temp_db)


def test_generate_affiliate_link(engine):
    raw_url = "https://example.com/product?id=99"
    utm_url = engine.generate_affiliate_link(raw_url, "EXP-TEST-001", "A", "pinterest")
    
    assert "utm_source=pinterest" in utm_url
    assert "utm_campaign=EXP-TEST-001" in utm_url
    assert "utm_term=A" in utm_url
    assert "id=99" in utm_url


def test_register_conversion(engine, temp_db):
    res = engine.register_conversion(
        conversion_id="CONV-123",
        experiment_id="EXP-TEST-001",
        click_id="CLK-999",
        payout_usd=50.0,
        commission_usd=5.0,
        status="approved"
    )
    assert res["conversion_id"] == "CONV-123"
    assert res["commission_usd"] == 5.0


def test_compute_experiment_roi(engine, temp_db):
    # Register 2 conversions
    engine.register_conversion("C1", "EXP-TEST-001", "CLK-1", 50.0, 5.0)
    engine.register_conversion("C2", "EXP-TEST-001", "CLK-2", 30.0, 3.0)
    
    # Compute ROI with 10 clicks
    metrics = engine.compute_experiment_roi("EXP-TEST-001", outbound_clicks=10)
    
    assert metrics["revenue"] == 8.0  # 5.0 + 3.0
    assert metrics["epc"] == 0.8  # 8.0 / 10
    assert metrics["rpc"] == 4.0  # 8.0 / 2
    assert metrics["cpa"] == 0.5  # cost is 1.0, 1.0 / 2
    assert metrics["ltv"] == 40.0  # (50.0 + 30.0) / 2
    assert metrics["roi"] == 7.0  # (8.0 - 1.0) / 1.0 = 7.0 (700% ROI)
