import sqlite3
import json
import time
from datetime import datetime, timezone
from src.services.exceptions import RetryableError

class CircuitBreakerMixin:
    def __init__(self, provider_name: str, db_path: str = "prod_db.sqlite3", max_failures: int = 5, reset_timeout_sec: int = 1800):
        self.cb_provider_name = provider_name
        self.cb_db_path = db_path
        self.cb_max_failures = max_failures
        self.cb_reset_timeout_sec = reset_timeout_sec
        self.cb_consecutive_failures = 0
        self.cb_state = "CLOSED"
        self.cb_last_failure_time = 0
        
    def _cb_log_event(self, event: str):
        try:
            with sqlite3.connect(self.cb_db_path) as conn:
                c = conn.cursor()
                ts = datetime.now(timezone.utc).isoformat() + "Z"
                c.execute('INSERT INTO provider_events (timestamp, provider, event, metadata_json) VALUES (?, ?, ?, ?)',
                          (ts, self.cb_provider_name, event, json.dumps({"failures": self.cb_consecutive_failures})))
                conn.commit()
        except Exception:
            pass

    def cb_check(self):
        if self.cb_state == "OPEN":
            if time.time() - self.cb_last_failure_time > self.cb_reset_timeout_sec:
                self.cb_state = "HALF_OPEN"
                self._cb_log_event("Circuit Half Open")
            else:
                raise RetryableError("CIRCUIT_OPEN", f"Circuit Breaker OPEN para {self.cb_provider_name}")
                
    def cb_record_success(self):
        if self.cb_state != "CLOSED":
            self.cb_state = "CLOSED"
            self.cb_consecutive_failures = 0
            self._cb_log_event("Recovered")
            
    def cb_record_failure(self):
        self.cb_consecutive_failures += 1
        self.cb_last_failure_time = time.time()
        if self.cb_consecutive_failures >= self.cb_max_failures and self.cb_state == "CLOSED":
            self.cb_state = "OPEN"
            self._cb_log_event("Circuit Opened")
        elif self.cb_state == "HALF_OPEN":
            self.cb_state = "OPEN"
            self._cb_log_event("Circuit Opened (Failed Half Open)")
