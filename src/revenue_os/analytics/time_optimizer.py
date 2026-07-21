import random
import logging
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

from src.revenue_os.analytics.database import ExperimentDatabase

logger = logging.getLogger("revenue_os.time_optimizer")


class TimeSlotOptimizer:
    """
    Aprende quais horários geram melhor CTR/engagement usando Thompson Sampling
    com distribuição Beta por slot de hora (0-23).
    
    Desativada por padrão (ENABLE_SMART_SCHEDULING=False).
    Requer 30+ dias de dados para ativação.
    """
    
    def __init__(self, db: ExperimentDatabase):
        self.db = db
        self._ensure_table()
    
    def _ensure_table(self):
        """Garante que a tabela time_slot_performance existe."""
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute('''
                    CREATE TABLE IF NOT EXISTS time_slot_performance (
                        hour_slot INTEGER PRIMARY KEY,
                        total_posts INTEGER DEFAULT 0,
                        total_impressions INTEGER DEFAULT 0,
                        total_clicks INTEGER DEFAULT 0,
                        total_saves INTEGER DEFAULT 0,
                        avg_ctr REAL DEFAULT 0.0,
                        alpha REAL DEFAULT 1.0,
                        beta REAL DEFAULT 1.0,
                        updated_at TEXT
                    )
                ''')
                # Inicializa os 24 slots se vazios
                c.execute("SELECT COUNT(*) FROM time_slot_performance")
                if c.fetchone()[0] == 0:
                    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    for hour in range(24):
                        c.execute('''
                            INSERT OR IGNORE INTO time_slot_performance 
                            (hour_slot, total_posts, total_impressions, total_clicks, total_saves, avg_ctr, alpha, beta, updated_at)
                            VALUES (?, 0, 0, 0, 0, 0.0, 1.0, 1.0, ?)
                        ''', (hour, now))
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao criar tabela time_slot_performance: {e}")
    
    def record_outcome(self, hour: int, impressions: int, clicks: int, saves: int):
        """
        Registra o resultado de uma publicação feita nesse slot de hora.
        Atualiza os parâmetros alpha/beta da distribuição Beta.
        """
        if hour < 0 or hour > 23:
            logger.warning(f"Slot de hora inválido: {hour}")
            return
        
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Definimos "sucesso" como CTR > mediana ou saves > 0
        success = (clicks > 0 and impressions > 0 and (clicks / impressions) > 0.02) or saves > 0
        
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                
                if success:
                    c.execute('''
                        UPDATE time_slot_performance 
                        SET total_posts = total_posts + 1,
                            total_impressions = total_impressions + ?,
                            total_clicks = total_clicks + ?,
                            total_saves = total_saves + ?,
                            alpha = alpha + 1.0,
                            avg_ctr = CASE WHEN (total_impressions + ?) > 0 
                                           THEN CAST((total_clicks + ?) AS REAL) / (total_impressions + ?) * 100 
                                           ELSE 0.0 END,
                            updated_at = ?
                        WHERE hour_slot = ?
                    ''', (impressions, clicks, saves, impressions, clicks, impressions, now, hour))
                else:
                    c.execute('''
                        UPDATE time_slot_performance 
                        SET total_posts = total_posts + 1,
                            total_impressions = total_impressions + ?,
                            total_clicks = total_clicks + ?,
                            total_saves = total_saves + ?,
                            beta = beta + 1.0,
                            avg_ctr = CASE WHEN (total_impressions + ?) > 0 
                                           THEN CAST((total_clicks + ?) AS REAL) / (total_impressions + ?) * 100 
                                           ELSE 0.0 END,
                            updated_at = ?
                        WHERE hour_slot = ?
                    ''', (impressions, clicks, saves, impressions, clicks, impressions, now, hour))
                
                conn.commit()
            logger.info(f"Outcome registrado: hora={hour}, success={success}, impressions={impressions}, clicks={clicks}")
        except Exception as e:
            logger.error(f"Erro ao registrar outcome no slot {hour}: {e}")
    
    def get_optimal_schedule(self, n_posts: int) -> List[int]:
        """
        Usa Thompson Sampling para selecionar os n melhores slots de hora.
        Retorna lista de horas (0-23) ordenadas.
        """
        slots = []
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute("SELECT hour_slot, alpha, beta FROM time_slot_performance")
                rows = c.fetchall()
                
                for row in rows:
                    hour, alpha, beta_param = row
                    # Amostra da distribuição Beta
                    sample = random.betavariate(max(0.1, alpha), max(0.1, beta_param))
                    slots.append((hour, sample))
        except Exception as e:
            logger.error(f"Erro ao calcular schedule otimo: {e}")
            # Fallback: horários uniformemente distribuídos
            return self._default_schedule(n_posts)
        
        if not slots:
            return self._default_schedule(n_posts)
        
        # Ordena por score (Thompson Sampling) e pega os top n
        slots.sort(key=lambda x: x[1], reverse=True)
        selected_hours = sorted([s[0] for s in slots[:n_posts]])
        
        return selected_hours
    
    def _default_schedule(self, n_posts: int) -> List[int]:
        """Fallback: horários uniformemente distribuídos entre 9h e 22h."""
        available = list(range(9, 23))
        random.shuffle(available)
        return sorted(available[:n_posts])
    
    def get_slot_stats(self) -> List[Dict[str, Any]]:
        """Retorna estatísticas de todos os slots."""
        stats: List[Dict[str, Any]] = []
        try:
            with self.db._get_conn() as conn:
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute("SELECT * FROM time_slot_performance ORDER BY hour_slot")
                for row in c.fetchall():
                    stats.append(dict(row))
        except Exception as e:
            logger.error(f"Erro ao listar slots: {e}")
        return stats
