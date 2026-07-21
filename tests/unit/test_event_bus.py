import pytest
from src.core.events.event_bus import EventBus, Event
from src.revenue_os.analytics.database import ExperimentDatabase
from src.core.cognition.repository import CognitiveRepository
from src.core.cognition.belief_manager import BeliefManager
from src.core.cognition.evidence_engine import EvidenceEngine

@pytest.fixture
def clean_bus():
    """Garante um barramento limpo sem listeners residuais entre testes."""
    bus = EventBus()
    bus.clear_listeners()
    return bus

@pytest.fixture
def in_memory_db():
    return ExperimentDatabase(":memory:")

def test_event_bus_subscribe_and_publish(clean_bus):
    calls = []
    
    def handler(event: Event):
        calls.append(event)
        
    clean_bus.subscribe("EvidenceCreated", handler)
    
    payload = {"hypothesis_id": 42, "niche": "finance"}
    event = clean_bus.publish("EvidenceCreated", payload)
    
    assert len(calls) == 1
    assert calls[0].event_type == "EvidenceCreated"
    assert calls[0].payload == payload
    assert calls[0].timestamp == event.timestamp

def test_event_bus_subscribe_global(clean_bus):
    calls = []
    
    def global_handler(event: Event):
        calls.append(event)
        
    clean_bus.subscribe_global(global_handler)
    
    clean_bus.publish("BeliefUpdated", {"id": 1})
    clean_bus.publish("DecisionGenerated", {"action": "scale"})
    
    assert len(calls) == 2
    assert calls[0].event_type == "BeliefUpdated"
    assert calls[1].event_type == "DecisionGenerated"

def test_event_bus_persistence(in_memory_db, clean_bus):
    # Inicializa o barramento com o banco de dados
    bus = EventBus(in_memory_db)
    
    payload = {"hypothesis": "minimalist_techno", "status": "approved"}
    bus.publish("HypothesisChanged", payload)
    
    # Busca histórico do banco SQLite
    history = bus.get_event_history("HypothesisChanged")
    assert len(history) >= 1
    assert history[0].event_type == "HypothesisChanged"
    assert history[0].payload == payload
    assert history[0].timestamp is not None

def test_belief_manager_integration(in_memory_db, clean_bus):
    bus = EventBus(in_memory_db)
    
    # 1. Configura repositório cognitivo e mocka uma crença
    repo = CognitiveRepository(in_memory_db)
    with in_memory_db._get_conn() as conn:
        c = conn.cursor()
        # Cria crenças com a coluna atualizada correta
        c.execute("""
            INSERT INTO beliefs (statement, confidence_score, updated_at)
            VALUES (?, ?, ?)
        """, ("Pinterest organic traffic conversion is high", 0.70, "2026-07-19T00:00:00Z"))
        conn.commit()
        
    # Inscreve listener para monitorar a emissão do evento
    events_captured = []
    bus.subscribe("BeliefUpdated", lambda e: events_captured.append(e))
    
    manager = BeliefManager(repo)
    manager.evolve_belief(
        belief_id=1,
        evidence_confidence=0.80,
        impact="positivo",
        reason="CTR was high",
        quality_score=0.90
    )
    
    assert len(events_captured) == 1
    assert events_captured[0].event_type == "BeliefUpdated"
    assert events_captured[0].payload["belief_id"] == 1
    assert events_captured[0].payload["old_confidence"] == 0.70
    assert events_captured[0].payload["new_confidence"] > 0.70

def test_evidence_engine_integration(in_memory_db, clean_bus):
    bus = EventBus(in_memory_db)
    
    repo = CognitiveRepository(in_memory_db)
    with in_memory_db._get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO evidence (hypothesis_id, experiment_id, claim, confidence_score, impact, timestamp, narrative)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (1, "EXP-100", "Hook CTR significantly above average", 0.85, "positivo", "2026-07-19T00:00:00Z", "Some description"))
        conn.commit()
        
    events_captured = []
    bus.subscribe("EvidenceEvaluated", lambda e: events_captured.append(e))
    
    engine = EvidenceEngine(repo)
    engine.evaluate_evidence(
        evidence_id=1,
        sample_size=12000,
        statistical_confidence=0.95,
        reliability=0.90
    )
    
    assert len(events_captured) == 1
    assert events_captured[0].event_type == "EvidenceEvaluated"
    assert events_captured[0].payload["evidence_id"] == 1
    assert events_captured[0].payload["sample_size"] == 12000
    assert events_captured[0].payload["quality_score"] > 0.0

