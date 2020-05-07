---
layout: post
title: "C++ 복사생성자"
date: 2018-02-20 12:00
categories: Program_Language
tags: C++
---

C++ 관련 복사생성자에 대해 정리한다.

------

### 명시적[^1], 묵시적[^2] 초기화

[^1]: 내용이나 뜻을 분명하게 드러내 보이는
[^2]: 직접적으로 말이나 행동으로 드러내지 않고 은연중에 뜻을 나타내 보이는

```c++
#include <iostream>

using std::cout;
using std::endl;

class First{
    int val;
    public:
        First(int a){
            val = a;
        }
        void ShowData(){
            cout << val << endl;
        }
};

int main(void)
{
    int a = 10;     // 명시적 초기화  // C 형태의 초기화 
    int b(20);      // 묵시적 초기화	// C++ 형태의 초기화

    First f1(10);   // 묵시적 초기화
    f1.ShowData();

    First f2=20;    // 명시적 초기화
    f2.ShowData();

    cout << "a: " << a <<endl;
    cout << "b: " << b <<endl;

    return 0;
}
```

![15](https://user-images.githubusercontent.com/29933947/36366052-b01e0b56-158f-11e8-9b13-7fb5eefa5753.png)





### 복사 생성자

  . 자기 자신과 같은 형태의(자료형) 객체를 인자로 받을 수 있는 생성자

  . 생성자를 통한 메모리 할당 및 메모리 공간을 참조하는 멤버 변수가 존재할 때, 객체의 소멸로 인한 잘못된 메모리 참조를 

​    막기 위해 활용

#### 형태

```c++
#include <iostream>
using std::cout;
using std::endl;

class First{
    public:
        First(){
            cout << "First() 호출" << endl;
        }
        First(int a){
            cout << "First(int a) 호출" << endl;
        }
  		// 복사 생성자
  		// const 인자로 전달된 객체의 내용 변경을 허용하지 않음 (선택사항) 
  		// & 인자로 전달된 객체를 레퍼런스로 받음 (필수사항
        First(const First& a){
            cout << "First(const First& a) 호출" << endl;
        }
};

int main(void)
{
    First f1;   // call First();
    First f2(100);   // call First(int a);
    First f3(f2);   // call First(const First& a);

    return 0;
}
```

![1](https://user-images.githubusercontent.com/29933947/36382060-0d5df84a-15cb-11e8-98fc-6890f6b48201.png)

  . `&`  연산자의 경우, 생략하면 무한루프에 빠지게 됨



#### 디폴트(Default) 복사 생성자

  . 작성하지 않은 경우, 자동으로 삽입됨

  . 멤버 변수 대 맴버 변수의 복사를 수행함 → 메모리 영역을 할당하지 않은 채,  멤버변수 주소값을 전달

  . 따라서, 클래스 마다 디폴트 복사 생성자의 정의된 형태는 다름

```c++
#include <iostream>

using std::cout;
using std::endl;

class Point{
    int x, y;
    public:
        Point(int _x, int _y){
            x = _x;
            y = _y;
        }
  		// default copy constructor
  		// 해당 함수가 없어도 정상 작동, 함수의 역할은 디폴트 복사 생성자의 역할과 동일
    	/*
        Point(const Point& p){
            x = p.x;
            y = p.y;
        }
        */
        void ShowData(){
            cout << x << " " << y << endl;
        }
};

int main(void)
{
    Point p1(10, 20);
    Point p2(p1);

    p1.ShowData();
    p2.ShowData();

    return 0;
}
```

![2](https://user-images.githubusercontent.com/29933947/36382388-0ae88a98-15cc-11e8-89b8-5d722b6a5c3e.png)



#### Shallow copy

  . 디폴트 복사 생성자를 통해 객체를 생성할 때, 메모리 할당이 필요한 경우이면, 매개변수의 복사는 단순히 주소값을 참조하는 값을 복사하게 되어, 객체 소멸시 잘못된 메모리를 참조하게 되는 문제점을 지니고 있음



![_ _ 2](https://user-images.githubusercontent.com/29933947/36523809-bfadd192-17e6-11e8-8181-068c417307af.png)



  . 위와 같은 객체 생성 환경에서, 객체 소멸 순서에 의해 p2 객체가 소멸되면, p1 객체 소멸 시 p2 객체 소멸로 인해 이미 "ABC", "010-123-4567" 에 대한 메모리 공간이 해제 되어,  p1 객체 소멸에 참조할 메모리 공간을 찾을 수 없음

![_ 3](https://user-images.githubusercontent.com/29933947/36523986-94d476dc-17e7-11e8-8151-9f23bc51bcd9.png)



> 아래 예제에서는 char *name, char *phone의 멤버변수는 포인터 형태로 주소값을 가지고 있기 때문에, 
>
> 디폴트 복사 생성자에 의한 멤버변수 대 멤버변수 복사를 수행하면 주소값만 복사되어 두 개의 객체가 하나의 값을 가리키는 형상이 됨(위 그림)

```c++
#include <iostream>
#include <string.h>

using std::cout;
using std::endl;

class Person{
    char *name;
    char *phone;
    int age;

  	// 사용자 복사 생성자 선언 및 정의 안함    
    public:
        Person(char * _name, char* _phone, int _age);
        ~Person();    // 소멸자        
        void ShowData();
};

Person::Person(char * _name, char* _phone, int _age)
{
    name = new char[strlen(_name) + 1];    
    strcpy(name, _name);    

    phone = new char[strlen(_phone) + 1];
    strcpy(phone, _phone);
    age = _age;
}

Person::~Person()
{
    delete []name;
    delete []phone;
}

void Person::ShowData()
{
    cout << " name : " << name << endl;
    cout << " phone : " << phone << endl;
    cout << " age : " << age << endl;    
}

int main()
{
    Person p1("ABC", "010-123-4567", 30);
  	// 객체 생성 시, 디폴트 복사 생성자 호출
  	// 단순 주소값 복사만 이루어짐
    Person p2(p1);  // Person p2 = p1;
    
    p1.ShowData();
    p2.ShowData();

    return 0; 
}
```



#### Deep copy

  . 생성자 내에서 동적할당을 수행할 경우, 소멸자에 의한 객체 소멸 시, 디폴트 복사 생성자의 shallow copy로 인한 메모리 잘못된 참조를 막기 위해 deep copy를 하는 복사 생성자를 정의해야함



![_ _ 1](https://user-images.githubusercontent.com/29933947/36523793-b41c3184-17e6-11e8-9836-06518b70da01.png)



```c++
#include <iostream>
#include <string.h>

using std::cout;
using std::endl;

class Person{
    char *name;     // const 제외하면 ISO C++  forbids converting a string constant to "cahr*" 에러 발생
    char *phone;
    int age;

    public:
        Person(char * _name, char* _phone, int _age);
        Person(const Person& p);    // 복사 생성자
        ~Person();    // 소멸자        
        void ShowData();
};

// 객체를 인자로 받는 객체 생성 시, 사용자 지정 복사 생성자 정의 
Person::Person(const Person& p)
{
    name = new char[strlen(p.name) + 1];    
    strcpy(name, p.name);    

    phone = new char[strlen(p.phone) + 1];
    strcpy(phone, p.phone);
    age = p.age;

}

Person::Person(char * _name, char* _phone, int _age)
{
    name = new char[strlen(_name) + 1];    
    strcpy(name, _name);    

    phone = new char[strlen(_phone) + 1];
    strcpy(phone, _phone);
    age = _age;
}

Person::~Person()
{
    delete []name;
    delete []phone;
}

void Person::ShowData()
{
    cout << " name : " << name << endl;
    cout << " phone : " << phone << endl;
    cout << " age : " << age << endl;    
}

int main()
{
    Person p1("ABC", "010-123-4567", 30);
    Person p2(p1);  // Person p2 = p1;
    
    p1.ShowData();
    p2.ShowData();

    return 0; 
}
```

![6](https://user-images.githubusercontent.com/29933947/36523671-1029449a-17e6-11e8-80a8-90a7bc968b05.png)



  . `단! 위 코드에서는 아래와 같은 경고가 발생한다.`

![5](https://user-images.githubusercontent.com/29933947/36523670-0fff89ca-17e6-11e8-980f-5640af4b5823.png)



### 복사 생성자의 경우에 따른 호출 시점

#### 기존에 생성된 객체로 새로운 객체 초기화

  . 추후

#### 함수 호출 시 객체를 값에 의해 전달

  . 추후

#### 함수 내에서 객체를 값에 의해 리턴

  . 추후



