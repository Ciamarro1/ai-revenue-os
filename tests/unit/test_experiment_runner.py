import os
import pytest
import tempfile
import sqlite3
from unittest.mock import MagicMock, patch

from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.hypothesis_registry import HypothesisRegistry
from src.reality.base import CapabilityRegistry, Publisher, MetricsProvider, PublishedContent, CanonicalMetrics, ResearchProvider
from src.reality.research.schemas import ResearchReport
from src.services.experiment_runner import ExperimentRunner, ExperimentState
from src.factory.base import FactoryRegistry, VideoGenerator
from src.factory.schemas import GeneratedAsset

@pytest.fixture
def temp_db():
    # Injeta banco de dados em memória
    db = ExperimentDatabase(":memory:")
    
    # Aplica migrações necessárias para a consistência lógica (ex: system_state, decisions)
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
            
    yield db
    # Limpa conexões se restarem
    if hasattr(db, "conn") and db.conn:
        db.conn.close()

def test_hypothesis_registry_lifecycle(temp_db):
    registry = HypothesisRegistry(temp_db)
    
    # 1. Registro
    h_id = registry.register_hypothesis(
        statement="A curiosidade negativa melhora a retenção.",
        category="lifestyle",
        metric_target="retention_3s"
    )
    assert h_id > 0
    
    # Registro duplicado retorna o mesmo ID
    h_id_dup = registry.register_hypothesis(
        statement="A curiosidade negativa melhora a retenção.",
        category="lifestyle",
        metric_target="retention_3s"
    )
    assert h_id_dup == h_id

    # 2. Leitura
    hypo = registry.get_hypothesis(h_id)
    assert hypo["statement"] == "A curiosidade negativa melhora a retenção."
    assert hypo["status"] == "testing"
    assert hypo["confidence_score"] == 0.50
    assert hypo["experiments_count"] == 0

    # 3. Evolução Cíclica - Validada (confiança sobe)
    registry.update_hypothesis_stats(h_id, outcome=True)
    hypo = registry.get_hypothesis(h_id)
    assert hypo["experiments_count"] == 1
    assert hypo["confidence_score"] == 0.60
    assert hypo["status"] == "testing"

    registry.update_hypothesis_stats(h_id, outcome=True)
    registry.update_hypothesis_stats(h_id, outcome=True) # 0.80 -> validated
    hypo = registry.get_hypothesis(h_id)
    assert hypo["confidence_score"] == 0.80
    assert hypo["status"] == "validated"

    # 4. Evolução Cíclica - Rejeitada (confiança cai)
    h_id_rejected = registry.register_hypothesis(
        statement="Hooks de piadas bobas melhoram CTR de finanças.",
        category="finance",
        metric_target="ctr"
    )
    
    registry.update_hypothesis_stats(h_id_rejected, outcome=False)
    registry.update_hypothesis_stats(h_id_rejected, outcome=False)
    registry.update_hypothesis_stats(h_id_rejected, outcome=False) # 0.20 -> rejected
    hypo_rej = registry.get_hypothesis(h_id_rejected)
    assert hypo_rej["confidence_score"] == 0.20
    assert hypo_rej["status"] == "rejected"

def test_experiment_runner_complete_cycle(temp_db):
    registry = HypothesisRegistry(temp_db)
    
    reality_registry = CapabilityRegistry()
    
    # Mock do ResearchProvider
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
    
    # Mock do Publisher
    mock_publisher = MagicMock(spec=Publisher)
    mock_publisher.provider_name = "api"
    mock_publisher.confidence_score = 1.0
    mock_publisher.publish_image.return_value = PublishedContent(
        content_id="pin_mock_456",
        platform="pinterest",
        status="published",
        url="http://pinterest.com/pin/pin_mock_456"
    )
    reality_registry.register_publisher(mock_publisher)
    
    # Mock da Factory
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
    
    # Mock do MetricsProvider
    mock_metrics = MagicMock(spec=MetricsProvider)
    mock_metrics.provider_name = "api"
    mock_metrics.confidence_score = 1.0
    mock_metrics.get_metrics.return_value = CanonicalMetrics(
        impressions=1000,
        outbound_clicks=50,
        saves=25
    )
    reality_registry.register_metrics_provider(mock_metrics)
    
    # Patch VideoQualityGate
    with patch('src.services.experiment_runner.VideoQualityGate.check_quality', return_value=True):
        runner = ExperimentRunner(
            db=temp_db,
            registry=registry,
            reality_registry=reality_registry,
            factory_registry=factory_registry
        )
        
        # Executa o ciclo operacional científico completo
        result = runner.run_cycle()
        
    assert result["status"] == "success"
    assert result["final_state"] == ExperimentState.CALIBRATED.value
    assert result["experiment_id"].startswith("EXP-")
    
    # Verifica inserções no SQLite
    with temp_db._get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM experiments")
        assert cursor.fetchone()[0] == 1
        
        cursor.execute("SELECT COUNT(*) FROM metrics")
        assert cursor.fetchone()[0] == 1

