---
layout: post
title: "C언어 전처리문(Preprocessor)"
date: 2018-01-12 18:55
categories: Program-Language
tags: c
---

C언어 전처리문 관련한 정보를 기술한다.

------

## 정의

프로그램이 컴파일 되기 전 미리 실행되는 코드로 선행처리문 이라고도 지칭함

주로 코드의 일부를 활성화/비활성화 하는데 사용됨

```mermaid
graph LR
  A[Source file] --> |Preprocessor| B[Preprocessed file]
  B --> |Compiler| C[Object file<br/> ...01010001...]
  C --> |Linker| D[Executable file]
```

## 종류

#### 파일포함

 . 프로그램에 특정 파일을 첨부하여 하나의 파일처럼 컴파일하며 첨부된 파일의 함수나 변수를 사용 가능

  `#include<stdio.h>`



#### 형태정의

 ![_ _ 1](https://user-images.githubusercontent.com/29933947/34866163-e7f0f24e-f7be-11e7-94b9-912a50719a48.png)

 . 컴파일 수행 시, 매크로를 만나면 몸체의 내용으로 치환

 . 매개변수 존재하는 형태(함수)로도 사용가능함

```java
#define DOUBLE(X) X*2
```

​    : DOUBLE(X) 형태이면 X 곱하기 2를 수행하도록 지정함

##### ex)    

```java
#include <stdio.h>

#define PI 3.14
#define DOUBLE(X) (X*2)


int main()
{
    printf("PI is %f\n", PI);
    printf("PI x 2 = %f\n", DOUBLE(PI));

    return 0;
}
```

 ![4](https://user-images.githubusercontent.com/29933947/34866479-04082406-f7c0-11e7-8c61-315cfad259a1.png)

> \#undef

   . #define 으로 정의된 매크로를 사용을 중단하도록 한다



#### 조건부 컴파일

 . #if, #ifdef, #ifndef, #else, #elif, #endif 등

 . 컴파일 조건에 따라 컴파일 여부가 결정되도록 함

1. \#if - #endif

   . if 조건이 참일 때, 해당 코드를 수행

   . 특정 코드를 선택하여 실행하고자 할때 사용함

   ```java
   #include <stdio.h>

   #define PI 3.14
   #define DOUBLE(X) X*2
   #define NONSKIP 0
   #define SKIP 1

   int main()
   {
       
   #if NONSKIP
       printf("PI is %f\n", PI);
       printf("PI x 2 = %f\n", DOUBLE(PI));
   #endif

   #if SKIP
       printf("Skip calculation\n");
   #endif

       return 0;
   }
   ```

   ![5](https://user-images.githubusercontent.com/29933947/34867510-b86027f2-f7c3-11e7-8ffe-29219f055e03.png)

   ​

2. \#ifdef - #endif

   . 조건이 정의되었을 경우, 해당 코드를 수행함

   ```java
   #include <stdio.h>

   #define PI 3.14
   #define DOUBLE(X) X*2
   #define NONSKIP 0
   //#define SKIP 

   int main()
   {
       
   #ifdef NONSKIP
       printf("PI is %f\n", PI);
       printf("PI x 2 = %f\n", DOUBLE(PI));
   #endif

   #ifdef SKIP
       printf("Skip calculation\n");
   #endif

       return 0;
   }
   ```

   ![4](https://user-images.githubusercontent.com/29933947/34866479-04082406-f7c0-11e7-8c61-315cfad259a1.png)

3. \#ifndef, #endif

   . 정의되지 않았다면, 지정된 정의를 수행

   . 헤더 파일의 중복포함을 막기 위해 사용됨

   ​

4. \#elseif, #else

   . if문의 else, elseif 와 같은 역할

   ```java
   #include <stdio.h>

   #define NUM 2

   int main()
   {
       
   #if NUM==1
       printf("Number is %d\n",NUM);
   #elif NUM==2
       printf("Number is %d\n",NUM);
   #else
       printf("Error\n");
   #endif

       return 0;
   }
   ```

   ![6](https://user-images.githubusercontent.com/29933947/34867878-24b13a9e-f7c5-11e7-985b-335beaa71d4b.png)

   #### 기타

   > 문자열 치환 \# 연산자

   . 매크로의 값을 문자로 치환

   ```
   #define STR(A) #A
   ```

   > 매크로 값(몸체) 단순 연결 연산자 \##
   >

   . 매크로의 값을 단순히 연결함

   ```java
   #include <stdio.h>
   #define NUM(X,Y) X ## Y

   int main()
   {
       printf("Number is %d\n",NUM(1,2));
       return 0;
   }
   ```

   ![7](https://user-images.githubusercontent.com/29933947/34869149-5aa31b14-f7c9-11e7-9477-568f16b29093.png)

