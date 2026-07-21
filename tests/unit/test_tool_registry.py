import pytest
import sqlite3
from src.core.kernel import CognitiveKernel
from src.core.cognition.models import Provider, Tool, Capability, ToolExecution, Action, PlanStep, Plan
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

def test_tool_registry_benchmarking_and_lifecycle(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)

    # 1. Registrar Provedor e Capacidade
    provider_rep = Provider(name="Replicate", description="Run models")
    cap_image = Capability(name="Generate Image", description="Generates visual assets")

    # 2. Registrar Ferramenta 1 (Flux v1)
    tool_flux = Tool(
        name="Flux v1",
        version="1.0.0",
        provider_id=0, # Atualizado no registro
        capabilities="Generate Image",
        cost=0.02,
        latency=5.0,
        reliability=0.95,
        health_score=1.0
    )
    saved_flux = kernel.tools.register(provider_rep, tool_flux, cap_image)
    assert saved_flux.id is not None
    assert saved_flux.provider_id is not None

    # Registrar Ferramenta 2 (Gemini Image API) sob Provedor 2
    provider_google = Provider(name="Google GenAI", description="Google model provider")
    tool_gemini = Tool(
        name="Gemini Image API",
        version="2.0.0",
        provider_id=0,
        capabilities="Generate Image",
        cost=0.05,
        latency=2.0,
        reliability=0.99,
        health_score=1.0
    )
    saved_gemini = kernel.tools.register(provider_google, tool_gemini, cap_image)
    
    # 3. Testar Descoberta e Otimização Multi-Provedor (Multi-Objective Selection)
    # Flux Utility = (0.95 * 1.0) / (0.02 * 5.0) = 9.5
    # Gemini Utility = (0.99 * 1.0) / (0.05 * 2.0) = 9.9
    # Esperado: Gemini Image API selecionado
    optimal_tool = kernel.tools.select_tool("Generate Image")
    assert optimal_tool is not None
    assert optimal_tool.name == "Gemini Image API"

    # 4. Registrar uma Ação para associar a execução da ferramenta no grafo
    obj = kernel.planning.create_objective(description="Marketing Campaign", target_metric="CTR")
    plan = kernel.planning.repository.save_plan(Plan(objective_id=obj.id, statement="Test plan"))
    step = kernel.planning.repository.save_plan_step(PlanStep(plan_id=plan.id, step_number=1, action_description="Step"))
    action = kernel.executive.create_action(step.id)

    # 5. Executar a Ferramenta com Telemetria (Sucesso)
    mock_run_count = 0
    def mock_logic():
        nonlocal mock_run_count
        mock_run_count += 1
        return "image_path_success.png"

    exec_res = kernel.tools.execute(
        tool_id=saved_gemini.id,
        action_id=action.id,
        execution_fn=mock_logic,
        cost=0.05
    )

    assert exec_res["success"] is True
    assert exec_res["result"] == "image_path_success.png"
    assert mock_run_count == 1
    assert exec_res["latency"] > 0.0

    # Verificar atualização de métricas agregadas da ferramenta (confiabilidade e latência móveis)
    updated_tool = kernel.tools.repository.get_tool(saved_gemini.id)
    assert updated_tool.health_score == 1.0 # Permanece excelente
    assert updated_tool.reliability > 0.90 # Atualizado de forma móvel

    # Verificar que o Grafo de Evidências registrou a execução e sua rastreabilidade
    exec_history = kernel.tools.get_tool_executions(saved_gemini.id)
    assert len(exec_history) == 1
    exec_log = exec_history[0]
    
    node_exec = kernel.repo.get_node(f"tool_execution:{exec_log.id}")
    assert node_exec is not None
    
    # Aresta: Execução -> Ferramenta ("runs")
    edges_exec = kernel.repo.get_edges_from(f"tool_execution:{exec_log.id}")
    assert any(e.relation_type == "runs" and e.target == f"tool:{saved_gemini.id}" for e in edges_exec)

    # Aresta: Ação -> Execução ("invokes")
    edges_action = kernel.repo.get_edges_from(f"action:{action.id}")
    assert any(e.relation_type == "invokes" and e.target == f"tool_execution:{exec_log.id}" for e in edges_action)

    # 6. Executar com Falha (Testar decaimento de Health e Confiabilidade)
    def mock_fail_logic():
        raise RuntimeError("Model rate limit exceeded")

    with pytest.raises(RuntimeError):
        kernel.tools.execute(
            tool_id=saved_gemini.id,
            action_id=action.id,
            execution_fn=mock_fail_logic,
            cost=0.05
        )

    updated_tool_fail = kernel.tools.repository.get_tool(saved_gemini.id)
    assert updated_tool_fail.health_score < 1.0 # Decaiu após erro!
    assert updated_tool_fail.reliability < 0.99 # Decaiu após erro!