def test_variant_alternation(temp_db):
    registry = HypothesisRegistry(temp_db)
    reality_registry = CapabilityRegistry()
    
    # Mock do ResearchProvider
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
    
    # Mock do Publisher
    mock_publisher = MagicMock(spec=Publisher)
    mock_publisher.provider_name = "api"
    mock_publisher.confidence_score = 1.0
    mock_publisher.publish_image.return_value = PublishedContent(
        content_id="pin_mock_111",
        platform="pinterest",
        status="published",
        url="http://pinterest.com/pin/111"
    )
    reality_registry.register_publisher(mock_publisher)
    
    # Mock da Factory
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
    
    # Mock do MetricsProvider
    mock_metrics = MagicMock(spec=MetricsProvider)
    mock_metrics.provider_name = "api"
    mock_metrics.confidence_score = 1.0
    mock_metrics.get_metrics.return_value = CanonicalMetrics(impressions=1000, outbound_clicks=50, saves=25)
    reality_registry.register_metrics_provider(mock_metrics)

    with patch('src.services.experiment_runner.VideoQualityGate.check_quality', return_value=True):
        runner1 = ExperimentRunner(db=temp_db, registry=registry, reality_registry=reality_registry, factory_registry=factory_registry)
        res1 = runner1.run_cycle()
        assert res1["status"] == "success"
        
        # O primeiro deve ser Variante A
        with temp_db._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT variant_id FROM experiments WHERE experiment_id = ?", (res1["experiment_id"],))
            assert c.fetchone()[0] == "A"
            
        runner2 = ExperimentRunner(db=temp_db, registry=registry, reality_registry=reality_registry, factory_registry=factory_registry)
        res2 = runner2.run_cycle()
        assert res2["status"] == "success"
        
        # O segundo sob o mesmo statement deve ser Variante B
        with temp_db._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT variant_id FROM experiments WHERE experiment_id = ?", (res2["experiment_id"],))
            assert c.fetchone()[0] == "B"

def test_safety_policy_budget_limits(temp_db):
    from src.revenue_os.analytics.profile import ExperimentProfile
    registry = HypothesisRegistry(temp_db)
    
    # Mock do profile com limites rigorosos
    mock_profile = MagicMock(spec=ExperimentProfile)
    mock_profile.name = "strict_canary"
    mock_profile.config = {
        "safety_policy": {
            "max_cost_per_day": 1.0,
            "max_daily_posts": 2,
            "max_provider_errors": 5
        }
    }
    
    runner = ExperimentRunner(
        db=temp_db,
        registry=registry,
        reality_registry=CapabilityRegistry(),
        factory_registry=FactoryRegistry(),
        profile=mock_profile
    )
    
    # Injeta gastos simulados excedendo o limite diário no banco
    with temp_db._get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO experiments (experiment_id, variant_id, platform, published_at, generation_cost_usd, status)
            VALUES ('EXP-MOCK-OLD', 'B', 'pinterest', datetime('now'), 1.5, 'PUBLISHED')
        """)
        conn.commit()
        
    # Tenta rodar a checagem de política e deve abortar a execução por ultrapassar orçamento
    with pytest.raises(SystemExit):
        runner._check_safety_policy()

def test_human_override(temp_db):
    registry = HypothesisRegistry(temp_db)
    runner = ExperimentRunner(
        db=temp_db,
        registry=registry,
        reality_registry=CapabilityRegistry(),
        factory_registry=FactoryRegistry()
    )
    
    # Ativa override humano no banco
    temp_db.set_system_state("HUMAN_OVERRIDE", {"active": True, "reason": "Pausa manual de emergência"})
    
    with pytest.raises(SystemExit):
        runner._check_safety_policy()

def test_experiment_identity_and_learning(temp_db):
    import json
    import shutil
    from pathlib import Path
    
    registry = HypothesisRegistry(temp_db)
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
    mock_publisher.publish_image.return_value = PublishedContent(
        content_id="pin_mock_777",
        platform="pinterest",
        status="published",
        url="http://pinterest.com/pin/777"
    )
    reality_registry.register_publisher(mock_publisher)
    
    factory_registry = FactoryRegistry()
    mock_generator = MagicMock(spec=VideoGenerator)
    mock_generator.provider_name = "mock_factory"
    # Cria arquivo temporário fake para o asset.path existir e permitir escrita de bundles
    fd, fake_path = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    
    mock_generator.generate.return_value = GeneratedAsset(
        path=fake_path,
        duration=45,
        resolution="1080x1920",
        provider="mock_factory",
        confidence=1.0
    )
    factory_registry.register_video_generator(mock_generator)
    
    mock_metrics = MagicMock(spec=MetricsProvider)
    mock_metrics.provider_name = "api"
    mock_metrics.confidence_score = 1.0
    mock_metrics.get_metrics.return_value = CanonicalMetrics(impressions=1000, outbound_clicks=50, saves=25)
    reality_registry.register_metrics_provider(mock_metrics)

    with patch('src.services.experiment_runner.VideoQualityGate.check_quality', return_value=True):
        runner = ExperimentRunner(db=temp_db, registry=registry, reality_registry=reality_registry, factory_registry=factory_registry)
        res = runner.run_cycle()
        assert res["status"] == "success"
        
        # Verifica se identity.json foi escrito no bundle
        exp_id = res["experiment_id"]
        exp_dir = Path("experiments") / exp_id
        identity_path = exp_dir / "identity.json"
        assert identity_path.exists()
        
        with open(identity_path, "r") as f:
            identity_data = json.load(f)
            assert identity_data["experiment_id"] == exp_id
            assert "hypothesis_hash" in identity_data
            assert "genome_hash" in identity_data
            assert "prompt_hash" in identity_data
            
        # Verifica se decision.json contem learning_value_score
        decision_path = exp_dir / "decision.json"
        assert decision_path.exists()
        with open(decision_path, "r") as f:
            decision_data = json.load(f)
            assert "learning_value_score" in decision_data
            assert decision_data["learning_value_score"] >= 0.0
            
        # Verifica persistência no DB
        with temp_db._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT learning_value_score FROM experiments WHERE experiment_id = ?", (exp_id,))
            row = c.fetchone()
            assert row[0] is not None
            assert row[0] >= 0.0
            
        # Limpeza
        if exp_dir.exists():
            shutil.rmtree(exp_dir)
        if os.path.exists(fake_path):
            os.remove(fake_path)


