import pytest
from src.revenue_os.analytics.attribution import AttributionEngine

@pytest.fixture
def attribution_engine():
    return AttributionEngine()

def test_single_touch(attribution_engine):
    touchpoints = [{"experiment_id": "EXP-A", "timestamp": "2026-07-11T10:00:00Z"}]
    total_revenue = 100.0
    
    credit = attribution_engine.distribute_revenue(touchpoints, total_revenue)
    
    assert credit["EXP-A"] == 100.0

def test_dual_touch(attribution_engine):
    touchpoints = [
        {"experiment_id": "EXP-A"},
        {"experiment_id": "EXP-B"}
    ]
    total_revenue = 100.0
    
    credit = attribution_engine.distribute_revenue(touchpoints, total_revenue)
    
    assert credit["EXP-A"] == 50.0
    assert credit["EXP-B"] == 50.0

def test_multi_touch_hybrid_model(attribution_engine):
    # 40% First, 40% Last, 20% Decay (distribuído entre os do meio)
    touchpoints = [
        {"experiment_id": "EXP-DISCOVERY"},  # First Touch (40%)
        {"experiment_id": "EXP-MID-1"},      # Decay (peso menor)
        {"experiment_id": "EXP-MID-2"},      # Decay (peso maior por ser mais recente)
        {"experiment_id": "EXP-CLOSER"}      # Last Touch (40%)
    ]
    total_revenue = 1000.0
    
    credit = attribution_engine.distribute_revenue(touchpoints, total_revenue)
    
    assert credit["EXP-DISCOVERY"] == 400.0
    assert credit["EXP-CLOSER"] == 400.0
    
    # Pool = 200.0. Distribuído linearmente (1 para MID-1, 2 para MID-2) = Total 3.
    # MID-1 = 200 * (1/3) = 66.67
    # MID-2 = 200 * (2/3) = 133.33
    assert credit["EXP-MID-1"] == 66.67
    assert credit["EXP-MID-2"] == 133.33
