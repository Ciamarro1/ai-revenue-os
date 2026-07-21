import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from src.revenue_os.analytics.database import ExperimentDatabase

class DecisionQueue:
    """
    Fila de Decisão (Sprint 6.3).
    Gerencia o ciclo de vida dos experimentos (Pending -> Running -> Completed -> Failed)
    e prioriza a execução com base nos escores científicos.
    """
    def __init__(self, db: ExperimentDatabase):
        self.db = db
        self._init_db()

    def _init_db(self):
        with self.db._get_conn() as conn:
            c = conn.cursor()
            # Adiciona a coluna priority se não existir na tabela experiments
            try:
                c.execute("ALTER TABLE experiments ADD COLUMN priority REAL DEFAULT 1.0")
            except sqlite3.OperationalError:
                pass
            conn.commit()

    def enqueue(self, experiment_id: str, hypothesis_id: int, priority: float = 1.0) -> None:
        """Enfileira um experimento no estado 'Pending'."""
        with self.db._get_conn() as conn:
            c = conn.cursor()
            ts = datetime.now(timezone.utc).isoformat() + "Z"
            # Registra/Sobrescreve com status 'Pending'
            c.execute("""
                INSERT OR REPLACE INTO experiments (experiment_id, hypothesis_id, status, published_at, priority)
                VALUES (?, ?, 'Pending', ?, ?)
            """, (experiment_id, hypothesis_id, ts, priority))
            conn.commit()

    def get_pending(self) -> List[Dict[str, Any]]:
        """Busca experimentos pendentes ordenados por prioridade decrescente."""
        with self.db._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("""
                SELECT * FROM experiments 
                WHERE status = 'Pending' 
                ORDER BY priority DESC, experiment_id ASC
            """)
            return [dict(row) for row in c.fetchall()]

    def transition_state(self, experiment_id: str, from_state: str, to_state: str) -> bool:
        """Transiciona de forma segura o status de um experimento."""
        with self.db._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE experiments 
                SET status = ? 
                WHERE experiment_id = ? AND status = ?
            """, (to_state, experiment_id, from_state))
            conn.commit()
            return c.rowcount > 0

    def update_status(self, experiment_id: str, status: str) -> None:
        """Atualiza diretamente o status de um experimento no banco."""
        with self.db._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE experiments 
                SET status = ? 
                WHERE experiment_id = ?
            """, (status, experiment_id))
            conn.commit()
