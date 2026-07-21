---
name: superpowers
description: >-
  Use this skill to orchestrate multi-agent development loops, perform automated
  testing (pytest), run lint/format checks, and ensure step-by-step verification
  of code changes.
---

# Superpowers: Multi-Agent Verification Loop

This skill enables the agent to act as a self-verifying software engineer by establishing validation loops, spawning verification subagents, and utilizing test coverage.

## Verification Workflow

### 1. Define Verification Criteria
Before editing any files, outline the criteria of success:
- What unit tests should pass?
- What performance/functional bounds must be met?
- Is tipagem estrita (Pydantic v2 schemas) maintained?

### 2. Launch Verification Subagent
If executing complex modifications, invoke a `self` subagent specialized in code review or regression testing.
```json
{
  "TypeName": "self",
  "Role": "Code Reviewer & QA",
  "Prompt": "Review the proposed changes for potential regression, test coverage, and strict typing compliance."
}
```

### 3. Automated Validation Pipeline
Always run the verification scripts and test suites:
- **Run python unit tests**:
  ```powershell
  .\venv\Scripts\python -m pytest tests/unit -v
  ```
- **Run lint and style checks (Ruff & Black)**:
  ```powershell
  ruff check src/
  black --check src/
  ```

### 4. Continuous Calibration & Feedback
- If a test fails, capture the traceback, correct the file, and re-run the test immediately.
- Do not stop until all tests pass with 100% green status.
