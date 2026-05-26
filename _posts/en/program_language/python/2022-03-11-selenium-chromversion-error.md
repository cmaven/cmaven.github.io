---
title: "Selenium SessionNotCreatedException — ChromeDriver Version Error"
description: "How to fix Selenium's SessionNotCreatedException caused by a ChromeDriver version mismatch, and how to use webdriver-manager for automatic version matching."
excerpt: "Fix Selenium's SessionNotCreatedException by installing webdriver-manager for automatic ChromeDriver version matching."
date: 2022-03-11
last_modified_at: 2026-05-26
categories: Python
tags: [Error, Selenium, ChromeDriverManager, Webdrivermanager, ChromeDriver, version-mismatch]
ref: selenium-chromversion-error
---

:bulb: This post explains how to fix the **`SessionNotCreatedException`** error in Selenium caused by a ChromeDriver version mismatch, and how to use **webdriver-manager** so the correct driver version is always selected automatically.
{: .notice--info}

# [01] The Problem — ChromeDriver Version Mismatch

When you run a Selenium script that calls `webdriver.Chrome()`, you may encounter an error like the following:

```python
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
browser = webdriver.Chrome(options=options)
```

![selenium common exceptions Error](https://user-images.githubusercontent.com/76153041/157777747-7d159990-d730-40ca-b990-a8cf214506e8.png)

*Figure 1. `SessionNotCreatedException` — the installed ChromeDriver version does not match the installed Chrome browser version.*

The error message usually reads:

```text
selenium.common.exceptions.SessionNotCreatedException:
Message: session not created: This version of ChromeDriver only supports Chrome version XX
Current browser version is YY.Z.AAAA.BB
```

### Why This Happens

Selenium's `webdriver.Chrome()` requires a separate **ChromeDriver** binary that must match the major version of your installed Chrome browser. Chrome updates automatically and silently in the background, so the locally installed ChromeDriver quickly falls out of sync. The table below shows what triggers the mismatch:

| Event | Effect |
|---|---|
| Chrome auto-updates to a new major version | ChromeDriver becomes incompatible overnight |
| You install Chrome for the first time without downloading ChromeDriver | No driver binary found at all |
| You manually downloaded ChromeDriver months ago | ChromeDriver version is stale |
| You deploy to a new machine with a different Chrome version | Hard-coded driver path breaks |

### How to Find Your Current Chrome Version

Before fixing the issue it is useful to confirm the installed Chrome version:

- **Windows**: Open Chrome → `⋮` menu → Help → About Google Chrome
- **macOS**: Chrome menu → About Google Chrome
- **Linux (Ubuntu/Debian)**:

```shell
google-chrome --version
# Example output: Google Chrome 124.0.6367.201
```

The first number (`124` in the example) is the major version. ChromeDriver must share the same major version number.

# [02] Solution — webdriver-manager for Automatic Version Matching

Manually downloading and updating ChromeDriver is error-prone. The **`webdriver-manager`** library solves this entirely: it queries the ChromeDriver release API, downloads the correct driver for your installed Chrome version, and caches it locally.

### Step 1 — Install webdriver-manager

```shell
pip install webdriver-manager
```

### Step 2 — Update Your Selenium Script

Replace the plain `webdriver.Chrome()` call with one that uses `ChromeDriverManager().install()`:

```python
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

service = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=options)
```

> **Note:** Selenium 4.x introduced the `Service` object. Passing the driver path directly as the first positional argument (the Selenium 3 style) still works but is deprecated.

On first run `webdriver-manager` prints the driver download progress to the console. Subsequent runs use the cached binary unless Chrome has updated.

### What webdriver-manager Does Internally

| Step | Detail |
|---|---|
| Reads installed Chrome version | Queries the local Chrome binary for its version string |
| Fetches matching ChromeDriver | Downloads from the official ChromeDriver release endpoint |
| Caches the binary | Stores under `~/.wdm/` (or `%USERPROFILE%\.wdm\` on Windows) |
| Auto-updates | Re-downloads if the cached version no longer matches Chrome |

# [03] Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `SessionNotCreatedException` persists after installing webdriver-manager | Old-style call without `Service` object | Use `Service(ChromeDriverManager().install())` as shown above |
| `WebDriverException: ChromeDriver only supports Chrome version XX` | `webdriver-manager` cached an old driver | Delete `~/.wdm/` and re-run the script |
| `ModuleNotFoundError: No module named 'webdriver_manager'` | Package not installed in active environment | Activate your virtualenv, then run `pip install webdriver-manager` |
| Script hangs on driver download in CI/offline environment | No internet access to download driver | Pre-download the driver and pass the path directly with `Service('/path/to/chromedriver')` |
| Chrome opens but immediately closes | ChromeDriver version matched but Chrome binary path is wrong | Set `options.binary_location` to the explicit Chrome install path |

Reference: [https://stackoverflow.com/questions/60296873/sessionnotcreatedexception-message-session-not-created-this-version-of-chrome](https://stackoverflow.com/questions/60296873/sessionnotcreatedexception-message-session-not-created-this-version-of-chrome)
