---
title: "Selenium Error — </button> is not clickable at point"
description: "How to resolve Selenium's 'element is not clickable at point' error using maximize_window() or explicit waits."
excerpt: "Call maximize_window() or scroll the element into view when Selenium cannot click a button due to viewport size."
date: 2022-02-28
last_modified_at: 2026-05-26
categories: Python
tags: [Crawling, Selenium, Error]
ref: selenium-click-error
---

:bulb: Selenium's `element click intercepted` error usually means the target element is outside the visible viewport or covered by another element. Maximizing the browser window is the quickest fix, but this post also covers the other common causes.
{: .notice--info}

# [01] The Error — Element Is Not Clickable at Point

When automating a browser with Selenium, a click action on a button can raise:

```text
Message: element click intercepted: Element <button type="button" class="btn_cancel">
...</button> is not clickable at point (337, 698).
Other element would receive the click: ...
```

![element_position_error](https://user-images.githubusercontent.com/76153041/155912469-cd0d00da-e3e1-4648-8b8e-906c07ea4a49.png)

*Figure 1. Selenium WebDriver raising `element click intercepted` when the button is outside the visible area of a small browser window.*

## Why This Happens

Selenium calculates the click coordinates `(x, y)` relative to the browser viewport. If the browser window is too small — which is the default when ChromeDriver launches a new window — the target element may be:

- **Below the fold** — the element exists in the DOM but is scrolled out of view.
- **Covered** — a sticky header, a cookie banner, or another overlay sits on top of the coordinates Selenium is trying to click.
- **Off-screen** — the element's calculated position is outside the current viewport dimensions entirely.

| Root cause | Description |
|---|---|
| Small default window size | ChromeDriver opens a compact window (~800×600) by default |
| Sticky/fixed overlay | A banner or nav bar covers the element at those coordinates |
| Element not yet rendered | JavaScript has not finished positioning the element |
| Wrong scroll position | Page has not scrolled to bring the element into view |

# [02] Solutions

## Fix 1 — Maximize the window (most common fix)

Call `maximize_window()` immediately after creating the driver. This expands the browser to the full screen size, making most elements reachable without scrolling.

```python
browser = webdriver.Chrome(options=options)
# Add this line right after driver creation
browser.maximize_window()
```

This one line resolves the error in the majority of cases where the window is simply too small.

## Fix 2 — Set an explicit window size

If you are running in a headless environment where `maximize_window()` has no effect, set a fixed large size instead:

```python
browser = webdriver.Chrome(options=options)
browser.set_window_size(1920, 1080)
```

For headless Chrome, also pass the window size as a Chrome option:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
browser = webdriver.Chrome(options=options)
```

## Fix 3 — Scroll the element into view

If the element is below the fold and you cannot resize the window, scroll it into view before clicking:

```python
from selenium.webdriver.common.by import By

element = browser.find_element(By.CSS_SELECTOR, "button.btn_cancel")
browser.execute_script("arguments[0].scrollIntoView(true);", element)
element.click()
```

## Fix 4 — Use JavaScript click as a last resort

When an overlay is blocking the element and cannot be dismissed, a JavaScript-driven click bypasses Selenium's coordinate check entirely:

```python
element = browser.find_element(By.CSS_SELECTOR, "button.btn_cancel")
browser.execute_script("arguments[0].click();", element)
```

Note: JS click skips any pointer-event checks the browser normally enforces. Use it only when the element is genuinely interactive but physically obscured.

## Fix 5 — Wait for overlays to disappear

If a loading spinner or cookie banner temporarily covers the button, wait for it to become invisible before clicking:

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

wait = WebDriverWait(browser, 10)
# Wait until the overlay is gone
wait.until(EC.invisibility_of_element_located((By.ID, "loading-overlay")))
# Then click the button
button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn_cancel")))
button.click()
```

# [03] Troubleshooting

| Symptom | Recommended fix |
|---|---|
| Error on first click after page load | `maximize_window()` or set `--window-size` |
| Error in headless mode only | Add `--window-size=1920,1080` to Chrome options |
| Error due to sticky header | Scroll element into view with `scrollIntoView` |
| Click lands on wrong element | JS click via `execute_script("arguments[0].click()")` |
| Intermittent error (timing-dependent) | Add `WebDriverWait` + `element_to_be_clickable` |

For a broader reference on all causes of this error, see the [Testim blog post on element-not-clickable](https://www.testim.io/blog/selenium-element-is-not-clickable-at-point/).
