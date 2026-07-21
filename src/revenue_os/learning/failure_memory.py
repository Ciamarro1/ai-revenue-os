import sqlite3
from typing import List, Dict, Any
from src.revenue_os.analytics.database import ExperimentDatabase

class FailureMemory:
    """
    Memória de Rejeição/Falha do Laboratório.
    Mapeia os ganchos e categorias que apresentaram desempenho severamente insatisfatório
    (ex: alto custo com zero cliques, CTR < 0.5% ou retenção < 3s residual).
    """
    def __init__(self, db: ExperimentDatabase):
        self.db = db

    def get_failed_genomes(self, max_reward: float = 15.0) -> List[Dict[str, Any]]:
        """
        Retorna parâmetros criativos que geraram baixo retorno/recompensa.
        """
        query = """
            SELECT 
                h.statement,
                h.category,
                e.variant_id,
                m.ctr_percent,
                m.retention_3s_percent,
                m.reward_score,
                e.generation_cost_usd
            FROM experiments e
            JOIN metrics m ON e.experiment_id = m.experiment_id
            JOIN hypotheses h ON e.hypothesis_id = h.id
            WHERE m.reward_score <= ? OR m.ctr_percent < 0.8
            ORDER BY m.reward_score ASC
        """
        results = []
        conn = self.db._get_conn()
        try:
            c = conn.cursor()
            c.execute(query, (max_reward,))
            rows = c.fetchall()
            for r in rows:
                results.append({
                    "statement": r[0],
                    "category": r[1],
                    "variant_id": r[2],
                    "ctr_percent": r[3],
                    "retention_3s_percent": r[4],
                    "reward_score": r[5],
                    "cost_usd": r[6]
                })
        finally:
            if conn and self.db.db_file != ":memory:":
                conn.close()
        return results
