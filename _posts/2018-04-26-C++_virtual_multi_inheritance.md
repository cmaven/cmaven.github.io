---
layout: post
title: "C++ 가상함수와 다중상속"
date: 2018-04-26 12:00
categories: Program_Langague
tags: C++
---

C++의 가상함수와 다중 상속에 대해 정리한다.

------

###가상함수 동작 방식

```c++
#include <iostream>
using std::cout;
using std::endl;

class Base{
    int a, b;
    public:
        virtual void func1() { cout << " func1( ... ) " << endl; }
        virtual void func2() { cout << " func2( ... ) " << endl; }
};

class Derived : public Base{
    int c, d;
    public:
        virtual void func1() { cout << " overriding func1( ... ) " << endl; }
        void func3() { cout << " func3( ... ) " << endl; }        
};

int main(void)
{
    Base* bbb = new Base();
    bbb->func1();

    Derived* ddd = new Derived();
    ddd->func1();

    return 0;
}
```

![1](https://user-images.githubusercontent.com/29933947/39279152-44a442d8-4932-11e8-9bb5-f9d35ea0a019.png)



#### 가상 함수 테이블 (Virtual Table)

  . 한 개 이상의 가상함수를 포함하는 클래스에 대해, 컴파일러는 `가상 함수 테이블` 을 생성함

  . VTable은 실제 호출되어야 할 함수의 위치 정보를 가지고 있는 테이블



  . Base 클래스에 대한 가상 함수 테이블 형상

![_ 1](https://user-images.githubusercontent.com/29933947/39279872-a186a2bc-4936-11e8-921a-594355511a69.png)



  . Derived 클래스에 대한 가상 함수 테이블 형상

  . Derived 클래스에서 Base 클래스의 func1()을 오버라이딩 하여, 해당 함수에 대한 번지수 (Value)는 테이블에 참조되지 않음

![_ 4](https://user-images.githubusercontent.com/29933947/39279885-bba7dee0-4936-11e8-861a-6dc6eb523302.png)





   . 가상 함수 테이블과 가상 함수와의 관계, 이는 main 함수가 호출되기 전의 프로그램 메모리 구조 형상

![_ 3](https://user-images.githubusercontent.com/29933947/39279871-a15d9cfa-4936-11e8-93fa-8cc957f1df06.png)



  . main 함수 호출 후, 가상 함수 테이블과 가상 함수와의 관계

  .  하나 이상의 가상 함수를 멤버로 지니는 클래스의 객체에는 VTable을 위한 포인터가 멤버로 추가된다.(자동으로)

  .  때문에, 가상함수를 지니는 클래스가 많아질 수록 프로그램의 성능은 떨어지게 됨

![_ 5](https://user-images.githubusercontent.com/29933947/39289578-b16fe07c-4967-11e8-87f3-f81c9fc0324b.png)





### 다중 상속

> 하나의 Derived 클래스가 둘 이상의 Base 클래스를 상속하는 것

  . 일반적으로 클래스들의 관계를 복잡하게 만들고, 관리에 어려움이 있어 많이 쓰이지 않는다.

```c++
#include <iostream>
using std::cout;
using std::endl;

class Base1{
    public:
        void String(){
            cout << " BASE1::String " << endl;
        }
};

class Base2{
    public:
        void String(){
            cout << " BASE2::String " << endl;
        }
};

class Derived : public Base1, public Base2{
    public:
        void ShowString(){
            String();   // Base1::String(); 으로 변경해야 컴파일 가능
            String();   // Base2::String(); 으로 변경해야 컴파일 가능
        }
};

int main(void){
    Derived ddd;
    ddd.ShowString();
    return 0;
}
```

  . 위의 예제소스는 상속받는 클래스에서 ShowString을 호출 시, 가져와야할 String 함수가 모호하여 에러가 발생함

```c++
        void ShowString(){
            Base1::String();
            Base2::String();
        }
```

  .  위와 같이 직접 지정해 주어야 함



#### Virtual Base 클래스

```c++
#include <iostream>
using std::cout;
using std::endl;

class Base{
    public:
        void String1(){
            cout << " Base::String " << endl;
        }
};

// class Derived1 : virtual public Base
class Derived1 : public Base {
    public:
        void String2(){
            cout << " Derived1::String " << endl;
        }
};

// class Derived2 : virtual public Base
class Derived2 : public Base {
    public:
        void String3(){
            cout << " Derived2::String " << endl;
        }
};

class Last : public Derived1, public Derived2{
    public:
        void ShowString(){
          	// ambiguous 오류 발생
            // String1()이, Derived1, Derived2 어느 String1을 호출할 것인지 모름
            String1();      // Base 클래스의 String1
            String2();      // Derived 클래스의 String2
            String3();      // Derived 클래스의 String3
        }
};

int main(void)
{
    Last lll;
    lll.ShowString();

    return 0;
}
```

![1](https://user-images.githubusercontent.com/29933947/39310620-d3396d66-49a5-11e8-8ba5-34fb9d304cfd.png)



  . 위와 같은 오류는, 아래 도식처럼  Last 클래스가 Base 클래스를 두 번 상속 받기 때문에 발생한 문제이다.

  . 이는 Derived1, Derived2로부터 한 번씩 상속을 받앗기 때문에, 두 번 상속 받게 되는 것임



![_ 1](https://user-images.githubusercontent.com/29933947/39310121-9313bc6a-49a4-11e8-9944-c7434d79abac.png)



  . 이를 해결하기 위해서는 Virtual 상속을 활용해야 한다.

  . 위 코드를 아래와 같이 수정하면 오류 없이 실행 가능하다. 단, 다중 상속은 사용하지 않는 것이 좋다.

```c++
class Derived1 : virtual Base {
    public:
        void String2(){
            cout << " Derived1::String " << endl;
        }
};

class Derived2 : virtual Base {
    public:
        void String3(){
            cout << " Derived2::String " << endl;
        }
};
```

