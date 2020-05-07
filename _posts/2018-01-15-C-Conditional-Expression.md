---
layout: post
title: "C언어 삼항연산자"
date: 2018-01-15 17:00
categories: Program-Language
tags: c
---

C언어의 삼항연산자에 대해 작성한다

------

## 구성

 . (Condition) <span style="color:blue">?</span> (True Result) <span style="color:blue">:</span> (False Result)

 . 조건( Condition)에 따라 참일 경우, `:` 앞 부분의 값이 반환되고, 거짓일 경우, `:` 뒷 부분의 값이 반환됨

## 예시

```c
#include <stdio.h>

int main()
{
    int result;
    int a = 100, b = 200;
    
    result = (a < b) ? a + 10 : b - 10;
    printf("Result: %d\n", result);

    return 0;
}
```

![9](https://user-images.githubusercontent.com/29933947/34932524-85cf6f82-fa16-11e7-87c6-ab7f66f91d71.png)
