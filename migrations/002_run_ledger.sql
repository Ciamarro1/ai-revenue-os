CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    started_at TEXT,
    finished_at TEXT,
    profile TEXT,
    runner_version TEXT,
    git_commit TEXT,
    hostname TEXT,
    pid INTEGER,
    status TEXT,
    exit_reason TEXT,
    worker_id TEXT
);

-- SQLite ALTER TABLE support is limited, but ADD COLUMN is supported.
-- If the column already exists, this might fail, so in the migrate script we will ignore duplicates.
ALTER TABLE experiments ADD COLUMN run_id TEXT;
