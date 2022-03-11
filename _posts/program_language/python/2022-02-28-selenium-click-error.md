---
title: "Selenium Error-</button> is not clickable at point"
date: 2022-02-28
categories: Python
tags: [Crawling, Selenium, Error]
---

Selenium 사용 시, 버튼 클릭 오류
------

### 상황

- selenium 사용 시, 버튼 클릭 부분에서 Error 발생  
- `Message: element click intercepted: Element <button type="button" class="btn_cancel">...</button> is not clickable at point (337, 698).`

![element_position_error](https://user-images.githubusercontent.com/76153041/155912469-cd0d00da-e3e1-4648-8b8e-906c07ea4a49.png)

### 원인

구동한 웹브라우저의 크기가 너무 작을 경우 발생할 수 있음

> 그 외 다른 문제로 발생할 수도 있음  
> 참고: [Link](https://www.testim.io/blog/selenium-element-is-not-clickable-at-point/)

### 해결방안

`maximize_windows()` 호출하여 창 크기 최대화 

```python
browser = webdriver.Chrome(options=options)
# 추가
browser.maximize_window()
```