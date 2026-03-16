---
title: "Fatal error in launcher-Unable to create process using"
description: "Python venv 가상환경을 다른 머신에서 사용할 때 발생하는 경로 오류 해결 방법"
excerpt: "venv 환경을 git clone으로 다른 머신에서 사용 시 Unable to create process using 오류 해결법"
date: 2022-05-02
categories: Python
tags: [Python, Error, Venv, 가상환경, pip, Fatal-error]
---

:bulb: Python 또는 Pip 명령어 실행 시, Process 경로 오류로 실행되지 않을 때의 해결 방법을 작성한다.
{: .notice--info}

# [01] 상황

- 환경: Windows 10, VSCode, Git
- Machine A에서 Python의 venv 환경을 구성
- 결과물을 Github Repository에 업로드
- Machine B에서 추가작업을 위해 Github Repository 다운로드(git clone)
- 가상환경에 진입하여(`.\venv\Scripts\activate`) python, pip 명령어를 수행하면 아래 오류 발생
  - Fatal error in launcher: Unable to create process using "경로1" "경로2"

![python-interpretor error](https://user-images.githubusercontent.com/76153041/166196784-6a0f42e0-6add-4129-a556-4b6270f84a64.png)

# [02] 원인

가상환경에 설정되어 있는 Python, Pip 등의 경로가 서로 다름 (Machine A에는 E:...에, Machine B에는 D:...에)

# [03] 해결방안

:warning: 아래 방법은 임시해결 방안이다. 실행 환경이 달라지면 매번 재설치해야 하는 번거로움이 있다. VENV의 환경변수만 업데이트하는 방안 확인 필요.
{: .notice--warning}

## 3-1. 가상환경 Upgrade

```shell
# 가상환경 진입 전
python -m venv --upgrade venv
```

## 3-2. 패키지 재설치

```shell
# 가상환경 진입 후, pip 재설치
python -m pip install --upgrade --force-reinstall pip

# 오류가 발생하는 패키지 재설치
pip uninstall flask
pip install flask
```
