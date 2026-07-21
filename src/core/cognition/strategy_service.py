import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from src.core.cognition.models import Goal, Strategy, Constraint, Opportunity, Plan, GraphNode, GraphEdge
from src.core.cognition.strategy_repository import StrategyRepository
from src.core.cognition.planning_repository import PlanningRepository
from src.core.cognition.repository import CognitiveRepository

class StrategyService:
    """
    StrategyService (Sprint 6.6).
    Otimiza a seleção de estratégias baseando-se em objetivos multi-objetivo,
    calculando retorno esperado (revenue, learning, confidence, info gain) vs custos/riscos.
    """
    def __init__(
        self,
        strategy_repo: StrategyRepository,
        planning_repo: PlanningRepository,
        cognitive_repo: CognitiveRepository,
        db: Any
    ):
        self.strategy_repo = strategy_repo
        self.planning_repo = planning_repo
        self.cognitive_repo = cognitive_repo
        self.db = db

    def optimize_strategies(self, goal_id: int) -> List[Strategy]:
        goal = self.strategy_repo.get_goal(goal_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} não encontrado.")

        # Registrar nó do Goal no Grafo
        goal_node_id = f"goal:{goal.id}"
        self.cognitive_repo.save_node(GraphNode(
            id=goal_node_id,
            type="goal",
            label=f"Goal: {goal.name} (Target: {goal.target_value})"
        ))

        # Aresta: Conecta o Goal com o Objetivo correspondente se houver
        with self.db._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM objectives WHERE target_metric = ? LIMIT 1", (goal.target_metric,))
            obj_row = c.fetchone()
            if obj_row:
                self.cognitive_repo.save_edge(GraphEdge(
                    source=goal_node_id,
                    target=f"objective:{obj_row[0]}",
                    relation_type="targets",
                    weight=1.0
                ))

        # 1. Recuperar estratégias propostas para este Goal
        strategies = self.strategy_repo.get_strategies_by_goal(goal_id)
        if not strategies:
            # Se não houver estratégias pré-cadastradas, criamos uma default baseada no Goal
            default_strat = Strategy(
                goal_id=goal_id,
                statement=f"Estratégia para maximizar {goal.target_metric} via variantes otimizadas",
                expected_revenue=100.0,
                expected_learning=0.8,
                risk=1.5,
                cost=2.0
            )
            strategies = [self.strategy_repo.save_strategy(default_strat)]

        # 2. Otimização Multi-objetivo
        optimized_list = []
        for strat in strategies:
            # expected_confidence_gain = 0.5 * (1.0 - (1.0 / max(1.0, strat.risk)))
            expected_confidence_gain = 0.3
            
            # expected_info_gain = 1.0 - (1.0 / max(1.0, strat.expected_learning))
            expected_info_gain = 0.4
            
            # Multi-objective Utility score:
            # Maximize: Expected Revenue, Expected Learning, Expected Confidence Gain, Expected Info Gain
            # Minimize: Risk, Cost, Time (assumido default = 1.0)
            benefits = strat.expected_revenue + (strat.expected_learning * 100.0) + (expected_confidence_gain * 50.0) + (expected_info_gain * 50.0)
            costs_risks = max(0.1, strat.risk + strat.cost + 1.0) # 1.0 representa o tempo operacional
            
            priority_score = benefits / costs_risks
            strat.priority_score = round(priority_score, 2)
            strat.status = "Active"
            saved_strat = self.strategy_repo.save_strategy(strat)

            # Registrar nó da estratégia no Grafo
            strat_node_id = f"strategy:{saved_strat.id}"
            self.cognitive_repo.save_node(GraphNode(
                id=strat_node_id,
                type="strategy",
                label=saved_strat.statement[:50]
            ))

            # Aresta: Estratégia -> Goal ("pursues")
            self.cognitive_repo.save_edge(GraphEdge(
                source=strat_node_id,
                target=goal_node_id,
                relation_type="pursues",
                weight=1.0
            ))

            # 3. Integração com Planning Engine (gerar ou refinar Plano)
            # Verifica se há plano associado ao objetivo da métrica
            if obj_row:
                objective_id = obj_row[0]
                plan_statement = f"Plano derivado da estratégia: {saved_strat.statement}"
                
                # Criar Plano associado
                plan = Plan(
                    objective_id=objective_id,
                    statement=plan_statement,
                    status="Draft",
                    priority_score=saved_strat.priority_score
                )
                saved_plan = self.planning_repo.save_plan(plan)

                # Registrar aresta no Grafo: Estratégia -> Plano ("refines")
                self.cognitive_repo.save_edge(GraphEdge(
                    source=strat_node_id,
                    target=f"plan:{saved_plan.id}",
                    relation_type="refines",
                    weight=1.0
                ))

            optimized_list.append(saved_strat)

        return optimized_list
