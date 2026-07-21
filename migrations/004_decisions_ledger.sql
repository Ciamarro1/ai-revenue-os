CREATE TABLE IF NOT EXISTS experiment_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id TEXT,
    run_id INTEGER,
    decision_point TEXT,
    chosen_value TEXT,
    rejected_alternatives_json TEXT,
    reason TEXT,
    decision_policy TEXT,
    policy_version TEXT,
    confidence REAL,
    inputs_hash TEXT,
    seed INTEGER,
    timestamp TEXT
);
