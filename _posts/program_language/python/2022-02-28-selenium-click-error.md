---
title: "Selenium Error-</button> is not clickable at point"
description: "Selenium에서 'element is not clickable at point' 오류 발생 시 maximize_window()로 해결하는 방법을 안내합니다."
excerpt: "Selenium에서 'element is not clickable at point' 오류 발생 시 maximize_window()로 해결하는 방법을 안내합니다."
date: 2022-02-28
last_modified_at: 2026-05-26
categories: Python
tags: [Crawling, Selenium, Error]
ref: selenium-click-error
---

:bulb: Selenium에서 버튼 클릭 시 `element is not clickable at point` 오류가 발생하면, 브라우저 창 크기가 너무 작아서 요소가 가려진 것이 원인일 수 있으며 `maximize_window()` 호출로 해결됩니다.
{: .notice--info}

---

# [01] 상황

- selenium 사용 시, 버튼 클릭 부분에서 Error 발생  
- `Message: element click intercepted: Element <button type="button" class="btn_cancel">...</button> is not clickable at point (337, 698).`

![element_position_error](https://user-images.githubusercontent.com/76153041/155912469-cd0d00da-e3e1-4648-8b8e-906c07ea4a49.png)

*그림 1. Selenium 버튼 클릭 시 발생하는 `element is not clickable at point` 오류 화면*

---

# [02] 원인

구동한 웹브라우저의 크기가 너무 작을 경우 발생할 수 있음

> 그 외 다른 문제로 발생할 수도 있음  
> 참고: [Link](https://www.testim.io/blog/selenium-element-is-not-clickable-at-point/)

창 크기가 작으면 대상 요소가 다른 요소에 가려지거나 뷰포트 밖으로 벗어나 클릭 이벤트를 받지 못한다.

---

# [03] 해결방안

`maximize_window()` 호출하여 창 크기 최대화

```python
browser = webdriver.Chrome(options=options)
# 추가
browser.maximize_window()
```
