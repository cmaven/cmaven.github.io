---
title: "Pip Error — ERROR: No module named pip"
description: "How to recover when 'No module named pip' appears during a pip upgrade — reinstall pip using get-pip.py or ensurepip."
excerpt: "Reinstall pip with get-pip.py or python -m ensurepip when a failed upgrade leaves pip missing entirely."
date: 2022-02-16
last_modified_at: 2026-05-26
categories: Python
tags: [Error, Pip, Venv]
ref: pip-error-no-module
---

:bulb: Running `pip install --upgrade pip` can leave pip in a broken state if the reinstall step fails mid-way. This post shows how to get pip working again without reinstalling Python.
{: .notice--info}

# [01] The Problem — pip Disappears After an Upgrade Attempt

When pip upgrades itself it first **uninstalls** the current version, then installs the new one. If that second step fails — due to a permission error, a disk-full condition, or an antivirus lock — the old pip is already gone and the new one never landed. The result is a Python environment with no pip at all.

## Symptoms

- After running `pip install --upgrade pip`, the terminal shows `Access is denied.`
- Any follow-up command using `pip` raises `No module named pip`.

```text
$ pip install --upgrade pip
ERROR: Access is denied.

$ python -m pip install --upgrade pip
C:\...\python.exe: No module named pip
```

![01_get-pip install when pip suddenly stops working](https://user-images.githubusercontent.com/76153041/154236547-701486e1-087f-49a5-ba01-889958cadbc4.png)

*Figure 1. `No module named pip` printed after a failed self-upgrade leaves no pip installed.*

## Why This Happens

`pip install --upgrade pip` is a special case: pip is asked to replace a file it is currently running from. On Windows especially, the file lock held by the running process can block the write, causing the two-phase uninstall-then-install to abort between phases.

| Phase | What happens on failure |
|---|---|
| Uninstall old pip | Old pip files are removed |
| Install new pip | Write blocked → new pip files never appear |
| Net result | **No pip at all** |

# [02] Solution — Reinstall pip

## Option A: get-pip.py (works everywhere)

Download the official pip bootstrapper and run it directly with your Python interpreter. This bypasses pip's self-upgrade mechanism entirely.

```bash
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

On Windows without `curl`:

```bash
# PowerShell
Invoke-WebRequest -Uri https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py
python get-pip.py
```

After running `get-pip.py`, verify the installation:

```bash
pip --version
```

![02_get-pip install when pip suddenly stops working](https://user-images.githubusercontent.com/76153041/154235531-dd61c88a-1c63-4e0a-a85e-a26e400d549e.png)

*Figure 2. `get-pip.py` successfully reinstalls pip and prints the new version.*

## Option B: ensurepip (built into Python 3.4+)

Python ships with a built-in module called `ensurepip` that can install pip without any network download:

```bash
python -m ensurepip --upgrade
```

If this raises `ensurepip is disabled in this environment` (common in system Python on Debian/Ubuntu), use Option A or install the distro package:

```bash
sudo apt install python3-pip
```

## Option C: Upgrade safely in the future

To avoid the permission issue on Windows, always run the upgrade through the module interface rather than through the pip script itself:

```bash
python -m pip install --upgrade pip
```

This invokes pip as a Python module rather than an executable, which sidesteps the file-lock problem on most systems.

# [03] Troubleshooting

| Symptom | Fix |
|---|---|
| `Access is denied` on Windows | Run terminal as Administrator, or use `python -m pip` |
| `ensurepip is disabled` | Use `get-pip.py` or `apt install python3-pip` |
| pip installs but wrong version | Run `pip install --upgrade pip` after bootstrapping |
| Inside a venv, pip still missing | Recreate venv: `python -m venv --upgrade-deps venv` |

After recovery, check the pip version and the Python it belongs to to make sure everything is consistent:

```bash
pip --version
# Example output: pip 24.0 from /usr/local/lib/python3.11/site-packages/pip (python 3.11)
which pip       # Linux/macOS
where pip       # Windows
```
