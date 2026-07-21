import sqlite3
import json
import logging
from datetime import datetime, timezone
from typing import List, Optional, Any
from src.core.cognition.models import Hypothesis

logger = logging.getLogger(__name__)

class HypothesisRepository:
    """
    HypothesisRepository (Sprint 6.2).
    Gerencia a persistência de hipóteses científicas no SQLite.
    """
    def __init__(self, db: Any):
        self.db = db

    def _get_conn(self):
        if hasattr(self.db, "conn") and self.db.conn:
            return self.db.conn
        if isinstance(self.db, str):
            return sqlite3.connect(self.db)
        return self.db

    def save_hypothesis(self, hypothesis: Hypothesis) -> Hypothesis:
        """Salva ou atualiza uma hipótese."""
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        conn = self._get_conn()
        c = conn.cursor()
        
        if hypothesis.id is None:
            c.execute("""
                INSERT INTO hypotheses (statement, confidence_score, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (hypothesis.statement, hypothesis.confidence_score, hypothesis.status, ts, ts))
            hypothesis.id = c.lastrowid
            hypothesis.created_at = ts
            hypothesis.updated_at = ts
        else:
            c.execute("""
                UPDATE hypotheses
                SET statement = ?, confidence_score = ?, status = ?, updated_at = ?
                WHERE id = ?
            """, (hypothesis.statement, hypothesis.confidence_score, hypothesis.status, ts, hypothesis.id))
            hypothesis.updated_at = ts
        
        # Check if caller is managing transaction or not
        if not hasattr(self.db, "conn"):
            conn.commit()
            
        return hypothesis

    def get_hypothesis(self, hypothesis_id: int) -> Optional[Hypothesis]:
        """Recupera uma hipótese pelo ID."""
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT id, statement, confidence_score, status, created_at, updated_at
            FROM hypotheses
            WHERE id = ?
        """, (hypothesis_id,))
        row = c.fetchone()
        if row:
            return Hypothesis(
                id=row[0],
                statement=row[1],
                confidence_score=row[2],
                status=row[3],
                created_at=row[4],
                updated_at=row[5]
            )
        return None

    def get_hypotheses(self) -> List[Hypothesis]:
        """Recupera todas as hipóteses."""
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT id, statement, confidence_score, status, created_at, updated_at
            FROM hypotheses
            ORDER BY id DESC
        """)
        rows = c.fetchall()
        return [
            Hypothesis(
                id=row[0],
                statement=row[1],
                confidence_score=row[2],
                status=row[3],
                created_at=row[4],
                updated_at=row[5]
            )
            for row in rows
        ]

    def update_hypothesis_status(self, hypothesis_id: int, status: str) -> None:
        """Atualiza o status de uma hipótese."""
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            UPDATE hypotheses
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (status, ts, hypothesis_id))
        if not hasattr(self.db, "conn"):
            conn.commit()

    def update_hypothesis_confidence(self, hypothesis_id: int, confidence: float) -> None:
        """Atualiza a confiança de uma hipótese."""
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            UPDATE hypotheses
            SET confidence_score = ?, updated_at = ?
            WHERE id = ?
        """, (confidence, ts, hypothesis_id))
        if not hasattr(self.db, "conn"):
            conn.commit()
