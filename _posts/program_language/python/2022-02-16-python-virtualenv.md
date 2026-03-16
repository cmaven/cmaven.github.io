---
title: "Python 가상 환경(Virtual Environment)"
description: "Python 가상 환경을 pipenv, venv로 구성하는 방법 (Linux, Windows)"
excerpt: "pipenv, venv를 사용한 Python 가상 환경 구성 및 활성화 방법"
date: 2022-02-16
categories: Python
tags: [Python, Pipenv, Venv, Virtualenv, 가상환경]
---

:bulb: Python 가상 환경(Virtual Environment)을 구성하는 방법을 작성한다.
{: .notice--info}

:triangular_flag_on_post: 작성 중
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
