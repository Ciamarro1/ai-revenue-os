import sqlite3
from typing import List, Dict, Any
from src.revenue_os.analytics.database import ExperimentDatabase

class SuccessMemory:
    """
    Memória de Sucesso do Laboratório.
    Filtra os genomas (hooks, categorias, tópicos) dos experimentos mais lucrativos e eficientes
    (ex: percentil superior de reward_score).
    """
    def __init__(self, db: ExperimentDatabase):
        self.db = db

    def get_success_genomes(self, min_reward: float = 50.0) -> List[Dict[str, Any]]:
        """
        Retorna uma lista de parâmetros criativos que geraram recompensa superior ao limiar.
        """
        query = """
            SELECT 
                h.statement,
                h.category,
                e.variant_id,
                e.variant_desc,
                m.ctr_percent,
                m.retention_3s_percent,
                m.reward_score,
                e.revenue_usd
            FROM experiments e
            JOIN metrics m ON e.experiment_id = m.experiment_id
            JOIN hypotheses h ON e.hypothesis_id = h.id
            WHERE m.reward_score >= ?
            ORDER BY m.reward_score DESC
        """
        results = []
        # Obtém conexão a partir do motor de DB
        conn = self.db._get_conn()
        try:
            c = conn.cursor()
            c.execute(query, (min_reward,))
            rows = c.fetchall()
            for r in rows:
                results.append({
                    "statement": r[0],
                    "category": r[1],
                    "variant_id": r[2],
                    "variant_desc": r[3],
                    "ctr_percent": r[4],
                    "retention_3s_percent": r[5],
                    "reward_score": r[6],
                    "revenue_usd": r[7]
                })
        finally:
            if conn and self.db.db_file != ":memory:":
                conn.close()
        return results
