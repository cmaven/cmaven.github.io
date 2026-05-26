---
title: "Setting the Flask ENV Variable"
description: "How to set the FLASK_APP environment variable on Linux, PowerShell, and Bash so Flask runs the file you want."
excerpt: "How to set the FLASK_APP environment variable on Linux, PowerShell, and Bash"
date: 2022-05-02
last_modified_at: 2026-05-26
categories: Python
tags: [Python, Flask, FLASK_APP, environment-variable, web-server]
ref: python-flask-set-env
---

:bulb: This post covers how to set the `FLASK_APP` environment variable so `flask run` starts the correct file.
{: .notice--info}

# [01] Why FLASK_APP Matters

When you run `flask run`, Flask looks for an application in the following order:

1. `app.py` in the current directory
2. `wsgi.py` in the current directory
3. The value of the `FLASK_APP` environment variable

If your entry-point file has any other name — for example `test.py`, `server.py`, or `main.py` — Flask cannot find it automatically and exits with an error similar to:

```text
Error: Could not locate a Flask application. Use the 'flask --app' option, 'FLASK_APP' environment variable, or a 'wsgi.py' file in the current directory.
```

Setting `FLASK_APP` tells Flask exactly which file (or module) to import.

# [02] Setting FLASK_APP

Choose the command that matches your operating system and shell.

## Linux / macOS (Bash or Zsh)

```shell
export FLASK_APP=test
flask run
```

The `export` command makes the variable available to child processes. If you want it to persist across terminal sessions, add it to `~/.bashrc` or `~/.zshrc`.

## Windows — PowerShell

```powershell
$env:FLASK_APP="test.py"
flask run
```

In PowerShell, environment variables are set via `$env:`. This lasts for the current session only.

## Windows — Command Prompt (CMD)

```shell
set FLASK_APP=test
flask run
```

## Windows — Bash (Git Bash / WSL)

```shell
set FLASK_APP=test
flask run
```

# [03] Persistent Configuration with .env

Typing the export command every time is repetitive. Flask supports a `.env` file in the project root that is loaded automatically when `python-dotenv` is installed:

```shell
pip install python-dotenv
```

Create `.env` in the project root:

```text
FLASK_APP=test.py
FLASK_ENV=development
```

From now on, `flask run` picks up both variables without any manual export.

:warning: Add `.env` to your `.gitignore` to avoid committing secrets.
{: .notice--warning}

# [04] Quick Reference

| Platform | Command |
|----------|---------|
| Linux / macOS | `export FLASK_APP=test` |
| PowerShell | `$env:FLASK_APP="test.py"` |
| CMD | `set FLASK_APP=test` |
| Persistent (any OS) | Add `FLASK_APP=test.py` to `.env` + install `python-dotenv` |

# [05] Modern Alternative — flask --app Flag

Flask 2.2+ added the `--app` CLI option, which avoids the environment variable entirely:

```shell
flask --app test run
```

This is the recommended approach for newer projects because it is explicit and works identically on all platforms without exporting variables.

# [06] Notes

Once `FLASK_APP` is set, Flask resolves the application factory automatically. For multi-environment workflows, keep the variable in a `.env` file checked into the project (without secrets) and load it via `python-dotenv` or your shell profile. Distinguish between development (`FLASK_ENV=development`) and production by exporting different `.env` files in CI/CD.
