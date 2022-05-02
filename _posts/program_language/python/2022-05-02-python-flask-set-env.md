---
title: "Flask ENV 설정"
date: 2022-05-02
categories: Python
tags: [Flask]
---

Flask 실행을 위한 ENV 설정
------

- Flask는 `flask run` 실행 시, 명령어를 실행하는 디렉토리의 `app.py` 또는 `wsgi.py`를 찾아 서버를 구동한다.
- 위의 파일명을 변경하였을 경우, `FLASK_APP=파일명`을 설정해줘야, 정상적으로 실행이 가능하다.  

- 파일명이 `test.py` 일 경우

```shell
# linux 환경
export FLASK_APP=test

# Powershell (Windows 10, vscode)
$env:FLASK_APP="test.py"

# Bashshell (Windows 10, vscode)
set FLASK_APP=test
```  

