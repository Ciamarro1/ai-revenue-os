import logging
import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from src.revenue_os.analytics.database import ExperimentDatabase

logger = logging.getLogger("revenue_os.board_tracker")


class BoardTracker:
    """
    Rastreia métricas por board do Pinterest e calcula Trust Score individual.
    Permite ao sistema decidir futuramente qual board é melhor para cada tipo de conteúdo.
    """
    
    def __init__(self, db: ExperimentDatabase):
        self.db = db
        self._ensure_table()
    
    def _ensure_table(self):
        """Garante que a tabela board_metrics existe."""
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute('''
                    CREATE TABLE IF NOT EXISTS board_metrics (
                        board_name TEXT PRIMARY KEY,
                        total_posts INTEGER DEFAULT 0,
                        total_impressions INTEGER DEFAULT 0,
                        total_clicks INTEGER DEFAULT 0,
                        total_saves INTEGER DEFAULT 0,
                        avg_ctr REAL DEFAULT 0.0,
                        trust_score INTEGER DEFAULT 100,
                        created_at TEXT,
                        updated_at TEXT
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao criar tabela board_metrics: {e}")
    
    def record_publish(self, board_name: str, experiment_id: str):
        """Registra uma publicação no board."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                # Upsert: cria se não existe, incrementa se existe
                c.execute("SELECT total_posts FROM board_metrics WHERE board_name = ?", (board_name,))
                row = c.fetchone()
                if row:
                    c.execute('''
                        UPDATE board_metrics 
                        SET total_posts = total_posts + 1, updated_at = ?
                        WHERE board_name = ?
                    ''', (now, board_name))
                else:
                    c.execute('''
                        INSERT INTO board_metrics (board_name, total_posts, created_at, updated_at)
                        VALUES (?, 1, ?, ?)
                    ''', (board_name, now, now))
                conn.commit()
            logger.info(f"Publicacao registrada no board '{board_name}' (exp: {experiment_id})")
        except Exception as e:
            logger.error(f"Erro ao registrar publicacao no board: {e}")
    
    def update_metrics(self, board_name: str, impressions: int, clicks: int, saves: int):
        """Atualiza métricas acumuladas do board."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute('''
                    UPDATE board_metrics 
                    SET total_impressions = total_impressions + ?,
                        total_clicks = total_clicks + ?,
                        total_saves = total_saves + ?,
                        avg_ctr = CASE WHEN (total_impressions + ?) > 0 
                                       THEN CAST((total_clicks + ?) AS REAL) / (total_impressions + ?) * 100 
                                       ELSE 0.0 END,
                        updated_at = ?
                    WHERE board_name = ?
                ''', (impressions, clicks, saves, impressions, clicks, impressions, now, board_name))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao atualizar metricas do board '{board_name}': {e}")
    
    def update_board_trust(self, board_name: str, delta: int):
        """Ajusta o Trust Score de um board específico."""
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute("SELECT trust_score FROM board_metrics WHERE board_name = ?", (board_name,))
                row = c.fetchone()
                if row:
                    new_score = max(0, min(100, row[0] + delta))
                    c.execute("UPDATE board_metrics SET trust_score = ? WHERE board_name = ?",
                              (new_score, board_name))
                    conn.commit()
        except Exception as e:
            logger.error(f"Erro ao atualizar trust score do board: {e}")
    
    def get_best_board(self, content_category: str = None) -> str:
        """
        Retorna o board com melhor performance.
        Para o estágio atual, sempre retorna 'AI Revenue OS' (board único).
        Futuramente usará content_category para matching.
        """
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute('''
                    SELECT board_name FROM board_metrics 
                    WHERE trust_score >= 50 
                    ORDER BY avg_ctr DESC, trust_score DESC 
                    LIMIT 1
                ''')
                row = c.fetchone()
                if row:
                    return row[0]
        except Exception as e:
            logger.error(f"Erro ao buscar melhor board: {e}")
        
        return "AI Revenue OS"  # Default
    
    def get_board_stats(self) -> List[Dict[str, Any]]:
        """Retorna estatísticas de todos os boards."""
        boards: List[Dict[str, Any]] = []
        try:
            with self.db._get_conn() as conn:
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute("SELECT * FROM board_metrics ORDER BY total_posts DESC")
                for row in c.fetchall():
                    boards.append(dict(row))
        except Exception as e:
            logger.error(f"Erro ao listar boards: {e}")
        return boards
