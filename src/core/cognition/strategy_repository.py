import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from src.core.cognition.models import Goal, Strategy, Constraint, Opportunity

class StrategyRepository:
    """
    StrategyRepository (Sprint 6.6).
    Persiste e recupera objetivos, estratégias, restrições e oportunidades no SQLite.
    """
    def __init__(self, db: Any):
        self.db = db

    def _get_conn(self):
        return self.db._get_conn()

    # ==========================================
    # Operações de Objetivos de Longo Prazo (Goals)
    # ==========================================
    def save_goal(self, goal: Goal) -> Goal:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if goal.id is None:
                c.execute("""
                    INSERT INTO goals (name, target_metric, target_value, current_value, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (goal.name, goal.target_metric, goal.target_value, goal.current_value, goal.status, ts))
                goal.id = c.lastrowid
                goal.created_at = ts
            else:
                c.execute("""
                    UPDATE goals SET name = ?, target_metric = ?, target_value = ?, current_value = ?, status = ?
                    WHERE id = ?
                """, (goal.name, goal.target_metric, goal.target_value, goal.current_value, goal.status, goal.id))
            conn.commit()
        return goal

    def get_goal(self, goal_id: int) -> Optional[Goal]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, name, target_metric, target_value, current_value, status, created_at
                FROM goals WHERE id = ?
            """, (goal_id,))
            r = c.fetchone()
            if r:
                return Goal(id=r[0], name=r[1], target_metric=r[2], target_value=r[3], current_value=r[4], status=r[5], created_at=r[6])
        return None

    def get_goals(self) -> List[Goal]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, name, target_metric, target_value, current_value, status, created_at
                FROM goals ORDER BY id DESC
            """)
            rows = c.fetchall()
            return [
                Goal(id=r[0], name=r[1], target_metric=r[2], target_value=r[3], current_value=r[4], status=r[5], created_at=r[6])
                for r in rows
            ]

    # ==========================================
    # Operações de Estratégias (Strategies)
    # ==========================================
    def save_strategy(self, strategy: Strategy) -> Strategy:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if strategy.id is None:
                c.execute("""
                    INSERT INTO strategies (goal_id, statement, expected_revenue, expected_learning, risk, cost, status, priority_score, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (strategy.goal_id, strategy.statement, strategy.expected_revenue, strategy.expected_learning, strategy.risk, strategy.cost, strategy.status, strategy.priority_score, ts, ts))
                strategy.id = c.lastrowid
                strategy.created_at = ts
                strategy.updated_at = ts
            else:
                c.execute("""
                    UPDATE strategies SET goal_id = ?, statement = ?, expected_revenue = ?, expected_learning = ?, risk = ?, cost = ?, status = ?, priority_score = ?, updated_at = ?
                    WHERE id = ?
                """, (strategy.goal_id, strategy.statement, strategy.expected_revenue, strategy.expected_learning, strategy.risk, strategy.cost, strategy.status, strategy.priority_score, ts, strategy.id))
                strategy.updated_at = ts
            conn.commit()
        return strategy

    def get_strategy(self, strategy_id: int) -> Optional[Strategy]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, goal_id, statement, expected_revenue, expected_learning, risk, cost, status, priority_score, created_at, updated_at
                FROM strategies WHERE id = ?
            """, (strategy_id,))
            r = c.fetchone()
            if r:
                return Strategy(id=r[0], goal_id=r[1], statement=r[2], expected_revenue=r[3], expected_learning=r[4], risk=r[5], cost=r[6], status=r[7], priority_score=r[8], created_at=r[9], updated_at=r[10])
        return None

    def get_strategies_by_goal(self, goal_id: int) -> List[Strategy]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, goal_id, statement, expected_revenue, expected_learning, risk, cost, status, priority_score, created_at, updated_at
                FROM strategies WHERE goal_id = ? ORDER BY priority_score DESC
            """, (goal_id,))
            rows = c.fetchall()
            return [
                Strategy(id=r[0], goal_id=r[1], statement=r[2], expected_revenue=r[3], expected_learning=r[4], risk=r[5], cost=r[6], status=r[7], priority_score=r[8], created_at=r[9], updated_at=r[10])
                for r in rows
            ]

    def get_strategies(self) -> List[Strategy]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, goal_id, statement, expected_revenue, expected_learning, risk, cost, status, priority_score, created_at, updated_at
                FROM strategies ORDER BY priority_score DESC
            """)
            rows = c.fetchall()
            return [
                Strategy(id=r[0], goal_id=r[1], statement=r[2], expected_revenue=r[3], expected_learning=r[4], risk=r[5], cost=r[6], status=r[7], priority_score=r[8], created_at=r[9], updated_at=r[10])
                for r in rows
            ]

    # ==========================================
    # Restrições (Constraints)
    # ==========================================
    def save_constraint(self, constraint: Constraint) -> Constraint:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if constraint.id is None:
                c.execute("""
                    INSERT INTO constraints (description, constraint_type, value, created_at)
                    VALUES (?, ?, ?, ?)
                """, (constraint.description, constraint.constraint_type, constraint.value, ts))
                constraint.id = c.lastrowid
                constraint.created_at = ts
            else:
                c.execute("""
                    UPDATE constraints SET description = ?, constraint_type = ?, value = ?
                    WHERE id = ?
                """, (constraint.description, constraint.constraint_type, constraint.value, constraint.id))
            conn.commit()
        return constraint

    def get_constraints(self) -> List[Constraint]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, description, constraint_type, value, created_at
                FROM constraints ORDER BY id DESC
            """)
            rows = c.fetchall()
            return [
                Constraint(id=r[0], description=r[1], constraint_type=r[2], value=r[3], created_at=r[4])
                for r in rows
            ]

    # ==========================================
    # Oportunidades (Opportunities)
    # ==========================================
    def save_opportunity(self, opp: Opportunity) -> Opportunity:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if opp.id is None:
                c.execute("""
                    INSERT INTO opportunities (name, description, expected_revenue, expected_learning, score, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (opp.name, opp.description, opp.expected_revenue, opp.expected_learning, opp.score, ts))
                opp.id = c.lastrowid
                opp.created_at = ts
            else:
                c.execute("""
                    UPDATE opportunities SET name = ?, description = ?, expected_revenue = ?, expected_learning = ?, score = ?
                    WHERE id = ?
                """, (opp.name, opp.description, opp.expected_revenue, opp.expected_learning, opp.score, opp.id))
            conn.commit()
        return opp

    def get_opportunities(self) -> List[Opportunity]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, name, description, expected_revenue, expected_learning, score, created_at
                FROM opportunities ORDER BY score DESC
            """)
            rows = c.fetchall()
            return [
                Opportunity(id=r[0], name=r[1], description=r[2], expected_revenue=r[3], expected_learning=r[4], score=r[5], created_at=r[6])
                for r in rows
            ]
