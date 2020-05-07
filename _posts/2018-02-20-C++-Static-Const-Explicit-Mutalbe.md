---
layout: post
title: "C++ Static, Const, Explicit, Mutalbe"
date: 2018-02-20 12:00
categories: Program_Language
tags: C++
---

C++ static, const, explicit, mutable 에 대해 정리한다.

------

### const

#### 기본

1. 변수 상수화

   ```c++
   const int val1;
   // val1 = 10;      !불가

   const doule val2 = 20.0;
   // val2 = 30.0     !불가
   ```

   ​

2. 포인터가 가리키는 데이터 상수화

   ```c++
   int val1 = 10;
   const int * p = &val1;
   // *p = 20;       !불가
   ```

   ​

3. 포인터 자체 상수화

   ```c++
   int val1 = 10;
   int val2 = 20;
   int const * p = &val1;
   *p = 20;
   // p = &val2;    !불가
   ```

   ​

#### 멤버변수

  . 생성자 함수에 `:` 으로 연결된 멤버 이니셜라이져(member initializer)를 활용하여, 상수화 된 변수를 초기화 함

  . 멤버 이니셜라이져는 생성자보다 먼저 실행됨

  . const 멤버 변수가 아닌 일반 멤버 변수도 초기화가 가능함

```c++
#include <iostream>

using std::cout;
using std::endl;

class Student{
    const int id;
    int age;
    char name[20];
    char major[30];

    public:
        // 멤버 이니셜라이져 (member initializer)
        Student(int _id, int _age, char * _name, char* _major) : id(_id), age(_age)
        {
            // id = _id;    const int 이기 때문에 이 방법은 컴파일 오류
            // age = _age;  일반 멤버변수도 멤버 이니셜라이져 방법으로 초기화 가능
            strcpy(name, _name);
            strcpy(major, _major);            
        }
    void ShowData(){
        cout << "학번: " << id << endl;
        cout << "나이: " << age << endl;
        cout << "이름: " << name << endl;
        cout << "학과: " << major << endl;
    }
};

int main()
{
    Student K(201812345, 20, "Kim Young Mi", "Computer Science");
    Student P(201878901, 21, "Park Chan Ki", "English");

    K.ShowData();
    cout << endl;
    P.ShowData();
}
```



#### 멤버함수

```c++
...
void ShowData() const
{
 	cout << "학번: " << id << endl;
 	...
}
...
```

  . 멤버 함수가 상수화 되면

1.  해당 함수를 통해 멤버 변수의 값이 변경되는 것이 허용되지 않음
2.  상수화되지 않은 함수의 호출을 허용하지 않음
3.  멤버 변수의 포인터를 리턴하는 것을 허용하지 않음

```c++
#include <iostream>
using std::cout;
using std::endl;

class Count{
    int cnt;

    public:
        // 생성자, 초기화
        Count() : cnt(0) {}
  
        /* 상수화된 함수에서 포인터 리턴을 할 수 없으므로, 컴파일 에러
        int * GetPtr() const {
             return &cnt;
        }
        */
  
        // 리턴 포인터(포인터가 가리키는 값)를 상수화
        // 따라서, 상수화된 함수 내에서 포인터 값을 리턴할 수 있음
        // ※ 포인터를 상수화 시키려면 const int * GetPtr [확인 필요]
        const int * GetPtr() const {
          return &cnt;
        }
  
        void Increment(){
          cnt++;
        }
  
        /*  상수화된 함수에서 상수화되지 않은 함수를 호출하므로, 컴파일 에러
        void ShowData() const {
            ShowIntro();
            cout << cnt << endl;
        }
        void ShowIntro(){
            cout << "count 값: " << endl;
        }
        */
  
        void ShowData() const {
          ShowIntro();
          cout << cnt << endl;
        }
        void ShowIntro() const {
            cout << "count 값: " << endl;
        }
};

int main()
{
    Count count;
    count.Increment();
    count.ShowData();
    return 0;
}
```

