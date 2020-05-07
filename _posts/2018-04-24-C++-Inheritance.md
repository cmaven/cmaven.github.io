---
layout: post
title: "C++ Inheritance (상속)"
date: 2018-04-24 12:00
categories: Program_Language
tags: C++
---

C++의 상속 개념 및 사용법에 관해 정리한다.

------

### 개요

> 기존에 정의한 클래스를 재활용하기 위한 방법

> 클래스의 공통되는 부분을 Base 클래스로 추상화 하고, 특징을 지닌 Derived 클래스를 정의할 수 있음

  . B 클래스가 A 클래스를 상속할 경우

​    : B 클래스는 "A 클래스에 선언되어 있는 멤버 + B 클래스에 선언된 멤버" 를 지님

  . 상속되는 클래스 : Super class or Base class

  . 상속받는 클래스 : Sub class or Derived class



```c++
						class Base : public Derived
```

```c++
#include <iostream>
#include <cstring>

using std::endl;
using std::cout;

class Person
{
    int age;
    char name[20];

    public:
        int GetAge() const {
            return age;
        }
        const char* GetName() const {
            return name;
        }
        Person(int _age=1, char* _name="none"){
            age = _age;
            strcpy(name, _name);
        }    
};

class Student: public Person    // Person 클래스를 상속
{
    char major[20];

    public:
        Student(char* _major){
            strcpy(major, _major);
        }
        const char* GetMajor() const {
            return major;            
        }
        void ShowData() const {
            cout << "이름 :" << GetName() << endl;
            cout << "나이 :" << GetAge() << endl;
            cout << "전공 :" << GetMajor() << endl;
        }
};

int main(void)
{
    Student Lee("Computer");
    Lee.ShowData();

    return 0;
}
```

