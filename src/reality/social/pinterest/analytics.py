import sqlite3
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from src.adapters.base import CanonicalMetrics
from src.integrations.pinterest.errors import PinterestError

class AnalyticsManager:
    """
    Componente especializado em recuperar métricas do Pinterest
    com caching persistente de 30 minutos (TTL) via SQLite.
    """
    
    def __init__(self, auth_headers: Dict[str, str], rate_limit_mgr, db_path: str = "knowledge/pinterest_cache.db"):
        self.headers = auth_headers
        self.rate_limit_mgr = rate_limit_mgr
        if db_path == ":memory:":
            self.db_file = ":memory:"
        else:
            self.db_file = Path(__file__).parent.parent.parent.parent.parent / db_path
            self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_file))
        self._init_db()

    def _get_conn(self):
        return self.conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics_cache (
                    content_id TEXT PRIMARY KEY,
                    impressions INTEGER,
                    outbound_clicks INTEGER,
                    saves INTEGER,
                    cached_at REAL
                )
            """)
            conn.commit()

    def get_metrics(self, pin_id: str) -> CanonicalMetrics:
        """
        Retorna as métricas canônicas do Pin, servindo do cache se válido.
        """
        # 1. Verifica cache local
        cached = self._read_cache(pin_id)
        if cached:
            print(f"📦 [AnalyticsManager] Cache hit para Pin ID: {pin_id}")
            return cached
            
        # 2. Chamada à API
        print(f"🌐 [AnalyticsManager] Cache miss. Buscando métricas reais para Pin ID: {pin_id}...")
        url = f"https://api.pinterest.com/v5/pins/{pin_id}/analytics"
        params = {"metric_types": "IMPRESSION,OUTBOUND_CLICK,SAVE"}
        
        self.rate_limit_mgr.check_and_wait("pinterest")
        response = requests.get(url, headers=self.headers, params=params)
        self._update_rate_limits(response.headers)
        
        if response.status_code == 429:
            reset_ts = float(response.headers.get("x-ratelimit-reset", time.time() + 60))
            self.rate_limit_mgr.handle_rate_limit_error("pinterest", reset_ts)
            # Tenta novamente
            response = requests.get(url, headers=self.headers, params=params)
            
        if response.status_code != 200:
            raise PinterestError(f"Erro ao obter analytics do Pin {pin_id}: {response.text}")
            
        data = response.json()
        
        # Faz parse seguro das métricas
        all_metrics = data.get("all", {})
        summary = all_metrics.get("summary_metrics", {})
        
        impressions = int(summary.get("IMPRESSION", 0))
        outbound_clicks = int(summary.get("OUTBOUND_CLICK", 0))
        saves = int(summary.get("SAVE", 0))
        
        metrics = CanonicalMetrics(
            impressions=impressions,
            outbound_clicks=outbound_clicks,
            saves=saves,
            spend=None,
            revenue=None
        )
        
        # 3. Grava no cache
        self._write_cache(pin_id, metrics)
        return metrics

    def _read_cache(self, pin_id: str) -> Optional[CanonicalMetrics]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT impressions, outbound_clicks, saves, cached_at FROM analytics_cache WHERE content_id = ?",
                (pin_id,)
            )
            row = cursor.fetchone()
            
        if row:
            impressions, outbound_clicks, saves, cached_at = row
            # TTL de 30 minutos (1800 segundos)
            if time.time() - cached_at < 1800:
                return CanonicalMetrics(
                    impressions=impressions,
                    outbound_clicks=outbound_clicks,
                    saves=saves,
                    spend=None,
                    revenue=None
                )
        return None

    def _write_cache(self, pin_id: str, metrics: CanonicalMetrics):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO analytics_cache (content_id, impressions, outbound_clicks, saves, cached_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(content_id) DO UPDATE SET
                    impressions = excluded.impressions,
                    outbound_clicks = excluded.outbound_clicks,
                    saves = excluded.saves,
                    cached_at = excluded.cached_at
            """, (pin_id, metrics.impressions, metrics.outbound_clicks, metrics.saves, time.time()))
            conn.commit()

    def _update_rate_limits(self, headers: Dict[str, str]):
        limit = headers.get("x-ratelimit-limit")
        remaining = headers.get("x-ratelimit-remaining")
        reset = headers.get("x-ratelimit-reset")
        if limit and remaining and reset:
            self.rate_limit_mgr.update_limits("pinterest", limit, remaining, reset)



