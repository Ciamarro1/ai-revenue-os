CREATE TABLE IF NOT EXISTS hypotheses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    statement TEXT,
    metric_target TEXT,
    tests_run INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS experiments (
    experiment_id TEXT PRIMARY KEY,
    hypothesis_id INTEGER,
    variant_id TEXT,
    published_at TEXT,
    platform TEXT,
    creative_hash TEXT,
    generation_cost_usd REAL,
    revenue_usd REAL,
    status TEXT,
    market_segment TEXT,
    worker_id TEXT,
    lock_timestamp TEXT,
    FOREIGN KEY(hypothesis_id) REFERENCES hypotheses(id)
);

CREATE TABLE IF NOT EXISTS experiment_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id TEXT,
    timestamp TEXT,
    event_type TEXT,
    payload_json TEXT
);

CREATE TABLE IF NOT EXISTS factory_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    render_time REAL,
    failure_rate REAL,
    retry_rate REAL,
    recovery_time REAL,
    avg_cpu REAL,
    avg_ram REAL,
    disk_usage REAL,
    free_disk REAL,
    audio_failures INTEGER,
    subtitle_failures INTEGER
);

CREATE TABLE IF NOT EXISTS metrics (
    experiment_id TEXT PRIMARY KEY,
    impressions INTEGER,
    outbound_clicks INTEGER,
    saves INTEGER,
    recorded_at TEXT,
    FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
);
