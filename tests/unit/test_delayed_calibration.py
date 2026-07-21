import pytest
from datetime import datetime, timezone, timedelta
from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.hypothesis_registry import HypothesisRegistry
from src.revenue_os.analytics.delayed_calibrator import DelayedCalibrator
from src.revenue_os.analytics.schemas import ExperimentContract, Hypothesis, Variant, Economics


class MockMetricsProvider:
    def get_metrics(self, experiment_id):
        class MockMetrics:
            impressions = 2000
            outbound_clicks = 80
            saves = 10
        return MockMetrics()


@pytest.fixture
def temp_db():
    return ExperimentDatabase(":memory:")


@pytest.fixture
def registry(temp_db):
    return HypothesisRegistry(db=temp_db)


@pytest.fixture
def calibrator(temp_db, registry):
    return DelayedCalibrator(db=temp_db, registry=registry, metrics_provider=MockMetricsProvider())


def test_sync_observing_experiments_still_observing(calibrator, temp_db):
    # Seed an experiment published just now
    published_now = datetime.now(timezone.utc).isoformat() + "Z"
    exp = ExperimentContract(
        experiment_id="EXP-ACTIVE",
        hypothesis=Hypothesis(statement="test hypothesis", metric_target="revenue"),
        variant=Variant(id="A", description="test description"),
        economics=Economics(generation_cost_usd=1.0, revenue_usd=0.0),
        creative_hash="hash123",
        platform="pinterest",
        published_at=published_now,
        status="OBSERVING"
    )
    temp_db.insert_experiment(exp)
    
    # Run sync, should not calibrate because it's inside the 72 hour window
    synced = calibrator.sync_observing_experiments(observation_window_hours=72.0)
    assert synced == 0
    
    # Verify status is still OBSERVING
    experiments = temp_db.get_experiments_by_hypothesis("test hypothesis")
    assert len(experiments) == 1
    assert experiments[0].status == "OBSERVING"


def test_sync_observing_experiments_expired(calibrator, temp_db):
    # Seed an experiment published 4 days ago
    published_old = (datetime.now(timezone.utc) - timedelta(days=4)).isoformat() + "Z"
    exp = ExperimentContract(
        experiment_id="EXP-ACTIVE",
        hypothesis=Hypothesis(statement="test hypothesis", metric_target="revenue"),
        variant=Variant(id="A", description="test description"),
        economics=Economics(generation_cost_usd=1.0, revenue_usd=0.0),
        creative_hash="hash123",
        platform="pinterest",
        published_at=published_old,
        status="OBSERVING"
    )
    temp_db.insert_experiment(exp)
    
    # Run sync, should finalize and calibrate
    synced = calibrator.sync_observing_experiments(observation_window_hours=72.0)
    assert synced == 1
    
    # Verify status is now CALIBRATED
    experiments = temp_db.get_experiments_by_hypothesis("test hypothesis")
    assert len(experiments) == 1
    assert experiments[0].status == "CALIBRATED"
    # Verify learning score was computed
    assert experiments[0].learning_value_score > 0.0
