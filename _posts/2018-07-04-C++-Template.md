---
layout: post
title: "C++ Template"
data: 2018-07-04 12:00
categories: Program_Language
tags: C++
---

C++ Template에 대해 정리한다.

-------

ㆍ기능적 측면은 정해져 있으나, 데이터 타입은 정해져 있지 않을 경우 또는 다양한 데이터 타입을 하나의 기능으로 처리하도록 하기 위해 사용함

> 표준 템플릿의 모음 : STL(Standard Template Library)



#### 형태

```c++
template <typename T>
// == template <class T>
```

> T라는 이름(typename)에 대해, 다음에 정의하는 대상을 템플릿으로 선언한다



#### 함수템플릿

ㆍ다중 인자(둘 이상의 타입) 템플릿

ㆍ함수템플릿 특수화

```c++
#include <iostream>
#include <cstring>

using std::cout;
using std::endl;

template <typename T>   // 타입에 상관없이 덧셈 연산 수행
T Add(T a, T b){
    return a+b;
}

template <typename T1, typename T2>     // 둘 이상의 타입에 대응
void ShowData(T1 a, T2 b){
    cout << "[ " << a << ", " << b << " ]" << endl;    
}

template <typename T>
int SizeOf(T a){
    return sizeof(a);
}

// 정확한 표현 
// template <> int SizeOf<char *>(char* a)
template <>             // 함수 템플릿 특수화 선언
int SizeOf(const char * a){   // 전달 인자가 char*인 경우에는 이 함수 호출
    return strlen(a);
}

int main(void){
    int i=10;
    const char* str = "Hello!";

    cout << "--------------------------" << endl;
    // 인자에 상관없는 덧셈 연산    
    cout << Add(10, 20) << endl;
    cout << Add(1.1, 2.2) << endl;

    cout << "--------------------------" << endl;
    // 서로 다른 두개의 타입에 대한 처리
    ShowData(1, 2);
    ShowData(3, 2.5);

    cout << "--------------------------" << endl;
    // 특수한 타입에 대하여 별도 연산(함수 템플릿 특수화)
    cout << SizeOf(i) << endl;
    cout << SizeOf(str) << endl;

    return 0;
}
```

