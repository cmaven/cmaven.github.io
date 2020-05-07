---
layout: post
title: "C언어 디버깅 매크로(__FUNCTION__ ...)"
date: 2018-01-15 16:25
categories: Program-Language
tags: c
---

C언어의 디버깅에 사용될 수 있는 특정 매크로에 대해 작성한다

------

### \__FILE__

 . 현재 소스 파일의 이름을 문자 리터럴(literal)로 표시함

#### \__LINE__

 . 현재 소스 파일의 줄 번호

 . 10진수 정수 리터럴로 표시함

#### \__FUNCTION__ 

 . 현재 소스 파일의 함수명을 표시함

 . 컴파일러마다 다르게 처리되기 때문에, 사용에 주의를 요함(향후 확인 필요)

#### \__func__

 . 현재 소스 파일의 함수명을 표시함

 . 컴파일러가 처리함(향후 확인 필요)



## 사용예

 . 디버깅시, 로그를 소스코드의 실행 위치 로그를 남기기 위해 사용

```java
#include <stdio.h>

#define ENTERING printf("Entering FILE %s FUNC %s LINE %d \n", \
__FILE__, \
__func__, \
__LINE__)
#define LEAVING printf("Entering FILE %s FUNC %s LINE %d \n", \
__FILE__, \
__func__, \
__LINE__)

int main()
{
    ENTERING;
    
    printf("\nDEBUG Marco Test\n\n");

    LEAVING;

    return 0;
}
```

![10](https://user-images.githubusercontent.com/29933947/34934444-d4c39738-fa1d-11e7-8b14-cb042c04375f.png)



