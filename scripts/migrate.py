import os
import sqlite3
import hashlib
from datetime import datetime, timezone
from pathlib import Path

def get_checksum(file_path: Path) -> str:
    with open(file_path, "rb") as f:
        content = f.read().replace(b"\r\n", b"\n")
        return hashlib.sha256(content).hexdigest()

def migrate(db_path: str = "prod_db.sqlite3", migrations_dir: str = "migrations"):
    mig_dir = Path(migrations_dir)
    if not mig_dir.exists():
        print(f"Directory {migrations_dir} does not exist.")
        return

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                checksum TEXT,
                applied_at TEXT
            )
        ''')
        
        c.execute("SELECT version, checksum FROM schema_migrations")
        applied_migrations = {row[0]: row[1] for row in c.fetchall()}
        
        sql_files = sorted([f for f in mig_dir.iterdir() if f.suffix == ".sql"])
        
        for sql_file in sql_files:
            version = sql_file.stem
            current_checksum = get_checksum(sql_file)
            
            if version in applied_migrations:
                if applied_migrations[version] != current_checksum:
                    raise RuntimeError(f"Checksum mismatch for migration {version}! File was altered after being applied.")
                continue # Already applied
                
            print(f"Applying migration: {version}")
            with open(sql_file, "r", encoding="utf-8") as f:
                script = f.read()
                
            try:
                # SQLite execute() only does single statement, executescript() does multiple
                c.executescript(script)
            except sqlite3.OperationalError as e:
                # Se for "duplicate column name", ignorar já que SQLite não suporta IF NOT EXISTS no ALTER TABLE
                if "duplicate column name" not in str(e).lower():
                    raise e
                    
            ts = datetime.now(timezone.utc).isoformat() + "Z"
            c.execute('INSERT INTO schema_migrations (version, checksum, applied_at) VALUES (?, ?, ?)',
                      (version, current_checksum, ts))
        
        conn.commit()
    print("Migrations up to date.")

if __name__ == "__main__":
    migrate()
