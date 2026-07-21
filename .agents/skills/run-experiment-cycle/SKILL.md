---
name: run-experiment-cycle
description: >-
  Use this skill when the user asks to run, debug, validate, or troubleshoot
  a complete experiment cycle of the AI Revenue OS. Covers the 9-state pipeline
  from CREATED through CALIBRATED, including readiness checks, quality gates,
  and post-run verification. Also use when the user mentions ExperimentRunner,
  shadow mode, canary release, or experiment states.
---

# Run Experiment Cycle

This skill guides the agent through running and validating the AI Revenue OS
experiment pipeline — the core loop that discovers and validates revenue-generating
content patterns.

## Prerequisites
1. Verify the virtual environment is active: `.\venv\Scripts\python --version`
2. Ensure `prod_db.sqlite3` exists and is not locked
3. Confirm API keys are set in `.env` (OPENROUTER_API_KEY, NVIDIA_API_KEY)

## Steps

### 1. Readiness Check
Run the infrastructure validator:
```powershell
.\venv\Scripts\python scripts/run_readiness_check.py
```
Confirm all checks pass (Health Score >= 90.0, no AUTOPAUSE flag).

### 2. Run the Experiment (Stop at Quality Check)
For a controlled test, stop before publication:
```powershell
.\venv\Scripts\python -m src.services.experiment_runner --stop-at-state QUALITY_CHECKED
```

### 3. Validate Generated Assets
- Check the experiment folder: `experiments/<EXP-ID>/`
- Verify media files exist (`.mp4` or `.jpg`)
- Confirm `manifest.json` or metadata files are present

### 4. Verify Database State
Query the database for the experiment:
```sql
SELECT experiment_id, status, hypothesis_id FROM experiments ORDER BY rowid DESC LIMIT 5;
SELECT * FROM publication_queue WHERE status = 'pending';
```

### 5. Run Unit Tests (Regression Check)
```powershell
.\venv\Scripts\python -m pytest tests/unit -v --tb=short
```
All tests must pass before proceeding.

### 6. Full Pipeline (If Ready for Canary)
To run the complete cycle including publication:
```powershell
.\venv\Scripts\python scripts/run_exp_001b0_canary.py
```

## Troubleshooting
- **AUTOPAUSE activated:** Check Health Score via `scripts/run_dashboard.py`
- **FAILED_PERMANENT:** Check `error_message` in `experiments` table
- **Quality Gate failure:** Review `render_qa.py` output in experiment folder
- **Provider timeout:** Check circuit breaker status in `src/mcp/health_monitor.py`

## Post-Run Verification
- Run the OQ Functional test: `.\venv\Scripts\python scripts/run_oq_functional.py`
- Confirm the Decision Ledger was updated (check `decisions.jsonl` or `decisions_ledger` table)
