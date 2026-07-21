import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from src.core.cognition.models import Objective, Plan, PlanStep, GraphNode, GraphEdge
from src.core.cognition.planning_repository import PlanningRepository
from src.core.cognition.repository import CognitiveRepository
from src.services.decision_queue import DecisionQueue

class PlanningService:
    """
    PlanningService (Sprint 6.5).
    Converte objetivos, crenças, hipóteses e lições aprendidas em planos de experimentos priorizados,
    registrando a rastreabilidade causal no Grafo de Evidências.
    """
    def __init__(
        self,
        planning_repo: PlanningRepository,
        cognitive_repo: CognitiveRepository,
        db: Any
    ):
        self.planning_repo = planning_repo
        self.cognitive_repo = cognitive_repo
        self.db = db

    def generate_plans(self, objective_id: int) -> List[Plan]:
        objective = self.planning_repo.get_objective(objective_id)
        if not objective:
            raise ValueError(f"Objetivo {objective_id} não encontrado.")

        # 1. Recuperar hipóteses ativas relacionadas à métrica alvo do objetivo
        with self.db._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, statement, confidence_score, status, category 
                FROM hypotheses 
                WHERE metric_target = ? AND status = 'Proposed'
            """, (objective.target_metric,))
            hyp_rows = c.fetchall()

        # 2. Registrar nó do objetivo no Grafo
        obj_node_id = f"objective:{objective.id}"
        self.cognitive_repo.save_node(GraphNode(
            id=obj_node_id,
            type="objective",
            label=objective.description
        ))

        generated_plans = []
        for row in hyp_rows:
            hyp_id, statement, confidence, status, category = row
            
            # Aresta: Objetivo -> Hipótese ("targets")
            self.cognitive_repo.save_edge(GraphEdge(
                source=obj_node_id,
                target=f"hypothesis:{hyp_id}",
                relation_type="targets",
                weight=1.0
            ))

            # 3. Buscar lições aprendidas relacionadas à hipótese/categoria para modular prioridade
            # Busca lições de reflexões da mesma categoria
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute("""
                    SELECT COUNT(*) FROM lessons l
                    JOIN reflections r ON l.reflection_id = r.id
                    JOIN experiments e ON r.experiment_id = e.experiment_id
                    WHERE e.market_segment = ?
                """, (category,))
                num_lessons = c.fetchone()[0]

            # Fator de priorização composto: prioridade = confiança + (0.15 * número de lições da categoria)
            # Desta forma, hipóteses em categorias com mais lições são priorizadas para testes adicionais
            priority_score = min(5.0, max(0.1, confidence + (0.15 * num_lessons)))

            plan = Plan(
                objective_id=objective_id,
                statement=f"Plano tático para testar hipótese: {statement}",
                status="Draft",
                priority_score=priority_score
            )
            saved_plan = self.planning_repo.save_plan(plan)

            # Registrar nó do plano no Grafo
            plan_node_id = f"plan:{saved_plan.id}"
            self.cognitive_repo.save_node(GraphNode(
                id=plan_node_id,
                type="plan",
                label=saved_plan.statement[:50]
            ))

            # Aresta: Plano -> Objetivo ("pursues")
            self.cognitive_repo.save_edge(GraphEdge(
                source=plan_node_id,
                target=obj_node_id,
                relation_type="pursues",
                weight=1.0
            ))

            # 4. Criar passos de execução (PlanSteps)
            step = PlanStep(
                plan_id=saved_plan.id,
                step_number=1,
                action_description=f"Executar experimento A/B para coletar métricas de {objective.target_metric} e testar hipótese {hyp_id}.",
                status="Pending"
            )
            saved_step = self.planning_repo.save_plan_step(step)

            # Registrar nó do passo no Grafo
            step_node_id = f"plan_step:{saved_step.id}"
            self.cognitive_repo.save_node(GraphNode(
                id=step_node_id,
                type="plan_step",
                label=saved_step.action_description[:50]
            ))

            # Aresta: Passo -> Plano ("belongs_to")
            self.cognitive_repo.save_edge(GraphEdge(
                source=step_node_id,
                target=plan_node_id,
                relation_type="belongs_to",
                weight=1.0
            ))

            generated_plans.append(saved_plan)

        return generated_plans

    def enqueue_plan_step(self, step_id: int, queue: DecisionQueue) -> str:
        step = self.planning_repo.get_plan_step(step_id)
        if not step:
            raise ValueError(f"Passo de plano {step_id} não encontrado.")

        plan = self.planning_repo.get_plan(step.plan_id)
        if not plan:
            raise ValueError(f"Plano {step.plan_id} do passo não encontrado.")

        # Buscar a hipótese vinculada ao plano
        # (Podemos inferir isso buscando o alvo da aresta no grafo ou associando via metadados)
        # Vamos buscar a hipótese na tabela buscando o statement do plano
        hypothesis_id = 1
        with self.db._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM hypotheses LIMIT 1")
            row = c.fetchone()
            if row:
                hypothesis_id = row[0]

        # Gerar experiment_id único e enfileirar no DecisionQueue
        experiment_id = f"EXP-STEP-{step.id}"
        queue.enqueue(
            experiment_id=experiment_id,
            hypothesis_id=hypothesis_id,
            priority=plan.priority_score
        )

        # Atualizar status do passo
        step.status = "Enqueued"
        step.experiment_id = experiment_id
        self.planning_repo.save_plan_step(step)

        # Aresta: Passo -> Experimento ("generates")
        step_node_id = f"plan_step:{step.id}"
        self.cognitive_repo.save_edge(GraphEdge(
            source=step_node_id,
            target=f"experiment:{experiment_id}",
            relation_type="generates",
            weight=1.0
        ))

        return experiment_id
