---
name: pinterest-debug
description: >-
  Use this skill when the user needs to debug Pinterest integration issues,
  validate session cookies, test the Playwright publisher, troubleshoot upload
  failures, check Vision Fallback behavior, or diagnose any issue related to
  the Pinterest API client or browser automation in the AI Revenue OS.
---

# Pinterest Debug Protocol

This skill provides a systematic approach to debugging the Pinterest integration
layer, which spans both the API client (`src/integrations/pinterest/`) and the
Playwright-based publisher (`src/execution/publisher/pinterest_playwright.py`).

## Architecture Overview
```
Pinterest Integration has TWO independent paths:
1. API Path: src/integrations/pinterest/ → Official Pinterest v5 API (metrics, auth)
2. Browser Path: src/execution/publisher/pinterest_playwright.py → Playwright (upload, publish)
```

## Step 1: Validate Session Cookies

Check if the session file exists and is not expired:
```powershell
Test-Path config/sessions/pinterest.json
```

If missing or expired, re-authenticate:
```powershell
.\venv\Scripts\python scripts/setup_session.py --platform pinterest
```
This opens a **headful** browser for manual login. After login, cookies are persisted.

## Step 2: Test API Health
```powershell
.\venv\Scripts\python scripts/run_pinterest_op.py --operation health_check
```

Expected output:
- ✅ Authentication valid
- ✅ Rate limits OK (check `knowledge/rate_limits.db`)
- ✅ Board access confirmed

### Common API Issues
| Error | Cause | Fix |
| :--- | :--- | :--- |
| 401 Unauthorized | Token expired | Re-run `setup_session.py` |
| 429 Too Many Requests | Rate limit hit | Wait 60s, check `rate_limit.py` |
| 403 Forbidden | App not approved | Check Pinterest Developer Console |

## Step 3: Test Playwright Publisher (Headless)

Run a dry test of the publisher without actually posting:
```powershell
.\venv\Scripts\python -c "
from src.execution.publisher.pinterest_playwright import PinterestPlaywrightPublisher
pub = PinterestPlaywrightPublisher()
print('Publisher initialized successfully')
"
```

### Playwright Debug Checklist
1. **Viewport:** Must be 1280x800 (hardcoded for Vision Fallback consistency)
2. **Cookies loaded:** Check that `config/sessions/pinterest.json` has valid entries
3. **Headless mode:** Default for automation; use `--headed` flag in setup_session only
4. **Selectors:** If Pinterest changes their UI, selectors may break → Vision Fallback activates

## Step 4: Test Vision Fallback

If the Playwright publisher encounters a broken selector, it:
1. Takes a screenshot of the current page
2. Sends it to Gemini 2.5 Flash (via OpenRouter API)
3. Gemini returns either a text selector (`text="Salvar"`) or pixel coordinates `(x, y)`
4. The publisher retries the action with the new selector

**Verify OpenRouter API key is set:**
```powershell
$env:OPENROUTER_API_KEY
```

## Step 5: Check Publication Evidence

After a successful (or failed) publish, evidence is stored:
```
experiments/<EXP-ID>/publication_evidence/
├── publish_success.png    # Screenshot of success state
├── publish_failure.png    # Screenshot if failed
└── publication_evidence.json  # Step-by-step log
```

Review the evidence:
```powershell
Get-ChildItem experiments/*/publication_evidence/ -Recurse
```

## Step 6: Check Queue Worker

The QueueWorker processes jobs from the `publication_queue` table:
```powershell
.\venv\Scripts\python src/execution/queue_worker.py
```

Query pending jobs:
```sql
SELECT job_id, platform, status, attempts, error_message 
FROM publication_queue 
ORDER BY scheduled_at DESC 
LIMIT 10;
```

## Step 7: Metrics Scraping

After publication (24-72h wait), verify metrics collection:
```powershell
.\venv\Scripts\python scripts/run_metrics_sync.py
```

Check scraped data:
```sql
SELECT e.experiment_id, m.impressions, m.ctr_percent, m.retention_3s_percent
FROM experiments e
JOIN metrics m ON e.experiment_id = m.experiment_id
WHERE e.platform = 'pinterest'
ORDER BY e.published_at DESC
LIMIT 5;
```

## Common Failure Patterns

| Symptom | Likely Cause | Resolution |
| :--- | :--- | :--- |
| "Element not found" in logs | Pinterest UI changed | Vision Fallback should auto-recover; if not, update selectors in `pinterest_playwright.py` |
| Empty screenshots | Playwright crashed or page didn't load | Check if cookies are valid; re-run `setup_session.py` |
| CAPTCHA detected | Too many automated actions | Pause operations 24h; consider adding delays between publishes |
| "Circuit Breaker Open" | Too many provider failures | Check `src/mcp/health_monitor.py` health scores |
| Metrics show all zeros | Scraping selector broke or pin was removed | Manually verify the pin exists on Pinterest |
