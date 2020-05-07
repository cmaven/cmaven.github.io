---
layout: post
title: "C언어 입출력 함수"
date: 2018-02-19 11:00
categories: Program_Language
tags: c
---

C언어 입출력 함수에 대해 기술한다

------

  . C언어는 입출력 시, Buffer OverFlow(BOF)의 위험 존재



##### 취약함수

```c
scanf, gets, sprintf, strcpy, strcat
```

##### 대응함수

```c
fscanf, sscanf, fgets, strncpy, strncat
```

> scanf_s 등의 _s 접미어로 붙는 함수는 gcc 표준함수가 아님. Microsoft 에서 제공하는 함수





### 입력

###fgets

  . 모든 입력은 문자열로 수행

  . 정수, 실수형에 대한 변환은 `문자열형변환`  함수를 사용함 

  . 입력에 사용할 버퍼는 메모리 동적 할당 방식을 사용 (테스트 필요)

  . 입력 시, 문자 혹은 숫자에 대한 입력을 제한하고 싶을 경우, isdigt()  함수를 활용하여 구분



------- **(실수형에 대한 테스트 필요), (버퍼 동작할당 추가 후 테스트 필요), (정수가 포함되어 있는 문자열 중, 정수만을 추출 변환하는 방법 추가 후 테스트 필요)** -------

```c
#include <stdio.h>

char * fgets(char * s, int n, FILE * stream);
```





```c
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int check_input_type(char * str, int k)
{
    int i;
    
    for(i=0; i < k ;i++)
    {
        // 입력된 값이 없을 경우, 입력된 문자열의 마지막일 경우 반복문 탈출
        if(*(str+i) == '\0')
            break;

      	// buf에 저장된 문자를 숫자 형태인지, 문자형태인지 판단
        if (isdigit(*(str+i)))
            printf("this is number: %c \n", *(str+i));    
        else
            printf("this is character: %c \n", *(str+i));
    }
    return 0;
}

int main(void)
{
    char buf[50];

    printf("입력:");
    fgets(buf, sizeof(buf), stdin);    
    buf[strlen(buf) - 1] = '\0';    
    
    check_input_type(buf, sizeof(buf)/sizeof(char));

  return 0;
}
```

![3](https://user-images.githubusercontent.com/29933947/36020576-8edc8718-0dc6-11e8-8e6c-422078f5a9f4.png)





#### 문자열 형변환 함수

```c
#include <stdlib.h>
...
int atoi(const char * str);			// 문자열 -> int 형
int atol(const char * str);			// 문자열 -> long 형
int atof(const char * str);			// 문자열 -> double 형
...
```



.. 추후 추가 작성 ..





