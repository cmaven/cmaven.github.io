---
title: "Selenium SessionNotCreatedException — ChromeDriver 버전 오류"
description: "Selenium에서 ChromeDriver 버전 불일치로 SessionNotCreatedException 발생 시 webdriver-manager로 해결하는 방법입니다."
excerpt: "Selenium에서 ChromeDriver 버전 불일치로 SessionNotCreatedException 발생 시 webdriver-manager로 해결하는 방법입니다."
date: 2022-03-11
last_modified_at: 2026-05-26
categories: Python
tags: [Error, Selenium, ChromeDriverManager, Webdrivermanager]
ref: selenium-chromversion-error
---

:bulb: Selenium 실행 시 `SessionNotCreatedException`이 발생하면 설치된 Chrome 브라우저 버전과 ChromeDriver 버전이 맞지 않는 것이 원인이며, `webdriver-manager` 라이브러리로 버전을 자동 관리하면 해결됩니다.
{: .notice--info}

---

# [01] 상황

- webdriver.Chrome() 형태로 실행 시, 현재 ChromeDriver Version이 지원되지 않는다는 오류 메시지 발생 후, 실행 중지됨

```python
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
browser = webdriver.Chrome(options=options)
```

![selenium common exceptions Error](https://user-images.githubusercontent.com/76153041/157777747-7d159990-d730-40ca-b990-a8cf214506e8.png)

*그림 1. ChromeDriver 버전 불일치로 발생하는 SessionNotCreatedException 오류 화면*

Chrome 브라우저가 자동 업데이트되면 기존에 수동으로 내려받은 ChromeDriver와 버전이 어긋나 이 오류가 반복적으로 발생한다.

---

# [02] 해결방안

## webdriver-manager 설치

```shell
pip install webdriver-manager
```

## Python 코드 내부에 webdriver-manager 사용

기존 `webdriver.Chrome(options=options)` 호출 대신 `ChromeDriverManager().install()`로 드라이버 경로를 자동 지정한다.

```python
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
```

참고: [https://stackoverflow.com/questions/60296873/sessionnotcreatedexception-message-session-not-created-this-version-of-chrome](https://stackoverflow.com/questions/60296873/sessionnotcreatedexception-message-session-not-created-this-version-of-chrome)
