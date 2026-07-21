---
name: awesome-agent-skills
description: >-
  Use this skill when you need to bridge the agent into desktop and SaaS tools
  like Slack, Notion, or Gmail using MCP or external webhook integrations.
---

# Awesome Agent Skills: Desktop & API Bridge

This skill defines instructions on how to integrate the agent securely with collaboration, documentation, and messaging systems.

## Integrations

### 1. Slack Notifications
- To send status updates, logs, or alerts to a Slack channel:
  - Verify if a Slack MCP tool or webhook URL is configured in the environment.
  - Send structured JSON payloads to the webhook containing formatted messages, alerts, or summaries.

### 2. Notion Decision Ledger
- Keep the `decisions.jsonl` ledger in sync with a central documentation page:
  - Document system calibrations, hypothesis status (validated/rejected), and experiment outcomes.
  - Write concise, structural bullet points.

### 3. Gmail Reporting
- Format automated performance reports for stakeholders:
  - Focus on clear metrics (impressions, CTR%, retention).
  - List validated hypotheses and any triggered system flags (like AUTOPAUSE).
