---
layout: post
title: "코드 분리"
date: 2018-02-20 12:00
categories: Program_Language
tags: C, C++
---

코드 분리

------

> 일반적으로 하나의 파일이 하나의 기능을 담당하도록 구성



### C언어 기준

#### extern

  . 변수 혹은 함수의 자료형 및 선언 위치를 알려주는데 사용됨

  . 함수의 경우 extern 선언을 생략 가능

```c
...
  extern int num;	// int형 변수 num이 외부에 선언되어 있음
  extern void Increment(void);	// void Increment(void) 함수가 외부에 정의도어 있음
  // void Increment(void); 의 형태로 생략가능함
```



#### static

  . 전역변수에 대한 static 선언은 `외부파일` 의 접근을 차단하는 역할을 함



 ##### 파일분할 예시

```c
/* num.c */
int num=0;
```

```c
/* func.c */
extern int num;		// 외부 위치에 num이 선언되어 있음을 컴파일러에 알림

void Increment(void)
{
    num++;    
}

int GetNum(void)
{
    return num;
}
```

```c
/* main.c */
#include <stdio.h>

// 두 함수가 외부 위치에 정의되어 있음을 컴파일러에 알림
extern void Increment(void);	
extern int GetNum(void);

int main(void)
{
    int a = 0;
    a = GetNum();
    printf("num is : %d \n", a);
    Increment();
    a = GetNum();
    printf("num++ is : %d \n", a);
    return 0;
}
```

![1](https://user-images.githubusercontent.com/29933947/36182887-1a3b2d9a-116f-11e8-8f1d-70dbf5246cbe.png)





#### 헤더파일 포함 방법

> extern 방식 보다 일반적으로 사용됨

```c#
#include <header.h>		// C의 표준 헤더파일에서 해당 파일을 찾음

#include "header.h"		// 소스파일이 저장된 디렉토리에서 헤더 파일을 찾음
```



##### 헤더파일 중복 회피 방법

  . C 전처리문(매크로)를 활용함

  . #ifdef , ifndef를 활용하여 관련 내용이 정의되어 있을 경우, 재 포함시키지 않도록 조절

  . 명시적으로 한 번 include 되는 헤더파일일 경우에도, 만약을 대비해 조건문을 설정해 놓는 것이 좋음



```c
/* div.h */
#ifndef __DIV_H__   // __DIV_H__ 가 정의되어 있지 않다면, 정의(아래 define)
#define __DIV_H__   

typedef struct div{
    int quotient;    // 몫
    int remainder;  // 나머지
} Div;

#endif
```

```c
/* div-func.h */
#ifndef __DIV_FUNC_H__
#define __DIV_FUNC_H__

#include "div.h"
    Div IntDiv(int num1, int num2);

#endif
```

```c
/* div-func.c */
#include "div-func.h"

Div IntDiv(int num1, int num2)
{
    Div dval;
    dval.quotient = num1 / num2;
    dval.remainder = num1 % num2;
    return dval;
}
```

```c
/* main.c */
#include <stdio.h>
#include "div.h"
#include "div-func.h"	// 선언되는 헤더파일을 포함하면, 컴파일러가 알아서 정의된 함수를 포함시켜 줌

int main(void)
{
    Div val = IntDiv(5, 3);
    printf("몫: %d \n", val.quotient);
    printf("나머지: %d \n", val.remainder);

    return 0;
}

```



##### 코드 분할 일반적 예

```c
/* basicArith.h */

#define PI 3.14
double Add(double num1, double num2);
double Min(double num1, double num2);
double Mul(double num1, double num2);
double Div(double num1, double num2);
```

```c
/* basicArith.c */

double Add(double num1, double num2)
{
    return num1+num2;
}
double Min(double num1, double num2)
{
    return num1-num2;
}
double Mul(double num1, double num2)
{
    return num1*num2;
}
double Div(double num1, double num2)
{
    return num1/num2;
}
```

```c
/* areaArith.h */

double TriangleArea(double base, double height);
double CircleArea(double rad);
```

```c
/* areaArith.c */

#include "basicArith.h"

double TriangleArea(double base, double height)
{
    return Div(Mul(base, height), 2);
}
double CircleArea(double rad)
{
    return Mul(Mul(rad, rad), PI);
}
```

```c
/* roundArith.h */

double RectangleRound(double base, double height);
double SquareRound(double side);
```

```c
/* roundArith.c */

#include "basicArith.h"

double RectangleRound(double base, double height)
{
    return Mul(Add(base, height), 2);
}
double SquareRound(double side)
{
    return Mul(side, 4);
}

```

```c
/* main.c */

#include <stdio.h>
#include "areaArith.h"
#include "roundArith.h"

int main(void)
{
    printf("삼각형 넓이(및변 4, 높이 2: %g \n",
            TriangleArea(4,2));
    printf("원 넓이(반지름 3): %g \n",
            CircleArea(3));
    
    printf("직사각형 둘레(및변 2.5, 높이 5.2: %g \n",
            RectangleRound(2.5,5.2));
    printf("정사각형 둘레(변의 길이 3): %g \n",
            SquareRound(3));
}
```





### C++ 기준

> C++은 일반적으로 클래스 선언은 헤더 파일로 구현, 멤버 함수의 정의는 .cpp로 구현함

![4](https://user-images.githubusercontent.com/29933947/36130911-8cb78bec-10b2-11e8-92bf-27e56baf8c6b.png)