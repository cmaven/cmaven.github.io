---
layout: post
title: "C 구조체"
date: 2018-01-26 00:30
categories: Program_Language
tags: c
---

C 언어의 구조체에 대해 정리한다.

------

  . 하나 이상의 변수(정수형, 실수형, 포인터, 배열 등)을 묶어 새로운 자료형을 정의

```c
...  
struct person
{
  char name[20];
  char phonenum[20];
  int age;
};

typedef struct point
{
  int pos_x;
  int pos_y;
}Point;

...
 
int main(void)
{
  // 구조체 변수 선언 방법: struct type_name val_name;
  struct person p1;		
  
  // 초기화 방법1, 문자열, 정수형을 바로 대입할 수 있음
  struct person p2 = {"김철수", "010-1111-2222", 20};
  struct person p3;
  Point pos1;
  
  // 초기화 방법2, 배열에 문자열을 입력하기 위해 strcpy 함수를 사용함
  strcpy(p1.name, "홍길동");
  strcpy(p1.phonenum, "010-1234-5678");
  p1.age = 10;			// 구조체 변수 p1의 멤버변수 age에 20을 저장
  
  // 구조체 변수 멤버 변수 접근 방법
  printf("이름 입력:"); scanf("%s", p3.name);	    // 배열 멤버변수는 이름(=주소값) 접근
  printf("나이 입력:"); scanf("%d", &p3.age); // 정수형 멤버변수는 주소값 접근
  
  return 0;
}
```



### 구조체 배열 및 포인터

#### 구조체 배열

```c
...
struct point
{
  int pos_x;
  int pos_y;
};

...
int main(void)
{
  struct point arr[4];
  struct point arr1[3] = {		// 초기화 방법
    {1,2},
    {3,4}    
  };
  ....
}
```

