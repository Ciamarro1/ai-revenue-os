import pytest
from src.core.kernel import CognitiveKernel
from src.core.cognition.models import Observation, Belief, GraphNode, GraphEdge
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

def test_evidence_graph_and_traceability(in_memory_db, clean_bus):
    kernel = CognitiveKernel(in_memory_db)
    
    # 1. Registrar crença
    belief_1 = Belief(statement="Pinterest CTR is high", confidence_score=0.5)
    saved_belief = kernel.repo.save_belief(belief_1)
    
    # 2. Processar uma observação associada
    obs = Observation(
        source="pinterest_scraper",
        metric_name="CTR",
        value=2.8,
        raw_data="CTR data payload"
    )
    
    # Executa o pipeline de BeliefService, que insere nós e arestas no grafo
    evidence = kernel.beliefs.process_observation(
        observation=obs,
        related_belief_id=saved_belief.id,
        baseline_value=1.5
    )
    
    # 3. Testar rastreabilidade de Observações para uma Crença
    traces = kernel.repo.trace_observations_for_belief(saved_belief.id)
    assert len(traces) == 1
    assert traces[0].source == "pinterest_scraper"
    assert traces[0].value == 2.8

    # 4. Testar rastreabilidade de Experimentos para uma Crença
    exp_traces = kernel.repo.trace_experiments_for_belief(saved_belief.id)
    assert len(exp_traces) == 1
    assert exp_traces[0] == f"OBS-{traces[0].id}"

    # 5. Criar um nó de Decisão e ligá-lo à Crença no grafo
    decision_node_id = "decision:456"
    kernel.repo.save_node(GraphNode(
        id=decision_node_id,
        type="decision",
        label="Decision to scale Pinterest campaign"
    ))
    
    # Aresta: Crença -> Decisão
    kernel.repo.save_edge(GraphEdge(
        source=f"belief:{saved_belief.id}",
        target=decision_node_id,
        relation_type="triggers"
    ))
    
    # Testar rastreabilidade de Evidências para a Decisão
    # Deve encontrar a evidência que suportou a crença que por sua vez engatilhou a decisão
    evidence_traces = kernel.repo.trace_evidence_for_decision(456)
    assert len(evidence_traces) == 1
    assert evidence_traces[0].id == evidence.id
    assert evidence_traces[0].impact == "positivo"
