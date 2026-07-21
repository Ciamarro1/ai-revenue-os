import pytest
import sqlite3
from src.core.kernel import CognitiveKernel
from src.core.cognition.models import Observation, Belief, GraphNode, GraphEdge
from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.hypothesis_registry import HypothesisRegistry
from src.reality.base import CapabilityRegistry, Publisher, MetricsProvider, CanonicalMetrics, ResearchProvider
from src.reality.research.schemas import ResearchReport
from src.factory.base import FactoryRegistry, VideoGenerator
from src.factory.schemas import GeneratedAsset
from src.services.experiment_runner import ExperimentRunner, ExperimentState
from src.ports.observation_adapter import ObservationAdapter
from src.adapters.pinterest.observation_adapter import PinterestObservationAdapter
from src.integrations.pinterest.analytics import AnalyticsManager
from src.services.decision_queue import DecisionQueue
from src.services.observation_scheduler import ObservationScheduler
from src.services.learning_loop import LearningLoop
from unittest.mock import MagicMock, patch

@pytest.fixture
def in_memory_db():
    db = ExperimentDatabase(":memory:")
    from pathlib import Path
    mig_dir = Path(__file__).parent.parent.parent / "migrations"
    if mig_dir.exists():
        sql_files = sorted([f for f in mig_dir.iterdir() if f.suffix == ".sql"])
        with db._get_conn() as conn:
            c = conn.cursor()
            for sql_file in sql_files:
                with open(sql_file, "r", encoding="utf-8") as f:
                    script = f.read()
                try:
                    c.executescript(script)
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower() and "already exists" not in str(e).lower():
                        raise e
            conn.commit()
    return db

def test_complete_learning_loop_cycle(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)
    
    # 1. Preparar crença e hipótese
    belief = kernel.beliefs.repo.save_belief(Belief(statement="Niche conversion is high", confidence_score=0.50))
    hyp = kernel.hypotheses.create("Pinterest saturates in niche", initial_confidence=0.50)
    
    # 2. Configurar mocks para o ExperimentRunner
    reality_registry = CapabilityRegistry()
    
    mock_researcher = MagicMock(spec=ResearchProvider)
    mock_researcher.provider_name = "mock_openmanus"
    mock_researcher.confidence_score = 1.0
    mock_researcher.execute_research.return_value = ResearchReport(
        query="tendencias emergentes rentaveis",
        provider="mock_openmanus",
        sources=["fake_source"],
        trends=[{"topic": "mock_trend", "category": "mock_cat", "suggested_hook": "mock_hook"}],
        competitors=[],
        keywords=[]
    )
    reality_registry.register_research_provider(mock_researcher)
    
    mock_publisher = MagicMock(spec=Publisher)
    mock_publisher.provider_name = "api"
    mock_publisher.confidence_score = 1.0
    mock_publisher.publish_image.return_value = MagicMock(
        content_id="pin_real_loop_123",
        platform="pinterest",
        status="published",
        url="http://pinterest.com/pin/pin_real_loop_123"
    )
    reality_registry.register_publisher(mock_publisher)
    
    factory_registry = FactoryRegistry()
    mock_generator = MagicMock(spec=VideoGenerator)
    mock_generator.provider_name = "mock_factory"
    mock_generator.generate.return_value = GeneratedAsset(
        path="mock_video.mp4",
        duration=45,
        resolution="1080x1920",
        provider="mock_factory",
        confidence=1.0
    )
    factory_registry.register_video_generator(mock_generator)
    
    mock_metrics = MagicMock(spec=MetricsProvider)
    mock_metrics.provider_name = "api"
    mock_metrics.confidence_score = 1.0
    mock_metrics.get_metrics.return_value = CanonicalMetrics(
        impressions=1200,
        outbound_clicks=100,
        saves=50
    )
    reality_registry.register_metrics_provider(mock_metrics)
    
    # Injetar o Runner
    with patch('src.services.experiment_runner.VideoQualityGate.check_quality', return_value=True):
        runner = ExperimentRunner(
            db=in_memory_db,
            registry=HypothesisRegistry(in_memory_db),
            reality_registry=reality_registry,
            factory_registry=factory_registry
        )
        
        # 3. Inicializar DecisionQueue
        queue = DecisionQueue(in_memory_db)
        exp_id = "EXP-LOOP-TEST"
        queue.enqueue(exp_id, hyp.id, priority=5.0)
        
        # Verificar estado Pending
        pending_list = queue.get_pending()
        assert len(pending_list) == 1
        assert pending_list[0]["experiment_id"] == exp_id
        assert pending_list[0]["status"] == "Pending"
        
        # 4. Configurar ObservationAdapter e Scheduler
        # Criar mock do AnalyticsManager
        mock_analytics = MagicMock(spec=AnalyticsManager)
        mock_analytics.get_metrics.return_value = CanonicalMetrics(
            impressions=1500,
            outbound_clicks=200,
            saves=60
        )
        
        pinterest_adapter = PinterestObservationAdapter(mock_analytics)
        scheduler = ObservationScheduler(kernel, [pinterest_adapter])
        
        # 5. Criar LearningLoop
        loop = LearningLoop(
            kernel=kernel,
            runner=runner,
            queue=queue,
            scheduler=scheduler
        )
        
        # Executar uma iteração do loop científico
        res = loop.execute_loop_iteration(related_belief_id=belief.id)
        
        assert res["status"] == "success"
        assert res["experiment_id"] == exp_id
        assert res["observations_count"] > 0
        
        # 6. Verificações pós-execução
        
        # A. Status do Experimento atualizou para Completed
        with in_memory_db._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT status FROM experiments WHERE experiment_id = ?", (exp_id,))
            assert c.fetchone()[0] == "Completed"
            
        # B. Novas Observações foram salvas no banco
        obs_list = kernel.repo.get_observations()
        assert len(obs_list) > 0
        assert any(o.metric_name == "Impressions" and o.value == 1500.0 for o in obs_list)
        
        # C. Evidência foi gerada e associada ao experimento correto
        evidences = kernel.evidence.get_by_experiment(exp_id)
        assert len(evidences) > 0
        latest_ev = evidences[0]
        assert latest_ev.experiment_id == exp_id
        
        # D. Confiança da crença foi modificada no Belief Engine
        updated_belief = kernel.beliefs.get_belief(belief.id)
        assert updated_belief.confidence_score != 0.50
        
        # E. Confiança da Hipótese foi revisada de forma Bayesiana no Hypothesis Engine
        updated_hyp = kernel.hypotheses.get(hyp.id)
        assert updated_hyp.confidence_score != 0.50
        
        # F. Atualizações automáticas do Grafo de Evidências
        # Deve ter conexões de traceabilidade para todos os nós criados
        node_exp = kernel.repo.get_node(f"experiment:{exp_id}")
        assert node_exp is not None
        
        edges = kernel.repo.get_edges_from(f"experiment:{exp_id}")
        # Deve ter conexões com a hipótese ("tests") e a observação ("triggers")
        assert len(edges) >= 1
        
        # Verificando se há aresta para a observação ou crença
        targets = [e.target for e in edges]
        assert any(t.startswith("observation:") for t in targets)
