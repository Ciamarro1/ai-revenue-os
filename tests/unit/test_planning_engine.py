import pytest
import sqlite3
from src.core.kernel import CognitiveKernel
from src.core.cognition.models import Objective, Plan, PlanStep, Belief, Reflection, Lesson
from src.revenue_os.analytics.database import ExperimentDatabase
from src.services.decision_queue import DecisionQueue

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

def test_planning_engine_lifecycle(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)
    
    # 1. Preparar Objetivo de Negócio
    objective = kernel.planning.create_objective(
        description="Aumentar tráfego e cliques no Pinterest",
        target_metric="CTR"
    )
    assert objective.id is not None
    assert objective.status == "Active"
    
    # 2. Cadastrar Hipótese propondo solução para esse objetivo
    hyp = kernel.hypotheses.create(
        statement="Imagens minimalistas têm CTR superior",
        initial_confidence=0.50
    )
    # Atualizar a hipótese para a métrica de teste 'CTR' e categoria 'travel'
    with in_memory_db._get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE hypotheses SET metric_target = 'CTR', category = 'travel', status = 'Proposed' 
            WHERE id = ?
        """, (hyp.id,))
        conn.commit()

    # 3. Criar uma Lição Aprendida histórica no segmento 'travel' para influenciar a priorização
    # Criamos o experimento do qual a lição se originou
    with in_memory_db._get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO experiments (experiment_id, hypothesis_id, status, market_segment, published_at)
            VALUES ('EXP-PREV-FAIL', ?, 'Completed', 'travel', '2026-07-19T00:00:00Z')
        """, (hyp.id,))
        conn.commit()
        
    ref = kernel.reflections.generate("EXP-PREV-FAIL", related_belief_id=1) # crença id 1 fictícia
    
    # 4. Gerar Planos de Experimentos
    plans = kernel.planning.generate_plans(objective.id)
    
    assert len(plans) == 1
    plan = plans[0]
    assert plan.objective_id == objective.id
    # priority_score = confidence (0.50) + 0.15 * count(lessons=1) = 0.65
    assert abs(plan.priority_score - 0.65) < 0.001
    
    # Verificar os passos do plano gerados
    steps = kernel.planning.get_plan_steps(plan.id)
    assert len(steps) == 1
    step = steps[0]
    assert step.status == "Pending"
    assert "A/B" in step.action_description

    # 5. Integrar com o DecisionQueue (Enqueue do passo do plano)
    queue = DecisionQueue(in_memory_db)
    exp_id = kernel.planning.enqueue_step(step.id, queue)
    
    assert exp_id == f"EXP-STEP-{step.id}"
    
    # Re-fetch step e verificar status
    updated_step = kernel.planning.repository.get_plan_step(step.id)
    assert updated_step.status == "Enqueued"
    assert updated_step.experiment_id == exp_id
    
    # Verificar que o experimento foi enfileirado na DecisionQueue com o status 'Pending' e prioridade do plano
    pending_experiments = queue.get_pending()
    assert len(pending_experiments) == 1
    assert pending_experiments[0]["experiment_id"] == exp_id
    assert pending_experiments[0]["priority"] == plan.priority_score
    assert pending_experiments[0]["status"] == "Pending"

    # 6. Validar rastreabilidade no Evidence Graph
    # Nós de objetivo, plano e passo de plano registrados
    node_obj = kernel.repo.get_node(f"objective:{objective.id}")
    node_plan = kernel.repo.get_node(f"plan:{plan.id}")
    node_step = kernel.repo.get_node(f"plan_step:{step.id}")
    
    assert node_obj is not None
    assert node_plan is not None
    assert node_step is not None
    
    # Aresta: Objetivo -> Hipótese ("targets")
    edges_obj = kernel.repo.get_edges_from(f"objective:{objective.id}")
    assert any(e.relation_type == "targets" and e.target == f"hypothesis:{hyp.id}" for e in edges_obj)
    
    # Aresta: Plano -> Objetivo ("pursues")
    edges_plan = kernel.repo.get_edges_from(f"plan:{plan.id}")
    assert any(e.relation_type == "pursues" and e.target == f"objective:{objective.id}" for e in edges_plan)
    
    # Aresta: Passo -> Plano ("belongs_to")
    edges_step = kernel.repo.get_edges_from(f"plan_step:{step.id}")
    assert any(e.relation_type == "belongs_to" and e.target == f"plan:{plan.id}" for e in edges_step)

    # Aresta: Passo -> Experimento ("generates")
    assert any(e.relation_type == "generates" and e.target == f"experiment:{exp_id}" for e in edges_step)
