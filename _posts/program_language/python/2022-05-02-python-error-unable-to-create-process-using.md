---
title: "Fatal error in launcher-Unable to create process using"
date: 2022-05-02
categories: Python
tags: [Error, Venv]
---

Python 또는 Pip 명령어 실행 시, Process 경로 오류로 문제로 실행되지 않을 때
------

### 상황

- 환경
  - Windows 10
  - VScode
  - Git  


- Machine A에서 Python의 venv 환경을 구성
- 결과물을 Github Repository에 업로드
- Machine B에서 추가작업을 위해 Github Repository 다운로드(git clone)
- 가상환경에 진입하여(`.\venv\Scripts\activate`) python 명령어, pip 명령어를 수행하면 아래 오류 발생
  - Fatal error in launcher: Unable to create process using "경로1" "경로2" ???

![python-interpretor error](https://user-images.githubusercontent.com/76153041/166196784-6a0f42e0-6add-4129-a556-4b6270f84a64.png)  

### 원인  
- 가상환경에 설정되어 있는 Python, Pip 등의 경로가 서로 다름(Machine A에는 E:...에, Machine B에는 D:....에)  

### 해결방안  
- <b><span style="color:#fa2c6d">아래 방법은 임시해결 방안</span></span></b>
  - 실행 환경이 달라지면, 매번 재설치해야하는 번거러움이 있음
  - VENV의 환경변수만 업데이트 하는 방안 확인 필요함

### 가상환경 Upgrade  
```shell
# 가상환경 진입 전
python -m venv --upgrade venv
```

### 패키지재설치  
```shell
# 가상환경 진입 후, pip 재설치
python -m pip install --upgrade --force-reinstall pip

# 오류가 발생하는 패키지 재설치
pip uninstall flask
pip install flask
```  
