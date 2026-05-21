---
title: "Setting the Flask ENV Variable"
description: "How to set the FLASK_APP environment variable so Flask runs the file you want"
excerpt: "How to set the FLASK_APP environment variable on Linux, PowerShell, and Bash"
date: 2022-05-02
categories: Python
tags: [Python, Flask, FLASK_APP, environment-variable, web-server]
ref: python-flask-set-env
---

:bulb: This post covers how to set the FLASK_APP environment variable to run Flask.
{: .notice--info}

# [01] Setting FLASK_APP

- When you run `flask run`, Flask looks for `app.py` or `wsgi.py` in the current directory and starts the server.
- If you renamed those files, you must set `FLASK_APP=<filename>` for it to run correctly.

When the file is named `test.py`:

```shell
# Linux
export FLASK_APP=test

# PowerShell (Windows 10, VSCode)
$env:FLASK_APP="test.py"

# Bash shell (Windows 10, VSCode)
set FLASK_APP=test
```