![_ 1](https://user-images.githubusercontent.com/29933947/35397649-58e387a4-0233-11e8-8a8c-73abbf42fd19.png)

#### 구조체 포인터

```c
...
strcut point pos = {10,20};
struct point * pptr = &pos;	// 포인터 변수 pptr이 구조체 변수 pos를 가리킴

// pptr이 가리키는 구조체 변수의 멤버에 값 저장
pptr->pos_x = 30; // (*pptr).pos_x = 30;
pptr->pos_y = 40; // (*pptr).pos_y = 40;
...
```

  . 포인터 변수를 구조체의 멤버로도 선언 가능함

```c
#include <stdio.h>

struct point
{
    int pos_x;
    int pos_y;
};

struct circle
{
    double radius;
    struct point * center;
};

int main()
{
    struct point cen = {2, 6};
    double rad = 2.5;
    
    struct circle ring = {rad, &cen}; // point형 구조체 변수 center의 주소값
    
    printf("원의 반지름은: %g \n", ring.radius);
    printf("원의 중심은: %d %d \n", ring.center->pos_x, ring.center->pos_y);
    
    return 0;
}
```

![2](https://user-images.githubusercontent.com/29933947/35399109-dec9e6d0-0236-11e8-8ac8-72214218193b.png)



### 함수의 인자로 전달되는 구조체

```c
#include <stdio.h>

typedef struct point
{
    int pos_x;
    int pos_y;
}Point;

// 구조체 변수의 call by value
void ShowPosition(Point pos)
{
    printf("< %d %d > \n", pos.pos_x, pos.pos_y );
}

Point CurrentPosition(void)
{
    Point cen;
    Printf("Input current pos: ");
    scanf("%d %d", &cen.pos_x, &cen.pos_y);
    
    return cen;
}

// 구조체 변수의 call by reference
void SymmetryPosition(Point * ptr)
{
    ptr->pos_x = (ptr->pos_x) * -1;
    ptr->pos_y = (ptr->pos_y) * -1;
}

int main()
{
    Point curPos = CurrentPosition();
    ShowPosition(CurPos);				// 구조체 복사

    SymmetryPosition(&curPos);			// curPos 구조체의 멤버변수 조작을 위한 주소 전달
    ShowPosition(curPos);				// 구조체 복사

    return 0;
}
```

![4](https://user-images.githubusercontent.com/29933947/35420036-a5848b08-027e-11e8-99bc-286442cf153e.png)

  . 구조체 변수를 대상으로 대입연산, 주소값 반환(&) 연산, 구조체 변수 크기 반환(sizeof) 연산 등이 허용

  . 사칙연산은 별도의 함수를 정의하여 수행해야함

```c
#include <stdio.h>

typedef struct point
{
    int pos_x;
    int pos_y;
}Point;

Point AddPosition(Point pos1, Point pos2)
{
    Point pos = {pos1.pos_x + pos2.pos_x, pos1.pos_y + pos2.pos_y};
    return pos;
}

int main()
{
    Point pos1 = { 1, 2 };
    Point pos2 = { 3, 4 };
    Point result;
    
    result = AddPosition(pos1, pos2);
    printf("<X: %2d Y: %2d >\n", result.pos_x, result.pos_y);
    
    return 0;
}
```

![5](https://user-images.githubusercontent.com/29933947/35420252-ccb935b0-027f-11e8-9456-a4bca417d3ad.png)

#### 구조체 중첩

  . 구조체의 멤버변수로 구조체 선언 가능

```c
#include <stdio.h>

typedef struct point
{
    int pos_x;
    int pos_y;
}Point;

typedef struct circle
{
    Point cen;
    double rad;
}Circle;

void ShowCircleInfo(Circle * cptr)
{
    printf("[ %d %d ] \n", (cptr->cen).pos_x, (cptr->cen).pos_y);
    printf("radius: %g \n\n", cptr->rad);
}

int main()
{
    Circle c1 = {`{1, 2}`, 2.5};
    Circle c2 = {3, 4, 5.5};
    
    ShowCircleInfo(&c1);
    ShowCircleInfo(&c2);
    
    return 0;
}
```

![6](https://user-images.githubusercontent.com/29933947/35420598-c75e7b78-0281-11e8-8864-cda11c0800a4.png)



### 공용체(union)

![_ 1](https://user-images.githubusercontent.com/29933947/35429986-b78671aa-02b9-11e8-90bd-b78c702966bb.png)

  . 공용체를 구성하는 멤버변수 중, 데이터형의 크기가 (메모리 차지 공간) 가장 큰 데이텨형 만큼의 메모리 공간 사용

  . 할당된 메모리 공간을 멤버변수들이 공유하게 됨

  . 데이터형의 메모리 공간에 얽매이지 않는 접근방식을 제공하기 위함

```c
#include <stdio.h>

typedef struct dbshort
{
    unsigned short upper;   // 2byte
    unsigned short lower;   // 2byte
} DBShort;

typedef union rdbuf
{
    int iBuf;   // 4byte
    char bBuf[4];   // 4byte
    DBShort sBuf;   // 4byte
} RDBuf;

int main(void)
{
    RDBuf buf;
    printf("정수 입력: "); scanf("%d", &(buf.iBuf));
    
    printf(" 상위 2바이트: %u \n ", buf.sBuf.upper);
    printf(" 하위 2바이트: %u \n ", buf.sBuf.lower);
    printf(" 상위 1바이트 아스키 코드: %c \n ", buf.bBuf[0]);
    printf(" 상위 1바이트 아스키 코드: %c \n ", buf.bBuf[3]);
    
    return 0;    
}

```

![17](https://user-images.githubusercontent.com/29933947/35430344-36283c22-02bb-11e8-9e2c-27415221b69b.png)

![_ 2](https://user-images.githubusercontent.com/29933947/35429988-b7b34ee6-02b9-11e8-93c5-eefd14dcde17.png)



### 열거형(enum)

  . 저장이 가능 한 값 자체를 정수의 형태로 선언하여 사용

  . 반복되는 정해진 상수에 대해 프로그램 가독성을 높이기 위해 종종 사용됨

```c
#include <stdio.h>

typedef enum scale
{
    Do = 1, Re = 2, Mi = 3
} Scale;

void Sound(Scale a)
{
    switch(a)
    {
        case Do:
            puts("도");
            return;
        case Re:
            puts("레");
            return;
        case Mi:
            puts("미");
            return;
    }
}

int main(void)
{
    Scale tone;
    // for(tone = 1; tone <= 3; tone += 1)
    for(tone = Do; tone <= Mi; tone += 1)
        Sound(tone);
    return 0;
}
```

![18](https://user-images.githubusercontent.com/29933947/35430597-550ba7c2-02bc-11e8-84ba-435698cb734c.png)
