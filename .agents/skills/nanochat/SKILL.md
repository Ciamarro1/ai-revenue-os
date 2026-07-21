---
name: nanochat
description: >-
  Use this skill to apply Andrej Karpathy's Coding Guidelines to eliminate LLM
  hallucinations and bad coding habits, enforcing strict verification and minimal edits.
---

# Nanochat: Andrej Karpathy's Coding Guidelines

This skill implements specific rules to systematically eliminate LLM hallucinations, avoid breaking existing features, and maintain clean and verifiable code codebases.

## Core Rules

1. **Be Skeptical of Your Initial Code**:
   - Double check your assumptions about existing APIs, methods, and functions.
   - Do not hallucinate or guess parameter names. Read the source code or definitions of imports first.

2. **Strict Verification**:
   - Every file change must be immediately verified by tests if available.
   - Do not complete a task until you run the target tests.

3. **Incremental and Clean Edits**:
   - Prefer making small, precise, contiguous edits using the `replace_file_content` tool.
   - Avoid rewriting entire files or large chunks if you are only changing a few lines.
   - Preserve comments and formatting.

4. **Verify Imports and Types**:
   - Ensure all imports exist and classes/functions are typed with strict type annotations (like Pydantic v2 schemas).
