---
title: "Selenium Error-SessionNotCreatedException-version of chromeDriver"
date: 2022-03-11
categories: Python
tags: [Error, Selenium, ChromeDriverManager, Webdrivermanager]
---

Selenium 에서 ChromeWebDriver 실행 시, 지원하지 않는 버전 오류가 발생 시
------

### 상황

- webdriver.Chrome() 형태로 실행 시, 현재 ChromeDriver Version이 지원되지 않는다는 오류 메시지 발생 후, 실행 중지됨
 
``` python
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
browser = webdriver.Chrome(options=options)
```

![selenium common exceptions Error](https://user-images.githubusercontent.com/76153041/157777747-7d159990-d730-40ca-b990-a8cf214506e8.png)


### 해결방안

#### webdriver-manager 설치

``` shell
pip install webdriver-manager
```
  
#### Python 코드 내부에 webdriver-manager 사용

``` python
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
browser = webdriver.Chrome(ChromeDriverManager().install(),options=options)
```


참고: [https://stackoverflow.com/questions/60296873/sessionnotcreatedexception-message-session-not-created-this-version-of-chrome](https://stackoverflow.com/questions/60296873/sessionnotcreatedexception-message-session-not-created-this-version-of-chrome)


