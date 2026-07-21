import pytest
from src.core.kernel import CognitiveKernel
from src.core.cognition.models import Observation, Belief, GraphNode, GraphEdge
from src.revenue_os.analytics.database import ExperimentDatabase
from src.core.events.event_bus import EventBus

@pytest.fixture
def clean_bus():
    bus = EventBus()
    bus.clear_listeners()
    return bus

@pytest.fixture
def in_memory_db():
    return ExperimentDatabase(":memory:")

def test_hypothesis_engine_lifecycle(in_memory_db, clean_bus):
    kernel = CognitiveKernel(in_memory_db)
    
    # 1. Test creation
    hyp = kernel.hypotheses.create("Pinterest saturates in niche", initial_confidence=0.50)
    assert hyp.id is not None
    assert hyp.statement == "Pinterest saturates in niche"
    assert hyp.confidence_score == 0.50
    assert hyp.status == "Proposed"
    
    # Verify graph node is registered
    node = kernel.repo.get_node(f"hypothesis:{hyp.id}")
    assert node is not None
    assert node.type == "hypothesis"
    assert node.properties["confidence"] == 0.50

    # 2. Test evaluation against supporting evidence (Bayesian revision)
    # Primeiro criamos uma observação e rodamos a pipeline para ter uma evidência no banco
    # Precisamos de uma crença para a pipeline original
    belief = kernel.beliefs.repo.save_belief(Belief(statement="Niche conversion is high"))
    obs = Observation(source="pinterest_scraper", metric_name="CTR", value=2.9)
    evidence = kernel.beliefs.process_observation(obs, related_belief_id=belief.id, baseline_value=1.5)
    
    # Agora avaliamos a evidência contra a hipótese como suporte
    new_confidence = kernel.hypotheses.evaluate(
        hypothesis_id=hyp.id,
        evidence_id=evidence.id,
        is_supporting=True,
        learning_rate=0.20
    )
    # prior = 0.50. evidence confidence = 0.85 (source pinterest_scraper ends with scraper). lr = 0.20
    # expected new = prior + (1 - prior) * ev_confidence * lr = 0.50 + 0.50 * 0.85 * 0.20 = 0.585
    assert abs(new_confidence - 0.585) < 0.001
    
    # Re-fetch hypothesis and assert status/confidence updates
    updated_hyp = kernel.hypotheses.get(hyp.id)
    assert updated_hyp.confidence_score == new_confidence
    assert updated_hyp.status == "Proposed"

    # Verificar que o grafo conecta a evidência à hipótese com relação "supports"
    edges = kernel.repo.get_edges_to(f"hypothesis:{hyp.id}")
    matching_edges = [e for e in edges if e.source == f"evidence:{evidence.id}"]
    assert len(matching_edges) == 1
    assert matching_edges[0].relation_type == "supports"
    assert matching_edges[0].weight == evidence.confidence_score

    # 3. Test evaluation against contradicting evidence
    new_confidence_contradict = kernel.hypotheses.evaluate(
        hypothesis_id=hyp.id,
        evidence_id=evidence.id,
        is_supporting=False,
        learning_rate=0.20
    )
    # prior = 0.585. ev_conf = 0.85. lr = 0.20
    # expected new = prior - prior * ev_conf * lr = 0.585 - 0.585 * 0.85 * 0.20 = 0.48555
    assert abs(new_confidence_contradict - 0.48555) < 0.001
    
    # 4. Test validation threshold promotion
    # Elevar a confiança para >= 0.85
    # prior = 0.48555. is_supporting = True, lr = 0.90
    new_high_confidence = kernel.hypotheses.evaluate(
        hypothesis_id=hyp.id,
        evidence_id=evidence.id,
        is_supporting=True,
        learning_rate=0.90
    )
    updated_hyp_high = kernel.hypotheses.get(hyp.id)
    assert updated_hyp_high.confidence_score >= 0.85
    assert updated_hyp_high.status == "Validated"

    # 5. Test promotion to experiment
    exp_id = kernel.hypotheses.promote(hyp.id)
    assert exp_id == f"EXP-HYP-{hyp.id}"

    # Verify connection in graph: experiment -> hypothesis via "tests"
    exp_edges = kernel.repo.get_edges_from(f"experiment:{exp_id}")
    tests_edges = [e for e in exp_edges if e.target == f"hypothesis:{hyp.id}"]
    assert len(tests_edges) == 1
    assert tests_edges[0].relation_type == "tests"
