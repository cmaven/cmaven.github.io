---
title: "Python 가상 환경(Virtual Environment)"
date: 2022-02-16
categories: Python
tags: [Pipenv, Venv, Virtualenv]
---

Python 가상 환경 구성 방법
------

**작성 중**


``` shell
apt-get install -y python3-pip
pip3 install --user pipenv

export PIPENV_VENV_IN_PROJECT=true

mkdir venv
cd venv

python3 -m pipenv --python 3.6
python3 -m pipenv install

python3 -m pipenv shell
```


``` shell
python -m venv venv

# Windows
.venv/Script/activate

# Linux
source .venv/bin/activate
```


