---
layout: post
title: "C++ Inheritance Example"
date: 2018-04-25 12:00
categories: Program_Language
tags: C++
---

C++의 상속 개념을 활용한, 객체 지향 예제 프로그램 작성하고 정리한다.

------

### 고용 형태에 따른 급여 관리 프로그램

  . 새로운 클래스가 추가되어도 프로그램의 다른 영역에 변경이 가해지지 않는 프로그램 작성

  . 고용직(Permanent), 임시직(Temporary) 의 고용형태가 존재



##### 필요한 개념

1. 클래스 상속
2. 함수 오버라이딩
3. 가상 함수(virtual function)
4. 객체 포인터 개념



```c++
#include <iostream>
#include <cstring>
using std::endl;
using std::cout;

/* ============= Employee Class ============= */
class Employee{
    protected:
        char name[20];
    public:
        Employee(char* _name);
        const char* GetName();
        virtual int GetPay(){
            return 0;
        }
        // virtual int Getpay()=0; 과 같은 정의
};

Employee::Employee(char* _name)
{
    strcpy(name, _name);
}
const char* Employee::GetName()
{
    return name;
}

/* ============= Permanent Class ============= */
class Permanent : public Employee
{
    private:
        int salary;     // 기본 급여
    public:
        Permanent(char* _name, int sal);
        int GetPay();
};

Permanent::Permanent(char* _name, int sal) : Employee(_name)
{
    salary = sal;
}
int Permanent::GetPay()
{
    return salary;
}

/* ============= Temporary Class ============= */
class Temporary : public Employee
{
    private:
        int time;
        int pay;
    public:
        Temporary(char* _name, int _time, int _pay);
        int GetPay();
};

Temporary::Temporary(char* _name, int _time, int _pay) : Employee(_name)
{
    time = _time;
    pay = _pay;
}
int Temporary::GetPay()
{
    return time*pay;
}

/* ============= Department Class ============= */
class Department
{
    private:
        Employee * empList[10];
        int index;
    public:
        Department(): index(0) { };
        void AddEmployee(Employee * emp);       // Employee 객체 포인터로 되어 있기 때문에,
                                                // Main에서 Permanent 객체를 생성한 값을
  	                                            // 넣어도 무관함(상속받았기 때문)
        void ShowList();                        // 급여 리스트 출력
};

void Department::AddEmployee(Employee * emp)
{
    empList[index++] = emp;
}
void Department::ShowList()
{
    for(int i=0; i<index; i++)
    {
        cout << "[" << i+1 << "] " << "name : " << empList[i]->GetName() << endl;
        // 아래 코드는, Department의 empList로 접근하려는 GetPay가 Department
        // 내의 멤버가 아니기 때문에, Employee에 virtual 함수를 지정하지 않으면 오류를 발생함
        cout << "salary: " << empList[i]->GetPay() << endl; 
    }
}

/* ============= Main ============= */
int main()
{
    Department department;

    department.AddEmployee(new Permanent( "Lee", 2000));
    department.AddEmployee(new Permanent( "Oh", 4000));
    department.AddEmployee(new Temporary("KANG", 10, 150));
    department.AddEmployee(new Temporary("Son", 12, 250));

    department.ShowList();

    return 0;
}
```



#### 클래스에 명시되지 않은 멤버 접근 문제

> Employee 클래스에 `virtual int GetPay()=0;` 이 존재하지 않을 경우,
>
> Department 클래스의 `empList[i]->GetPay()` 부분은 오류가 발생한다.



![11](https://user-images.githubusercontent.com/29933947/39238962-94932db8-48ba-11e8-8a30-d480bda570f1.png)





> empList[] 배열은 각각, Permanent 혹은 Temporary 객체를 가리키고 있다
>
> 그런데, Employee 클래스에는 GetPay() 가 선언되어 있지 않기 때문에 오류가 발생한다.
>
> * 객체 포인터(배열)은 클래스에 존재하는 멤버에만 접근이 가능하도록 함



![_ 11](https://user-images.githubusercontent.com/29933947/39238673-cf5eb7ce-48b9-11e8-9903-8064b2a8308c.png)



> Employee에 GetPay() 가상함수를 추가함으로서, Employee 클래스를 상속받은 Permanent, Temporary 객체에 대한 포인터(배열)를 통한 GetPay() 함수의 호출이 가능해짐



![_ 12](https://user-images.githubusercontent.com/29933947/39238636-bbebeb8a-48b9-11e8-96f0-f1eee23e8f4d.png)



![10](https://user-images.githubusercontent.com/29933947/39238961-94679fae-48ba-11e8-83d1-f31816804135.png)



#### 순수 가상 함수와 추상 클래스 (Abstract class)

```c++
// 순수 가상함수
// GetPay 함수는 호출될 일이 없기 때문에, 선언만하고 정의는 하지 않는다는 뜻
virtual int GetPay()=0;
```

> 하나 이상의 멤버 함수가 순수 가상 함수인 클래스를 가리켜 `추상(Abstract) 클래스` 라 지칭한다.
>
> 추상 클래스는 객체화 할 수 없다.