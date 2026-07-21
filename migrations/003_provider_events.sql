CREATE TABLE IF NOT EXISTS provider_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    provider TEXT,
    event TEXT,
    metadata_json TEXT
);
