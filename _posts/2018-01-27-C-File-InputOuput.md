---
layout: post
title: "C 파일 입출력"
date: 2018-01-27 00:30
categories: Program_Language
tags: c
---

C언어의 파일 입출력에 대해 정리한다.

------

  ### 파일입출력 스트림

![2](https://user-images.githubusercontent.com/29933947/35490439-f390d642-04e2-11e8-895b-09382131dfe1.png)

  . r+, w+ 등의 읽기와 쓰기가 가능한 모드도 있으나, 작업 변경 버퍼 비움 필요와 위험성으로 사용하지 않음

  . 바이너리 파일(Binary file)은 컴퓨터가 인식할 수 있는 데이터 및 주로 음원, 이미지 들의 파일

  

### 파일 입출력 기본함수

```c
#include <stdio.h>
FILE * fopen(const char * filename, const char * mode)
```

  . File : 구조체 이름

  . filename: 작업할 파일 이름

  . mode: 입출력 스트림 지정

  . 지정한 파일과의 입출력 스트림을 형성하고, 스트림 정보를 FILE 구조체 변수에 담아 변수의 주소 값을 반환

![_ 1](https://user-images.githubusercontent.com/29933947/35490156-eab03c36-04e0-11e8-9d36-1e9695cc4ec5.png)



  . fopen 함수 호출 시, FILE 구조체 변수 생성

  . 생성된 FILE 구조체 변수에는 파일에 대한 정보 담김

  .  FILE 구조체 포인터는 파일을 가리키는 '지시자' 역할



```c
#include <stdio.h>
int fclose(FILE * stream);
int fflush(FILE * stream);
```

  . 성공 시, `0` , 실패 시 `EOF` 반환

  . fclose는 파일과 연결된 스트림을 해제하는 함수

  . fclose는 운영체제가 할당한 자원의 반환, 버퍼링 되었던 데이터의 출력을 위함

  . fflush는 출력버퍼를 비우는 함수



```c
#include <stdio.h>

int filecheck(FILE ** file)
{
    if(file==NULL)
    {
        puts("파일 오픈 실패");
        return -1;
    }
}

int main(void)
{
  FILE * fpw = fopen("filefunctest.txt", "wt");
  FILE * fpr = NULL;
  char str[50];
  int ch, i;

  filecheck(&fpw);

  fputc('A', fpw);
  fputc('B', fpw);
  fputc('C', fpw);
  fputc('1', fpw);
  fputc('2', fpw);
  fputc('3', fpw);

  fputs("This is filefunc test \n", fpw);

  fclose(fpw);


  fpr=fopen("filefunctest.txt", "rt");
  filecheck(&fpr);

  for(i=0; i<6; i++)
  {
     ch = fgetc(fpw);
     printf("%c \n", ch);
  }

  fgets(str, sizeof(str), fpw);
  printf("%s", str);

  fclose(fpr);

  return 0;
}
```

![2](https://user-images.githubusercontent.com/29933947/35491350-6191dbd6-04e9-11e8-8f7d-69b563771b1e.png)



#### feof

  . 파일의 끝을 확인하는 함수

  . 파일 복사 시, 주로 사용됨

```c
#include <stdio.h>
int feof(FILE * stream);
```

  . 파일의 끝에 도달하면 0이 아닌 값을 반환함

```c
#include <stdio.h>

int main(void)
{
    FILE * src=fopen("src.txt", "rt");
    FILE * des=fopen("des.txt", "wt");
    char str[20];

    if(src==NULL || des==NULL)
    {
        puts("파일 오픈 실패");
        return -1;
    }

    while(fgets(str, sizeof(str), src) != NULL)
        fputs(str, des);

    if(feof(src)!=0)
        puts("파일 복사 완료");
    else
        puts("파일 복사 실패");

    fclose(src);
    fclose(des);

    return 0;
}
```

![3](https://user-images.githubusercontent.com/29933947/35491653-2423b8b2-04eb-11e8-93c8-bda0535dcea1.png)



####fread, fwrite

  . 바이너리 데이터의 입출력에 사용되는 함수

```c
#include <stdio.h>
size_t fread(void * buffer, size_t size, size_t count, FILE * stream);
size_t fwrite(void * buffer, size_t size, size_t count, FILE * stream);
```

  . 함수 호출 성공 시, 전달 인자 `count` , 실패 또는 파일의 끝 도달 시 `count` 보다 작은 값을 반환함

```c
#include <stdio.h>

int main(void)
{
    FILE * src = fopen ("src.bin", "rb");
    FILE * des = fopen ("des.bin", "wb");
    char buf[20];
    int readCnt;
    
    if(src==NULL || des==NULL){
        puts("파일 오픈 실패");
        return -1;
    }
    
    while(1)
    {
        readCnt = fread((void*)buf, 1, sizeof(buf), src);
        
        if(readCnt < sizeof(buf))
        {
            if(feof(src)!=0)
            {
                fwrite((void*)buf, 1, readCnt, des);
                puts("파일 복사 완료");
                break;
            }
            else
                puts("파일 복사 실패");
            
            break;
        }
        
        fwrite((void*)buf, 1, sizeof(buf), des);
    }
    
    fclose(src);
    fclose(des);
    
    return 0;
}
```

  . 복사할 src.bin 값

![9](https://user-images.githubusercontent.com/29933947/35544516-17899a9a-05ae-11e8-800a-8994231979bd.png)

  . 파일 복사

![12](https://user-images.githubusercontent.com/29933947/35544517-17b0e5e6-05ae-11e8-9320-62c2917ce14a.png)

  . 복사된 des.bin 값

![10](https://user-images.githubusercontent.com/29933947/35544515-1760933e-05ae-11e8-871b-2f403d663c64.png)



#### fprintf, fscanf

  . 텍스트, 바이너리로 이루어진 데이터의 입출력에 사용되는 함수

  . printf, scanf의 함수와 동일한 구조이면서, 첫 번째 인자에 FILE 구조체 포인터가 위치하는 것이 차이점

```c
#include <stdio.h>

int main(void)
{
  char name[10]; // 텍스트 데이터
  char sex;      // 텍스트 데이터
  int age;       // 바이너리 데이터
  
  // for write
  FILE * fpw = fopen("mix-data.txt", "wt");  
  int i;
  
  // for read
  FILE *fpr = NULL;
  int ret;
  
  for(i=0; i<3; i++)
  {
    printf("이름 성별 나이 순 입력: ");
    scanf("%s %c %d", name, &sex, &age);
    getchar(); // buffer에 남아 있는 개행문자 \n 의 소멸을 위해
               // 엔터 키의 입력을 읽어들이지 않고 입력버퍼에 두는 scanf에 특성에 따름
    fprintf(fpw, "%s %c %d", name, sex, age);
  }
  
  fclose(fpw);
    
  fpr = fopen("mix-data.txt", "rt");
  
  while(1)
  {
    ret = fscanf(fpr, "%s %c %d", name, &sex, &age);
    if(ret == EOF)
      break;
    printf("%s %c %d \n", name, sex, age);
  }
  
  fclose(fpr);
  
  return 0;  
}
```

![13](https://user-images.githubusercontent.com/29933947/35544642-d9005cf4-05ae-11e8-85bd-87802b064e96.png)



#### fseek

  . `파일 위치 지시자`를 직접 이동시키고자 할 때, 사용하는 함수

> 파일 위치 지시자 
>
> - FILE 구조체 멤버 중, 파일의 위치 정보를 저장하고 있는 멤버
> - fgets, fputs, fread, fwrite 같은 파일 관련 함수가 호출될 때마다 참조 및 갱신됨
> - 파일이 처음 개방되면 무조건 파일의 맨 앞부분을 가리킴

```c
#include <stdio.h>
int fseek(FILE * stream, long offset, int wherefrom);
// stream 으로 전달된 파일 위치 지시자를 wherefrom에서 부터 offset만큼 이동
```

  . 성공 시 `0`, 실 패 시 `0이 아닌 값` 반환

  . wherefrom의 지시자

| 매개변 수 wherefrom | 파일 위치 지시자              |
| --------------- | ---------------------- |
| SEEK_SET(0)     | 파일 맨 앞에서부터 이동을 시작      |
| SEEK_CUR(1)     | 현재 위치에서부터 이동을 시작       |
| SEEK_END(2)     | 파일 맨 끝(EOF)에서부터 이동을 시작 |

  . 매개변수 offset은 양의 정수, 음의 정수 모두 가능

  . 음의 정수일 경우 파일의 시작 위치를 향해서 파일 위치 지시자가 이동함

![1](https://user-images.githubusercontent.com/29933947/35545197-4566680a-05b1-11e8-9d51-737428aef0fd.png)



#### ftell

  . 현재 파일 위치 지시자 정보 확인

```c
#include <stdio.h>
long ftell(FILE *stream)
```

  . Byte 단위 반환

​    ex)파일 위치 지시자가 첫 번째 바이트 가리킬 경우 0, 세번 째 가리킬 경우 2 반환

```c
#include <stdio.h>

/* ftell을 이용하여 파일 위치 지시자의 정보를 임시로 저장하고 활용하는 프로그램 */
int main(void)
{
  long fpos;
  int i;
  
  // 파일 생성
  FILE * fp = fopen("text.txt", "wt");
  fputs("1234-", fp);
  fclose(fp);
  
  // 파일 개방
  fp = fopen("text.txt", "rt");
  
  for(i=0; i<4; i++)
  {
    putchar(fgetc(fp));
    fpos = ftell(fp);			// 파일 위치 지시자의 위치 저장
    fseek(fp, -1, SEEK_END);	// EOF 바로 앞으로 파일 위치 지시자 이동 후, 출력
    putchar(fgetc(fp));
    fseek(fp, fpos, SEEK_SET);  // 이전의 파일 위치 지시자 위치로 이동
  }
  fclose(fp);
  return 0;
}
```

![14](https://user-images.githubusercontent.com/29933947/35544671-fe190ff4-05ae-11e8-8e8d-f99d0b4eccb5.png)



#### 구조체 변수 입출력

  . 구조체 변수를 하나의 바이너리 데이터로 인식하고 처리하도록 함

  . 따라서, fwrite, fread 함수를 사용한다.

```c
#include <stdio.h>
typedef struct fren
{
  char name[10];
  char sex;
  int age;
} Friend;

int main(void)
{
  FILE * fp;
  Friend myfren1;
  Friend myfren2;
  
  // Write
  fp = fopen("friend.bin", "wb");
  printf("이름, 성별, 나이 순 입력: ");
  scanf("%s %s %d", myfren1.name, &(myfren1.sex), &(myfren1.age));
  fwrite((void*)&myfren1, sizeof(myfren1), 1, fp);
  fclose(fp);
  
  // Read
  fp = fopen("friend.bin", "rb");
  fread((void*)&myfren2, sizeof(myfren2), 1, fp);  
  printf("%s %s %d", myfren2.name, &(myfren2.sex), myfren2.age);
  fclose(fp);
  
  return 0;
}
```

![16](https://user-images.githubusercontent.com/29933947/35544923-117e1fc0-05b0-11e8-8b07-b923ba821559.png)