![1](https://user-images.githubusercontent.com/29933947/42253619-787e23f4-7f7d-11e8-8d02-6e199b24e15b.png)



#### 클래스템플릿

```c++
#include <iostream>
using std::cout;
using std::endl;

template <typename T>
class Data{
    private:
        T data;
    public:
        Data(T d);
        void SetData(T d);
        T Getdata();
};

template <typename T>
Data<T>::Data(T d){				// Data<T> 형태로 선언해 주어야함
    data=d;
}

template <typename T>
void Data<T>::SetData(T d){
    data=d;
}

template <typename T>
T Data<T>::Getdata(){
    return data;
}

int main(void){
    Data<int> d1(0);        // T를 int로 간주하고 객체를 생성함
    d1.SetData(100);

    Data<char> d2('c');     // T를 char로 간주하고 객체를 생성함

    cout << d1.Getdata() << endl;
    cout << d2.Getdata() << endl;

    return 0;
}
```

![5](https://user-images.githubusercontent.com/29933947/42253635-876a07b6-7f7d-11e8-823e-ae4150a8ae7a.png)





```c++
// 객체 생성
// ClassName<typename> Object<type>
Data<int> d1(0);
Data<char> d2('C');
```

> 클래스 템플릿을 기반으로 객체 생성 시,결정하고자 하는 자료형을 명시적으로 선언

ㆍ객체 생성 순서는 메모리 할당 → 생성자 호출

ㆍ생성자 호출 시, 전달 인자를 통해 자료형을 결정하고자 할 경우, 메모리 할당에 문제가 생김

ㆍ따라서, 메모리 공간 할당을 위한 명시적 선언 필요

ㆍ다른 이유는(근본적), 클래스 템플릿은 생성자를 통해서 전달되는 인자의 자료형과 결정되어야 할 템플릿의 자료형이 다를 수 있음



```c++
// ClassName<typename>::FunctionName(type...)
Data<T>::SetData(); // a
Data::SetData();	// b
```

> 클래스 템플릿의 선언과 정의를 구분할 경우, 'a' 형식을 사용

ㆍa : T 타입에 대해서 템플릿으로 정의되어 있는 Data 클래스 템플릿의 멤버함수 정의

ㆍb : Data 클래스의 멤버함수 정의



##### Stack 템플릿화

> 다양한 데이터를 저장하기 위한 Stack 객체를 생성 가능하게 함

```c++
/*

// =============== 아래 프로그램을 Template화 =================

#include <iostream>
using std::cout;
using std::endl;

class Stack{
    private:
        int topIdx;     // 마지막 입력된 위치의 인덱스
        char* stackPtr; // 스택포인터
    public:
        Stack(int s=10);
        ~Stack();
        void Push(const char& pushValue);
        char Pop();
};

Stack::Stack(int len){
    topIdx=-1;                  // 스택 인덱스 초기화
    stackPtr=new char[len];     // 데이터 저장 위한 배열 선언    
}

Stack::~Stack(){
    delete [] stackPtr;    
}

void Stack::Push(const char& pushValue){    // 스택에 데이터 입력
    stackPtr[++topIdx] = pushValue;
}

char Stack::Pop(){                          // 스택에서 데이터 꺼냄
    return stackPtr[topIdx--];
}

int main(){
    Stack stack(10);
    stack.Push('A');
    stack.Push('B');
    stack.Push('C');

    for(int i=0; i<3; i++){
        cout << stack.Pop() << endl;
    }

    return 0;
}

*/

#include <iostream>
using std::cout;
using std::endl;

template <typename T>
class Stack{
    private:
        int topIdx;     // 마지막 입력된 위치의 인덱스
        T* stackPtr; // 스택포인터
    public:
        Stack(int s=10);
        ~Stack();
        void Push(const T& pushValue);
        T Pop();
};

template <typename T>
Stack<T>::Stack(int len){
    topIdx=-1;                  // 스택 인덱스 초기화
    stackPtr=new T[len];        // 데이터 저장 위한 배열 선언    
}

template <typename T>
Stack<T>::~Stack(){
    delete [] stackPtr;    
}

template <typename T>
void Stack<T>::Push(const T& pushValue){    // 스택에 데이터 입력
    stackPtr[++topIdx] = pushValue;
}

template <typename T>
T Stack<T>::Pop(){                          // 스택에서 데이터 꺼냄
    return stackPtr[topIdx--];
}

int main(){
    Stack<char> stack1(10);
    stack1.Push('A');
    stack1.Push('B');
    stack1.Push('C');

    for(int i=0; i<3; i++){
        cout << stack1.Pop() << endl;
    }

    Stack<int> stack2(10);
    stack2.Push(100);
    stack2.Push(200);
    stack2.Push(300);

    for(int i=0; i<3; i++){
        cout << stack2.Pop() << endl;
    }

    return 0;
}
```

![3](https://user-images.githubusercontent.com/29933947/42253634-85e5cbdc-7f7d-11e8-848e-daa5a6599380.png)





#### 템플릿 인스턴스화

> 함수 템플릿은 타입별로 실제 호출이 가능하게 만들어지는 템플릿 함수를 만들기 위한 틀
>
> 클래스 템플릿은 객체화가 가능한 클래스를 만들기 위한 틀

> 클래스 템플릿은 하나의 파일 내에 선언과 정의가 함께 있어야 함(2011년, 이 후 확인 필요)

![_aaaaa](https://user-images.githubusercontent.com/29933947/42258989-659c3908-7f99-11e8-80c7-b7f6d64a33e0.png)