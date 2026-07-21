import pytest
from src.core.kernel import CognitiveKernel
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

def test_cognitive_kernel_initialization(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)
    assert kernel.beliefs is not None
    assert kernel.evidence is not None
    assert kernel.decision is not None
    assert kernel.memory is not None
    assert kernel.events is not None

def test_kernel_belief_evolution_and_event_publishing(in_memory_db, clean_bus):
    kernel = CognitiveKernel(in_memory_db)
    
    # 1. Configurar banco com uma crença inicial
    with in_memory_db._get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO beliefs (statement, confidence_score, updated_at)
            VALUES (?, ?, ?)
        """, ("Nicho financeiro converte melhor com vídeo", 0.60, "2026-07-19T00:00:00Z"))
        conn.commit()

    # 2. Executar evolução através da API de crenças
    new_score = kernel.beliefs.evolve(
        belief_id=1,
        evidence_confidence=0.85,
        impact="positivo",
        reason="high viral CTR",
        quality_score=0.90
    )
    
    assert new_score > 0.60
    
    # 3. Verificar que o evento correspondente foi publicado e gravado no histórico
    history = kernel.events.get_history("BeliefUpdated")
    assert len(history) == 1
    assert history[0].payload["belief_id"] == 1
    assert history[0].payload["new_confidence"] == new_score

def test_kernel_evidence_registration_and_evaluation(in_memory_db, clean_bus):
    kernel = CognitiveKernel(in_memory_db)
    
    # 1. Registrar evidência
    evidence = kernel.evidence.register(
        hypothesis_id=1,
        experiment_id="EXP-100",
        claim="Creative hook variation alpha outperformed beta",
        confidence_score=0.90,
        impact="positivo",
        narrative="CTR difference was statistically significant"
    )
    
    assert evidence.id == 1
    assert evidence.experiment_id == "EXP-100"
    
    # 2. Avaliar qualidade da evidência
    quality = kernel.evidence.evaluate(
        evidence_id=evidence.id,
        sample_size=15000,
        statistical_confidence=0.95,
        reliability=0.90
    )
    
    assert quality > 0.0
    
    # 3. Verificar evento publicado
    history = kernel.events.get_history("EvidenceEvaluated")
    assert len(history) == 1
    assert history[0].payload["evidence_id"] == 1
    assert history[0].payload["quality_score"] == quality

def test_kernel_decision_evaluation(in_memory_db, clean_bus):
    kernel = CognitiveKernel(in_memory_db)
    
    # 1. Mockar crença
    with in_memory_db._get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO beliefs (statement, confidence_score, updated_at)
            VALUES (?, ?, ?)
        """, ("Video hooks are better", 0.70, "2026-07-19T00:00:00Z"))
        conn.commit()
        
    # 2. Avaliar decisão com recomendação TEST (score intermediário)
    # Expected: (0.70 * 0.80 * 0.60) - 0.10 = 0.336 - 0.10 = 0.236 -> TEST
    res_test = kernel.decision.evaluate_decision(
        belief_id=1,
        expected_impact=0.60,
        risk=0.10,
        default_quality=0.80
    )
    assert res_test["recommendation"] == "TEST"
    assert res_test["decision_score"] == 0.236
    
    # 3. Avaliar decisão com recomendação EXECUTE (score alto)
    # Expected: (0.70 * 0.90 * 0.90) - 0.05 = 0.567 - 0.05 = 0.517 -> EXECUTE
    res_execute = kernel.decision.evaluate_decision(
        belief_id=1,
        expected_impact=0.90,
        risk=0.05,
        default_quality=0.90
    )
    assert res_execute["recommendation"] == "EXECUTE"
    assert res_execute["decision_score"] == 0.517

def test_kernel_memory_rag_context(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)
    
    # 1. Salvar memória episódica
    kernel.memory.store(
        content="Cooking pins did not perform well in Q2",
        memory_type="episodic",
        metadata={"niche": "cooking", "quarter": "Q2"}
    )
    
    # 2. Recuperar contexto semântico
    context = kernel.memory.get_context(current_niche="cooking", query="Q2 performance")
    assert "MEMÓRIAS OPERACIONAIS E APRENDIZADOS ANTERIORES" in context
    assert "Cooking pins did not perform" in context


