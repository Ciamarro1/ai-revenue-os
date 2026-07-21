---
name: agent-skills
description: >-
  Use this skill to perform automated QA audits on frontend/web applications,
  scoring code against performance, UX, and accessibility benchmarks.
---

# Agent Skills: Frontend QA & UX Scanning Engine

This skill outlines guidelines and procedures for auditing web interfaces to ensure they meet modern performance, visual, and accessibility standards.

## Audit Checklist

### 1. Performance
- Ensure critical assets (images, styles) are loaded with appropriate priorities.
- Verify image tags have width and height specified to prevent layout shift.
- Avoid unnecessary script loads in header tags.

### 2. User Experience (UX) & Design
- Validate color contrast ratios to meet contrast standards.
- Check responsive styles: test views on mobile viewports (e.g., 375px width).
- Ensure smooth micro-animations and transition states (e.g., hover effects).

### 3. Accessibility (a11y)
- Every image MUST have a descriptive `alt` attribute.
- Interactive elements must be keyboard-navigable and have distinct `:focus` states.
- Use semantic HTML tags (e.g., `<main>`, `<article>`, `<header>`, `<footer>`) instead of generic nested `<div>`s.

### 4. Scan Implementation
- Run a custom scan script or validation tool when editing frontend code.
- Generate a QA score (0 to 100) before marking frontend tasks as completed.
