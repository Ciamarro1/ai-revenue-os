---
name: db-health-check
description: >-
  Use this skill when the user asks to check the health of the database,
  verify experiment states, audit the publication queue, inspect hypotheses,
  check for AUTOPAUSE flags, or diagnose any data-related issue in the
  AI Revenue OS SQLite database (prod_db.sqlite3).
---

# Database Health Check

This skill provides systematic queries and procedures for auditing the
operational health of the AI Revenue OS database.

## Quick Health Summary
Run these queries sequentially to get a full picture:

### 1. System State (AUTOPAUSE Check)
```sql
SELECT * FROM system_state;
```
- If `AUTOPAUSE = true`, the system has halted all external operations.
- Check the `reason` column for the trigger cause.

### 2. Experiment Pipeline Status
```sql
SELECT status, COUNT(*) as count 
FROM experiments 
GROUP BY status 
ORDER BY count DESC;
```
Expected healthy distribution: Mostly `COMPLETED` or `CALIBRATED`, 
few `FAILED_PERMANENT`, zero stuck in `PUBLISHED`.

### 3. Publication Queue Health
```sql
SELECT status, COUNT(*) as count 
FROM publication_queue 
GROUP BY status;
```
- `pending > 10`: Backlog building up, check QueueWorker
- `failed > 0`: Review error messages:
```sql
SELECT job_id, error_message, attempts, max_attempts 
FROM publication_queue 
WHERE status = 'failed';
```

### 4. Hypothesis Confidence
```sql
SELECT id, statement, status, confidence_score, experiments_count 
FROM hypotheses 
ORDER BY confidence_score DESC 
LIMIT 10;
```
- Validated hypotheses should have `confidence_score > 0.7`
- Rejected hypotheses confirm the system is learning

### 5. Metrics Completeness
```sql
SELECT COUNT(*) as total_experiments,
       COUNT(m.experiment_id) as with_metrics,
       COUNT(*) - COUNT(m.experiment_id) as missing_metrics
FROM experiments e
LEFT JOIN metrics m ON e.experiment_id = m.experiment_id
WHERE e.status NOT IN ('FAILED_PERMANENT', 'FAILED_RETRYABLE');
```

### 6. Calibration Drift
```sql
SELECT AVG(ctr_percent) as avg_ctr,
       MIN(ctr_percent) as min_ctr,
       MAX(ctr_percent) as max_ctr,
       COUNT(*) as sample_size
FROM metrics
WHERE ctr_percent IS NOT NULL;
```

### 7. Run History
```sql
SELECT run_id, profile, started_at, ended_at, status
FROM run_ledger
ORDER BY started_at DESC
LIMIT 5;
```

## Red Flags to Watch For
- AUTOPAUSE = true without a known cause
- `failed` jobs in publication_queue with `attempts >= max_attempts`
- Hypotheses with `experiments_count > 10` still in `testing` status
- Metrics with `ctr_percent = 0.0` across many experiments (possible scraping failure)
- Experiments stuck in intermediate states (`PUBLISHED` but never `OBSERVED`)

## Recovery Actions
- **Clear AUTOPAUSE:** Only after fixing root cause:
  ```sql
  UPDATE system_state SET value = 'false' WHERE key = 'AUTOPAUSE';
  ```
- **Retry failed jobs:** Reset a specific job:
  ```sql
  UPDATE publication_queue SET status = 'pending', attempts = 0 WHERE job_id = 'JOB-XXXX';
  ```
- **Run integrity check:**
  ```powershell
  .\venv\Scripts\python scripts/run_oq_functional.py
  ```
