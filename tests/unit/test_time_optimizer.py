import pytest
from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.time_optimizer import TimeSlotOptimizer


@pytest.fixture
def temp_db():
    return ExperimentDatabase(":memory:")


@pytest.fixture
def optimizer(temp_db):
    return TimeSlotOptimizer(db=temp_db)


def test_initial_slots(optimizer):
    stats = optimizer.get_slot_stats()
    assert len(stats) == 24  # 0-23
    assert all(s["total_posts"] == 0 for s in stats)


def test_record_outcome(optimizer):
    optimizer.record_outcome(hour=14, impressions=1000, clicks=50, saves=10)
    stats = optimizer.get_slot_stats()
    slot_14 = next(s for s in stats if s["hour_slot"] == 14)
    assert slot_14["total_posts"] == 1
    assert slot_14["total_impressions"] == 1000


def test_record_multiple_outcomes(optimizer):
    for _ in range(5):
        optimizer.record_outcome(hour=19, impressions=500, clicks=25, saves=5)
    stats = optimizer.get_slot_stats()
    slot_19 = next(s for s in stats if s["hour_slot"] == 19)
    assert slot_19["total_posts"] == 5


def test_optimal_schedule(optimizer):
    # Record good performance at specific hours
    optimizer.record_outcome(hour=9, impressions=1000, clicks=100, saves=50)
    optimizer.record_outcome(hour=14, impressions=1000, clicks=80, saves=30)
    optimizer.record_outcome(hour=19, impressions=1000, clicks=120, saves=60)
    
    schedule = optimizer.get_optimal_schedule(n_posts=3)
    assert len(schedule) == 3
    assert all(0 <= h <= 23 for h in schedule)
    assert schedule == sorted(schedule)  # Sorted by hour


def test_optimal_schedule_more_than_available(optimizer):
    schedule = optimizer.get_optimal_schedule(n_posts=5)
    assert len(schedule) == 5


def test_default_schedule(optimizer):
    schedule = optimizer._default_schedule(n_posts=5)
    assert len(schedule) == 5
    assert all(9 <= h <= 22 for h in schedule)


def test_invalid_hour_ignored(optimizer):
    optimizer.record_outcome(hour=25, impressions=100, clicks=5, saves=1)
    stats = optimizer.get_slot_stats()
    assert len(stats) == 24  # No new slot created


def test_thompson_sampling_favors_good_slots(optimizer):
    # Create very strong performance at hour 20
    for _ in range(20):
        optimizer.record_outcome(hour=20, impressions=5000, clicks=500, saves=100)
    # Create poor performance at hour 5
    for _ in range(20):
        optimizer.record_outcome(hour=5, impressions=5000, clicks=1, saves=0)
    
    # Run multiple schedules and check hour 20 appears more often
    appearances_20 = 0
    appearances_5 = 0
    for _ in range(50):
        schedule = optimizer.get_optimal_schedule(n_posts=5)
        if 20 in schedule:
            appearances_20 += 1
        if 5 in schedule:
            appearances_5 += 1
    
    assert appearances_20 > appearances_5
