import json
import time
import shutil
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timezone

class RunReporter:
    """
    Gera o contêiner imutável de lote (Run Report).
    Grava versions.lock.json, metrics e events consolidando a caixa-preta.
    """
    def __init__(self, db_path: str = "prod_db.sqlite3"):
        self.db_path = db_path
        self.runs_dir = Path("runs")
        self.runs_dir.mkdir(exist_ok=True)
        
    def _calculate_schema_hash(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name")
                schema = "".join(str(row[0]) for row in c.fetchall())
                return hashlib.md5(schema.encode()).hexdigest()
        except:
            return "unknown"

    def generate_report(self, run_id: int):
        run_hash = f"RUN_{datetime.now(timezone.utc).strftime('%Y_%m_%d')}_{run_id:04d}"
        run_dir = self.runs_dir / run_hash
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Summary
        summary = {
            "run_id": run_id,
            "hash": run_hash,
            "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
            "experiments_created": 0,
            "dlq_count": 0,
            "retries": 0
        }
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            # Fetch events
            c.execute("SELECT * FROM experiment_events WHERE experiment_id IN (SELECT experiment_id FROM experiments WHERE run_id = ?)", (run_id,))
            events = [dict(row) for row in c.fetchall()]
            with open(run_dir / "events.jsonl", "w") as f:
                for ev in events:
                    f.write(json.dumps(ev) + "\n")
                    if ev["event_type"] == "FAILED_PERMANENT":
                        summary["dlq_count"] += 1
                    if ev["event_type"] == "FAILED_RETRYABLE":
                        summary["retries"] += 1
                        
            c.execute("SELECT COUNT(*) as c FROM experiments WHERE run_id = ?", (run_id,))
            summary["experiments_created"] = c.fetchone()["c"]
            
        with open(run_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)
            
        # 2. Versions.lock
        versions = {
            "code_version": "v1.0-freeze",
            "schema_hash": self._calculate_schema_hash(),
            "runner_version": "v2.0"
        }
        with open(run_dir / "versions.lock.json", "w") as f:
            json.dump(versions, f, indent=2)
            
        # 3. Copy Profile
        prof = Path("config/experiment_profile.yaml")
        if prof.exists():
            shutil.copy(prof, run_dir / "profile.yaml")
            
        print(f"📦 [RunReporter] Caixa-preta gravada em {run_dir}")
        return run_dir
