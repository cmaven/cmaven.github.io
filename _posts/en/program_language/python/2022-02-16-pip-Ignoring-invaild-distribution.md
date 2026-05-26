---
title: "Pip WARNING — Resolving 'Ignoring invalid distribution -ip'"
description: "Why pip emits 'Ignoring invalid distribution -ip' and how to fix it by removing the leftover temporary directory."
excerpt: "Remove the leftover ~ip directory from your site-packages to silence the 'Ignoring invalid distribution' warning."
date: 2022-02-16
last_modified_at: 2026-05-26
categories: Python
tags: [Error, Pip, Venv]
ref: pip-Ignoring-invaild-distribution
---

:bulb: The `WARNING: Ignoring invalid distribution -ip` message means pip found a broken partial installation in your `site-packages` folder. It is safe to remove it manually, and this post walks through every step.
{: .notice--info}

# [01] The Warning and Where It Comes From

When running any `pip install` command you may suddenly see a line like:

```text
WARNING: Ignoring invalid distribution -ip (c:\users\...\lib\site-packages)
```

This warning appears **before** pip does any real work. It does not prevent the installation from succeeding, but it indicates a leftover artifact that can occasionally cause confusing failures in upgrade workflows.

![python-warning, Ignoring invaild distribution -ip](https://user-images.githubusercontent.com/76153041/154229759-3a872fbd-370d-4303-bd15-e053eb2827ed.png)

*Figure 1. The WARNING printed at the top of a `pip install selenium` run.*

## Why Does This Happen?

When pip installs or upgrades a package it creates a temporary staging directory inside `site-packages`. The directory name is the package name prefixed with a tilde (`~`). For example, upgrading pip itself creates `~ip` (short for `~pip` with the `p` already consumed).

If the process is interrupted — by a permission error, a forced kill, a power loss, or an antivirus scan locking the file — the staging directory is never cleaned up. On the next pip run, pip scans `site-packages`, detects the broken directory whose name starts with `~`, and emits the warning.

| Trigger | Likely culprit |
|---|---|
| `Access is denied.` during upgrade | Windows file-lock / antivirus |
| Interrupted shell session | `Ctrl+C` during `pip install` |
| Disk-full condition | Not enough space to complete the write |
| Virtual-env corruption | Force-deleted env while pip was running |

## Where to Look

The warning message itself tells you the exact path, for example:

```text
c:\users\username\appdata\local\programs\python\python310\lib\site-packages
```

Open that directory in your file explorer or terminal and look for any entry whose name **starts with a tilde `~`** (e.g., `~ip`, `~ selenium`, `~numpy`).

![python-warning, Ignoring invaild distribution -ip directory check](https://user-images.githubusercontent.com/76153041/154229906-59930097-fce2-42a9-9c88-acb1fca67dab.png)

*Figure 2. The `site-packages` folder showing the orphaned `~ip` directory.*

# [02] Fixing the Warning

## Step 1 — Verify pip still works

Before deleting anything, confirm pip's current state:

```bash
pip --version
```

If this raises `No module named pip`, stop here and see the companion post on reinstalling pip via `get-pip.py`. If it prints a version number, proceed.

## Step 2 — Delete the orphaned directory

**Windows (PowerShell or cmd):**

```bash
cd C:\Users\<you>\AppData\Local\Programs\Python\Python310\Lib\site-packages
# List candidates first
dir /ad | findstr "^~"
# Remove the orphan (replace ~ip with the actual name shown)
rmdir /s /q ~ip
```

**macOS / Linux:**

```bash
cd $(python -c "import site; print(site.getsitepackages()[0])")
# List candidates
ls -d ~* 2>/dev/null
# Remove
rm -rf "~ip"
```

![python-warning, Ignoring invaild distribution -ip directory deleted](https://user-images.githubusercontent.com/76153041/154229784-99ba096e-8645-45e5-96e6-fe45bcccd276.png)

*Figure 3. The `~ip` directory has been deleted from `site-packages`.*

## Step 3 — Confirm the warning is gone

Re-run any pip command:

```bash
pip install --dry-run selenium
```

The `WARNING: Ignoring invalid distribution` line should no longer appear.

![python-warning, Ignoring invaild distribution -ip WARNING resolved after deletion](https://user-images.githubusercontent.com/76153041/154229799-47af874e-e7a2-4d7e-8d1f-82affd7dc51e.png)

*Figure 4. Clean pip output after the orphaned directory is removed — no WARNING line.*

# [03] Troubleshooting and Edge Cases

### The directory reappears after deletion

This usually means an antivirus or endpoint-protection tool is re-creating the lock. Try:

1. Temporarily disable real-time scanning.
2. Run the pip upgrade in an **elevated** terminal (`Run as Administrator` on Windows, `sudo` on Linux/macOS).
3. Upgrade pip with the module syntax instead of the script:

```bash
python -m pip install --upgrade pip
```

### Multiple `~` directories are present

Delete all of them. Each one corresponds to a separate interrupted installation. They are all safe to remove.

```bash
# PowerShell — remove every ~ directory at once
Get-ChildItem -Path . -Directory | Where-Object { $_.Name -like "~*" } | Remove-Item -Recurse -Force
```

```bash
# bash — same effect
find . -maxdepth 1 -type d -name '~*' -exec rm -rf {} +
```

### pip is missing entirely after cleanup

If removing the directory leaves pip broken, reinstall it:

```bash
python -m ensurepip --upgrade
```

Or download and run the official bootstrapper:

```bash
curl -sS https://bootstrap.pypa.io/get-pip.py | python
```

### Working inside a virtual environment

The path inside a venv is different. Activate the venv first, then find the right `site-packages`:

```bash
source venv/bin/activate          # Linux/macOS
# or
.\venv\Scripts\activate           # Windows

python -c "import site; print(site.getsitepackages())"
```

Navigate to that path and delete the orphaned `~*` directory as above.

# [04] Summary

| Step | Command / Action |
|---|---|
| Check pip health | `pip --version` |
| Find orphan dirs | `ls -d ~*` in `site-packages` |
| Delete orphan | `rm -rf "~ip"` (adjust name) |
| Re-verify | `pip install --dry-run <pkg>` |
| If pip is missing | `python -m ensurepip --upgrade` |

The fix is straightforward: the warning points directly at the problem directory, and removing it silences the warning immediately. No reinstallation of Python is needed in the normal case.
