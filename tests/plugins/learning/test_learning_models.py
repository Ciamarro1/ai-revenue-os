from src.revenue_os.plugins.learning.models import (
    HypothesisState,
    EconomicBrainWeight,
    LearningCycleResult,
    LearningConfig
)

def test_hypothesis_state_schema():
    h = HypothesisState(hypothesis_id="H1", statement="Test statement", prior_confidence=0.5)
    assert h.hypothesis_id == "H1"
    assert h.status == "CANDIDATE"

def test_economic_brain_weight_schema():
    w = EconomicBrainWeight(param_name="conversion_rate", current_weight=0.04, previous_weight=0.03, delta=0.01)
    assert w.param_name == "conversion_rate"
    assert w.delta == 0.01

def test_learning_cycle_result_schema():
    r = LearningCycleResult(
        cycle_id="C1", total_ledger_entries=10, real_production_entries=5,
        ignored_benchmark_entries=5, hypotheses_evaluated=2, promoted_count=1,
        rejected_count=0, weights_recalibrated=2, dataset_version="DS-V1"
    )
    assert r.real_production_entries == 5
    assert r.ignored_benchmark_entries == 5

def test_learning_config_schema():
    cfg = LearningConfig(promotion_threshold=0.90)
    assert cfg.promotion_threshold == 0.90
