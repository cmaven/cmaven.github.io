---
title: "Selenium Error — </button> is not clickable at point"
description: "How to resolve Selenium's 'element is not clickable at point' error by calling maximize_window()."
excerpt: "How to resolve Selenium's 'element is not clickable at point' error by calling maximize_window()."
date: 2022-02-28
categories: Python
tags: [Crawling, Selenium, Error]
ref: selenium-click-error
---

Button click error when using Selenium
------

### Situation

- An error occurs when clicking a button with Selenium.
- `Message: element click intercepted: Element <button type="button" class="btn_cancel">...</button> is not clickable at point (337, 698).`

![element_position_error](https://user-images.githubusercontent.com/76153041/155912469-cd0d00da-e3e1-4648-8b8e-906c07ea4a49.png)

### Cause

This can happen when the launched browser window is too small.

> Other causes are also possible.
> Reference: [Link](https://www.testim.io/blog/selenium-element-is-not-clickable-at-point/)

### Solution

Call `maximize_window()` to maximize the window.

```python
browser = webdriver.Chrome(options=options)
# add this line
browser.maximize_window()
```
