---
name: playwright-performance
description: >-
  Use this skill to optimize headless browser resources, selector timeouts,
  viewport setups, and performance profiles in Playwright automation scripts.
---

# Playwright Performance: Browser Optimization

This skill provides rules to configure headless browser workflows efficiently, reducing memory footprint, eliminating selector timing issues, and optimizing resource limits.

## Optimization Rules

### 1. Viewport & Resource Control
- Standardize the viewport size (fixed `1280x800` viewport for consistency).
- Disable loading images/stylesheets when only textual interaction or DOM scraping is needed:
  ```python
  # Route block to speed up page loads
  await page.route("**/*.{png,jpg,jpeg,css}", lambda route: route.abort())
  ```

### 2. Precise Element Selection
- Prefer using robust test attributes (e.g., `data-testid`) over fragile visual coordinates or complex CSS selectors.
- Set explicit timeouts for wait statements instead of using global long sleeps:
  ```python
  # Avoid time.sleep(10). Use explicit selector waits:
  await page.wait_for_selector("[data-testid='submit-button']", timeout=5000)
  ```

### 3. Session State Reusability
- Reuse cookies and local storage states via state files to bypass repetitive logins and prevent rate-limiting triggers.
