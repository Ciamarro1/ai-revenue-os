import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from src.core.cognition.models import Objective, Plan, PlanStep

class PlanningRepository:
    """
    PlanningRepository (Sprint 6.5).
    Persiste e recupera objetivos, planos e passos de planejamento científico no SQLite.
    """
    def __init__(self, db: Any):
        self.db = db

    def _get_conn(self):
        return self.db._get_conn()

    # ==========================================
    # Operações de Objetivos (Objectives)
    # ==========================================
    def save_objective(self, objective: Objective) -> Objective:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if objective.id is None:
                c.execute("""
                    INSERT INTO objectives (description, target_metric, status, created_at)
                    VALUES (?, ?, ?, ?)
                """, (objective.description, objective.target_metric, objective.status, ts))
                objective.id = c.lastrowid
                objective.created_at = ts
            else:
                c.execute("""
                    UPDATE objectives SET description = ?, target_metric = ?, status = ?
                    WHERE id = ?
                """, (objective.description, objective.target_metric, objective.status, objective.id))
            conn.commit()
        return objective

    def get_objective(self, objective_id: int) -> Optional[Objective]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, description, target_metric, status, created_at
                FROM objectives WHERE id = ?
            """, (objective_id,))
            r = c.fetchone()
            if r:
                return Objective(id=r[0], description=r[1], target_metric=r[2], status=r[3], created_at=r[4])
        return None

    def get_objectives(self) -> List[Objective]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, description, target_metric, status, created_at
                FROM objectives ORDER BY id DESC
            """)
            rows = c.fetchall()
            return [
                Objective(id=r[0], description=r[1], target_metric=r[2], status=r[3], created_at=r[4])
                for r in rows
            ]

    # ==========================================
    # Operações de Planos (Plans)
    # ==========================================
    def save_plan(self, plan: Plan) -> Plan:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if plan.id is None:
                c.execute("""
                    INSERT INTO plans (objective_id, statement, status, priority_score, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (plan.objective_id, plan.statement, plan.status, plan.priority_score, ts, ts))
                plan.id = c.lastrowid
                plan.created_at = ts
                plan.updated_at = ts
            else:
                c.execute("""
                    UPDATE plans SET objective_id = ?, statement = ?, status = ?, priority_score = ?, updated_at = ?
                    WHERE id = ?
                """, (plan.objective_id, plan.statement, plan.status, plan.priority_score, ts, plan.id))
                plan.updated_at = ts
            conn.commit()
        return plan

    def get_plan(self, plan_id: int) -> Optional[Plan]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, objective_id, statement, status, priority_score, created_at, updated_at
                FROM plans WHERE id = ?
            """, (plan_id,))
            r = c.fetchone()
            if r:
                return Plan(id=r[0], objective_id=r[1], statement=r[2], status=r[3], priority_score=r[4], created_at=r[5], updated_at=r[6])
        return None

    def get_plans_by_objective(self, objective_id: int) -> List[Plan]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, objective_id, statement, status, priority_score, created_at, updated_at
                FROM plans WHERE objective_id = ? ORDER BY priority_score DESC
            """, (objective_id,))
            rows = c.fetchall()
            return [
                Plan(id=r[0], objective_id=r[1], statement=r[2], status=r[3], priority_score=r[4], created_at=r[5], updated_at=r[6])
                for r in rows
            ]

    def get_plans(self) -> List[Plan]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, objective_id, statement, status, priority_score, created_at, updated_at
                FROM plans ORDER BY priority_score DESC
            """)
            rows = c.fetchall()
            return [
                Plan(id=r[0], objective_id=r[1], statement=r[2], status=r[3], priority_score=r[4], created_at=r[5], updated_at=r[6])
                for r in rows
            ]

    # ==========================================
    # Operações de Passos (PlanSteps)
    # ==========================================
    def save_plan_step(self, step: PlanStep) -> PlanStep:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if step.id is None:
                c.execute("""
                    INSERT INTO plan_steps (plan_id, step_number, action_description, experiment_id, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (step.plan_id, step.step_number, step.action_description, step.experiment_id, step.status, ts))
                step.id = c.lastrowid
                step.created_at = ts
            else:
                c.execute("""
                    UPDATE plan_steps SET plan_id = ?, step_number = ?, action_description = ?, experiment_id = ?, status = ?
                    WHERE id = ?
                """, (step.plan_id, step.step_number, step.action_description, step.experiment_id, step.status, step.id))
            conn.commit()
        return step

    def get_plan_steps(self, plan_id: int) -> List[PlanStep]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, plan_id, step_number, action_description, experiment_id, status, created_at
                FROM plan_steps WHERE plan_id = ? ORDER BY step_number ASC
            """, (plan_id,))
            rows = c.fetchall()
            return [
                PlanStep(id=r[0], plan_id=r[1], step_number=r[2], action_description=r[3], experiment_id=r[4], status=r[5], created_at=r[6])
                for r in rows
            ]

    def get_plan_step(self, step_id: int) -> Optional[PlanStep]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, plan_id, step_number, action_description, experiment_id, status, created_at
                FROM plan_steps WHERE id = ?
            """, (step_id,))
            r = c.fetchone()
            if r:
                return PlanStep(id=r[0], plan_id=r[1], step_number=r[2], action_description=r[3], experiment_id=r[4], status=r[5], created_at=r[6])
        return None

    def update_plan_step_status(self, step_id: int, status: str) -> None:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("UPDATE plan_steps SET status = ? WHERE id = ?", (status, step_id))
            conn.commit()
