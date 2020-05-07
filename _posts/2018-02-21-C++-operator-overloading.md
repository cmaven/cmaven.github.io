---
layout: post
title: "C++ 연산자 오버로딩"
date: 2018-02-21 12:00
categories: Program_Language
tags: C++
---

C++ 의 연산자 오버로딩에 대해 정리한다.

------

### 개요

  . 객체도 기본 자료형 변수처럼, 덧셈, 뺄셈 등 연산들을 가능하게 하는 방법

```c++
... 
int a = 10 + 20;		// 일반산술연산
Point p3 = p1 + p2;		// 객체의 경우, 연산자 오버로딩 함수 호출
...
```

  . `operator` 키워드와 연산자를 묶어 함수의 이름을 정의

##### 주의할 점

> 잘못 사용하거나 남용할 경우, 프로그램을 복잡하고 이해하기 어렵게 만들 수 있음

> 연산자의 우선 순위, 결합성을 바꿀 수 없음

> 디폴트 매개 변수 설정 불가능

> 디폴트 연산자들의 기본 기능을 빼앗을 수 없음 ex) + → A + B + C (이항연산을 삼항연산으로 변경 불가능)



```c++
#include <iostream>

using std::endl;
using std::cout;

class Point{
    private:
        int x, y;
    public:
  		// `:` 멤버 이니셜라이져(member initializer) 활용한 생성자 초기화
        Point(int _x=0, int _y=0):x(_x), y(_y){}
        void ShowPosition();
        void operator+(int val);        
};

void Point::ShowPosition(){
    cout << x << " " << y << endl;
}

// 연산자 오버로딩
void Point::operator+(int val)
{
    x += val;
    y += val;
}

int main(void)
{
    Point p(1,5);
    p.ShowPosition();

    p.operator+(10);
    // p+10;	위 행을 본 행으로 교체하여도 문제 없이 작동함
  	// 이 때, p가 기본 자료형 변수라면 단순 덧셈 연산
    // p가 객체라면, p.operator+(10) 으로 변경하여 수행
    p.ShowPosition();

    return 0;
}
```

