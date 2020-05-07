---
layout: post
title: "String, strcpy 수행 시, constant warning"
date: 2018-06-21 12:00
categories: Program_Language
tags: C++
---

C++ String 사용 시, constant 관련 warning 해결 방법에 대해 기술한다.

------

#### 소스코드

```c++
#include <iostream>
#include <string.h>

using std::cout;
using std::endl;

class Printer{
    private:
        char str[30];
    public:      
        //void SetString(const char * _str);
        void SetString(char * _str);
        void ShowString();
};

//void Printer::SetString(const char * _str){
void Printer::SetString(char * _str){     
    strcpy(str, _str);
}
void Printer::ShowString(){        
    cout << str << endl;
}

int main(void){
    Printer pnt;
    pnt.SetString("Hello World!");
    pnt.ShowString();

    pnt.SetString("I Love C++");
    pnt.ShowString();
    return 0;
}
```



#### 오류

```c++
chap_3-1-2.cpp:56:31: warning: ISO C++ forbids converting a string constant to 'char*' [-Wwrite-strings]
```



#### 원인

  . SetString 함수를 통해, str의 주소 값이 변경될 수 있는 위험성에 따라 경고가 발생함



#### 해결방안

> 문자열을 전달, 조작하는 인자에 const 키워드를 붙여줌
>
> 문자열을 가리키는 주소 값이 실수로 변경되는 오류를 미연에 방지

```c++
class Printer{
    private:
        //char * str;
        //const char* arr[];
        //const char * str;
        char str[30];
    public:      
        void SetString(const char * _str);	// const 키워드 추가
        // void SetString(char * _str);
        void ShowString();
};

void Printer::SetString(const char * _str){	// const 키워드 추가
//void Printer::SetString(char * _str){     
    strcpy(str, _str);
}
```

