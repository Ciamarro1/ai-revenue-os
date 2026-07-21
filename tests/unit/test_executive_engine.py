import pytest
import sqlite3
from src.core.kernel import CognitiveKernel
from src.core.cognition.models import Action, Objective, Plan, PlanStep
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

def test_executive_engine_lifecycle(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)
    
    # 1. Preparar Objetivo e PlanStep
    obj = kernel.planning.create_objective(description="Test target", target_metric="CTR")
    hyp = kernel.hypotheses.create(statement="Test hyp", initial_confidence=0.5)
    with in_memory_db._get_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE hypotheses SET metric_target = 'CTR', status = 'Proposed' WHERE id = ?", (hyp.id,))
        conn.commit()
        
    plans = kernel.planning.generate_plans(obj.id)
    plan = plans[0]
    steps = kernel.planning.get_plan_steps(plan.id)
    step = steps[0]

    # 2. Criar Ação a partir do Step
    action = kernel.executive.create_action(step.id)
    assert action.id is not None
    assert action.status == "Pending"

    # Verificar aresta no Grafo
    node_action = kernel.repo.get_node(f"action:{action.id}")
    assert node_action is not None
    edges_action = kernel.repo.get_edges_from(f"action:{action.id}")
    assert any(e.relation_type == "executes" and e.target == f"plan_step:{step.id}" for e in edges_action)

    # 3. Executar Ação (Sucesso)
    called_count = 0
    def success_logic():
        nonlocal called_count
        called_count += 1

    res = kernel.executive.execute(action.id, success_logic)
    assert res is True
    assert called_count == 1
    
    # Verificar status atualizado e log de histórico
    updated_action = kernel.executive.get_action(action.id)
    assert updated_action.status == "Completed"
    
    history = kernel.executive.get_execution_history(action.id)
    assert len(history) >= 2
    assert history[0].status == "Completed"

    # Verificar que uma observação foi emitida de volta
    edges_from_obs = kernel.repo.get_edges_to(f"action:{action.id}")
    assert any(e.relation_type == "verifies" and e.source.startswith("observation:") for e in edges_from_obs)

    # 4. Idempotency Guard: Reexecutar não chama o callback de novo
    res_retry = kernel.executive.execute(action.id, success_logic)
    assert res_retry is True
    assert called_count == 1 # Chamadas não mudaram

def test_executive_dependencies(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)
    
    # Criar duas ações
    obj = kernel.planning.create_objective(description="Test target", target_metric="CTR")
    plan = kernel.planning.repository.save_plan(Plan(objective_id=obj.id, statement="Test plan"))
    step1 = kernel.planning.repository.save_plan_step(PlanStep(plan_id=plan.id, step_number=1, action_description="Step 1"))
    step2 = kernel.planning.repository.save_plan_step(PlanStep(plan_id=plan.id, step_number=2, action_description="Step 2"))

    action_a = kernel.executive.create_action(step1.id)
    action_b = kernel.executive.create_action(step2.id)

    # B depende de A
    kernel.executive.add_dependency(action_b.id, action_a.id)

    # Tenta executar B (deve pausar porque A não foi concluído)
    res_b = kernel.executive.execute(action_b.id)
    assert res_b is False
    assert kernel.executive.get_action(action_b.id).status == "Paused"

    # Concluir A
    res_a = kernel.executive.execute(action_a.id)
    assert res_a is True

    # Tenta executar B de novo (deve rodar com sucesso agora)
    res_b_retry = kernel.executive.execute(action_b.id)
    assert res_b_retry is True
    assert kernel.executive.get_action(action_b.id).status == "Completed"

def test_executive_retry_limit(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)
    
    obj = kernel.planning.create_objective(description="Test target", target_metric="CTR")
    plan = kernel.planning.repository.save_plan(Plan(objective_id=obj.id, statement="Test plan"))
    step = kernel.planning.repository.save_plan_step(PlanStep(plan_id=plan.id, step_number=1, action_description="Step"))
    action = kernel.executive.create_action(step.id)

    # Configura limite baixo de retries
    with in_memory_db._get_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE actions SET max_retries = 2 WHERE id = ?", (action.id,))
        conn.commit()

    def failing_logic():
        raise RuntimeError("Erro temporário de conexão")

    # Tentativa 1 (Falha -> volta para Pending)
    res1 = kernel.executive.execute(action.id, failing_logic)
    assert res1 is False
    action_state = kernel.executive.get_action(action.id)
    assert action_state.status == "Pending"
    assert action_state.retry_count == 1

    # Tentativa 2 (Falha -> status final Failed)
    res2 = kernel.executive.execute(action.id, failing_logic)
    assert res2 is False
    action_state = kernel.executive.get_action(action.id)
    assert action_state.status == "Failed"
    assert action_state.retry_count == 2
