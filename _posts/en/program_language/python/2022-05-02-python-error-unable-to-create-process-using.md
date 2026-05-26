---
title: "Python Fatal error in launcher — Unable to create process"
description: "How to fix the path error that occurs when using a Python venv virtual environment cloned from a different machine."
excerpt: "How to fix the Unable to create process using error when reusing a venv environment cloned from git on another machine"
date: 2022-05-02
last_modified_at: 2026-05-26
categories: Python
tags: [Python, Error, Venv, virtual-environment, pip, Fatal-error]
ref: python-error-unable-to-create-process-using
---

:bulb: This post covers how to fix the process path error that prevents Python or pip commands from running inside a cloned virtual environment.
{: .notice--info}

# [01] Situation

- **Environment**: Windows 10, VSCode, Git
- Set up a Python `venv` virtual environment on **Machine A**
- Committed and pushed the entire project — including the `venv/` folder — to a GitHub repository
- Cloned (`git clone`) the repository on **Machine B** to continue work
- Entered the virtual environment with `.\venv\Scripts\activate` and ran `python` or `pip` commands
- The following error appeared immediately:

```text
Fatal error in launcher: Unable to create process using "path1" "path2"
```

![Fatal error in launcher: Unable to create process using error](https://user-images.githubusercontent.com/76153041/166196784-6a0f42e0-6add-4129-a556-4b6270f84a64.png)

*Figure 1. The "Fatal error in launcher: Unable to create process" error when running pip inside a venv cloned from another machine.*

# [02] Cause

A Python virtual environment stores **absolute paths** to the Python interpreter and pip executable inside several configuration files:

- `venv/Scripts/python.exe` — a wrapper that points back to the base Python
- `venv/Scripts/pip.exe` — similarly path-embedded
- `venv/pyvenv.cfg` — records `home = C:\Users\...\Python39` (the base interpreter path)

When Machine A creates the environment, it bakes in paths like `E:\Projects\myapp\venv\...`. After cloning on Machine B, those paths no longer exist — Machine B may have Python installed on `D:\` instead, or under a different username. Every launcher script fails because it cannot find the executable at the recorded path.

| Item | Machine A | Machine B |
|------|-----------|-----------|
| Python base path | `E:\Python39` | `D:\Python310` |
| venv path | `E:\Projects\app\venv` | `C:\Users\user\app\venv` |
| Result | Works | Launcher fails |

# [03] Solution

:warning: The methods below are workarounds. The fundamental fix is to **never commit the `venv/` folder** — add it to `.gitignore` and share only `requirements.txt` instead. If the runtime environment changes frequently, you will need to reinstall every time regardless.
{: .notice--warning}

## 3-1. Upgrade the Virtual Environment (Recommended)

Run this command **before** activating the virtual environment. It rewrites the launcher scripts with paths pointing to the currently active Python interpreter:

```shell
python -m venv --upgrade venv
```

After this completes, activate and verify:

```shell
.\venv\Scripts\activate
python --version
pip --version
```

## 3-2. Reinstall pip Inside the Environment

If `--upgrade` does not fully resolve the problem — for example if pip's launcher is still broken — reinstall pip from inside the activated environment:

```shell
# First, enter the virtual environment
.\venv\Scripts\activate

# Force-reinstall pip to rewrite its launcher
python -m pip install --upgrade --force-reinstall pip
```

If a specific package (e.g., Flask) also has a broken launcher, reinstall it:

```shell
pip uninstall flask
pip install flask
```

## 3-3. Recreate the Environment from Scratch (Most Reliable)

If the above steps still leave broken launchers, the cleanest solution is to delete the environment and recreate it:

```shell
# Delete the old venv folder
rm -rf venv          # Linux / macOS / Git Bash
Remove-Item -Recurse -Force venv   # PowerShell

# Recreate
python -m venv venv
.\venv\Scripts\activate

# Reinstall all packages
pip install -r requirements.txt
```

# [04] Prevent the Problem in the Future

Add the virtual environment folder to `.gitignore` so it is never committed:

```text
# .gitignore
venv/
.venv/
env/
```

Then export your dependencies before pushing:

```shell
pip freeze > requirements.txt
```

Teammates can recreate the environment on their machine with one command:

```shell
python -m venv venv
source venv/bin/activate     # Linux / macOS
.\venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

This approach is portable across machines, operating systems, and Python versions.