![16](https://user-images.githubusercontent.com/29933947/36366893-8df50076-1593-11e8-9525-94265b5eebbd.png)



  . C++ 연산자 오버로딩 개념(위 예제에서)

![_ 3](https://user-images.githubusercontent.com/29933947/36368028-c521c3f4-1598-11e8-95a2-efe697aafbc1.png)



### 멤버 함수에 의한 오버로딩

```c++
#include <iostream>

using std::endl;
using std::cout;

class Point{
    private:
        int x, y;
    public:
        Point(int _x=0, int _y=0): x(_x), y(_y){}
        void ShowPosition();
        Point operator+(const Point& p) const;
};

void Point::ShowPosition(){
    cout << x << " " << y << endl;
}
Point Point::operator+(const Point& p) const{
    Point temp(x + p.x, y + p.y);
    return temp;
}

int main(void)
{
    Point p1(1, 2);
    Point p2(3, 4);
    Point p3 = p1 + p2;
    p3.ShowPosition();

    return 0;
}
```

![17](https://user-images.githubusercontent.com/29933947/36369292-1b846e4a-159e-11e8-9b6c-1ce32733b06d.png)



#### `Point Point::operator+(const Point& p) const ` 이해

  . Point 객체를 인자로 전달 받음(Point p)

  . 함수 성능 향상을 위해 레퍼런스로 전달받음(Point &)

  . 전달 인자의 변경을 허용하지 않음 (const Point& p)

  . 함수 내에서 멤 버 변수의 조작을 할 필요 없으므로 함수 상수화(마지막 const)



#### 예제 객체 형성 및 연산 수행과정

  . 객체 생성

![_ 5](https://user-images.githubusercontent.com/29933947/36370204-8d6f55d0-15a1-11e8-9625-dea1c6ee25b7.png)



   . 연산 수행

![_ 4](https://user-images.githubusercontent.com/29933947/36370207-8f1951ec-15a1-11e8-93fc-9cdd16b917ba.png)







### 전역 함수에 의한 오버로딩

![_ 3](https://user-images.githubusercontent.com/29933947/36707783-3c2223c0-1bb3-11e8-92d1-1f4004ca1125.png)



  . 일반적으로 전역 함수에서 객체 멤버로의 접근(private 멤버로의 외부 함수에서 접근)은 불가능

  . 따라서, 전역 함수에서 연산자 오버로딩을 통한 객체 멤버의 조작을 위해서 `friend` 키워드를 활용함

  . 전역 함수에 의한 오버로딩은 최소화 하는 것이 바람직

```c++
#include <iostream>

using std::endl;
using std::cout;

class Point{
    private:
        int x;
        int y;
    public:
        Point(int _x=0, int _y=0):x(_x), y(_y){}
        void ShowData();
        // 외부에서 객체 멤버로의 접근을 위한 fried 선언
        friend Point operator+(const Point& p1, const Point& p2);     
};

void Point::ShowData(){
    cout << x << "  " << y << endl;
}

// 전역함수에 의한 연산자 오버로딩
Point operator+(const Point& p1, const Point& p2)
{
    Point temp(p1.x + p2.x, p1.y + p2.y);
    return temp;
}

int main(void)
{
    Point p1(10, 20);
    Point p2(20, 10);
    Point p3 = p1 + p2;
    p3.ShowData();  // Point p3 = operator+(p1, p2);

    return 0;
}
```

![4](https://user-images.githubusercontent.com/29933947/36711224-a0334e40-1bc5-11e8-9f3e-e0559352ae45.png)





### 단항 연산자의 오버로딩

![_ 2](https://user-images.githubusercontent.com/29933947/36769844-3bb568fc-1c8a-11e8-95ec-bdd3e143e563.png)

```c++
#include <iostream>

using std::endl;
using std::cout;

class Point{
    private:
        int x;
        int y;
    public:
        Point(int _x=0, int _y=0):x(_x), y(_y){}
        void ShowData();
        Point& operator++();
        // 외부에서 객체 멤버로의 접근을 위한 fried 선언
        friend Point& operator--(Point& p);     
};

void Point::ShowData(){
    cout << x << "  " << y << endl;
}

Point& Point::operator++()  // 멤버 변수에 의한 오버로딩
{
    x++;
    y++;
    return *this;		// Class Point로 인해 만들어진 객체 자신을 리턴
}
/* 
   이미 증가연산을 수행하였는데, 객체 자신을 리턴하는 이유 
   만약 자신을 리턴하지 않는다면,
   ++(++p); 
   (++p).ShowData();
   와 같은 연산과 연결되어 수행하는 명령을 실행할 수 없어 컴파일 에러가 발생함
*/

// 전역함수에 의한 연산자 오버로딩
Point& operator--(Point& p)
{
    p.x--;
    p.y--;
    return p;
}

int main(void)
{
    Point p(10, 20);
    ++p;    //  객체 p의 x, y 값을 1 씩 증가
    p.ShowData();

    --p;    //  객체 p의 x, y 값을 1 씩 감소
    p.ShowData();

    ++(++p);    //  객체 p의 x, y 값을 2 씩 증가
    p.ShowData();

    --(--p);    //  객체 p의 x, y 값을 2 씩 감소
    p.ShowData();

    return 0;
}
```

![1](https://user-images.githubusercontent.com/29933947/36733516-3782eaf0-1c14-11e8-9684-e10fa9cc0bfa.png)



  . 위 예제에서 연산자 오버로딩 시, 참조형`Point&` 를 리턴하는 이유

![_ 2](https://user-images.githubusercontent.com/29933947/36734451-e5f631f8-1c16-11e8-97bc-49587629d876.png)



#### 선 연산과 후연산

  . 전위(Prefix), 후위(Postfix) 연산자 선언에 대한 정의



![_aaaa](https://user-images.githubusercontent.com/29933947/42147150-55f1f558-7e07-11e8-9922-e4f40e89089f.png)

```c++
#include <iostream>

using std::endl;
using std::cout;

class Point{
    private:
        int x;
        int y;
    public:
        Point(int _x=0, int _y=0):x(_x), y(_y){}
        void ShowData();
        Point& operator++();
        Point operator++(int);        
};

void Point::ShowData(){
    cout << x << "  " << y << endl;
}

Point& Point::operator++()  // Prefix 연산자
{
    x++;
    y++;
    return *this;
}

Point Point::operator++(int)   // Postfix 연산자
{
    Point temp(x,y);    // Point temp(*this);
    // 아래 두줄은 ++(*this); 로 표현이 가능함
  	x++;		 
    y++;		
    return temp;
}

int main(void)
{
    Point p1(10, 20);
    (p1++).ShowData();    //  10, 20 출력
    p1.ShowData();        //  11, 21 출력

    Point p2(10, 20);
    (++p2).ShowData();    //  11, 21 출력

    return 0;
}
```

![1](https://user-images.githubusercontent.com/29933947/36769621-c08580b4-1c88-11e8-87c1-5481002ad521.png)



  . 후위(Postfix) 연산자 정의의 경우, 연산 전의 상태를 저장하기 위한 Temp 객체를 생성하고, 이를 반환한다. 이 때, Point& 형이 아닌 Point 형으로 반환하는 이유는, 지역객체이기 때문에 함수 호출이 끝나면 객체는 소멸되기 때문임



### 연산자 오버로딩 관련 교환법칙

#### 피연산자의 값을 변경시키지 않는 연산자 오버로딩

  . 아래 연산 방식은, 피연산자의 멤버 변수의 값을 변경 시킴

```c++
...
void Point::operator+(int val)
{
    x += val;
    y += val;
}

int main(void)
{
    Point p(1,5);
    p.ShowPosition();

    p.operator+(10);
    // p+10;
    p.ShowPosition();

    return 0;
}
...
```



  . 피연산자의 멤버 변수의 값을 변경 시키지 않고, 결과를 도출하는 방법

```c++
#include <iostream>

using std::endl;
using std::cout;

class Point{
    private:
        int x, y;
    public:
        Point(int _x=0, int _y=0):x(_x), y(_y){}
        void ShowPosition();
        Point operator+(int val);        
};

void Point::ShowPosition(){
    cout << x << " " << y << endl;
}
// 임시 Point 객체를 생성하여, 연산을 수행함
// 해당 방식으로, 피연산자의 값 변화 없이 결과를 도출할 수 있음
Point Point::operator+(int val)
{
    Point temp(x+val, y+val);
    return temp;
}

int main(void)
{
    Point p1(1,5);
    p1.ShowPosition();

    Point p2 = p1.operator+(10);
    // p2 = p1 + 10;  
    cout << "Point p2 member: " <<endl;  
    p2.ShowPosition();    

    cout << "Point p1 member: " <<endl;  
    p1.ShowPosition();    
    return 0;
}
```

![1](https://user-images.githubusercontent.com/29933947/36959779-30b53d32-2087-11e8-9925-7eaaebac43cf.png)





#### 피연산자의 교환이 가능한 연산자 오버로딩

  . 앞의 예제는 피연산자간의 교환이 성립되지 않음

  . 이를 해결하기 위해서는 `전역함수` 에 의한 연산자 오버로딩 방법을 사용해야 함

```c++
...
  p2 = p1 + 10;
  p2 = 10 + p1;
  // p2 = 10.operator+(p);
  // 위의 형태는 컴파일러가 해석할 수 없음 
...
```

```c++
#include <iostream>

using std::endl;
using std::cout;

class Point{
    private:
        int x, y;
    public:
        Point(int _x=0, int _y=0):x(_x), y(_y){}
        void ShowPosition();
        Point operator+(int val);  
        // 피연산자의 위치 교환 시, 사용될 함수 선언 
        // 전역함수 연산자 오버로딩 방법을 사용함
        friend Point operator+(int val, Point & p);      
};

void Point::ShowPosition(){
    cout << x << " " << y << endl;
}

Point Point::operator+(int val)
{
    Point temp(x+val, y+val);
    return temp;
}

Point operator+(int val, Point & p)
{
    return p+val;
}  

int main(void)
{
    Point p1(1,5);
    
    Point p2 = p1 + 10;
    p2.ShowPosition();

  	// 객체의 피연산 위치가 바뀜, 해당 연산은 전역함수 형태의 연산자 오버로딩 함수를 호출한다
    Point p3 = 100 + p2;
    p3.ShowPosition();
    
    return 0;
}
```

![2](https://user-images.githubusercontent.com/29933947/36960169-24c8034a-2089-11e8-974c-a9ed1772e558.png)



![_aaaaaaa](https://user-images.githubusercontent.com/29933947/42149968-323d0c40-7e13-11e8-997e-4bc2cc884f3f.png)





#### 임시객체 생성의 의미

  . 위 예제의 `temp(x+val, y+val)` 의 형태를 `return Point(x+val, y+val)` 로 변경 가능함

```c++
Point Point::operator+(int val)
{    
    return Point(x+val, y+val);
  	// Point 객체의 이름이 없음
  	// 해당 줄을 벗어나면 바로 소멸됨
}
```

  . 임시 객체는 `"이름이 없으며, 생성한 이후 그 줄에서 사용하지 않으면 바로 소멸됨"`



```c++
#include <iostream>
#include <string.h>

using std::cout;
using std::endl;

class Temp{
    char name[30];
    public:
        Temp(char * _name){
            strcpy(name, _name);
            cout << name << "객체가 생성됨" << endl;            
        }
        ~Temp(){            
            cout << name << "객체가 소멸됨" << endl;            
        }
};

int main(void)
{
    Temp aaa("aaa object");
    cout << "======= 임시 객체 생성 전 =======" << endl;
  	// 이름이 없는 형태의 임시 객체 생성
    Temp("temp object");
    cout << "======= 임시 객체 생성 후 =======" << endl;
    return 0;
}
```

![3](https://user-images.githubusercontent.com/29933947/36960562-e7a89d2e-208a-11e8-94b5-c53f849e265c.png)





### 연산자 오버로딩을 활용한 C++ 기초 입출력

  . cout, cin, endl은 실제로 연산자 오버로딩으로 구현됨

```c++
#include <iostream>

namespace mystd     // mystd 이름 공간
{
    char * endl = "\n";

    class ostream           // 클래스 ostream 정의
    {
        public:
            // 전달 인자에 따른(데이터 타입에 따른) 출력형식 지정
            void operator<<(char * str)
            {
                printf( "%s", str);
            }
            void operator<<(int i)
            {
                printf( "%d", i);
            }
            void operator<<(double i)
            {
                printf( "%e", i);
            }            
    };
    ostream cout;   // ostream 객체 생성
}

using mystd::cout;
using mystd::endl;

int main()
{
    cout << "Hello \n ";
    cout << 3.14;
    cout << endl;
    cout << 1;
    cout << endl;
    return 0;
}
```

![4](https://user-images.githubusercontent.com/29933947/36965895-5f5c1446-209e-11e8-9de5-f4378da10969.png)

  . 위의 예제에서, 

```c++
cout << "string" 은 cout 객체의 오버로딩 된 멤버 함수 operator << ("string")의 호출 문장
```



#### 연산 결합 지원

> cout << "Hello" << 100 << endl; 

  . 연산자를 오버로딩하고 있는 operator << 함수가 cout 객체를 반환해야 함

![_ 1 2](https://user-images.githubusercontent.com/29933947/37038907-74938c62-2199-11e8-9e59-559befd36e68.png)

```c++
#include <stdio.h>

namespace mystd     // mystd 이름 공간
{
    char * endl = "\n";

    class ostream           // 클래스 ostream 정의
    {
        public:
            // 전달 인자에 따른(데이터 타입에 따른) 출력형식 지정
            ostream& operator<<(char * str)	// & 참조에 의한 리턴
            {
                printf( "%s", str);
                return *this;
            }
            ostream& operator<<(int i)
            {
                printf( "%d", i);
                return *this;
            }
            ostream& operator<<(double i)
            {
                printf( "%e", i);
                return *this;
            }            
    };
    ostream cout;   // ostream 객체 생성
}

using mystd::cout;
using mystd::endl;

int main()
{
    cout << "Hello World" << endl << 3.14 << endl;
    return 0;
}
```

![6](https://user-images.githubusercontent.com/29933947/36967398-f8dee7ca-20a2-11e8-943c-f03e9f780ab0.png)



#### 객체 멤버 변수를 출력하는 방법

  . 예를 들어 x, y의 두 멤버 변수를 지닌 객체에 대해 출력을 수행할 때,

> Point p(1, 2)
>
> cout<< p;  

  . 위의 경우, `[ 1, 2 ]` 형식으로 출력되는 것을 원한다면 `전역 함수에 의한 오버로딩 방식` 을 사용해야 함

```c++
#include <iostream>

using std::endl;
using std::cout;

// <<의 전역 함수에 의한 오버로딩을 위해, cout 객체를 인자로 전달 받음
// cout 객체는 std의 ostream 클래스에 선언되어 있으므로, ostream을 사용하기 위한 선언이 필요
using std::ostream;

class Point{
    private:
        int x, y;
    public:
        Point(int _x=0, int _y=0):x(_x), y(_y){}
        friend ostream& operator<<(ostream& os, const Point& p);
  		// 전역함수가 Point  클래스에 접근하기 위한 friend 선언
};

ostream& operator<<(ostream& os, const Point& p)	// 전역 함수에 의한 오버로딩 방식
{
    os << " [ " << p.x << " , " << p.y << " ] " << endl;
    return os;
}

int main(void)
{
    Point p(1, 5);
    cout << p;      // operator<<(cout, p) 로 호출
    return 0;
}

```

![7](https://user-images.githubusercontent.com/29933947/36968092-dea91ec8-20a4-11e8-9b78-883071ccda63.png)



### 배열의 인덱스 연산자 오버로딩

#### 일반 자료형 배열 인덱스 연산자 오버로딩

```c++
#include <iostream>
using std::endl;
using std::cout;

const int SIZE=3;

class Arr{
    private:
        int arr[SIZE];
        int index;
    public:                 // i = index
        Arr():index(0){}
        int GetarrItem(int i);				// 요소 참조 함수
        void SetarrItem(int i, int item);   // 저장된 요소 변경 함수
        void AddarrItem(int item);			// 데이터를 배열에 저장하는 함수
        void ShowData();    
};

// 매개변수는 배열의 인덱스
int Arr::GetarrItem(int i){
    return arr[i];
}

void Arr::SetarrItem(int i, int item){
    if(index <= i)
    {
        cout << "non-existence" << endl;
        return;
    }
    arr[i] = item;
}

void Arr::AddarrItem(int item){
  	// 배열의 범위를 넘어서지 않는지 검사
    if(index >= SIZE) 
    {
        cout << "index is over the arr size" << endl;
        return;
    }
    arr[index++] = item;
}

void Arr::ShowData(){
    for(int i = 0; i < index; i++)
    {
        cout << "arr [ "<< i <<" ]= " << arr[i] << endl;
    }
}

int main(void){
    Arr arr;
    arr.AddarrItem(1);
    arr.AddarrItem(2);
    arr.AddarrItem(3);
    arr.ShowData();

    arr.SetarrItem(0,10);
    arr.SetarrItem(1,20);
    arr.SetarrItem(2,30);

    cout << arr.GetarrItem(0) << endl;
    cout << arr.GetarrItem(1) << endl;
    cout << arr.GetarrItem(2) << endl;

    return 0;
}
```

![9](https://user-images.githubusercontent.com/29933947/42153382-ebf94dba-7e1d-11e8-84de-d5d896413abc.png)



  . 위의 예제를 배열의 인덱스 연산자( [ , ] ) 로  접근할 수 있도록 수정함

```c++
#include <iostream>
using std::endl;
using std::cout;

const int SIZE=3;

class Arr{
    private:
        int arr[SIZE];
        int index;
    public:                 // i = index
        Arr():index(0){}
        int GetarrItem(int i);
        void SetarrItem(int i, int item);   
        void AddarrItem(int item);
        void ShowData();    
        int& Arr::operator[](int i);
};

int Arr::GetarrItem(int i){
    return arr[i];
}

void Arr::SetarrItem(int i, int item){
    if(index <= i)
    {
        cout << "non-existence" << endl;
        return;
    }
    arr[i] = item;
}

void Arr::AddarrItem(int item){
    if(index >= SIZE)
    {
        cout << "index is over the arr size" << endl;
        return;
    }
    arr[index++] = item;
}

void Arr::ShowData(){
    for(int i = 0; i < index; i++)
    {
        cout << "arr [ "<< i <<" ]= " << arr[i] << endl;
    }
}

int& Arr::operator[](int i){
    return arr[i];
}

int main(void){
    Arr arr;
    arr.AddarrItem(1);
    arr.AddarrItem(2);
    arr.AddarrItem(3);
    arr.ShowData();

    /*
    arr.SetarrItem(0,10);
    arr.SetarrItem(1,20);
    arr.SetarrItem(2,30);
    */

    arr[0] = 10;       // arr.operator[](0)
    arr[1] = 20;
    arr[2] = 20;

    /*
    cout << arr.GetarrItem(0) << endl;
    cout << arr.GetarrItem(1) << endl;
    cout << arr.GetarrItem(2) << endl;
    */

    cout << arr[0] << endl;
    cout << arr[1] << endl;
    cout << arr[2] << endl;

    return 0;
}
```

  . `arr [ 0 ] = 10 `  에서 , arr[i] 는 L-value로 사용되고 있음. 따라서, <span style="color:red">참조에 의한 리턴</span>이 이루어져야 값을 저장할 수 있음





#### 객체 배열 인덱스 연산자 오버로딩

  . 객체를 저장할 수 있는 배열 클래스 

```c++
#include <iostream>
using std::endl;
using std::cout;

using std::ostream;

const int SIZE=5;

/*-------------- Point Class ---------------*/
class Point{
    private:
        int x, y;
    public:
        Point(int _x=0, int _y=0):x(_x), y(_y){}
        friend ostream& operator<<(ostream& os, const Point& p);
};

ostream& operator<<(ostream& os, const Point& p){
        os << " [ " << p.x << " , " << p.y << " ] ";
        return os;
}

/*-------------- PointArr Class ---------------*/
class PointArr{
    private:
        Point arr[SIZE];
        int index;
    public:                 // i = index
        PointArr():index(0){}
        void AddarrItem(const Point& item);
        void ShowData();            
        Point& operator[](int i);   // 배열 요소 접근 연산자 오버로딩
};

void PointArr::AddarrItem(const Point& item){
    if(index >= SIZE)
    {
        cout << "index is over the arr size" << endl;
        return;
    }
    arr[index++] = item;
}

void PointArr::ShowData(){
    for(int i = 0; i < index; i++)
    {
        cout << "arr [ "<< i <<" ]= " << arr[i] << endl;
    }
}

Point& PointArr::operator[](int i){
    return arr[i];
}

int main(void){
    PointArr arr;
    arr.AddarrItem(Point(1,1));   // 임시 객체 형태, 생성되자마자 배열 복사 후, 소멸
    arr.AddarrItem(Point(2,2));
    arr.AddarrItem(Point(3,3));
    arr.ShowData();

    arr[0] = Point(10, 10);       // arr.operator[](0)
    arr[1] = Point(20, 20);
    arr[2] = Point(30, 30);

    cout << arr[0] << endl;
    cout << arr[1] << endl;
    cout << arr[2] << endl;

    return 0;
}
```

![10](https://user-images.githubusercontent.com/29933947/42153855-3674c2ba-7e1f-11e8-9475-ca7154ad0f16.png)





### 대입 연산자(`=`) 오버로딩

#### default 대입 연산자

  . 멤버 변수 대 멤버 변수의 복사가 이루어지는 `=` 연산자의 디폴트 오버로딩 = 얕은 복사(shallow copy)

```c++
#include <iostream>
using std::endl;
using std::cout;

using std::ostream;

class Point{
    private:
        int x, y;
    public:
        Point(int _x=0, int _y=0):x(_x), y(_y){}
        friend ostream& operator<<(ostream& os, const Point& p);
};

ostream& operator<<(ostream& os, const Point& p){
        os << " [ " << p.x << " , " << p.y << " ] ";
        return os;
}

/*  자동으로 생성되는 default 대입 연산자 정의
    리턴 타입이 Point& 이며, 자기자신(this)를 리턴하는 이유는, p1 = p2 = p3; 와 같은
    연속적인 대입연산에 대응하기 위함
    Point& Point::operator=(const Point& p)
    {
        x = p.x;
        y = p.y;
        return *this;
    }
*/

int main(void){
    Point p1(1, 2);
    Point p2(10, 20);
    cout << p1 << endl;
    cout << p2 << endl;

    p1 = p2; // p1.operator=(p2);
    cout << p1 << endl;

    return 0;
}
```



#### 깊은 복사(Deep copy) 대입 연산자

  . 디폴트 대입 연산자의 문제점

​    ① 얕은 복사(Shallow copy) : 멤버 변수 값 복사 시, 단순히 포인터 값만 복사하기 때문에, 객체가 소멸되는 시점에 특정 값은 두 번 삭제를 시도하는 문제점을 가짐( 밑의 "LEE" 의 경우 두번 삭제가 호출됨)

​    ② 메모리 유출 : 멤버 변수 복사가 끝나 포인터가 가리키는 위치가 바뀐 값("KIM")의 경우, 소멸되지 않고 프로그램이 종료될 때까지 메모리에 계속 남아있게 됨



![_ 1](https://user-images.githubusercontent.com/29933947/37195923-18b80ff0-23b8-11e8-87d0-ef16c684e561.png)

```c++
#include <iostream>
#include <string.h>

using std::endl;
using std::cout;
using std::ostream;

class Person{
    private:
        char* name;
    public:
        Person(char* _name);
        Person(const Person& p);
        ~Person();
        friend ostream& operator<<(ostream& os, const Person& p);
};

Person::Person(char* _name){
    name = new char[strlen(_name)+1];
    strcpy(name, _name);
}
Person::Person(const Person& p){
    name = new char[strlen(p.name)+1];
    strcpy(name, p.name);
}
Person::~Person(){
    delete[] name;
}

/*  자동으로 생성되는 default 대입 연산자 정의
    리턴 타잎이 Point& 이며, 자기자신(this)를 리턴하는 이유는, p1 = p2 = p3; 와 같은
    연속적인 대입연산에 대응하기 위함
    Person& Person::operator=(const Person& p)
    {
        name = p.name;        
        return *this;
    }
    
    해당 default 대입 연산자는 sallow copy을 수행 (멤버 변수 간 복사)
     - 두 개의 객체 사용 시, 특정 멤버 변수는 소멸자에 의해 메모리 공간 삭제 콜이 두번 일어남(에러발생)
     - 두 개의 객체 사용 시, 특정 멤버 변수가 지니고 있던 값을 가르키는 데이터가 변경되어, 데이터는 있으나, 소멸되지 않는 메모리 공간 발생
*/

// deep copy 를 수행하는 default 대입 연산자 정의
Person& Person::operator=(const Person& p)
{  
    delete [] name;		// 디폴트 대입 연산자의 두 번째 문제점인, 메모리 유출을 방지
    name = new char[strlen(p.name)+1];	// 깊은 복사 (deep copy)
    strcpy(name, p.name);				// 깊은 복사 (deep copy)
    return *this;
}    


ostream& operator<<(ostream& os, const Person& p){
    os << p.name;
    return os;
}

int main()
{
    Person p1("KIM");
    Person p2("LEE");

    cout << p1 << endl;
    cout << p2 << endl;

    p1 = p2;    // shallow copy

    cout << p1 << endl;

    return 0;
}
```



  . <span style="color:red; font-weight:bold">생성자 내에서 메모리 공간을 동적 할당하게 되면, 할당된 메모리를 해제하는 용도의 소멸자를 정의해야함, 복사 생성자와 대입 연산자도 깊은 복사를 하도록 정의해야 함</span>