![1](https://user-images.githubusercontent.com/29933947/36543886-6bdefe14-1828-11e8-997c-25e8ed8924a6.png)



#### 객체

  . 객체의 멤버변수의 조작이 불가능함

  . 상수화된 멤버 함수만 호출 가능

  . 상수화된 멤버변수만 호출 가능

```c++
#include <iostream>
using std::cout;
using std::endl;

class Cal{
    int num;
    
    public:
        Cal(int _num) : num(_num) {}
        void Add(int n)
        {
            num += n;
        }
        void ShowData()
        {
            cout << num << endl;
        }
};

int main()
{
    const Cal cal1(10);
    // cal1.Add(10);       // const 객체로 인해 const 되지 않은 멤버변수 변경 불가
    // cal1.ShowData();    // const 객체로 인해 const 되지 않은 멤버함수 호출 불가
    return  0;
}
```



#### const화된 함수의 오버로딩

  . `상수화된 함수인지, 아닌지` 에 따라서 함수 오버로딩이 성립함

```c++
#include <iostream>
using std::cout;
using std::endl;

class Cal{
    int num;
    
    public:
        Cal(int _num) : num(_num) {}
        void ShowData()
        {
            cout << "void ShowData() 호출함 " << endl;
            cout << "num: " << num << endl;
        }
        void ShowData() const {
            cout << "void ShowData() const 호출함 " << endl;
            cout << "num: " << num << endl;
        }
};

int main()
{
    const Cal cal1(10);
    Cal cal2(20);
      	
    cal1.ShowData();	// 상수화된 객체로서, 상수화된 함수를 호출함
    cal2.ShowData();	// 상수화되지 않은 객체로, 상수화되지 않은 함수를 호출함

    return  0;
}
```

![2](https://user-images.githubusercontent.com/29933947/36545467-47d58584-182c-11e8-92fc-231ef6a2727e.png)





### static

#### static 멤버의 특징

  . 메인 함수가 호출되기 전에 메모리 공간에 올라가고, 초기화 됨

  . Public으로 선언될 경우, 객체 생성 이전에도 접근이 가능함

  . 선언 시, 클래스 내에 위치한다고 하여, 객체의 멤버로 존재하는 것이 아님. 다만 클래스 내에서 직접 접근할 수 있는 권한이 부여된 것

  . "<span style="color:red; font-weight:bold">클래스 함수</span>", "<span style="color:red; font-weight:bold">클래스 변수</span>" 가 정확한 표현

  . 메모리의 데이터 영역에 올라감(전역변수와 같은 특징)



#### static 멤버 초기화

```c++
...
  // int Classname::static_member_name=value_of_initilization;
  int Person::count=1;
...
```



```c++
#include <iostream>
using std::cout;
using std::endl;

class First{
    int val;
    static int n;	// private 선언, 외부접근이 불가능함

    public:
        First(int a=0){
            val = a;
            n++;	// 내부접근은 가능
        }
        void ShowData(){
            cout <<"val: "<<val<<endl;
            cout <<"n: "<<n<<endl;
        }
};

int First::n=1; // 전역변수(클래스 멤버변수) 초기화

int main(void)
{
    First f1(20);
    f1.ShowData();

    First f2(40);
    f2.ShowData();

    return 0;
}
```

![1](https://user-images.githubusercontent.com/29933947/36655632-3ddebfd6-1b07-11e8-81e3-238f6f0db181.png)



  . 예제에서는 각 객체 내에는 변수 n이 멤버로 존재하지 않으며, 접근할 수 있는 접근 권한만 주어짐

![_ 1](https://user-images.githubusercontent.com/29933947/36655797-3e9e5e62-1b08-11e8-8ec4-bee38decb91b.png)







### explicit

  . 명시적[^1] 호출만을 허용

  . 아래 예제에서 `explicit` 선언을 한 생성자에 대해서는, 묵시적[^2] 호출을 허용하지 않아, 에러가 발생함

  . `explicit` 선언은 객체 생성 관계를 분명히 하고자 하는 경우에 사용됨

[^1]: 내용이나 뜻을 분명하게 드러내 보이는
[^2]: 직접적으로 말이나 행동으로 드러내지 않고 은연중에 뜻을 나타내 보이는

```c++
#include <iostream>
using std::cout;
using std::endl;

class First{
    public:
        explicit First(int a){
        //First(int a){
            cout << "explict First(int a)" << endl;
        }
};

int main(void)
{
    First first = 10;	// 묵시적으로 First first(10); 으로 변환됨
    return 0;
}
```

![14](https://user-images.githubusercontent.com/29933947/36365238-f9b05bec-158b-11e8-8cd7-1be8033214bf.png)





### mutable

  . const로 상수화된 멤버 함수에서 멤버 변수 조작을 위해 사용함

```c++
#include <iostream>
using std::cout;
using std::endl;

class mutable_test{
    private:
        mutable int val1;
        int val2;
    public:	
  		// 생성자 멤버 변수 초기화
        mutable_test() : val1(0), val2(0) {}
        void SetData(int a, int b) const
        {
            val1 = a;       // mutable val1 이므로 오류 없이 변경 가능
            // val2 = b;    // 상수화된 멤버함수는 멤버변수를 변경할 수 없음
        }        
        void ShowData()
        {
            cout << "val1: " << val1 << endl;
            cout << "val2: " << val2 << endl;
        }
};

int main()
{
    mutable_test m1;
    m1.SetData(10, 20);
    m1.ShowData();

    return 0;
}
```

![3](https://user-images.githubusercontent.com/29933947/36585195-37b53a52-18c0-11e8-8bcc-6d08544c02a2.png)