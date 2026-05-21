---
title: "Python Fatal error in launcher — Unable to create process"
description: "How to fix the path error that occurs when using a Python venv virtual environment on a different machine"
excerpt: "How to fix the Unable to create process using error when reusing a venv environment cloned from git on another machine"
date: 2022-05-02
categories: Python
tags: [Python, Error, Venv, virtual-environment, pip, Fatal-error]
ref: python-error-unable-to-create-process-using
---

:bulb: This post covers how to fix the process path error that prevents Python or pip commands from running.
{: .notice--info}

# [01] Situation

- Environment: Windows 10, VSCode, Git
- Set up a Python venv on Machine A
- Uploaded the result to a GitHub repository
- Downloaded (git clone) the repository on Machine B to continue work
- Entered the virtual environment (`.\venv\Scripts\activate`) and ran python/pip commands, triggering the following error:
  - Fatal error in launcher: Unable to create process using "path1" "path2"

![python-interpretor error](https://user-images.githubusercontent.com/76153041/166196784-6a0f42e0-6add-4129-a556-4b6270f84a64.png)

# [02] Cause

The Python/pip paths baked into the virtual environment differ between machines (e.g., `E:...` on Machine A vs. `D:...` on Machine B).

# [03] Solution

:warning: The methods below are workarounds. If the runtime environment changes, you have to reinstall every time. You should look into whether only the venv environment variables can be updated.
{: .notice--warning}

## 3-1. Upgrade the virtual environment

```shell
# Before entering the virtual environment
python -m venv --upgrade venv
```

## 3-2. Reinstall packages

```shell
# After entering the virtual environment, reinstall pip
python -m pip install --upgrade --force-reinstall pip

# Reinstall the package that throws the error
pip uninstall flask
pip install flask
```
