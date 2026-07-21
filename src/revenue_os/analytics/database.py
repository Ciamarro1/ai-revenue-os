import sqlite3
import json
from pathlib import Path
import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from src.revenue_os.analytics.schemas import ExperimentContract

class ExperimentDatabase:
    """
    Motor relacional SQLite do Laboratório.
    Criado para registrar todas as variantes e suportar análises matemáticas robustas.
    """
    def __init__(self, db_path: str = "knowledge/experiments.db"):
        if db_path == ":memory:":
            self.db_file = ":memory:"
            self.conn = sqlite3.connect(":memory:")
        else:
            self.db_file = Path(__file__).parent.parent.parent.parent / db_path
            self.db_file.parent.mkdir(parents=True, exist_ok=True)
            self.conn = None
        self._init_tables()

    def _get_conn(self):
        if self.db_file == ":memory:":
            return self.conn
        return sqlite3.connect(str(self.db_file))

    def _init_tables(self):
        with self._get_conn() as conn:
            c = conn.cursor()
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS hypotheses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    statement TEXT UNIQUE,
                    metric_target TEXT,
                    category TEXT,
                    status TEXT DEFAULT 'testing',
                    confidence_score REAL DEFAULT 0.50,
                    experiments_count INTEGER DEFAULT 0
                )
            ''')
            
            # Migrações caso o banco já existisse sem as novas colunas
            for col, col_type in [
                ("category", "TEXT"),
                ("status", "TEXT DEFAULT 'testing'"),
                ("confidence_score", "REAL DEFAULT 0.50"),
                ("experiments_count", "INTEGER DEFAULT 0"),
                ("created_at", "TEXT"),
                ("updated_at", "TEXT")
            ]:
                try:
                    c.execute(f"ALTER TABLE hypotheses ADD COLUMN {col} {col_type}")
                except sqlite3.OperationalError:
                    pass
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id TEXT PRIMARY KEY,
                    hypothesis_id INTEGER,
                    variant_id TEXT,
                    variant_desc TEXT,
                    creative_hash TEXT,
                    platform TEXT,
                    published_at TEXT,
                    generation_cost_usd REAL,
                    revenue_usd REAL,
                    status TEXT,
                    market_segment TEXT,
                    worker_id TEXT,
                    lock_timestamp TEXT,
                    FOREIGN KEY(hypothesis_id) REFERENCES hypotheses(id)
                )
            ''')
            
            for query in [
                'ALTER TABLE experiments ADD COLUMN worker_id TEXT',
                'ALTER TABLE experiments ADD COLUMN lock_timestamp TEXT',
                'ALTER TABLE experiments ADD COLUMN variant_desc TEXT',
                'ALTER TABLE experiments ADD COLUMN run_id TEXT',
                'ALTER TABLE experiments ADD COLUMN learning_value_score REAL DEFAULT 0.0',
                'ALTER TABLE experiments ADD COLUMN utm_url TEXT',
                'ALTER TABLE experiments ADD COLUMN epc REAL DEFAULT 0.0',
                'ALTER TABLE experiments ADD COLUMN rpc REAL DEFAULT 0.0',
                'ALTER TABLE experiments ADD COLUMN roi REAL DEFAULT 0.0',
                'ALTER TABLE experiments ADD COLUMN ltv REAL DEFAULT 0.0',
                'ALTER TABLE experiments ADD COLUMN cpa REAL DEFAULT 0.0'
            ]:
                try:
                    c.execute(query)
                except sqlite3.OperationalError:
                    pass
                
            c.execute('''
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
                )
            ''')
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS experiment_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id TEXT,
                    timestamp TEXT,
                    event_type TEXT,
                    payload_json TEXT
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    experiment_id TEXT PRIMARY KEY,
                    impressions INTEGER,
                    ctr_percent REAL,
                    retention_3s_percent REAL,
                    completion_rate_percent REAL,
                    conversion_count INTEGER,
                    reward_score REAL,
                    FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
                )
            ''')
            
            for query in [
                'ALTER TABLE metrics ADD COLUMN ctr_percent REAL',
                'ALTER TABLE metrics ADD COLUMN retention_3s_percent REAL',
                'ALTER TABLE metrics ADD COLUMN completion_rate_percent REAL',
                'ALTER TABLE metrics ADD COLUMN conversion_count INTEGER',
                'ALTER TABLE metrics ADD COLUMN reward_score REAL'
            ]:
                try:
                    c.execute(query)
                except sqlite3.OperationalError:
                    pass
            
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hypothesis_id INTEGER,
                    winning_variant_id TEXT,
                    confidence REAL,
                    reasoning TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(hypothesis_id) REFERENCES hypotheses(id)
                )
            ''')
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS research_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT,
                    provider TEXT,
                    timestamp TEXT,
                    sources TEXT,
                    trends TEXT,
                    competitors TEXT,
                    keywords TEXT,
                    confidence REAL,
                    source_quality REAL DEFAULT 0.8,
                    sample_size INTEGER DEFAULT 10
                )
            ''')
            
            # Migrações caso a tabela já exista
            for col, col_type in [("source_quality", "REAL DEFAULT 0.8"), ("sample_size", "INTEGER DEFAULT 10")]:
                try:
                    c.execute(f"ALTER TABLE research_reports ADD COLUMN {col} {col_type}")
                except sqlite3.OperationalError:
                    pass
            
            # Criar Tabela Assets
            c.execute('''
                CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id TEXT UNIQUE,
                    experiment_id TEXT,
                    factory TEXT,
                    prompt_hash TEXT,
                    creative_genome TEXT,
                    status TEXT,
                    file_path TEXT,
                    file_hash TEXT,
                    mime_type TEXT,
                    duration_seconds INTEGER,
                    resolution TEXT,
                    size_bytes INTEGER,
                    quality_score REAL,
                    created_at TEXT
                )
            ''')
            
            # Criar Tabela publication_queue
            c.execute('''
                CREATE TABLE IF NOT EXISTS publication_queue (
                    job_id TEXT PRIMARY KEY,
                    experiment_id TEXT,
                    platform TEXT,
                    media_path TEXT,
                    title TEXT,
                    description TEXT,
                    link TEXT,
                    board TEXT,
                    status TEXT DEFAULT 'pending',
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 3,
                    scheduled_at TEXT,
                    processed_at TEXT,
                    error_message TEXT,
                    FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
                )
            ''')
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS system_state (
                    key TEXT PRIMARY KEY,
                    value_json TEXT,
                    updated_at TEXT
                )
            ''')
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS image_hashes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id TEXT,
                    file_path TEXT,
                    phash TEXT,
                    ahash TEXT,
                    dhash TEXT,
                    created_at TEXT
                )
            ''')
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS board_metrics (
                    board_name TEXT PRIMARY KEY,
                    total_posts INTEGER DEFAULT 0,
                    total_impressions INTEGER DEFAULT 0,
                    total_clicks INTEGER DEFAULT 0,
                    total_saves INTEGER DEFAULT 0,
                    avg_ctr REAL DEFAULT 0.0,
                    trust_score INTEGER DEFAULT 100,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
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
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_graph (
                    source_concept TEXT,
                    target_concept TEXT,
                    weight REAL DEFAULT 1.0,
                    updated_at TEXT,
                    PRIMARY KEY (source_concept, target_concept)
                )
            ''')
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS affiliate_links (
                    link_id TEXT PRIMARY KEY,
                    experiment_id TEXT,
                    raw_url TEXT,
                    utm_url TEXT,
                    short_url TEXT,
                    created_at TEXT
                )
            ''')
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS affiliate_conversions (
                    id TEXT PRIMARY KEY,
                    experiment_id TEXT,
                    click_id TEXT,
                    payout_usd REAL,
                    commission_usd REAL,
                    converted_at TEXT,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS genome_dna_metrics (
                    genome_key TEXT PRIMARY KEY,
                    attribute_value TEXT,
                    total_posts INTEGER DEFAULT 0,
                    total_ctr REAL DEFAULT 0.0,
                    total_saves INTEGER DEFAULT 0,
                    total_revenue REAL DEFAULT 0.0,
                    total_roi REAL DEFAULT 0.0,
                    updated_at TEXT
                )
            ''')
            

            c.execute('''
                CREATE TABLE IF NOT EXISTS beliefs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    statement TEXT UNIQUE,
                    confidence_score REAL DEFAULT 0.50,
                    updated_at TEXT
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hypothesis_id INTEGER,
                    experiment_id TEXT,
                    claim TEXT,
                    confidence_score REAL,
                    impact TEXT,
                    timestamp TEXT,
                    narrative TEXT,
                    FOREIGN KEY(hypothesis_id) REFERENCES hypotheses(id)
                )
            ''')
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS learnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id TEXT,
                    pattern TEXT,
                    severity TEXT,
                    description TEXT,
                    created_at TEXT
                )
            ''')
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS belief_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    belief_id INTEGER,
                    old_confidence REAL,
                    new_confidence REAL,
                    change_reason TEXT,
                    timestamp TEXT,
                    FOREIGN KEY(belief_id) REFERENCES beliefs(id)
                )
            ''')
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS evidence_quality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evidence_id INTEGER UNIQUE,
                    sample_size INTEGER,
                    confidence REAL,
                    reliability REAL,
                    recency REAL,
                    quality_score REAL,
                    FOREIGN KEY(evidence_id) REFERENCES evidence(id)
                )
            ''')
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS semantic_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_type TEXT,
                    content TEXT,
                    metadata_json TEXT,
                    created_at TEXT
                )
            ''')
            
            c.execute('''
                CREATE TABLE IF NOT EXISTS cognitive_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT,
                    payload_json TEXT,
                    timestamp TEXT
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    metric_name TEXT,
                    value REAL,
                    timestamp TEXT,
                    raw_data TEXT
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS cognitive_graph_nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    label TEXT,
                    properties_json TEXT
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS cognitive_graph_edges (
                    source TEXT,
                    target TEXT,
                    relation_type TEXT,
                    weight REAL,
                    properties_json TEXT,
                    PRIMARY KEY (source, target, relation_type)
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS reflections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id TEXT,
                    analysis TEXT,
                    probable_cause TEXT,
                    confidence_delta REAL,
                    bayesian_explanation TEXT,
                    timestamp TEXT,
                    FOREIGN KEY(experiment_id) REFERENCES experiments(experiment_id)
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reflection_id INTEGER,
                    pattern_detected TEXT,
                    actionable_insight TEXT,
                    severity TEXT,
                    created_at TEXT,
                    FOREIGN KEY(reflection_id) REFERENCES reflections(id)
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS objectives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT,
                    target_metric TEXT,
                    status TEXT DEFAULT 'Active',
                    created_at TEXT
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    objective_id INTEGER,
                    statement TEXT,
                    status TEXT DEFAULT 'Draft',
                    priority_score REAL DEFAULT 1.0,
                    created_at TEXT,
                    updated_at TEXT,
                    FOREIGN KEY(objective_id) REFERENCES objectives(id)
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS plan_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id INTEGER,
                    step_number INTEGER,
                    action_description TEXT,
                    experiment_id TEXT,
                    status TEXT DEFAULT 'Pending',
                    created_at TEXT,
                    FOREIGN KEY(plan_id) REFERENCES plans(id)
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    target_metric TEXT,
                    target_value REAL,
                    current_value REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'Active',
                    created_at TEXT
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id INTEGER,
                    statement TEXT,
                    expected_revenue REAL,
                    expected_learning REAL,
                    risk REAL,
                    cost REAL,
                    status TEXT DEFAULT 'Proposed',
                    priority_score REAL DEFAULT 1.0,
                    created_at TEXT,
                    updated_at TEXT,
                    FOREIGN KEY(goal_id) REFERENCES goals(id)
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS constraints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT,
                    constraint_type TEXT,
                    value REAL,
                    created_at TEXT
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    expected_revenue REAL,
                    expected_learning REAL,
                    score REAL DEFAULT 1.0,
                    created_at TEXT
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    step_id INTEGER,
                    name TEXT,
                    status TEXT DEFAULT 'Pending',
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3,
                    created_at TEXT,
                    updated_at TEXT,
                    FOREIGN KEY(step_id) REFERENCES plan_steps(id)
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS action_dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id INTEGER,
                    depends_on_action_id INTEGER,
                    FOREIGN KEY(action_id) REFERENCES actions(id),
                    FOREIGN KEY(depends_on_action_id) REFERENCES actions(id)
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS execution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id INTEGER,
                    status TEXT,
                    error_message TEXT,
                    executed_at TEXT,
                    FOREIGN KEY(action_id) REFERENCES actions(id)
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT,
                    status TEXT DEFAULT 'Active',
                    created_at TEXT
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS tools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    version TEXT,
                    provider_id INTEGER,
                    capabilities TEXT,
                    cost REAL DEFAULT 0.0,
                    latency REAL DEFAULT 0.0,
                    reliability REAL DEFAULT 1.0,
                    health_score REAL DEFAULT 1.0,
                    created_at TEXT,
                    FOREIGN KEY(provider_id) REFERENCES providers(id)
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS capabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    description TEXT,
                    created_at TEXT
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS tool_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_id INTEGER,
                    latency REAL,
                    cost REAL,
                    success BOOLEAN,
                    error_message TEXT,
                    executed_at TEXT,
                    FOREIGN KEY(tool_id) REFERENCES tools(id)
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    description TEXT,
                    objective TEXT,
                    input_schema TEXT,
                    output_schema TEXT,
                    constraints TEXT,
                    metadata TEXT,
                    created_at TEXT
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS skill_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_id INTEGER,
                    step_order INTEGER,
                    capability_required TEXT,
                    tool_required TEXT,
                    input_mapping TEXT,
                    output_mapping TEXT,
                    retry_policy TEXT,
                    FOREIGN KEY(skill_id) REFERENCES skills(id)
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS skill_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_id INTEGER,
                    status TEXT,
                    input_data TEXT,
                    output_data TEXT,
                    error_message TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    FOREIGN KEY(skill_id) REFERENCES skills(id)
                )
            ''')

            c.execute('''
                CREATE TABLE IF NOT EXISTS skill_step_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_execution_id INTEGER,
                    step_id INTEGER,
                    status TEXT,
                    tool_execution_id INTEGER,
                    latency REAL,
                    error_message TEXT,
                    executed_at TEXT,
                    FOREIGN KEY(skill_execution_id) REFERENCES skill_executions(id),
                    FOREIGN KEY(step_id) REFERENCES skill_steps(id),
                    FOREIGN KEY(tool_execution_id) REFERENCES tool_executions(id)
                )
            ''')
            
            conn.commit()

    def _get_or_create_hypothesis(self, c, statement: str, metric_target: str) -> int:
        c.execute('SELECT id FROM hypotheses WHERE statement = ?', (statement,))
        row = c.fetchone()
        if row:
            return row[0]
        c.execute('INSERT INTO hypotheses (statement, metric_target) VALUES (?, ?)', (statement, metric_target))
        return c.lastrowid

    def start_run(self, profile: str, runner_version: str, worker_id: str) -> str:
        run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        commit = "mock-abc1234"
        pid = os.getpid()
        import socket
        hostname = socket.gethostname()
        
        with self._get_conn() as conn:
            c = conn.cursor()
            try:
                c.execute('''
                    INSERT INTO runs (run_id, started_at, profile, runner_version, git_commit, hostname, pid, status, worker_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (run_id, ts, profile, runner_version, commit, hostname, pid, "RUNNING", worker_id))
            except sqlite3.OperationalError:
                pass # migration pending
            conn.commit()
        return run_id
        
    def finish_run(self, run_id: str, exit_reason: str):
        with self._get_conn() as conn:
            c = conn.cursor()
            ts = datetime.now(timezone.utc).isoformat() + "Z"
            try:
                c.execute("UPDATE runs SET finished_at = ?, status = 'COMPLETED', exit_reason = ? WHERE run_id = ?",
                          (ts, exit_reason, run_id))
            except sqlite3.OperationalError:
                pass
            conn.commit()

    def log_event(self, experiment_id: str, event_type: str, metadata: dict = None):
        with self._get_conn() as conn:
            c = conn.cursor()
            ts = datetime.now(timezone.utc).isoformat() + "Z"
            meta_json = json.dumps(metadata) if metadata else "{}"
            c.execute('INSERT INTO experiment_events (experiment_id, event_type, payload_json, timestamp) VALUES (?, ?, ?, ?)',
                      (experiment_id, event_type, meta_json, ts))

    def log_decision(self, experiment_id: str, run_id: int, decision_point: str, chosen_value: str, 
                     rejected_alternatives: list, reason: str, decision_policy: str, 
                     policy_version: str, confidence: float, inputs_hash: str, seed: int):
        with self._get_conn() as conn:
            c = conn.cursor()
            ts = datetime.now(timezone.utc).isoformat() + "Z"
            c.execute('''
                INSERT INTO experiment_decisions 
                (experiment_id, run_id, decision_point, chosen_value, rejected_alternatives_json, 
                 reason, decision_policy, policy_version, confidence, inputs_hash, seed, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (experiment_id, run_id, decision_point, chosen_value, json.dumps(rejected_alternatives), reason,
                  decision_policy, policy_version, confidence, inputs_hash, seed, ts))
            
    def get_system_state(self, key: str):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute('SELECT value_json FROM system_state WHERE key = ?', (key,))
            row = c.fetchone()
            if row:
                return json.loads(row[0])
            return None
            
    def set_system_state(self, key: str, value: dict):
        with self._get_conn() as conn:
            c = conn.cursor()
            ts = datetime.now(timezone.utc).isoformat() + "Z"
            c.execute('''
                INSERT INTO system_state (key, value_json, updated_at) 
                VALUES (?, ?, ?) 
                ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json, updated_at=excluded.updated_at
            ''', (key, json.dumps(value), ts))

    def lock_experiments_for_calibration(self, worker_id: str, timeout_minutes: int = 30) -> List[ExperimentContract]:
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            now_ts = datetime.now(timezone.utc)
            c.execute("SELECT * FROM experiments WHERE status IN ('PUBLISHED', 'CALIBRATING')")
            rows = c.fetchall()
            
            locked_ids = []
            for row in rows:
                is_available = False
                if row['status'] == 'PUBLISHED':
                    is_available = True
                elif row['status'] == 'CALIBRATING':
                    lock_ts = row['lock_timestamp']
                    if lock_ts:
                        lock_time = datetime.fromisoformat(lock_ts.replace('Z', '+00:00'))
                        if (now_ts - lock_time).total_seconds() > timeout_minutes * 60:
                            is_available = True
                
                if is_available:
                    now_str = now_ts.isoformat() + "Z"
                    if row['status'] == 'PUBLISHED':
                        c.execute("UPDATE experiments SET status = 'CALIBRATING', worker_id = ?, lock_timestamp = ? WHERE experiment_id = ? AND status = 'PUBLISHED'", 
                                  (worker_id, now_str, row['experiment_id']))
                    else:
                        c.execute("UPDATE experiments SET status = 'CALIBRATING', worker_id = ?, lock_timestamp = ? WHERE experiment_id = ? AND status = 'CALIBRATING' AND lock_timestamp = ?", 
                                  (worker_id, now_str, row['experiment_id'], row['lock_timestamp']))
                                  
                    if c.rowcount > 0:
                        locked_ids.append(row['experiment_id'])
                        
            if not locked_ids:
                return []
                
            placeholders = ','.join(['?'] * len(locked_ids))
            c.execute(f"SELECT * FROM experiments WHERE experiment_id IN ({placeholders})", locked_ids)
            
            from src.revenue_os.analytics.schemas import Hypothesis, Variant, Economics
            
            pending = []
            for row in c.fetchall():
                exp = ExperimentContract(
                    experiment_id=row['experiment_id'],
                    market_segment=row['market_segment'],
                    hypothesis=Hypothesis(statement="mock", metric_target="retention"),
                    variant=Variant(id="A", description="mock"),
                    economics=Economics(generation_cost_usd=0.05, revenue_usd=0.0),
                    creative_hash=row['creative_hash'],
                    published_at=row['published_at'],
                    platform=row['platform'],
                    status=row['status']
                )
                pending.append(exp)
            return pending
            
    def log_factory_health(self, metrics: dict):
        with self._get_conn() as conn:
            c = conn.cursor()
            ts = datetime.now(timezone.utc).isoformat() + "Z"
            c.execute('''
                INSERT INTO factory_health (
                    timestamp, render_time, failure_rate, retry_rate, 
                    recovery_time, avg_cpu, avg_ram, disk_usage, 
                    free_disk, audio_failures, subtitle_failures
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ts, metrics.get("render_time", 0.0), metrics.get("failure_rate", 0.0),
                metrics.get("retry_rate", 0.0), metrics.get("recovery_time", 0.0),
                metrics.get("avg_cpu", 0.0), metrics.get("avg_ram", 0.0),
                metrics.get("disk_usage", 0.0), metrics.get("free_disk", 0.0),
                metrics.get("audio_failures", 0), metrics.get("subtitle_failures", 0)
            ))

    def insert_experiment(self, exp: ExperimentContract):
        with self._get_conn() as conn:
            c = conn.cursor()
            
            h_id = self._get_or_create_hypothesis(c, exp.hypothesis.statement, exp.hypothesis.metric_target)
            
            c.execute('''
                INSERT OR REPLACE INTO experiments 
                (experiment_id, hypothesis_id, variant_id, variant_desc, creative_hash, platform, published_at, 
                 generation_cost_usd, revenue_usd, status, run_id, learning_value_score, utm_url, epc, rpc, roi, ltv, cpa)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                exp.experiment_id, h_id, exp.variant.id, exp.variant.description, 
                exp.creative_hash, exp.platform, exp.published_at, 
                exp.economics.generation_cost_usd, exp.economics.revenue_usd, 
                exp.status, exp.run_id, exp.learning_value_score,
                exp.economics.utm_url, exp.economics.epc, exp.economics.rpc,
                exp.economics.roi, exp.economics.ltv, exp.economics.cpa
            ))
            
            c.execute('''
                INSERT OR REPLACE INTO metrics 
                (experiment_id, impressions, ctr_percent, retention_3s_percent, completion_rate_percent, conversion_count, reward_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                exp.experiment_id, 
                exp.real_world_metrics.impressions,
                exp.real_world_metrics.ctr_percent,
                exp.real_world_metrics.retention_3s_percent,
                exp.real_world_metrics.completion_rate_percent,
                exp.real_world_metrics.conversion_count,
                exp.reward_score
            ))
            conn.commit()
            
    def get_experiments_by_hypothesis(self, hypothesis_statement: str) -> List[ExperimentContract]:
        """Reidrata objetos Pydantic do SQLite para consumo do Metrics Engine."""
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            query = '''
                SELECT e.*, m.*, h.statement, h.metric_target 
                FROM experiments e
                JOIN metrics m ON e.experiment_id = m.experiment_id
                JOIN hypotheses h ON e.hypothesis_id = h.id
                WHERE h.statement = ?
            '''
            c.execute(query, (hypothesis_statement,))
            rows = c.fetchall()
            
            results = []
            for r in rows:
                exp = ExperimentContract(
                    experiment_id=r["experiment_id"],
                    hypothesis={
                        "statement": r["statement"],
                        "metric_target": r["metric_target"]
                    },
                    variant={
                        "id": r["variant_id"],
                        "description": r["variant_desc"]
                    },
                    economics={
                        "generation_cost_usd": r["generation_cost_usd"],
                        "revenue_usd": r["revenue_usd"],
                        "utm_url": r["utm_url"] if "utm_url" in r.keys() else None,
                        "epc": r["epc"] if "epc" in r.keys() else 0.0,
                        "rpc": r["rpc"] if "rpc" in r.keys() else 0.0,
                        "roi": r["roi"] if "roi" in r.keys() else 0.0,
                        "ltv": r["ltv"] if "ltv" in r.keys() else 0.0,
                        "cpa": r["cpa"] if "cpa" in r.keys() else 0.0
                    },
                    creative_hash=r["creative_hash"],
                    platform=r["platform"],
                    published_at=r["published_at"],
                    real_world_metrics={
                        "impressions": r["impressions"],
                        "ctr_percent": r["ctr_percent"],
                        "retention_3s_percent": r["retention_3s_percent"],
                        "completion_rate_percent": r["completion_rate_percent"],
                        "conversion_count": r["conversion_count"]
                    },
                    reward_score=r["reward_score"],
                    learning_value_score=r["learning_value_score"] if "learning_value_score" in r.keys() else 0.0,
                    status=r["status"]
                )
                results.append(exp)
            return results

    def enqueue_job(self, experiment_id: str, platform: str, media_path: str, title: str, description: str, link: str, board: str, scheduled_at: Optional[str] = None) -> str:
        """Adiciona um job de publicação na fila."""
        job_id = f"JOB-{uuid.uuid4().hex[:8].upper()}"
        ts = scheduled_at or (datetime.now(timezone.utc).isoformat() + "Z")
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO publication_queue (job_id, experiment_id, platform, media_path, title, description, link, board, scheduled_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            ''', (job_id, experiment_id, platform, media_path, title, description, link, board, ts))
            conn.commit()
        return job_id

    def get_pending_jobs(self) -> List[Dict[str, Any]]:
        """Recupera jobs que estão pendentes e cujo agendamento já passou."""
        now_ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('''
                SELECT * FROM publication_queue 
                WHERE status = 'pending' AND scheduled_at <= ?
            ''', (now_ts,))
            rows = c.fetchall()
            return [dict(r) for r in rows]

    def update_job_status(self, job_id: str, status: str, error_message: Optional[str] = None, attempts_increment: bool = False) -> None:
        """Atualiza o status de processamento de um job."""
        now_ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if attempts_increment:
                c.execute('''
                    UPDATE publication_queue 
                    SET status = ?, error_message = ?, attempts = attempts + 1, processed_at = ?
                    WHERE job_id = ?
                ''', (status, error_message, now_ts, job_id))
            else:
                c.execute('''
                    UPDATE publication_queue 
                    SET status = ?, error_message = ?, processed_at = ?
                    WHERE job_id = ?
                ''', (status, error_message, now_ts, job_id))
            conn.commit()
