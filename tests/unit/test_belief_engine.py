import pytest
from src.core.kernel import CognitiveKernel
from src.core.cognition.models import Observation, Belief
from src.revenue_os.analytics.database import ExperimentDatabase
from src.core.events.event_bus import EventBus

@pytest.fixture
def clean_bus():
    """Garante barramento limpo."""
    bus = EventBus()
    bus.clear_listeners()
    return bus

@pytest.fixture
def in_memory_db():
    return ExperimentDatabase(":memory:")

def test_belief_engine_pipeline(in_memory_db, clean_bus):
    # 1. Setup CognitiveKernel facade
    kernel = CognitiveKernel(in_memory_db)
    
    # 2. Cadastrar crença inicial
    initial_belief = Belief(statement="Pinterest CTR is high", confidence_score=0.5)
    saved_belief = kernel.repo.save_belief(initial_belief)
    assert saved_belief.id is not None
    assert saved_belief.confidence_score == 0.5

    # 3. Processar observação positiva (CTR acima do baseline)
    obs_positive = Observation(
        source="pinterest_scraper",
        metric_name="CTR",
        value=2.5,
        raw_data="Raw click log payload"
    )
    evidence_pos = kernel.beliefs.process_observation(
        observation=obs_positive,
        related_belief_id=saved_belief.id,
        baseline_value=1.5,
        tolerance_percent=10.0
    )

    # Verificar que observação e evidência foram registradas
    assert evidence_pos.id is not None
    assert evidence_pos.impact == "positivo"
    assert "superou o baseline" in evidence_pos.claim

    # Re-consultar crença e verificar evolução de confiança
    updated_belief_pos = kernel.beliefs.get_belief(saved_belief.id)
    assert updated_belief_pos.confidence_score > 0.5  # Confiança deve subir

    # 4. Processar observação negativa (CTR abaixo do baseline)
    obs_negative = Observation(
        source="pinterest_scraper",
        metric_name="CTR",
        value=0.5,
        raw_data="Raw negative log payload"
    )
    evidence_neg = kernel.beliefs.process_observation(
        observation=obs_negative,
        related_belief_id=saved_belief.id,
        baseline_value=1.5,
        tolerance_percent=10.0
    )

    assert evidence_neg.id is not None
    assert evidence_neg.impact == "negativo"
    assert "ficou abaixo do baseline" in evidence_neg.claim

    # Re-consultar crença e verificar queda de confiança
    updated_belief_neg = kernel.beliefs.get_belief(saved_belief.id)
    assert updated_belief_neg.confidence_score < updated_belief_pos.confidence_score  # Confiança deve cair

    # 5. Processar observação neutra (dentro da tolerância)
    obs_neutral = Observation(
        source="pinterest_scraper",
        metric_name="CTR",
        value=1.55,  # baseline = 1.5, tolerância = 10% (1.35 - 1.65)
        raw_data="Raw neutral log payload"
    )
    evidence_neu = kernel.beliefs.process_observation(
        observation=obs_neutral,
        related_belief_id=saved_belief.id,
        baseline_value=1.5,
        tolerance_percent=10.0
    )

    assert evidence_neu.id is not None
    assert evidence_neu.impact == "neutro"

    # Confiança não deve mudar em relação à rodada anterior
    final_belief = kernel.beliefs.get_belief(saved_belief.id)
    assert final_belief.confidence_score == updated_belief_neg.confidence_score
