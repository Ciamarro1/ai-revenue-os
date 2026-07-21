import sqlite3
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from src.core.cognition.models import Reflection, Lesson

class ReflectionRepository:
    """
    ReflectionRepository (Sprint 6.4).
    Persiste e recupera reflexões e lições aprendidas no banco de dados SQLite.
    """
    def __init__(self, db: Any):
        self.db = db

    def _get_conn(self):
        return self.db._get_conn()

    def save_reflection(self, reflection: Reflection) -> Reflection:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO reflections (experiment_id, analysis, probable_cause, confidence_delta, bayesian_explanation, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                reflection.experiment_id,
                reflection.analysis,
                reflection.probable_cause,
                reflection.confidence_delta,
                json.dumps(reflection.bayesian_explanation),
                ts
            ))
            reflection.id = c.lastrowid
            reflection.timestamp = ts
            conn.commit()
        return reflection

    def get_reflection(self, reflection_id: int) -> Optional[Reflection]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, experiment_id, analysis, probable_cause, confidence_delta, bayesian_explanation, timestamp
                FROM reflections
                WHERE id = ?
            """, (reflection_id,))
            r = c.fetchone()
            if r:
                return Reflection(
                    id=r[0],
                    experiment_id=r[1],
                    analysis=r[2],
                    probable_cause=r[3],
                    confidence_delta=r[4],
                    bayesian_explanation=json.loads(r[5]) if r[5] else {},
                    timestamp=r[6]
                )
        return None

    def get_reflections_by_experiment(self, experiment_id: str) -> List[Reflection]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, experiment_id, analysis, probable_cause, confidence_delta, bayesian_explanation, timestamp
                FROM reflections
                WHERE experiment_id = ?
                ORDER BY id DESC
            """, (experiment_id,))
            rows = c.fetchall()
            return [
                Reflection(
                    id=r[0],
                    experiment_id=r[1],
                    analysis=r[2],
                    probable_cause=r[3],
                    confidence_delta=r[4],
                    bayesian_explanation=json.loads(r[5]) if r[5] else {},
                    timestamp=r[6]
                )
                for r in rows
            ]

    def save_lesson(self, lesson: Lesson) -> Lesson:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO lessons (reflection_id, pattern_detected, actionable_insight, severity, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                lesson.reflection_id,
                lesson.pattern_detected,
                lesson.actionable_insight,
                lesson.severity,
                ts
            ))
            lesson.id = c.lastrowid
            lesson.created_at = ts
            conn.commit()
        return lesson

    def get_lessons_by_reflection(self, reflection_id: int) -> List[Lesson]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, reflection_id, pattern_detected, actionable_insight, severity, created_at
                FROM lessons
                WHERE reflection_id = ?
                ORDER BY id DESC
            """, (reflection_id,))
            rows = c.fetchall()
            return [
                Lesson(
                    id=r[0],
                    reflection_id=r[1],
                    pattern_detected=r[2],
                    actionable_insight=r[3],
                    severity=r[4],
                    created_at=r[5]
                )
                for r in rows
            ]

    def get_lessons(self) -> List[Lesson]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, reflection_id, pattern_detected, actionable_insight, severity, created_at
                FROM lessons
                ORDER BY id DESC
            """)
            rows = c.fetchall()
            return [
                Lesson(
                    id=r[0],
                    reflection_id=r[1],
                    pattern_detected=r[2],
                    actionable_insight=r[3],
                    severity=r[4],
                    created_at=r[5]
                )
                for r in rows
            ]
