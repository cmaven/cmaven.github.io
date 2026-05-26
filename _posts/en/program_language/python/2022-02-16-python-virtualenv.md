---
title: "Python Virtual Environment"
description: "How to set up a Python virtual environment with pipenv and venv on Linux and Windows."
excerpt: "How to create and activate a Python virtual environment using pipenv and venv."
date: 2022-02-16
last_modified_at: 2026-05-26
categories: Python
tags: [Python, Pipenv, Venv, Virtualenv, virtual-environment]
ref: python-virtualenv
---

:bulb: This post covers how to set up a Python virtual environment using both `pipenv` and the built-in `venv` module.
{: .notice--info}

# [01] Why Use a Virtual Environment?

A virtual environment isolates a project's Python packages from the system-wide Python installation. Without isolation, installing a library for one project can break another project that depends on a different version. Virtual environments solve this by giving each project its own private package directory.

| Tool | Key Feature | Best For |
|------|------------|---------|
| `venv` | Built into Python 3.3+ | Simple, dependency-light projects |
| `pipenv` | Combines pip + venv + Pipfile.lock | Projects that need reproducible lockfiles |

# [02] pipenv

`pipenv` manages both the virtual environment and a `Pipfile.lock` that pins exact dependency versions, making environments reproducible across machines.

## Install pipenv

```shell
apt-get install -y python3-pip
pip3 install --user pipenv
```

## Create and Activate the Environment

```shell
# Keep the .venv folder inside the project directory
export PIPENV_VENV_IN_PROJECT=true

mkdir myproject
cd myproject

# Create a new virtual environment targeting Python 3.6
python3 -m pipenv --python 3.6

# Install dependencies from Pipfile (or create an empty environment)
python3 -m pipenv install

# Activate the shell
python3 -m pipenv shell
```

After running `pipenv shell`, your prompt will change to show the environment name. Run `exit` to leave it.

## Key pipenv Commands

| Command | What it does |
|---------|-------------|
| `pipenv install <package>` | Install a package and add it to `Pipfile` |
| `pipenv install --dev <package>` | Install a dev-only dependency |
| `pipenv uninstall <package>` | Remove a package |
| `pipenv lock` | Update `Pipfile.lock` with pinned versions |
| `pipenv run python script.py` | Run a script without activating the shell |

# [03] venv

`venv` is built into Python 3 and requires no additional installation. It is the simplest way to create an isolated environment.

## Create and Activate

```shell
# Create a virtual environment named "venv" in the current directory
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate

# Activate on Linux / macOS
source .venv/bin/activate
```

Once activated, `pip install` installs packages into the local environment only. Your prompt will show `(venv)` to indicate the active environment.

## Deactivate

```shell
deactivate
```

## Recreate from requirements.txt

```shell
# Save current packages
pip freeze > requirements.txt

# On another machine: create a fresh venv and install
python -m venv venv
source venv/bin/activate       # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
```

# [04] Choosing Between pipenv and venv

- Use **venv** when you want the smallest footprint and are already managing a `requirements.txt`.
- Use **pipenv** when you need a lockfile (`Pipfile.lock`) for deterministic installs across CI and team members.

Both achieve the same core goal — package isolation — so the right choice depends on your project's complexity.
