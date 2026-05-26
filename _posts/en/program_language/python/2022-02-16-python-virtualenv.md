---
title: "Python Virtual Environment"
description: "How to set up a Python virtual environment with pipenv and venv (Linux, Windows)."
excerpt: "How to create and activate a Python virtual environment using pipenv and venv."
date: 2022-02-16
last_modified_at: 2026-05-26
categories: Python
tags: [Python, Pipenv, Venv, Virtualenv, virtual-environment]
ref: python-virtualenv
---

:bulb: This post covers how to set up a Python virtual environment.
{: .notice--info}

:triangular_flag_on_post: Work in progress
{: .notice--warning}

# [01] pipenv

```shell
apt-get install -y python3-pip
pip3 install --user pipenv

export PIPENV_VENV_IN_PROJECT=true

mkdir venv
cd venv

python3 -m pipenv --python 3.6
python3 -m pipenv install

python3 -m pipenv shell
```

# [02] venv

```shell
python -m venv venv

# Windows
.venv/Script/activate

# Linux
source .venv/bin/activate
```
