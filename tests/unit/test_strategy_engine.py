import pytest
import sqlite3
from src.core.kernel import CognitiveKernel
from src.core.cognition.models import Goal, Strategy, Constraint, Opportunity, Objective
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

def test_strategy_engine_lifecycle(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)
    
    # 1. Preparar Objetivo de Negócio no Planning
    objective = kernel.planning.create_objective(
        description="Aumentar tráfego Pinterest",
        target_metric="CTR"
    )

    # 2. Cadastrar Goal estratégico de longo prazo
    goal = kernel.strategy.create_goal(
        name="Liderar tráfego do nicho travel",
        target_metric="CTR",
        target_value=3.5,
        current_value=1.2
    )
    assert goal.id is not None
    assert goal.status == "Active"

    # 3. Adicionar restrição e oportunidade
    constraint = kernel.strategy.create_constraint(
        description="Budget mensal de anúncios",
        constraint_type="Budget",
        value=500.0
    )
    assert constraint.id is not None

    opp = kernel.strategy.create_opportunity(
        name="Pinterest Video Pins",
        description="Explorar ganchos visuais nos primeiros 3s de vídeo",
        expected_revenue=200.0,
        expected_learning=0.6
    )
    assert opp.id is not None
    assert opp.score > 200.0

    # 4. Cadastrar Estratégia candidata vinculada ao Goal
    strat = kernel.strategy.create_strategy(
        goal_id=goal.id,
        statement="Publicar infográficos minimalistas em alta frequência",
        expected_revenue=150.0,
        expected_learning=0.6,
        risk=2.0,
        cost=1.0
    )
    assert strat.id is not None
    assert strat.status == "Proposed"

    # 5. Otimizar Estratégias (Multi-Objetivo)
    optimized_strats = kernel.strategy.optimize(goal.id)
    assert len(optimized_strats) == 1
    active_strat = optimized_strats[0]
    assert active_strat.status == "Active"
    # Benefícios = 150 + 60 + 15 + 20 = 245.0
    # Custos/Riscos = risk(2.0) + cost(1.0) + time(1.0) = 4.0
    # Score = 245.0 / 4.0 = 61.25
    assert abs(active_strat.priority_score - 61.25) < 0.01

    # 6. Validar integração com Planning Engine
    # Um plano tático correspondente deve ter sido criado
    plans = kernel.planning.get_plans()
    assert len(plans) == 1
    assert "derivado da estratégia" in plans[0].statement
    assert plans[0].priority_score == active_strat.priority_score

    # 7. Validar Grafo de Evidências
    node_goal = kernel.repo.get_node(f"goal:{goal.id}")
    node_strat = kernel.repo.get_node(f"strategy:{active_strat.id}")
    
    assert node_goal is not None
    assert node_strat is not None

    # Aresta: Estratégia -> Goal ("pursues")
    edges_strat = kernel.repo.get_edges_from(f"strategy:{active_strat.id}")
    assert any(e.relation_type == "pursues" and e.target == f"goal:{goal.id}" for e in edges_strat)

    # Aresta: Estratégia -> Plano ("refines")
    assert any(e.relation_type == "refines" and e.target == f"plan:{plans[0].id}" for e in edges_strat)

    # Aresta: Goal -> Objetivo ("targets")
    edges_goal = kernel.repo.get_edges_from(f"goal:{goal.id}")
    assert any(e.relation_type == "targets" and e.target == f"objective:{objective.id}" for e in edges_goal)
