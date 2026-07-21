import pytest
from src.revenue_os.analytics.economic_brain import EconomicBrain
from src.revenue_os.security.feature_flags import SystemFeatureFlags
from src.revenue_os.cognition.hypothesis_registry import HypothesisRegistry

def test_economic_brain_confidence_weighting():
    brain = EconomicBrain()
    res_high_conf = brain.calculate_utility(
        expected_revenue=100.0, infra_cost=10.0, risk_factor=0.10, confidence=0.90
    )
    res_low_conf = brain.calculate_utility(
        expected_revenue=100.0, infra_cost=10.0, risk_factor=0.10, confidence=0.30
    )

    assert res_high_conf["weighted_revenue_usd"] == 90.0
    assert res_low_conf["weighted_revenue_usd"] == 30.0
    assert res_high_conf["total_utility_score"] > res_low_conf["total_utility_score"]

def test_system_feature_flags(tmp_path):
    config_path = tmp_path / "flags.json"
    flags = SystemFeatureFlags(config_path=config_path)

    assert flags.is_feature_enabled("knowledge_gain_weight_enabled") is True
    assert flags.is_feature_enabled("genome_mutation_enabled") is False

    flags.set_feature("genome_mutation_enabled", True)
    assert flags.is_feature_enabled("genome_mutation_enabled") is True
    assert config_path.exists()

def test_hypothesis_registry_prevention(tmp_path):
    storage = tmp_path / "hypotheses.json"
    registry = HypothesisRegistry(storage_path=storage)

    h1 = registry.register_hypothesis(
        statement="Gancho 'Aviso Urgente' aumenta CTR",
        niche="finance",
        reasoning="Sensação de escassez eleva atenção"
    )
    assert h1.status == "TESTING"

    # Avaliar como rejeitado
    eval_res = registry.evaluate_hypothesis(h1.id, observed_val=0.01, target_threshold=0.04)
    assert eval_res["status"] == "REJECTED"

    # Tentativa de registrar a mesma hipótese rejeitada deve lançar ValueError
    with pytest.raises(ValueError, match="foi rejeitada anteriormente"):
        registry.register_hypothesis(
            statement="Gancho 'Aviso Urgente' aumenta CTR",
            niche="finance",
            reasoning="Sensação de escassez eleva atenção"
        )
