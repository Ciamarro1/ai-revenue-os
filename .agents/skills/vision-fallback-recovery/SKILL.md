---
name: vision-fallback-recovery
description: >-
  Use this skill to implement self-healing browser automation using Vision LLMs
  (Gemini 2.5 Flash) when CSS/XPath selectors break.
---

# Vision Fallback Recovery: Self-Healing Playwright Scripts

This skill defines the workflow for self-healing browser automation. When DOM selectors fail or layouts change unexpectedly, the system leverages Vision LLM to resolve element coordinates from screenshots.

## Self-Healing Workflow

### 1. Detect Failure
- If a Playwright selector throws a `TimeoutError` or fails to locate an element:
  - Capture a full page screenshot.
  - Save the page layout hierarchy.

### 2. Query Vision LLM (Gemini 2.5 Flash)
- Send the screenshot along with a visual instruction query to the Vision model:
  - *"Inspect this screenshot. Find the bounding box coordinates (or center point) of the red 'Publish' button."*
  - Format the prompt to return normalized bounding box coordinates `[ymin, xmin, ymax, xmax]`.

### 3. Coordinate Translation & Atruation
- Map the normalized LLM coordinates back to the actual page viewport size:
  ```python
  x = center_x * viewport_width
  y = center_y * viewport_height
  ```
- Trigger a programmatic click directly at the calculated coordinate:
  ```python
  await page.mouse.click(x, y)
  ```
