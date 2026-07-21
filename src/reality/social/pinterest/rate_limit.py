import sqlite3
import time
from pathlib import Path
from src.integrations.pinterest.errors import PinterestRateLimitError

class RateLimitManager:
    """
    Gerencia os limites de requisição da API (Rate Limits) de forma persistente.
    Utiliza um banco SQLite compartilhado para que múltiplos processos paralelos 
    respeitem os limites impostos pelas plataformas.
    """
    
    def __init__(self, db_path: str = "knowledge/rate_limits.db"):
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
                CREATE TABLE IF NOT EXISTS rate_limits (
                    platform TEXT PRIMARY KEY,
                    limit_val INTEGER,
                    remaining INTEGER,
                    reset_timestamp REAL
                )
            """)
            conn.commit()

    def check_and_wait(self, platform: str = "pinterest"):
        """
        Verifica se o limite foi atingido e dorme até o reset_timestamp caso necessário.
        """
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT remaining, reset_timestamp FROM rate_limits WHERE platform = ?", 
                (platform,)
            )
            row = cursor.fetchone()
            
        if row:
            remaining, reset_timestamp = row
            now = time.time()
            if remaining is not None and remaining <= 0 and reset_timestamp and now < reset_timestamp:
                sleep_duration = reset_timestamp - now + 1.0  # Buffer de 1s
                print(f"⚠️ [RateLimitManager] Limite de requisições esgotado para {platform}. Aguardando {sleep_duration:.2f}s...")
                time.sleep(sleep_duration)

    def _parse_header_val(self, val: any) -> int:
        if val is None:
            return 0
        if isinstance(val, (int, float)):
            return int(val)
        try:
            part = str(val).split(",")[0].strip()
            subpart = part.split(";")[0].strip()
            return int(float(subpart))
        except (ValueError, TypeError, IndexError):
            return 0

    def _parse_float_val(self, val: any) -> float:
        if val is None:
            return 0.0
        if isinstance(val, (int, float)):
            return float(val)
        try:
            part = str(val).split(",")[0].strip()
            subpart = part.split(";")[0].strip()
            return float(subpart)
        except (ValueError, TypeError, IndexError):
            return 0.0

    def update_limits(self, platform: str, limit_val: any, remaining: any, reset_timestamp: any):
        """
        Atualiza os limites com base nos cabeçalhos HTTP recebidos da API.
        """
        l_val = self._parse_header_val(limit_val)
        r_val = self._parse_header_val(remaining)
        reset_val = self._parse_float_val(reset_timestamp)
        
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO rate_limits (platform, limit_val, remaining, reset_timestamp)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(platform) DO UPDATE SET
                    limit_val = excluded.limit_val,
                    remaining = excluded.remaining,
                    reset_timestamp = excluded.reset_timestamp
            """, (platform, l_val, r_val, reset_val))
            conn.commit()
            
    def handle_rate_limit_error(self, platform: str, reset_timestamp: any):
        """
        Registra o erro 429 e força a atualização do banco.
        """
        reset_val = self._parse_float_val(reset_timestamp)
        self.update_limits(platform, limit_val=0, remaining=0, reset_timestamp=reset_val)
        now = time.time()
        sleep_duration = max(5.0, reset_val - now + 1.0)
        print(f"🛑 [RateLimitManager] HTTP 429 Detectado! Forçando espera de {sleep_duration:.2f}s...")
        time.sleep(sleep_duration)



