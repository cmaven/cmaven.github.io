---
layout: post
date: 2018-07-05 12:00
title: "C++ Exception Handling"
categories: Program_Language
tags: C++
---

C++ 예외처리에 대해 정리한다.

------

### 예외처리(Try, Catch, Throw)

ㆍ예외 상황을 처리하는 코드부분을 독립시켜 유지보수 및 코드 가독성을 높이기 위함



#### 기본 구성

```c++
try {
   / * 예외 발생 예상 지역 */
   throw ex; 	// 예외 전달(catch block으로)
}
catch (처리되어야 할 예외의 종류) {
   / * 예외를 처리하는 코드가 존재할 위치 */
}
```

> 전달되는 예외와 이를 받아주는 변수의 자료형은 일치해야 함



ㆍ예외의 발생 및 처리 과정

![_](https://user-images.githubusercontent.com/29933947/42308058-6d5d065a-806f-11e8-8103-436cfdc27e92.png)



```c++
#include <iostream>
using std::cout;
using std::endl;
using std::cin;

int main(void){
    int a, b;

    cout << "두 개 숫자 입력: ";
    cin >> a >> b;

    try{
        cout << "Start a try block" << endl;

        if(b==0)
            throw b;
        cout << "a/b의 몫: "<< a/b << endl;
        cout << "a/b의 나머지: "<< a%b << endl;

        cout << "End a try block" << endl;
    }
    catch(int exception){
        cout << "Start a catch block" << endl;

        cout << exception << "입력" << endl;
        cout << "입력오류! 다시 실행하세요." << endl;

        cout << "End a catch block" << endl;
    }

    cout << "감사합니다." << endl;

    return 0;
}
```

ㆍ정상 실행

![5](https://user-images.githubusercontent.com/29933947/42308109-949438ce-806f-11e8-94b3-ee238dbf75ba.png)

ㆍ예외 발생

![6](https://user-images.githubusercontent.com/29933947/42308110-95e74dce-806f-11e8-86be-482421e4c45f.png)

> 예외가 발생하면 throw 이후의 try 블록 내의 소스들은 실행되지 않는다.



### 처리되지 않는 예외

#### Stack Unwinding(스택 풀기)

> 처리되지 않는 예외는 전달됨 = Stack Unwinding
>
> 예외가 전달되는 과정이 함수의 스택이 풀리는 순서와 일치하기 때문에, 이러한 명칭이 붙음



```c++
#include <iostream>
using std::cout;
using std::endl;

void fct1();
void fct2();
void fct3();

int main(void){
    try{
        fct1();
    }
    catch(int ex){
        cout << "예외: " << ex << endl;
    }
    return 0;
}

void fct1(){
    fct2();
}

void fct2(){
    fct3();
}

void fct3(){
    throw 100;
}
```

![1](https://user-images.githubusercontent.com/29933947/42322644-3d3796e2-8098-11e8-8540-dc686530e6d9.png)



ㆍStack Unwinding 순서

![_](https://user-images.githubusercontent.com/29933947/42325061-09d88d1c-80a0-11e8-9e0d-d54b578ee4fb.jpg)





#### abort 함수

> 처리되지 않는 예외의 경우, 헤더파일 stdlib.h 에 선언되어 있는 abort 함수가 호출됨

```c++
#include <iostream>
using std::endl;
using std::cout;
using std::cin;

int divide(int a, int b);   // a/b 몫만 반환

int main(void){
    int a, b;

    cout << "두 개의 숫자 입력: ";
    cin >> a >> b;
    cout << "a/b의 몫: " << divide(a,b) << endl;
    return 0;
}

int divide(int a, int b){
    if(b==0)
        throw b;
    return a/b;
}
```

ㆍ예외 발생 시,   abort() 호출될 경우 아래와 같은 오류가 발생함

![22222](https://user-images.githubusercontent.com/29933947/42322966-5f9ff58e-8099-11e8-9eb7-b9800738da9c.png)





### 전달되는 예외 명시

ㆍ유지보수 수월함을 위해 일반적으로 선언

```c++
// function1 함수는 int형 예외를 전달할 수 있다
int fucntion1(double d) throw (int)	
{
  ...
}

// function2 함수는 int형, double형, char*형 예외를 전달할 수 있다
int fucntion2(double d) throw (int, double, char *)	
{
  ...
}

// function3 함수는 어떠한 예외도 전달하지 않는다.
int fucntion3(double d) throw ()	
{
  ...
}

```



### 하나의 try + 여러 개의 catch 

` 