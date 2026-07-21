---
name: security-audit
description: >-
  Use this skill to audit secret storage, verify API key protection, and
  prevent credentials leakage in source code and decision logs.
---

# Security Audit: Secrets & Token Protection

This skill establishes workflows to ensure API keys, access tokens, and environment parameters remain fully isolated from the codebase, version control, and public logs.

## Audit Checklist

### 1. Secret Exposure Prevention
- **NO Hardcoded Keys**: Verify that no files in `src/` or `scripts/` contain raw strings matching API keys.
- **`.gitignore` Check**: Ensure `.env` and `prod_db.sqlite3` are always ignored by version control.
- **Log Sanitization**: Never write tokens, cookies, or authorization headers into `decisions.jsonl` or standard output logs.

### 2. Environment Validation
- Ensure key variables are read exclusively via Python's standard library or Pydantic `BaseSettings`:
  ```python
  import os
  api_key = os.getenv("GEMINI_API_KEY")
  ```

### 3. Dependency Check
- Regularly run a vulnerability scanner on the virtual environment:
  ```powershell
  pip install safety
  safety check
  ```
