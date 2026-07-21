import os
import pytest
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path

from src.core.cognition.models import Belief, Evidence
from src.core.cognition.repository import CognitiveRepository
from src.core.cognition.belief_manager import BeliefManager
from src.core.cognition.evidence_engine import EvidenceEngine
from src.revenue_os.analytics.database import ExperimentDatabase

@pytest.fixture
def temp_docs_dir(tmp_path):
    """Cria um diretório temporário para testes de documentação."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "cognition").mkdir()
    return docs_dir

@pytest.fixture
def in_memory_db():
    """Inicializa um banco relacional em memória para testes."""
    return ExperimentDatabase(":memory:")

def test_calculate_quality_score_math(in_memory_db):
    repo = CognitiveRepository(db=in_memory_db, docs_dir="")
    engine = EvidenceEngine(repo)
    
    # 1. Teste de amostra grande vs amostra pequena
    now_str = datetime.now(timezone.utc).isoformat() + "Z"
    
    small_sample = engine.calculate_quality_score(
        sample_size=10,
        statistical_confidence=0.95,
        reliability=1.0,
        timestamp_str=now_str
    )
    # log10(11)/5.0 = 1.04/5 = 0.208
    assert abs(small_sample["sample_size_factor"] - 0.208) < 0.01
    
    large_sample = engine.calculate_quality_score(
        sample_size=100000,
        statistical_confidence=0.95,
        reliability=1.0,
        timestamp_str=now_str
    )
    assert large_sample["sample_size_factor"] == 1.0

    # 2. Teste de decaimento de recência (15 dias de atraso -> recency_factor = 0.50)
    past_date = datetime.now(timezone.utc) - timedelta(days=15)
    past_str = past_date.isoformat() + "Z"
    decayed = engine.calculate_quality_score(
        sample_size=10000,
        statistical_confidence=0.95,
        reliability=1.0,
        timestamp_str=past_str
    )
    assert abs(decayed["recency_factor"] - 0.50) < 0.05
    
    # 3. Teste de decaimento severo (45 dias de atraso -> clamped a 0.10)
    old_date = datetime.now(timezone.utc) - timedelta(days=45)
    old_str = old_date.isoformat() + "Z"
    decayed_max = engine.calculate_quality_score(
        sample_size=10000,
        statistical_confidence=0.95,
        reliability=1.0,
        timestamp_str=old_str
    )
    assert decayed_max["recency_factor"] == 0.10

def test_evaluate_evidence_persistence_and_sync(temp_docs_dir, in_memory_db):
    repo = CognitiveRepository(db=in_memory_db, docs_dir="")
    repo.docs_path = temp_docs_dir
    engine = EvidenceEngine(repo)
    
    # Cria hipótese fictícia
    conn = in_memory_db._get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO hypotheses (statement, metric_target) VALUES ('finance clicks', 'ctr')")
    hyp_id = c.lastrowid
    conn.commit()
    
    # Cria evidência no banco
    e = Evidence(
        hypothesis_id=hyp_id,
        experiment_id="EXP-999",
        claim="Finance video CTR was 5.1%",
        confidence_score=0.95,
        impact="Positivo"
    )
    repo.register_evidence(e)
    assert e.id is not None
    
    # Avalia evidência
    quality_score = engine.evaluate_evidence(
        evidence_id=e.id,
        sample_size=500,
        statistical_confidence=0.95,
        reliability=0.80
    )
    
    assert quality_score > 0.0
    
    # Verifica se a qualidade foi persistida
    with repo._get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT sample_size, confidence, reliability, quality_score
            FROM evidence_quality
            WHERE evidence_id = ?
        """, (e.id,))
        row = c.fetchone()
        assert row is not None
        assert row[0] == 500
        assert row[1] == 0.95
        assert row[2] == 0.80
        assert abs(row[3] - quality_score) < 0.0001
        
    # Verifica se o Markdown evidence.md mostra o escore de qualidade
    markdown_file = temp_docs_dir / "cognition" / "evidence.md"
    assert markdown_file.exists()
    
    with open(markdown_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Qualidade da Evidência" in content
        assert "Escore Geral" in content
        assert "Tamanho da Amostra: 500" in content

def test_belief_manager_quality_score_integration(temp_docs_dir, in_memory_db):
    repo = CognitiveRepository(db=in_memory_db, docs_dir="")
    repo.docs_path = temp_docs_dir
    manager = BeliefManager(repo)
    
    # Cria duas crenças idênticas para comparação
    b1 = Belief(statement="Niche A works", confidence_score=0.50)
    repo.save_belief(b1)
    
    b2 = Belief(statement="Niche B works", confidence_score=0.50)
    repo.save_belief(b2)
    
    # 1. Evolução com alta qualidade (Q = 1.0)
    new_conf_high = manager.evolve_belief(
        belief_id=b1.id,
        evidence_confidence=0.90,
        impact="Positivo",
        reason="Evidência robusta",
        learning_rate=0.10,
        quality_score=1.0
    )
    
    # 2. Evolução com baixa qualidade (Q = 0.20)
    new_conf_low = manager.evolve_belief(
        belief_id=b2.id,
        evidence_confidence=0.90,
        impact="Positivo",
        reason="Evidência fraca",
        learning_rate=0.10,
        quality_score=0.20
    )
    
    # A crença com evidência robusta deve ter evoluído muito mais
    # Q = 1.0 -> 0.50 + 0.10 * 0.50 * 0.90 = 0.545
    # Q = 0.20 -> 0.50 + (0.10 * 0.20) * 0.50 * 0.90 = 0.50 + 0.02 * 0.45 = 0.509
    assert abs(new_conf_high - 0.545) < 0.001
    assert abs(new_conf_low - 0.509) < 0.001
    assert new_conf_high > new_conf_low

