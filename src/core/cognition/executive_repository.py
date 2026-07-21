import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from src.core.cognition.models import Action, ActionDependency, ExecutionHistory

class ExecutiveRepository:
    """
    ExecutiveRepository (Sprint 7.0).
    Persiste e recupera ações de execução, dependências e históricos no SQLite.
    """
    def __init__(self, db: Any):
        self.db = db

    def _get_conn(self):
        return self.db._get_conn()

    # ==========================================
    # Operações de Ações (Actions)
    # ==========================================
    def save_action(self, action: Action) -> Action:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if action.id is None:
                c.execute("""
                    INSERT INTO actions (step_id, name, status, retry_count, max_retries, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (action.step_id, action.name, action.status, action.retry_count, action.max_retries, ts, ts))
                action.id = c.lastrowid
                action.created_at = ts
                action.updated_at = ts
            else:
                c.execute("""
                    UPDATE actions SET step_id = ?, name = ?, status = ?, retry_count = ?, max_retries = ?, updated_at = ?
                    WHERE id = ?
                """, (action.step_id, action.name, action.status, action.retry_count, action.max_retries, ts, action.id))
                action.updated_at = ts
            conn.commit()
        return action

    def get_action(self, action_id: int) -> Optional[Action]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, step_id, name, status, retry_count, max_retries, created_at, updated_at
                FROM actions WHERE id = ?
            """, (action_id,))
            r = c.fetchone()
            if r:
                return Action(id=r[0], step_id=r[1], name=r[2], status=r[3], retry_count=r[4], max_retries=r[5], created_at=r[6], updated_at=r[7])
        return None

    def get_actions(self) -> List[Action]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, step_id, name, status, retry_count, max_retries, created_at, updated_at
                FROM actions ORDER BY id DESC
            """)
            rows = c.fetchall()
            return [
                Action(id=r[0], step_id=r[1], name=r[2], status=r[3], retry_count=r[4], max_retries=r[5], created_at=r[6], updated_at=r[7])
                for r in rows
            ]

    # ==========================================
    # Dependências (ActionDependencies)
    # ==========================================
    def add_dependency(self, action_id: int, depends_on_action_id: int) -> None:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO action_dependencies (action_id, depends_on_action_id)
                VALUES (?, ?)
            """, (action_id, depends_on_action_id))
            conn.commit()

    def get_dependencies_for_action(self, action_id: int) -> List[int]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT depends_on_action_id FROM action_dependencies
                WHERE action_id = ?
            """, (action_id,))
            rows = c.fetchall()
            return [r[0] for r in rows]

    # ==========================================
    # Histórico de Execução (ExecutionHistory)
    # ==========================================
    def log_execution(self, action_id: int, status: str, error_message: Optional[str] = None) -> ExecutionHistory:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO execution_history (action_id, status, error_message, executed_at)
                VALUES (?, ?, ?, ?)
            """, (action_id, status, error_message, ts))
            history_id = c.lastrowid
            conn.commit()
        return ExecutionHistory(id=history_id, action_id=action_id, status=status, error_message=error_message, executed_at=ts)

    def get_execution_history(self, action_id: int) -> List[ExecutionHistory]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, action_id, status, error_message, executed_at
                FROM execution_history WHERE action_id = ? ORDER BY id DESC
            """, (action_id,))
            rows = c.fetchall()
            return [
                ExecutionHistory(id=r[0], action_id=r[1], status=r[2], error_message=r[3], executed_at=r[4])
                for r in rows
            ]
