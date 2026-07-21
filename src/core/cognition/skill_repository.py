import sqlite3
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from src.core.cognition.models import Skill, SkillStep, SkillExecution, SkillStepExecution

class SkillRepository:
    """
    SkillRepository (Sprint 7.2).
    Persiste e recupera habilidades de negócio (Skills), passos e execuções no SQLite.
    """
    def __init__(self, db: Any):
        self.db = db

    def _get_conn(self):
        return self.db._get_conn()

    # ==========================================
    # Operações de Habilidades (Skills)
    # ==========================================
    def save_skill(self, skill: Skill) -> Skill:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if skill.id is None:
                # Inserir Skill
                c.execute("""
                    INSERT INTO skills (name, description, objective, input_schema, output_schema, constraints, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (skill.name, skill.description, skill.objective, skill.input_schema, skill.output_schema, skill.constraints, skill.metadata, ts))
                skill.id = c.lastrowid
                skill.created_at = ts
            else:
                # Atualizar Skill
                c.execute("""
                    UPDATE skills SET name = ?, description = ?, objective = ?, input_schema = ?, output_schema = ?, constraints = ?, metadata = ?
                    WHERE id = ?
                """, (skill.name, skill.description, skill.objective, skill.input_schema, skill.output_schema, skill.constraints, skill.metadata, skill.id))
                # Deletar passos antigos para reinserir
                c.execute("DELETE FROM skill_steps WHERE skill_id = ?", (skill.id,))

            # Inserir Passos (Steps)
            for s in skill.steps:
                c.execute("""
                    INSERT INTO skill_steps (skill_id, step_order, capability_required, tool_required, input_mapping, output_mapping, retry_policy)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (skill.id, s.step_order, s.capability_required, s.tool_required, s.input_mapping, s.output_mapping, s.retry_policy))
                s.id = c.lastrowid
                s.skill_id = skill.id

            conn.commit()
        return skill

    def get_skill(self, skill_id: int) -> Optional[Skill]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, name, description, objective, input_schema, output_schema, constraints, metadata, created_at
                FROM skills WHERE id = ?
            """, (skill_id,))
            r = c.fetchone()
            if not r:
                return None

            skill = Skill(
                id=r[0], name=r[1], description=r[2], objective=r[3],
                input_schema=r[4], output_schema=r[5], constraints=r[6],
                metadata=r[7], created_at=r[8], steps=[]
            )

            # Buscar passos
            c.execute("""
                SELECT id, skill_id, step_order, capability_required, tool_required, input_mapping, output_mapping, retry_policy
                FROM skill_steps WHERE skill_id = ? ORDER BY step_order ASC
            """, (skill_id,))
            step_rows = c.fetchall()
            skill.steps = [
                SkillStep(
                    id=sr[0], skill_id=sr[1], step_order=sr[2],
                    capability_required=sr[3], tool_required=sr[4],
                    input_mapping=sr[5], output_mapping=sr[6], retry_policy=sr[7]
                )
                for sr in step_rows
            ]
            return skill

    def get_skill_by_name(self, name: str) -> Optional[Skill]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM skills WHERE name = ?", (name,))
            row = c.fetchone()
            if row:
                return self.get_skill(row[0])
        return None

    def get_skills(self) -> List[Skill]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM skills ORDER BY id DESC")
            rows = c.fetchall()
            return [self.get_skill(r[0]) for r in rows]

    # ==========================================
    # Operações de Execução (SkillExecution & Steps)
    # ==========================================
    def save_skill_execution(self, exec_data: SkillExecution) -> SkillExecution:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if exec_data.id is None:
                c.execute("""
                    INSERT INTO skill_executions (skill_id, status, input_data, output_data, error_message, started_at, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (exec_data.skill_id, exec_data.status, exec_data.input_data, exec_data.output_data, exec_data.error_message, ts, exec_data.completed_at))
                exec_data.id = c.lastrowid
                exec_data.started_at = ts
            else:
                c.execute("""
                    UPDATE skill_executions SET status = ?, input_data = ?, output_data = ?, error_message = ?, completed_at = ?
                    WHERE id = ?
                """, (exec_data.status, exec_data.input_data, exec_data.output_data, exec_data.error_message, exec_data.completed_at, exec_data.id))
            conn.commit()
        return exec_data

    def get_skill_execution(self, exec_id: int) -> Optional[SkillExecution]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, skill_id, status, input_data, output_data, error_message, started_at, completed_at
                FROM skill_executions WHERE id = ?
            """, (exec_id,))
            r = c.fetchone()
            if r:
                return SkillExecution(id=r[0], skill_id=r[1], status=r[2], input_data=r[3], output_data=r[4], error_message=r[5], started_at=r[6], completed_at=r[7])
        return None

    def save_skill_step_execution(self, step_exec: SkillStepExecution) -> SkillStepExecution:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if step_exec.id is None:
                c.execute("""
                    INSERT INTO skill_step_executions (skill_execution_id, step_id, status, tool_execution_id, latency, error_message, executed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (step_exec.skill_execution_id, step_exec.step_id, step_exec.status, step_exec.tool_execution_id, step_exec.latency, step_exec.error_message, ts))
                step_exec.id = c.lastrowid
                step_exec.executed_at = ts
            else:
                c.execute("""
                    UPDATE skill_step_executions SET status = ?, tool_execution_id = ?, latency = ?, error_message = ?
                    WHERE id = ?
                """, (step_exec.status, step_exec.tool_execution_id, step_exec.latency, step_exec.error_message, step_exec.id))
            conn.commit()
        return step_exec

    def get_skill_step_executions(self, skill_execution_id: int) -> List[SkillStepExecution]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, skill_execution_id, step_id, status, tool_execution_id, latency, error_message, executed_at
                FROM skill_step_executions WHERE skill_execution_id = ? ORDER BY id ASC
            """, (skill_execution_id,))
            rows = c.fetchall()
            return [
                SkillStepExecution(
                    id=r[0], skill_execution_id=r[1], step_id=r[2], status=r[3],
                    tool_execution_id=r[4], latency=r[5], error_message=r[6], executed_at=r[7]
                )
                for r in rows
            ]