![5](https://user-images.githubusercontent.com/29933947/39176079-d3d98f5a-47e6-11e8-8ce7-97121bc009ea.png)



  . Student 객체가 처음 생성 되었을 때, 모습

![_ 1](https://user-images.githubusercontent.com/29933947/39176196-33e0a55a-47e7-11e8-987c-5148ea025b08.png)



#### 생성 및 소멸

  . 생성 과정

1. 메모리 공간 할당, 상속되는 클래스를 감안하여 메모리가 할당됨

   ![_ 2](https://user-images.githubusercontent.com/29933947/39177526-81882294-47ea-11e8-87ad-11c2306980e4.png)

2. Derived 클래스 생성자 호출

   ![_ 3](https://user-images.githubusercontent.com/29933947/39177528-82f5825c-47ea-11e8-8f4f-8ad2d8539757.png)

     : 이 때, BBB(init j) 생성자가 호출만 될 뿐, 함수의 몸체( { ... } )부분은 실행되지 않음

     : 상속하고 있는 AAA의 클래스 생성자가 우선 실행 된 후, 실행되어야 하기 때문임

     : 별 다른 선언(상속하고 있는 AAA 클래스의 어떤 생성자 호출할지 여부)가 없으면, Void 생성자 호출

     : 상속하고 있는 클래스의 특정 생성자 호출 시, `멤버 이니셜라이저` 활용

   ​

3. Base 클래스 생성자 실행

   ```c++
   // 상속하고 있는 AAA 클래스의 어떠한 생성자를 호출해야 한다는 선언이 존재하지 않음
   // 따라서, AAA 클래스(Base 클래스의) void 생성자가 호출 및 실행 됨
   BBB(int j){			
      cout << " BBB(int j) call!" << endl;
   }
   ```

   ```c++
   BBB(int j) : AAA(j) {				// j 인자를 받을 수 있는 AAA 클래스의 생성자를 호출!
      cout << " BBB(int j) call!" << endl; 
   }
   ```

   ![_ 4](https://user-images.githubusercontent.com/29933947/39177529-8456177e-47ea-11e8-8409-ef4420012c38.png)

   ​

4. Derived 클래스 생성자 실행

   ![_ 5](https://user-images.githubusercontent.com/29933947/39178519-e03d7c06-47ec-11e8-837f-9d5fc814205b.png)

   ​

```c++
#include <iostream>
#include <cstring>

using std::endl;
using std::cout;

class AAA{
    public:
        AAA(){
            cout << "AAA() call!" << endl;
        }
        AAA(int i){
            cout << "AAA(int i) call!" << endl;
        }    
};

class BBB : public AAA{
    public:
        BBB(){
            cout << "BBB() call!" << endl;
        }
        BBB(int j){
            cout << "BBB(int j) call!" << endl;
        }    
};

int main(void)
{
    cout << "객체 1 생성" << endl;
    BBB bbb1;		// BBB 생성자 호출 -> AAA 생성자(void) 호출/실행 -> BBB 생성자 실행

    cout << "객체 2 생성" << endl;
    BBB bbb2(10);	// BBB 생성자 호출 -> AAA 생성자(int) 호출/실행 -> BBB 생성자 실행

    return 0;
}
```

![6](https://user-images.githubusercontent.com/29933947/39177352-0cb60ff8-47ea-11e8-8004-9eeaba747841.png)



##### 상속 클래스 객체 생성에 따른 초기화

```c++
#include <iostream>
#i nclude <cstring>
using std::endl;
using std::cout;

class Person
{
    int age;
    char name[20];

    public:
        int GetAge() const {
            return age;
        }
        const char* GetName() const {
            return name;
        }
        Person(int _age=1, char* _name="none"){
            age = _age;
            strcpy(name, _name);
        }    
};

class Student: public Person
{
    char major[20];

    public:
        Student(int _age, char* _name, char* _major) : Person(_age, _name){
            // age = _age;          // compile error
            // strcpy(name, _name); // compile error
            strcpy(major, _major);
        }
        const char* GetMajor() const {
            return major;            
        }
        void ShowData() const {
            cout << "이름 :" << GetName() << endl;
            cout << "나이 :" << GetAge() << endl;
            cout << "전공 :" << GetMajor() << endl;
        }
};

int main(void)
{
    Student Lee(30, "Lee Yuna", "Computer");
    Lee.ShowData();

    return 0;
}
```

![7](https://user-images.githubusercontent.com/29933947/39178643-36c5fd46-47ed-11e8-85ad-3e9085c4036a.png)



   . 위 예제에서, `compile error`  로 주석 처리된 부분을 활성화 하기 위해서는, Person 클래스의 age,     

​     name을 public 멤버로 설정해야함  → `정보은닉` 문제 발생

  . 때문에, 예제에서 처럼, `: Person(_age, _name)` 을 통해 생성자 명시적 호출

```c++
        Student(int _age, char* _name, char* _major) : Person(_age, _name){
            strcpy(major, _major);
        }
```

  . 멤버변수 접근은 부모 클래스의 함수를 통해 수행하도록 함

```c++
        int GetAge() const {
            return age;
        }
        const char* GetName() const {
            return name;
        }
```

 

  . 소멸 과정

1.  Derived 클래스 소멸자 실행
2.  Base 클래스 소멸자 실행

```c++
#include <iostream>
#include <cstring>

using std::endl;
using std::cout;

class AAA{
    public:
        AAA(){
            cout << "AAA() call!" << endl;
        }
        ~AAA(){
            cout << " ~AAA() call!" << endl;
        }
 
};

class BBB : public AAA{
    public:
        BBB(){
            cout << "BBB() call!" << endl;
        }
        ~BBB(){
            cout << " ~BBB() call!" << endl;
        }    
};

int main(void)
{    
    BBB bbb;
    return 0;
}
```

![8](https://user-images.githubusercontent.com/29933947/39179286-e4497172-47ee-11e8-9eb4-19dc674e791f.png)

  . 상속받은 클래스에 대한 객체 소멸 시, 상속하는 클래스의 소멸자 호출!



### protected 멤버

  `protected 멤버는 외부에서 볼 때 private, 상속 관계에서는 public`

  `protected 멤버는 상속 관계에서만 접근을 허용함`



```c++
#include <iostream>
#include <cstring>

using std::endl;
using std::cout;

class AAA{
    private:
        int a;
    protected:
        int b; 
};

class BBB : public AAA{
    public:
        void SetData(){
            // a = 10; // private member, Compile Error
            b = 20; // protected member, working
        }    
};

int main(void)
{    
    AAA aaa;
    // aaa.a = 10; // private member, Compile Error
    // aaa.b = 20; // protected member, Compile Error

    BBB bbb;
    bbb.SetData();   

    return 0;
}
```



### 상속 형태

![_ 6](https://user-images.githubusercontent.com/29933947/39181318-3eb9ee7a-47f4-11e8-8427-daceb535cbba.png)

  . 각각의 상속은 본인보다 접근 권한이 넓은 것을 본인하고 동일하게 맞춤





### 상속 조건

#### IS-A 관계

![_ 7](https://user-images.githubusercontent.com/29933947/39181888-0820b46e-47f6-11e8-8a3e-d269b8494e0b.png)



#### HAS-A 관계

![_ 8](https://user-images.githubusercontent.com/29933947/39182054-82bbeca2-47f6-11e8-971f-75375f767e53.png)

```c++
#include <iostream>
using std::endl;
using std::cout;

class Cudgel{
    public:
        void Swing(){ cout << "Swing a cudgel!" << endl; }    
};

class Police : public Cudgel
{
    public:
        void UseWeapon(){ Swing(); }
};

int main()
{
    Police p1;
    p1.UseWeapon();
    return 0;
}
```

![9](https://user-images.githubusercontent.com/29933947/39182401-c0c95f56-47f7-11e8-8f6c-4e10bfa08e11.png)



##### HAS-A 관계와 유사한 역할을 하는 포함관계-1

```c++
#include <iostream>
using std::endl;
using std::cout;

class Cudgel{
    public:
        void Swing(){ cout << "Swing a cudgel!" << endl; }    
};

class Police
{
    Cudgel cud;     // 클래스 객체를 멤버화
    public:
        void UseWeapon(){ cud.Swing(); }
};

int main()
{
    Police p1;
    p1.UseWeapon();
    return 0;
}
```

![10](https://user-images.githubusercontent.com/29933947/39183183-24b9b95a-47fa-11e8-883f-5910502c21d2.png)



![_ 9](https://user-images.githubusercontent.com/29933947/39183485-1eb75674-47fb-11e8-8af5-65444a9b711c.png)



##### HAS-A 관계와 유사한 역할을 하는 포함관계-2

```c++
#include <iostream>
using std::endl;
using std::cout;

class Cudgel{
    public:
        void Swing(){ cout << "Swing a cudgel!" << endl; }    
};

class Police
{
    Cudgel* cud;     // 클래스 객체를 멤버화
    public:
        Police(){
            cud = new Cudgel;            
        }
        ~Police(){
            delete cud;
        }
        void UseWeapon(){ cud->Swing(); }
};

int main()
{
    Police p1;
    p1.UseWeapon();
    return 0;
}
```

![11](https://user-images.githubusercontent.com/29933947/39183184-24e63cdc-47fa-11e8-826d-2da314025d80.png)



![_ 10](https://user-images.githubusercontent.com/29933947/39183504-312de2dc-47fb-11e8-82df-157de38c9b2f.png)







### 상속된 객체와 포인터

#### 객체 포인터

> 해당 클래스의 객체 주소 값 뿐만 아니라, 이 클래스를 상속받는 Derived 클래스의 객체 주소 값도 저장 가능함

```c++
#include <iostream>
using std::endl;
using std::cout;

class Person{
    public:
        void Sleep(){
            cout << " Sleep " << endl;
        }
};

class Student : public Person{
    public:
        void Study(){
            cout << " Study " << endl;
        }
};

class PartTimeStd : public Student {
    public:
        void Work(){
            cout << " Work " << endl;
        }
};

int main(void){
    // ( Person* ) 는 객체 포인터로,
    // Person 클래스를 상속받는 클래스의 객체 주소 값도 저장할 수 있다
    Person* p1 = new Person;
    Person* p2 = new Student;
    Person* p3 = new PartTimeStd;

    p1->Sleep();
    p2->Sleep();
    p3->Sleep();
    
    return 0;
}
```

![1](https://user-images.githubusercontent.com/29933947/39220538-ba9f85b8-486c-11e8-9b0d-bdd3856f6493.png)



  . 각 클래스의 관계

![_ 1](https://user-images.githubusercontent.com/29933947/39220623-45431bc6-486d-11e8-8b15-1dd96f845e8c.png)





#### 객체 포인터 권한

```c++
#include <iostream>
using std::endl;
using std::cout;

class Person{
    public:
        void Sleep(){
            cout << " Sleep " << endl;
        }
};

class Student : public Person{
    public:
        void Study(){
            cout << " Study " << endl;
        }
};

class PartTimeStd : public Student {
    public:
        void Work(){
            cout << " Work " << endl;
        }
};

int main(void){
    Person* p3 = new PartTimeStd;

    p3->Sleep();

    // p3->Study(); // Error 원인
    // p3->Work(); // Error 원인
    
    return 0;
}
```

![_1111](https://user-images.githubusercontent.com/29933947/39223501-620b478c-487d-11e8-9379-cbc480b44ebc.png)



> A 클래스의 객체 포인터는 A 클래스 타입 내에 선언된 멤버에만 접근 가능함
>
> A 클래스를 상속받은 B 클래스의 경우, A 클래스 타입의 객체 포인터로 지정을 하였어도, A 클래스 타입 내에 선언된 멤버에만 접근이 가능하다



### 상속된 객체와 참조 관계

#### 객체 레퍼런스

```c++
#include <iostream>
using std::endl;
using std::cout;

class Person{
    public:
        void Sleep(){
            cout << " Sleep " << endl;
        }
};

class Student : public Person{
    public:
        void Study(){
            cout << " Study " << endl;
        }
};

class PartTimeStd : public Student {
    public:
        void Work(){
            cout << " Work " << endl;
        }
};

int main(void){
    PartTimeStd p;
    Student& ref1 = p;
    Person& ref2 = p;

    p.Sleep();
    ref1.Sleep();
    ref2.Sleep();
    
    return 0;
}
```

![2](https://user-images.githubusercontent.com/29933947/39227820-ac136018-4895-11e8-8280-85d196bb8e4e.png)

  . 레퍼런스는 이름을 하나 더 부여하는 것으로, 위 예제에서의 p 객체는 3개의 이름을 가지게 됨

  . 레퍼런스를 통해 객체와 해당 클래스를 상속하는 Derived 객체도 참조가 가능함



#### 객체 레퍼런스 권한

```c++
#include <iostream>
using std::endl;
using std::cout;

class Person{
    public:
        void Sleep(){
            cout << " Sleep " << endl;
        }
};

class Student : public Person{
    public:
        void Study(){
            cout << " Study " << endl;
        }
};

class PartTimeStd : public Student {
    public:
        void Work(){
            cout << " Work " << endl;
        }
};

int main(void){
    PartTimeStd p;
    p.Sleep();
    p.Study();
    p.Work();

    Person& ref = p;
    ref.Sleep();
    // ref.Study();    // Error
    // ref.Work();     // Error
    
    return 0;
}
```

   . 위 예제의 ref.Study(), ref.Work() 의 경우 Person 클래스는 멤버로 Study와 Work를 지니지 않기 때문에 컴파일 

​     오류를 발생시킨다.



##### 결론

```c++
1. PartTimeStd p;
   - PartTimeStd가 상속받은 모든 클래스에 접근 가능(단, public, protected)
2. PartTimeStd * p;
   - PartTimeStd Class에만 접근가능
3. PartTimeStd & p;
   - PartTimeStd Class에만 접근가능
```



### 정적, 동적 바인딩 (Static / Dynamic Binding)

> 정적 바인딩은 컴파일 시, 호출될 함수가 정해지도록 하는 방법
>
> `Base b; b.func();` 의 형태로 사용됨

> 동적 바인딩은 함수 호출 시,  상황에 따라 실제 호출되는 함수가 달라지는 방법
>
> `*Base b = new xxx; b->func();` 의 형태로 사용됨



#### 오버라이딩 (Overriding)

```c++
#include <iostream>
using std::endl;
using std::cout;

class Base{
    public:
        void func(){			// Dervied의 func()에 의해 오버라이딩 됨
            cout << "BASE" << endl;
        }
};

class Dervied : public Base {
    public:
        void func(){			// Base의 func()을 오버라이딩 함
            cout << "Dervied" << endl;
        }
};

int main(void)
{
    Dervied d;
    d.func();

    return 0;
}
```

![3](https://user-images.githubusercontent.com/29933947/39228538-9f3a2c74-4899-11e8-957d-b21dce738c91.png)



![_ 2](https://user-images.githubusercontent.com/29933947/39228817-ebb04308-489a-11e8-8a21-a0c428a1cb04.png)



> Base 클래스에 선언된 형태의 함수를 Derived 클래스에서 다시 선언하는 것
>
> 이 때, Base 클래스의 함수는 가려지게 된다(Hiding)







#### 오버라이딩 된 함수 호출

##### 포인터 활용

```c++
#include <iostream>
using std::endl;
using std::cout;

class Base{
    public:
        void func(){
            cout << "BASE" << endl;
        }
};

class Dervied : public Base{
    public:
        void func(){
            cout << "Dervied" << endl;
        }
};

int main(void)
{
    // Dervied d;
    // d.func();

    Dervied* d = new Dervied;
    d->func();

    Base* b = d;	// Base 객체 포인터로, Derived 객체 포인터 d 의 값을 받음
    b->func();
  	
  	// 즉, 선언된 객체 포인터 타입에 따라 접근할 수 있는 함수가 정해짐
  
    delete b;
    
    return 0;
}
```

![4](https://user-images.githubusercontent.com/29933947/39229992-df3497aa-489f-11e8-9612-35dca9ba1c1c.png)

  . Dervied 객체를 Dervied 포인터로 접근할 경우, Dervied 클래스 내에 선언된 멤버 함수만 접근할 수 있음

![_ 3](https://user-images.githubusercontent.com/29933947/39229964-bebdb470-489f-11e8-8157-2f2c0dd3cedf.png)



  . Dervied 객체를 Base 포인터로 접근할 경우 (`Dervied는 Base 클래스를 상속받은 클래스이기 때문에,  Base 포인터로 Dervied 객체 주소를 받을 수 있음`)  Base 클래스 내에 선언된 멤버 함수를 접근할 수 있음

  . 이는, Derived 객체를 포인터 입장에서는 Base 객체로 판단하기 때문임

![_ 4](https://user-images.githubusercontent.com/29933947/39229966-bf80156a-489f-11e8-8583-8d8522fe74c4.png)



##### 범위 지정 연산자 활용

  . 방법 1은 자주 쓰이는 방법이나, 방법 2는 클래스 디자인의 실패로 간주되어 자주 쓰이지 않는다

```c++
#include <iostream>
using std::endl;
using std::cout;

class Base{
    public:
        virtual void func(){
            cout << "BASE" << endl;
        }
};

class Dervied : public Base{
    public:
        void func(){ 
            Base::func();       // 방법 1
            cout << "Dervied" << endl;
        }
};

int main(void)
{    
    Base* b = new Dervied;
    cout << "첫 번째 시도입니다." << endl;
    b->func(); 

    cout << "두 번째 시도입니다." << endl;
    b->Base::func();            // 방법 2

    delete b;
        
    return 0;
}
```





#### 멤버 함수의 가상 (Virtual) 선언

> `virtual` 키워드를 함수 앞에 선언
>
> 해당 함수는 dynamic binding
>
> 만들어진 객체의 접근 형태에 따라, 사용할 함수를 선택하여 접근할 수 있다

```c++
#include <iostream>
using std::endl;
using std::cout;

class Base{
    public:
        virtual void func(){
            cout << "BASE" << endl;
        }
};

class Dervied : public Base{
    public:
        void func(){
            cout << "Dervied" << endl;
        }
};

int main(void)
{
    // Dervied d;
    // d.func();

    Dervied* d = new Dervied;
    d->func();

    Base* b = d;
    b->func();

    Base * k = new Base;
    k->func();

    delete b;
    delete k;    
    
    return 0;
}
```

![2](https://user-images.githubusercontent.com/29933947/42140965-641ac7ee-7de0-11e8-9619-f2b9d731a83d.png)



  . Base 포인터로 접근하더라도, Base 클래스 내의 func()은 virtual 선언이 되어 있어, Base 클래스를 상속받은 Dervied 클래스의 func()이 호출되게 됨

![_ 5](https://user-images.githubusercontent.com/29933947/39230454-7eedb4ce-48a1-11e8-96cf-8bac4bce5662.png)







```c++
#include <iostream>
using std::endl;
using std::cout;

class Base{
    public:
        virtual void func(){
            cout << "BASE" << endl;
        }
};

class FDervied : public Base{
    public:
        void func(){        // virtual void func();
            cout << "FDervied" << endl;
        }
};

class SDervied : public FDervied{
    public:
        void func(){        // virtual void func();
            cout << "SDervied" << endl;
        }
};

int main(void)
{    
    FDervied* fd = new SDervied;
    fd->func();

    Base* b = fd;
    b->func();

    delete b;
    
    return 0;
}
```

![6](https://user-images.githubusercontent.com/29933947/39230859-1482d6b2-48a3-11e8-9306-2c1115e19ab0.png)



  . 가상화 (virtual) 선언된 함수를 오버라이딩 하면, 최종적으로 오버라이딩한 함수만 Call을 받을 수 있게 됨

![_ 6](https://user-images.githubusercontent.com/29933947/39231173-2bd791b2-48a4-11e8-9951-947235abffdc.png)





![_ 7](https://user-images.githubusercontent.com/29933947/39231163-1e7789d2-48a4-11e8-906d-364e3be05bfd.png)

#### Virtual 소멸자

> virtual 키워드는 `가상함수`, `소멸자` 에 사용됨

```c++
#include <iostream>
#include <cstring>

using std::endl;
using std::cout;

class Base{
    char* str1;
    public:
        Base(char* _str1){
            str1 = new char[strlen(_str1)+1];
            strcpy(str1, _str1);
        }
  		~Base(){		// 소멸 시, 메모리 유출(누수) 발생 가능성 존재
        // virtual ~Base()	의 형태로 선언해야 함
            cout << " ~Base() call! " << endl;
            delete []str1;
        }
        virtual void ShowString(){
            cout << str1 << ' ';
        }
};

class Dervied : public Base {
    char* str2;
    public:
        Dervied(char* _str1, char* _str2) : Base(_str1){
            str2 = new char[strlen(_str2) + 1];
            strcpy(str2, _str2);
        }
        ~Dervied(){
            cout << " ~Dervied() call! " << endl;
            delete []str2;
        }
        virtual void ShowString(){
            Base::ShowString();
            cout << str2 << endl;
        }
};

int main()
{
    Base * b = new Dervied( "Hello", "Asia");
    Dervied * d = new Dervied( "Hello", "World");

    b->ShowString();		// Base의 ShowString()는 Virtual 이기 때문에, Dervied의 함수 호출
    d->ShowString();

    cout << "=============== 객체 소멸 =================" << endl;
    delete b;
    delete d;

    return 0;
}
```

![8](https://user-images.githubusercontent.com/29933947/39232899-c0150d1e-48a9-11e8-9603-7db4a3e657fd.png)





  . 실행 결과를 살펴보면, Dervied 객체는 2번 생성되었음에도 불구하고, 소멸자는 한 번만 호출되었음

  . 포인터 b가 가리키는 객체는 Dervied 객체이지만, Base 타입의 포인터로 가리키고 있기 때문에, 컴파일러는 Base 객체로 인식함. 따라서 Dervied 객체의 소멸자는 호출되지 않음

![_ 8](https://user-images.githubusercontent.com/29933947/39235101-f4df2394-48af-11e8-873f-960649e07192.png)



![_ 9](https://user-images.githubusercontent.com/29933947/39235106-f69673f4-48af-11e8-9432-d6f8d31aeff1.png)

##### 해결 방법

```c++
        virtual ~Base(){
            cout << " ~Base() call! " << endl;
            delete []str1;
        }
```

![9](https://user-images.githubusercontent.com/29933947/39235274-6d7ed3c6-48b0-11e8-8735-495fa6152621.png)



1.   Base 클래스의 소멸자를 호출
2.   Base 클래스의 소멸자가 virtual 이기 때문에 Derived 클래스의 소멸자를 호출함
3.   Derived 클래스의 소멸자는 Base 클래스를 상속하고 있기 때문에, Base 클래스의 소멸자를 재호출



![_ 10](https://user-images.githubusercontent.com/29933947/39235390-bbefe946-48b0-11e8-8203-c643d3d0b1a7.png)

