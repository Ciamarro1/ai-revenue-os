import sqlite3
from typing import Dict, Any, List, Optional
from src.revenue_os.analytics.database import ExperimentDatabase

class HypothesisRegistry:
    """
    Registro Científico de Hipóteses do Laboratório.
    Gerencia o ciclo de vida (testing, validated, rejected) e a confiança das hipóteses.
    """
    
    def __init__(self, db: ExperimentDatabase):
        self.db = db

    def register_hypothesis(self, statement: str, category: str, metric_target: str) -> int:
        """
        Registra uma nova hipótese no banco. Se já existir, retorna o ID correspondente.
        """
        with self.db._get_conn() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO hypotheses (statement, category, metric_target, status, confidence_score, experiments_count)
                    VALUES (?, ?, ?, 'testing', 0.50, 0)
                """, (statement, category, metric_target))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Já existe uma hipótese com este statement exato
                cursor.execute("SELECT id FROM hypotheses WHERE statement = ?", (statement,))
                row = cursor.fetchone()
                return row[0] if row else -1

    def get_hypothesis(self, hypothesis_id: int) -> Optional[Dict[str, Any]]:
        """
        Recupera os detalhes de uma hipótese específica.
        """
        with self.db._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, statement, category, metric_target, status, confidence_score, experiments_count
                FROM hypotheses WHERE id = ?
            """, (hypothesis_id,))
            row = cursor.fetchone()
            
        if row:
            return {
                "id": row[0],
                "statement": row[1],
                "category": row[2],
                "metric_target": row[3],
                "status": row[4],
                "confidence_score": row[5],
                "experiments_count": row[6]
            }
        return None

    def update_hypothesis_stats(self, hypothesis_id: int, outcome: bool):
        """
        Atualiza o número de experimentos executados e ajusta o nível de confiança.
        Outcome=True (validado pelo teste prático), Outcome=False (rejeitado/sem significância).
        Atingindo limites de confiança, transiciona o status para 'validated' ou 'rejected'.
        """
        hypo = self.get_hypothesis(hypothesis_id)
        if not hypo:
            return

        current_count = hypo["experiments_count"] + 1
        current_conf = hypo["confidence_score"]

        # Ajuste de confiança linear simples (incremento/decremento de 0.10 por evidência)
        if outcome:
            new_conf = min(0.99, current_conf + 0.10)
        else:
            new_conf = max(0.01, current_conf - 0.10)
        new_conf = round(new_conf, 2)

        # Transição de status
        if new_conf >= 0.80:
            new_status = "validated"
        elif new_conf <= 0.20:
            new_status = "rejected"
        else:
            new_status = "testing"

        with self.db._get_conn() as conn:
            conn.execute("""
                UPDATE hypotheses 
                SET experiments_count = ?, confidence_score = ?, status = ?
                WHERE id = ?
            """, (current_count, new_conf, new_status, hypothesis_id))
            conn.commit()

    def get_active_hypotheses(self) -> List[Dict[str, Any]]:
        """
        Retorna as hipóteses que ainda estão sob teste ativo ('testing').
        """
        with self.db._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, statement, category, metric_target, status, confidence_score, experiments_count
                FROM hypotheses WHERE status = 'testing'
            """)
            rows = cursor.fetchall()
            
        return [
            {
                "id": r[0],
                "statement": r[1],
                "category": r[2],
                "metric_target": r[3],
                "status": r[4],
                "confidence_score": r[5],
                "experiments_count": r[6]
            }
            for r in rows
        ]
