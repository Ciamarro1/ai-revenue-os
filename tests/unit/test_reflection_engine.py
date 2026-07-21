import pytest
import sqlite3
from src.core.kernel import CognitiveKernel
from src.core.cognition.models import Belief, Reflection, Lesson
from src.revenue_os.analytics.database import ExperimentDatabase

@pytest.fixture
def in_memory_db():
    db = ExperimentDatabase(":memory:")
    # Aplica migrações
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

def test_reflection_engine_lifecycle(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)
    
    # 1. Preparar crença e hipótese no DB
    belief = kernel.beliefs.repo.save_belief(Belief(statement="Audience engages with dark styles", confidence_score=0.60))
    hyp = kernel.hypotheses.create("Visual dark style increases retention", initial_confidence=0.50)
    
    # 2. Inserir experimento e métricas no DB para simular um teste concluído com baixo CTR
    exp_id = "EXP-REFL-MOCK"
    with in_memory_db._get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO experiments (experiment_id, hypothesis_id, status, market_segment, published_at)
            VALUES (?, ?, 'Completed', 'lifestyle', '2026-07-19T00:00:00Z')
        """, (exp_id, hyp.id))
        
        c.execute("""
            INSERT INTO metrics (experiment_id, impressions, ctr_percent, conversion_count, reward_score)
            VALUES (?, ?, ?, ?, ?)
        """, (exp_id, 1000, 0.8, 2, 0.15))
        conn.commit()

    # 3. Gerar a reflexão pós-experimento
    reflection = kernel.reflections.generate(experiment_id=exp_id, related_belief_id=belief.id)
    
    assert reflection.id is not None
    assert reflection.experiment_id == exp_id
    assert "Gancho visual ineficaz" in reflection.probable_cause
    assert reflection.confidence_delta == 0.0 # prior=0.50, current=0.50 (não recalibrado no teste síncrono)
    
    # Verificar metadados Bayesianos
    explanation = reflection.bayesian_explanation
    assert explanation["prior"] == 0.50
    assert explanation["posterior"] == 0.50
    assert "likelihood" in explanation
    
    # 4. Verificar persistência
    fetched_ref = kernel.reflections.get(reflection.id)
    assert fetched_ref is not None
    assert fetched_ref.probable_cause == reflection.probable_cause
    
    refs = kernel.reflections.list_by_experiment(exp_id)
    assert len(refs) == 1
    assert refs[0].id == reflection.id

    # 5. Verificar lições extraídas
    lessons = kernel.reflections.get_lessons_for_reflection(reflection.id)
    assert len(lessons) > 0
    # Como o CTR foi baixo (0.8%), o extractor deve identificar falha na retenção de cliques
    assert any("Falha na retenção de cliques" in l.pattern_detected for l in lessons)
    assert any("Aumentar contraste do texto" in l.actionable_insight for l in lessons)

    all_lessons = kernel.reflections.list_all_lessons()
    assert len(all_lessons) >= len(lessons)

    # 6. Verificar o Evidence Graph
    # Nó da reflexão deve estar no grafo
    node_ref = kernel.repo.get_node(f"reflection:{reflection.id}")
    assert node_ref is not None
    assert node_ref.type == "reflection"
    
    # Nó da lição deve estar no grafo
    node_lesson = kernel.repo.get_node(f"lesson:{lessons[0].id}")
    assert node_lesson is not None
    assert node_lesson.type == "lesson"
    
    # Aresta do Experimento para a Reflexão ("explains")
    edges_from_exp = kernel.repo.get_edges_from(f"experiment:{exp_id}")
    explains_edges = [e for e in edges_from_exp if e.relation_type == "explains" and e.target == f"reflection:{reflection.id}"]
    assert len(explains_edges) == 1

    # Aresta da Reflexão para a Hipótese ("analyzes")
    edges_from_ref = kernel.repo.get_edges_from(f"reflection:{reflection.id}")
    analyzes_edges = [e for e in edges_from_ref if e.relation_type == "analyzes" and e.target == f"hypothesis:{hyp.id}"]
    assert len(analyzes_edges) == 1

    # Aresta da Lição para a Crença ("refines")
    edges_from_lesson = kernel.repo.get_edges_from(f"lesson:{lessons[0].id}")
    refines_edges = [e for e in edges_from_lesson if e.relation_type == "refines" and e.target == f"belief:{belief.id}"]
    assert len(refines_edges) == 1
