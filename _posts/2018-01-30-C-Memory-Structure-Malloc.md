---
layout: post
title: "C 언어 메모리 구조 및 동적할당"
date: 2018-01-30 00:30
categories: Program-Language
tags: c
---

c 언어의 메모리 구조 및 동적할당 방법에 대해 정리한다.

------

### 메모리 구성

  . 운영체제에 의해 할당되는 메모리 공간 구조는 다음과 같음

![_ 1](https://user-images.githubusercontent.com/29933947/35561457-b6c8267c-05f3-11e8-8f74-c13644e5012b.png)

  . 코드(Code) 영역

​    : 실행할 프로그램의 코드가 저장되는 공간

​    : CPU가 코드영역에 저장된 명령문들을 하나씩 가져가 실행함

  . 데이터(Data) 영역

​    : 전역변수, Static 변수 할당

​    : 프로그램 시작과 동시에 메모리 공간에 할당, 프로그램 종료 시 까지 남아 있음

  . 스택(Stack) 영역

​    : 지역변수, 매개변수 할당

​    : 함수를 빠져나가면 소멸

  . 힙(Heap) 영역

​    : 프로그래머가 원하는 시점에 메모리 공간을 할당하고 해제하기 위한 영역



#### 프로그램 실행에 따른 메모리 변화

![_ -01](https://user-images.githubusercontent.com/29933947/36091026-ba91e3ce-1025-11e8-8cd4-01169f635898.png)





![_ -02](https://user-images.githubusercontent.com/29933947/36091027-bac0fd9e-1025-11e8-9708-b5a7314e9139.png)



![_ -03](https://user-images.githubusercontent.com/29933947/36091023-b9dbacd0-1025-11e8-9c25-73280506d89b.png)



![_ -04](https://user-images.githubusercontent.com/29933947/36091024-ba3a0dca-1025-11e8-93b4-96f0121ac009.png)



![_ -05](https://user-images.githubusercontent.com/29933947/36091025-ba63243a-1025-11e8-95ed-61985a2f5fb0.png)





### 메모리 동적할당

  . 지역변수와 같이 함수가 호출될 때 매번 할당이 이루어지지만, 할당이 되면 전역변수처럼 함수를 빠져나가도 소멸되지 않는 성격의 변수를 선언할 때 유용하미

  . 해당 변수를 힙 영역에 할당 및 소멸

```c
#include <stdio.h>
void * malloc(size_t size);		// 힙 영역에 메모리 공간 할당
void free(void * ptr);			// 힙 영역에 할당된 메모리 공간 해제
// 성공 시 할당된 메모리 주소 값, 실패 시 NULL 값 반환
```

  . 반환형이 void형 포인터인 malloc 함수는 형변환이 필수, 형변환 없을 경우 오류 발생

```c
...
void * ptr = malloc(sizeof(int));
// *ptr = 20;			// ptr이 void형 포인터이므로 컴파일 에러

// 선언 방법
int * ptr1 = (int *)malloc(sizeof(int));
double * ptr2 = (double *)malloc(sizeof(double));
int * ptr3 = (int *)malloc(sizeof(int) * 5 ));
double * ptr4 = (double *)malloc(sizeof(double) * 10 );
```

 

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char * ReadUserName(void)
{
    //char buf[30];
    char * name = (char *)malloc(sizeof(char) * 30);
    printf("이름?:");
    /* 이 경우, free() invalid pointer 에러가 발생함
       이는, malloc으로 할당받은 주소값을 name에 넣어놓고,
       name의 주소값을 변경 한 후, free를 수행하기 때문에,
       프로그램은 free 수행 시, 반환해야할 메모리를 잘못 참조하게 되기 때문
    fgets(buf, sizeof(buf), stdin);
    strncpy(name, buf, sizeof(buf)-1);
    name[sizeof(name)-1] = 0;
    name = buf;
    */
    fgets(name, sizeof(char) * 30, stdin);
    // gets(name); // gets은 메모리 사용 위험으로 권장하지 않음
    return name;
}

int main()
{
    char * name1;
    char * name2;

    name1 = ReadUserName();
    printf("name1: %s", name1);

    name2 = ReadUserName();
    printf("name2: %s", name2);

    printf("again name1: %s", name1);
    printf("again name2: %s", name2);

    free(name1);
    free(name2);

    return 0;
}
```

![1](https://user-images.githubusercontent.com/29933947/35566472-d9ccc81a-0604-11e8-91f3-967ad2ec0e07.png)

#### calloc 함수

```c
#include <stdlib.h>
void * calloc(size_t elt_count, size_t elt_size);
// 성공 시 할당된 메모리 주소 값, 실패 시 NULL 반환
```

  . malloc이 100 바이트를 힙 영역에 할당해주세요 라면,

  . calloc은 4바이트 크기의 블록(elt_size) 25개(elt_count)를 힙 영역에 할당해 주세요.

  . 또한, calloc은 할당된 공간을 모두 `0` 으로 초기화 함

#### realloc 함수

```c
#incldue <stdlib.h>
void * realloc(void * ptr, size_t size);
// 성공 시 할당된 메모리 주소 값, 실패 시 NULL 반환

...
 int * arr = (int *)malloc(sizeof(int)*3);
 arr = (int *)realloc(arr, sizeof(int)*5);
...
```

  . ptr이 가리키는 메모리의 크기를 size의 크기로 조절하는 함수

