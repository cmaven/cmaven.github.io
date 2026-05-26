---
title: "Selenium SessionNotCreatedException — ChromeDriver Version Error"
description: "How to fix Selenium's SessionNotCreatedException caused by a ChromeDriver version mismatch using webdriver-manager."
excerpt: "How to fix Selenium's SessionNotCreatedException caused by a ChromeDriver version mismatch using webdriver-manager."
date: 2022-03-11
last_modified_at: 2026-05-26
categories: Python
tags: [Error, Selenium, ChromeDriverManager, Webdrivermanager]
ref: selenium-chromversion-error
---

When running ChromeWebDriver in Selenium raises an unsupported version error
------

### Situation

- When launching with `webdriver.Chrome()`, an error appears stating that the current ChromeDriver version is not supported, and execution stops.

``` python
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
browser = webdriver.Chrome(options=options)
```

![selenium common exceptions Error](https://user-images.githubusercontent.com/76153041/157777747-7d159990-d730-40ca-b990-a8cf214506e8.png)


### Solution

#### Install webdriver-manager

``` shell
pip install webdriver-manager
```

#### Use webdriver-manager in your Python code

``` python
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
browser = webdriver.Chrome(ChromeDriverManager().install(),options=options)
```


Reference: [https://stackoverflow.com/questions/60296873/sessionnotcreatedexception-message-session-not-created-this-version-of-chrome](https://stackoverflow.com/questions/60296873/sessionnotcreatedexception-message-session-not-created-this-version-of-chrome)
