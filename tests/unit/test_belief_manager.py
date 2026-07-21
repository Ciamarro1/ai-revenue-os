import os
import pytest
from pathlib import Path

from src.core.cognition.models import Belief
from src.core.cognition.repository import CognitiveRepository
from src.core.cognition.belief_manager import BeliefManager
from src.revenue_os.analytics.database import ExperimentDatabase

@pytest.fixture
def temp_docs_dir(tmp_path):
    """Cria um diretório temporário para testes de documentação."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    
    # Cria as subpastas necessárias
    (docs_dir / "cognition").mkdir()
    
    return docs_dir

@pytest.fixture
def in_memory_db():
    """Inicializa um banco relacional em memória para testes."""
    return ExperimentDatabase(":memory:")

def test_belief_manager_evolution_positive(temp_docs_dir, in_memory_db):
    repo = CognitiveRepository(db=in_memory_db, docs_dir="")
    repo.docs_path = temp_docs_dir
    manager = BeliefManager(repo)
    
    # 1. Cria crença inicial (Confiança: 0.50)
    b = Belief(statement="Finance niche CTR is higher", confidence_score=0.50)
    repo.save_belief(b)
    assert b.id is not None
    
    # 2. Executa evolução positiva
    # Fórmula: new_conf = 0.50 + 0.10 * (1.0 - 0.50) * 0.90 = 0.50 + 0.045 = 0.545
    new_score = manager.evolve_belief(
        belief_id=b.id,
        evidence_confidence=0.90,
        impact="Positivo",
        reason="Campanha EXP-123 validou a hipótese",
        learning_rate=0.10
    )
    
    assert abs(new_score - 0.545) < 0.001
    
    # 3. Verifica se o histórico foi gravado
    with repo._get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT old_confidence, new_confidence, change_reason FROM belief_history WHERE belief_id = ?", (b.id,))
        rows = c.fetchall()
        assert len(rows) == 1
        assert rows[0][0] == 0.50
        assert abs(rows[0][1] - 0.545) < 0.001
        assert rows[0][2] == "Campanha EXP-123 validou a hipótese"

    # 4. Verifica se a trajetória foi escrita no Markdown
    markdown_file = temp_docs_dir / "cognition" / "beliefs.md"
    assert markdown_file.exists()
    
    with open(markdown_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Finance niche CTR is higher" in content
        # 0.545 * 100 = 54.5% -> 54% in markdown due to int()
        assert "Confiança Atual: 54%" in content
        assert "50% ➔ 54%" in content

def test_belief_manager_evolution_negative(temp_docs_dir, in_memory_db):
    repo = CognitiveRepository(db=in_memory_db, docs_dir="")
    repo.docs_path = temp_docs_dir
    manager = BeliefManager(repo)
    
    # 1. Cria crença inicial (Confiança: 0.80)
    b = Belief(statement="lifestyle niche has higher saves", confidence_score=0.80)
    repo.save_belief(b)
    
    # 2. Evolui negativamente
    # Fórmula: new_conf = 0.80 - 0.10 * 0.80 * 0.50 = 0.80 - 0.04 = 0.76
    new_score = manager.evolve_belief(
        belief_id=b.id,
        evidence_confidence=0.50,
        impact="Negativo",
        reason="Campanha EXP-124 obteve CTR pífio",
        learning_rate=0.10
    )
    
    assert abs(new_score - 0.76) < 0.001
    
    # 3. Verifica Markdown
    markdown_file = temp_docs_dir / "cognition" / "beliefs.md"
    with open(markdown_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "lifestyle niche has higher saves" in content
        assert "Confiança Atual: 76%" in content
        assert "80% ➔ 76%" in content

