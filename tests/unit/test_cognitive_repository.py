import os
import pytest
from pathlib import Path

from src.core.cognition.models import Belief, Evidence, Learning
from src.core.cognition.repository import CognitiveRepository
from src.revenue_os.analytics.database import ExperimentDatabase

@pytest.fixture
def temp_docs_dir(tmp_path):
    """Cria um diretório temporário para testes de documentação."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    
    # Cria as subpastas necessárias
    (docs_dir / "knowledge").mkdir()
    (docs_dir / "cognition").mkdir()
    
    return docs_dir

@pytest.fixture
def in_memory_db():
    """Inicializa um banco relacional em memória para testes."""
    return ExperimentDatabase(":memory:")

def test_beliefs_persistence_and_sync(temp_docs_dir, in_memory_db):
    repo = CognitiveRepository(db=in_memory_db, docs_dir="")
    repo.docs_path = temp_docs_dir
    
    # 1. Cria crença
    b = Belief(statement="Pinterest organic has 3x range", confidence_score=0.85)
    saved = repo.save_belief(b)
    
    assert saved.id is not None
    assert saved.updated_at is not None
    
    # 2. Verifica se a crença está no banco
    beliefs = repo.get_beliefs()
    assert len(beliefs) == 1
    assert beliefs[0].statement == "Pinterest organic has 3x range"
    assert beliefs[0].confidence_score == 0.85
    
    # 3. Verifica se o Markdown beliefs.md foi gerado corretamente
    markdown_file = temp_docs_dir / "cognition" / "beliefs.md"
    assert markdown_file.exists()
    
    with open(markdown_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Pinterest organic has 3x range** (Confiança Atual: 85%)" in content

def test_evidence_persistence_and_sync(temp_docs_dir, in_memory_db):
    repo = CognitiveRepository(db=in_memory_db, docs_dir="")
    repo.docs_path = temp_docs_dir
    
    # 1. Cria hipótese fictícia para foreign key
    conn = in_memory_db._get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO hypotheses (statement, metric_target) VALUES ('test statement', 'ctr')")
    hyp_id = c.lastrowid
    conn.commit()

    # 2. Registra evidência
    e = Evidence(
        hypothesis_id=hyp_id,
        experiment_id="EXP-001",
        claim="Click rate of Variant B was 4.5%",
        confidence_score=0.95,
        impact="Positivo",
        narrative="Variant B enriches and outperforms the core CTR baseline."
    )
    saved = repo.register_evidence(e)
    assert saved.id is not None
    assert saved.timestamp is not None
    
    # 3. Verifica se a evidência está no banco
    evidences = repo.get_evidence()
    assert len(evidences) == 1
    assert evidences[0].claim == "Click rate of Variant B was 4.5%"
    assert evidences[0].experiment_id == "EXP-001"
    
    # 4. Verifica se o Markdown evidence.md foi gerado
    markdown_file = temp_docs_dir / "cognition" / "evidence.md"
    assert markdown_file.exists()
    
    with open(markdown_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Click rate of Variant B was 4.5%" in content
        assert "Experimento**: EXP-001" in content
        assert "Impacto**: Positivo" in content
        assert "Variant B enriches and outperforms the core CTR baseline." in content

def test_learnings_persistence_and_sync(temp_docs_dir, in_memory_db):
    repo = CognitiveRepository(db=in_memory_db, docs_dir="")
    repo.docs_path = temp_docs_dir
    
    # 1. Registra aprendizado
    l = Learning(
        experiment_id="EXP-002",
        pattern="Visual Spam Filter",
        severity="HIGH",
        description="Duplicate images are blocked perceptual hashes hamming distance <= 10."
    )
    saved = repo.log_learning(l)
    assert saved.id is not None
    assert saved.created_at is not None
    
    # 2. Verifica se o aprendizado está no banco
    learnings = repo.get_learnings()
    assert len(learnings) == 1
    assert learnings[0].pattern == "Visual Spam Filter"
    assert learnings[0].severity == "HIGH"
    
    # 3. Verifica se o Markdown repository_learning.md foi gerado e inclui os aprendizados estáticos + dinâmicos
    markdown_file = temp_docs_dir / "knowledge" / "repository_learning.md"
    assert markdown_file.exists()
    
    with open(markdown_file, "r", encoding="utf-8") as f:
        content = f.read()
        # Verifica aprendizados estáticos nativos
        assert "Consistência Visual do Playwright" in content
        assert "Degradação de Trust Score e Cooldowns" in content
        # Verifica aprendizado dinâmico do loop automático
        assert "Visual Spam Filter" in content
        assert "Duplicate images are blocked perceptual hashes hamming distance <= 10." in content
        assert "Experimento: EXP-002" in content

