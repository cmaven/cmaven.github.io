---
layout: post
title: "C언어 정리-배열,포인터"
date: 2018-01-22 19:00
categories: Program-Language
tags: c
---

C언어 배열, 포인터 관련 내용 정리

------

#### 배열의 크기 

```c
int arr1[4] = {1,2,3};

arr1_length = sizeof(arr1) / sizeof(int);
```



#### 문자열 변수 표현

```c
char str[] = "Hello World";
```

![_ 1](https://user-images.githubusercontent.com/29933947/35223224-e8553ab2-ffc3-11e7-8683-bfce4d5f5a38.png)

 . ''\0''은 "NULL 문자", 해당 문자의 아스키 코드 값은 "0"

 . 저장된 데이터에 널문자가 존재하면 해당 데이터는 문자열로 취급함



#### 포인터

##### 정의

 . 메모리 직접 접근이 가능한 연산(주소값)

```c
int *ptr;
int num;

ptr = &num;
```

  . int * : int형 변수의 주소 값 저장을 위한 포인터 변수

  . ptr : 포인터 변수 이름

  . &num : int형 변수 num의 주소 값을 반환

##### 포인터형

```c
type * ptr;
type* ptr;
type *ptr;
```

  . type형 변수의 주소 값을 저장하는 포인터 변수

  . type은 int, double ... etc

  . 주소 값은 동일 시스템 내에선 크기가 동일(8bit, 16bit, 32bit, 64bit ... etc)

  . 포인터 변수가 가리키는 메모리의 접근 기준(몇 바이트를 접근할지)을 위해 "포인터형(type형)"을 선언

##### 연산자 '*'

```c
int num = 100;
int *pnum = &num;
*pnum += 20;
printf("number is %d \n", *pnum);
```

  . '*' 연산자는 포인터가 가리키는 메모리 공간에 접근 시 사용하는 연산자



#### 배열과 포인터 관계

  . 'arr[10]' 배열에서 배열의 이름인 'arr' 은 '포인터 상수'

  . 포인터 상수는, 포인터 변수와 달리 주소 값의 변경이 불가능함

  . 배열의 이름을 피연산자로 하는 * 연산 가능

  . 포인터 변수 ptr은 ptr[0], ptr[1] .. 등의 배열형태로 사용 가능

```c
#include <stdio.h>

int main(void)
{
	int arr[2] = {10, 20};
	int * ptr = arr; //int * ptr = arr[]
	
	printf("%d %d \n", ptr[0], arr[0]);
	printf("%d %d \n", ptr[1], arr[1]);	
	printf("%d %d \n", *ptr, *arr);	
}	
```

![1](https://user-images.githubusercontent.com/29933947/35225697-5c834782-ffcc-11e7-8053-3d11a4bbf9f0.png)

##### *(++ptr) vs *(ptr+1)

  . 두 연산은 모두, 현재 ptr이 가리키는 위치에서 4바이트(int형일 경우) 떨어진 메모리 공간을 가리킴

  . *(++ptr)은 ptr이 가리키는 주소값 자체를 증가시킴

  . *(ptr+1)은 ptr이 가리키는 위치에서 4바이트 떨어진 메모리 공간만을 가리킴

```c
#include <stdio.h>

int main(void)
{
	int arr[3] = {10, 20, 30};
	int * ptr = arr; //int * ptr = arr[]
	
	printf("\n");
	printf("*ptr: %d \n", *ptr);
	printf("ptr: %p \n", ptr);

	printf("\n");	
	printf("*(++ptr): %d \n", *(++ptr));
	printf("ptr after *(++ptr): %p \n", ptr);
	
	printf("\n");
	printf("*(ptr+1): %d \n", *(ptr+1));
	printf("ptr after *(ptr+1): %p \n", ptr);
	
	return 0;
}	
```

![4](https://user-images.githubusercontent.com/29933947/35227458-8138aab8-ffd1-11e7-8b16-ebabd990ffbd.png)



#### arr[i] ==  *(arr+i)

```c
..

int arr[3] = {10, 20, 30}
int * ptr=arr;

//동일 표현
arr[0], arr[1], arr[2]
*(arr+0), *(arr+1), *(arr+2)
ptr[0], ptr[1], ptr[2]
*(ptr+0), *(ptr+1), *(ptr+2)
```



#### 배열 혹은 포인터 선언에 의한 문자열

```c
#include <stdio.h>

int main(void)
{
 	char str1[] = "This is String"; // 변수 형태 문자열
  	char * str2 = "That is String";	// 상수 형태 문자열
  
  	printf("initial value: %s %s \n",str1, str2);
  	
  	str2 = "It is not String"; // 가리키는 대상 변경 가능, str1은 변경 불가
  	printf("change str2: %s\n", str2);
  
  	str1[0] = 'A';
  	//str2[0] = 'A'; // 컴파일 시 에러
  	
  	printf("after changing characther on s1: %s %s \n",str1, str2);
   	return 0;
}
```

![1](https://user-images.githubusercontent.com/29933947/35253634-de1fc650-0029-11e8-9ecc-934e3afcdc9b.png)

![_ 1](https://user-images.githubusercontent.com/29933947/35253451-da3e6aec-0028-11e8-93ec-79bd0eb7d1a0.png)

![_ 2](https://user-images.githubusercontent.com/29933947/35253458-dee89c16-0028-11e8-8dac-56ddc3795312.png)



   . ""로 묶인 문자열은 메모리에 저장되면 그 주소 값을 반환함

   . 따라서  printf("Hello World") 는 printf(0x123456)의 형태로 호출됨

   . ex) printf(0x123456) ....... void printf(char * str)



#### 포인터 배열

  . 배열 요소로 포인터를 가짐

```c
#include <stdio.h>

int main(void)
{
   	int num1=10, num2=20, num3=30;
   	
   	// 포인터 배열
 	int * arr[3]={&num1, &num2, &num3};
   	char * strArr[3] = {"String", "Array", "Test"};

   	printf("*arr[0]: %d \n", *arr[0]);
   	printf("*arr[1]: %d \n", *arr[1]);
   	printf("*arr[2]: %d \n", *arr[2]);
   	
   	printf("strArr[0]: %s \n", strArr[0]);
   	printf("strArr[1]: %s \n", strArr[1]);
   	printf("strArr[2]: %s \n", strArr[2]);
   	
   	return 0;
}
```

![2](https://user-images.githubusercontent.com/29933947/35254481-ba76f27e-002d-11e8-9847-1ab97e44ddfb.png)

![_ 3](https://user-images.githubusercontent.com/29933947/35254402-65e48b0e-002d-11e8-871c-d378c2fc3ba0.png)
![_ 4](https://user-images.githubusercontent.com/29933947/35254404-66161b42-002d-11e8-9594-d34036e6d86c.png)

#### 함수 인자의 배열 전달

  . 함수 호출 시, 전달되는 인자의 값은 매개변수에 복사

```c
#include <stdio.h>

// void ShowArrayParam(int paramp[], int len)
// 위 형태로도 선언 가능함
// 단! 매개변수로 선언할 때만 가능
void ShowArrayParam(int * param, int len)
{
    int i;
    for(i=0; i<len; i++)
        printf("Array[%d]: %d \n", i, param[i]);
}

void AddArrayParam(int * param, int len, int addnum)
{
    int i;
    for(i=0; i<len; i++)
        param[i] += addnum;
}

int main(void)
{
    int arr[3] = {1, 2, 3};
    
    printf("initial valume: %d %d %d \n", arr[0], *(arr+1), arr[2]);
    
    // 배열 이름 == 주소 값을 통한 함수의 매개변수로 배열 인자 전달
    AddArrayParam(arr, sizeof(arr)/sizeof(int), 10);
    ShowArrayParam(arr, sizeof(arr)/sizeof(int));
    
    AddArrayParam(arr, sizeof(arr)/sizeof(int), 100);
    ShowArrayParam(arr, sizeof(arr)/sizeof(int));
    
    return 0;
}
```

![3](https://user-images.githubusercontent.com/29933947/35255242-745c7148-0031-11e8-982c-2bb7d4a5b1b3.png)



#### 포인터 Const

```c
const int * ptr = &num1;
```

  . 포인터 변수가 참조하는 대상의 변경 허용하지 않음

  . ex) *ptr = 10; 의 경우 에러 발생

```c
int * const ptr = &num1;
```

  . 포인터 변수의 상수화

  . 한 번 저장된 주소값은 변경될 수 없음

  . ex) ptr = &num2; 의 경우 에러 발생

```c
const int * const ptr = &num1;
```

  . 포인터 변수에 저장된 주소 값(가리키는 대상)의 변경이 불가

  . 포인터 변수가 가리키는 대상의 값을 직접 변경 불가능



#### 더블 포인터 변수

```c
#include <stdio.h>

int main(void)
{
    int num = 10;
    int * ptr1 = &num;
    int **dptr = &ptr1;
    int * ptr2;
    
    printf("[address] ptr1: %p  *dptr: %p \n", ptr1, *dptr);
    printf("[value] *ptr: %d  **dptr: %d \n", *ptr1, **dptr);
    
    ptr2 = *dptr; // ptr2 = ptr1 과 동일
    
    printf("[address] ptr2: %p \n", ptr2);
    printf("[value] ptr2: %d \n", *ptr2);
    
    *ptr2 = 20; 
    // *ptr1 = 20; , **dptr = 20; , num = 20; 과 동일
    printf("[value] num: %d \n", num);

    return 0;
}
```

![9](https://user-images.githubusercontent.com/29933947/35266991-36c9d1e0-0068-11e8-880b-c4d4e6c091fe.png)

```c
#include <stdio.h>

void SwapPtr(int **dptr1, int **dptr2)
{
    int *temp = *dptr1;
    *dptr1 = *dptr2;
    *dptr2 = temp;
    
    /*
    int *temp = ptr1;
    ptr1 = ptr2;
    ptr2 = temp;
    */
}

int main(void)
{
    int num1 = 10 , num2 = 20;
    int *ptr1, *ptr2;
    ptr1 = &num1, ptr2 = &num2;
    
    printf("*ptr1 : %d,  *ptr2 : %d \n", *ptr1, *ptr2);
    
    SwapPtr(&ptr1, &ptr2);
    printf("*ptr1 : %d,  *ptr2 : %d \n", *ptr1, *ptr2);
    
    printf("num1 : %d,  num2 : %d \n", num1, num2);
    
    return 0;
}
```

![10](https://user-images.githubusercontent.com/29933947/35267482-c2a27572-0069-11e8-9e69-d8dda5517018.png)



  . 포인터 배열의 포인터형은 더블 포인터 형이다.

​      ex) *ptrArr[] 의 포인트 배열 이름인 'ptrArr' 은 int **dptr = ptrArr 로 연산되며, 더블포인터 형임

​      ! 2차원 배열 `int Arr[3][4]` 의 이름인 'Arr' 은 int ** 형이 아님



#### 다차원 배열의 포인터

##### 배열 포인터 변수

  . 2차원 이상 배열에서 사용되는 개념으로 배열을 가리키기 위한 포인터

 `int arr[3][4]`

  . 배열이름 arr이 가리키는 대상은 int형 변수

  . arr의 값을 1 증가시키면, sizeof(int) * 4의 크기만큼 주소 값이 증가하는 포인터 형

  .포인트 연산 시 sizeof(int) * 4의 크기만큼 값이 증가 및 감소하는 포인터 형

```c
...
int arr[3][4];
int (*ptr) [4];  // arr[3][4]를 가리킬 수 있는 포인터 변수

ptr = arr;

// ptr[0][0], ptr[0][1], ptr[0][2], ptr[0][3],
// *(ptr+1)[0], *(ptr+1)[1], *(ptr+1)[2], *(ptr+1)[3],
// *(*(ptr+1)+0), *(*(ptr+1)+1), **(ptr+1)+2, **(ptr+1)+3,
...
```

![_ 1 2](https://user-images.githubusercontent.com/29933947/35281973-acf1d460-0097-11e8-8982-9318e0d805b6.png)

```c
#include <stdio.h>

int main()
{
    int i;
    
    int arr1[2][2] = {
        {1, 2}, {3, 4}
    };
    int arr2[3][2] = {
        {1, 2}, {3, 4}, {5, 6}
    };
    int arr3[4][2] = {
        {1, 2}, {3, 4}, {5, 6}, {7, 8}
    };
    
    int (*ptr)[2];
    
    ptr = arr1;
    printf("Arr1 \n");
    for(i=0; i < 2; i++)
        printf("%d %d \n", ptr[i][0], ptr[i][1]);
        
    ptr = arr2;
    printf("Arr2 \n");
    for(i=0; i < 3; i++)
        printf("%d %d \n", *(ptr+i)[0], ptr[i][1]);    
    
    ptr = arr3;
    printf("Arr3 \n");
    for(i=0; i < 4; i++)
        //printf("%d %d \n", *(ptr+i)[0], *(*(ptr+i)+1));    
        printf("%d %d \n", *(ptr+i)[0], **(ptr+i)+1);    
    return 0;
}
```

![1](https://user-images.githubusercontent.com/29933947/35280745-72b47dbe-0094-11e8-9732-9c8e9a05a468.png)

##### 2차원 배열 함수 인자 전달

```c
#include <stdio.h>

// void ShowArr(int arr[][4], int column)
// 매개 변수에서만 서로 치환 가능
void ShowArr(int (*arr)[4], int column)
{
    int i, j;
    
    for(i=0; i<column; i++)
    {
        for(j=0; j<4; j++)
            printf(" %2d ", arr[i][j]);
        printf("\n");
    }
    printf("\n");
}

// int SumArr(int (*arr)[4], int column)
// 매개 변수에서만 서로 치환 가능
int SumArr(int arr[][4], int column)
{
    int i, j, sum = 0;
    for(i=0; i<column; i++)
        for(j=0; j<4; j++)
            sum += arr[i][j];
    return sum;
}

int main()
{
    int arr1[2][4] = {1, 2, 3, 4, 5, 6, 7, 8};
    int arr2[3][4] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
    
    // sizeof(arr1)은 전체 배열의 크기
    // sizeof(arr1[0])은 배열 1행의 크기
    ShowArr(arr1, sizeof(arr1)/sizeof(arr1[0]));
    ShowArr(arr2, sizeof(arr2)/sizeof(arr2[0]));   
        
    printf("sum of arr1: %d \n",
         SumArr(arr1, sizeof(arr1)/sizeof(arr1[0])));
    printf("sum of arr2: %d \n"
        ,SumArr(arr2, sizeof(arr2)/sizeof(arr1[0])));
        
    return 0;
}
```

![2](https://user-images.githubusercontent.com/29933947/35283962-e98c224a-009c-11e8-87fa-229d0d944f0e.png)





#### 함수 포인터

  . 함수들이 바이너리 형태로 메모리 공간에 저장된 주소 값을 저장하는 포인터 변수

  . 함수 포인터 형은 함수의 반환형과 매개변수 선언을 통해 결정됨

```c
...
int cfunc(int num1, num2){ .... }

int (*fptr) (int, int);
fptr = cfunc;
fptr(1, 2) // cfunc(3,4) 와 동일
...
```

```c
#include <stdio.h>

int WhoIsFirst(int age1, int age2, int (*cmp)(int n1, int n2))
{
    return cmp(age1, age2);
}

int OlderFirst(int age1, int age2)
{
    if(age1 > age2)
        return age1;
    else if(age1 < age2)
        return age2;
    else
        return 0;
}

int main(void)
{
    int age1 = 20;
    int age2 = 30;
    int first;
    
    printf("입장 순서 \n");
  	first = WhoIsFirst(age1, age2, OlderFirst);   // OlderFirst 함수를 인자로 전달
    printf("%d세와 %d세 중 %d세가 먼저 입장! \n", age1, age2, first);
    
    return 0;
}
```

![3](https://user-images.githubusercontent.com/29933947/35287052-e12f21ee-00a4-11e8-8658-d015ce4f08a2.png)



##### void 포인터

`void * ptr`

  . 어떠한 변수의 주소 값이든 지정 가능

  . 단, 포인터 연산, 값의 변경 참조는 불가능함



#### 메인함수 인자 전달

##### char * argv[]

  . argv 는 char 형 더블 포인터 변수

  . char 형 포인터 변수로 이루어진 1차원 배열의 이름을 전달 받을 수 있는 매개 변수

​     `void cfunc(int * arr)`

​     `void cfunc(int arr[])`

```c
#include <stdio.h>

// void ShowString(int argc, char ** argv)
void ShowString(int argc, char * argv[])
{
    int i;
    for(i=0; i<argc; i++)
        printf("%s \n", argv[i]);
}

int main(void)
{
    char * str[2] = {
        "This is String",
        "That is String"
    };
    
    ShowString(2, str);
    
    return 0;
}
```

![4](https://user-images.githubusercontent.com/29933947/35288082-2c301d90-00a7-11e8-9ae4-797a136407fc.png)

