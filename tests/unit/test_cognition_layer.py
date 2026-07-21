import os
import shutil
from pathlib import Path
import pytest
from src.agents.cognition_layer import RuntimeCognitiveLayer
from src.revenue_os.analytics.database import ExperimentDatabase

@pytest.fixture
def temp_docs_dir(tmp_path):
    """Cria um diretório temporário para testes de documentação."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    
    # Cria as subpastas
    (docs_dir / "runtime").mkdir()
    (docs_dir / "cognition").mkdir()
    
    # Seed de templates básicos
    with open(docs_dir / "runtime" / "current_blockers.md", "w", encoding="utf-8") as f:
        f.write("# CURRENT BLOCKERS\n\n- [ ] [HIGH] Test Blocker: Descrição\n")
        
    with open(docs_dir / "cognition" / "beliefs.md", "w", encoding="utf-8") as f:
        f.write("# SYSTEM BELIEFS\n\n- Test Belief (Confiança: 50%)\n")
        
    return docs_dir

@pytest.fixture
def in_memory_db():
    """Inicializa um banco relacional em memória para testes."""
    return ExperimentDatabase(":memory:")

def test_load_and_add_blockers(temp_docs_dir):
    # Inicializa a camada cognitiva apontando para a pasta temporária
    cog = RuntimeCognitiveLayer(db=None, docs_dir=str(temp_docs_dir.relative_to(temp_docs_dir.parent.parent)))
    cog.docs_path = temp_docs_dir  # Override para garantir caminho absoluto
    
    # 1. Carrega bloqueadores iniciais
    blockers = cog.load_blockers()
    assert len(blockers) == 1
    assert blockers[0]["title"] == "Test Blocker"
    assert blockers[0]["severity"] == "HIGH"
    assert blockers[0]["resolved"] is False

    # 2. Adiciona bloqueador novo
    cog.add_blocker("Second Blocker", "Descrição do segundo", "LOW")
    blockers = cog.load_blockers()
    assert len(blockers) == 2
    assert blockers[1]["title"] == "Second Blocker"
    assert blockers[1]["severity"] == "LOW"
    
    # 3. Resolve bloqueador
    cog.resolve_blocker("Test Blocker")
    blockers = cog.load_blockers()
    assert blockers[0]["resolved"] is True
    assert blockers[1]["resolved"] is False

def test_load_and_add_beliefs(temp_docs_dir):
    cog = RuntimeCognitiveLayer(db=None, docs_dir="")
    cog.docs_path = temp_docs_dir
    
    # 1. Carrega crenças iniciais
    beliefs = cog.load_beliefs()
    assert len(beliefs) == 1
    assert beliefs[0]["statement"] == "Test Belief"
    assert beliefs[0]["confidence_percent"] == 50.0

    # 2. Atualiza confiança de crença existente
    cog.add_belief("Test Belief", 95.0)
    beliefs = cog.load_beliefs()
    assert len(beliefs) == 1
    assert beliefs[0]["confidence_percent"] == 95.0

    # 3. Adiciona crença nova
    cog.add_belief("New Belief", 30.0)
    beliefs = cog.load_beliefs()
    assert len(beliefs) == 2
    assert beliefs[1]["statement"] == "New Belief"
    assert beliefs[1]["confidence_percent"] == 30.0

def test_sync_database_state(temp_docs_dir, in_memory_db):
    cog = RuntimeCognitiveLayer(db=in_memory_db, docs_dir="")
    cog.docs_path = temp_docs_dir
    
    # Insere dados de mock no banco em memória
    conn = in_memory_db._get_conn()
    c = conn.cursor()
    
    # Insere Hipóteses
    c.execute("""
        INSERT INTO hypotheses (statement, metric_target, category, status, confidence_score, experiments_count)
        VALUES ('Ganchos negativos geram mais cliques', 'ctr_percent', 'finance', 'validated', 0.85, 3)
    """)
    c.execute("""
        INSERT INTO hypotheses (statement, metric_target, category, status, confidence_score, experiments_count)
        VALUES ('Imagens geram conversão maior', 'ctr_percent', 'lifestyle', 'testing', 0.50, 1)
    """)
    
    # Insere Experimento
    c.execute("""
        INSERT INTO experiments (experiment_id, hypothesis_id, variant_id, variant_desc, creative_hash, platform, published_at, generation_cost_usd, revenue_usd, status, market_segment)
        VALUES ('EXP-001', 1, 'A', 'Controle', 'hash123', 'pinterest', '2026-07-18', 2.50, 10.00, 'CALIBRATED', 'finance')
    """)
    
    # Insere Métrica associada
    c.execute("""
        INSERT INTO metrics (experiment_id, impressions, ctr_percent, retention_3s_percent, completion_rate_percent, conversion_count, reward_score)
        VALUES ('EXP-001', 1000, 2.50, 45.0, 30.0, 5, 10.0)
    """)
    conn.commit()

    # Roda a sincronização
    cog.sync_database_state()
    
    # 1. Verifica se current_state.md foi atualizado
    current_state_file = temp_docs_dir / "runtime" / "current_state.md"
    assert current_state_file.exists()
    
    with open(current_state_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Total de Experimentos Executados | 1" in content
        assert "Total de Hipóteses Cadastradas | 2" in content
        assert "Hipóteses Validadas | 1" in content
        assert "Hipóteses Rejeitadas | 0" in content
        assert "CTR Médio Geral | 2.50%" in content
        assert "Faturamento Total Acumulado (USD) | $10.00" in content
        assert "Custo de Geração Acumulado (USD) | $2.50" in content
        assert "Margem Geral / ROI | 300.00%" in content
        
    # 2. Verifica se hypotheses.md foi atualizado
    hypotheses_file = temp_docs_dir / "cognition" / "hypotheses.md"
    assert hypotheses_file.exists()
    
    with open(hypotheses_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Ganchos negativos geram mais cliques" in content
        assert "Imagens geram conversão maior" in content
        assert "85.0%" in content
        assert "50.0%" in content
