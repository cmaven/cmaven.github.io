---
title: "GitBlog Post 작성 방법"
date: 2022-02-15
categories: Gitblog
tags: [Template, GithubBlog]
---

:triangular_flag_on_post: 2024-02-20 수정
{: .notice--warning}

>Post 최상단 내용 작성  

- 해당 페이지가 Post임을 표시

    ```python
    ---
    title: "GitBlog"
    date: 2022-02-15
    categories: Gitblog
    tags: [Temaplte]
    ---

    '''
    포스트 정보 작성

    * categories
    - 직접 생성한 categories와 매칭
    - C / C++ / css / docker / excel / git / gitblog / html / k8s / linux / python /storage / vscode / windows
    - 앞문자 대문자
    * tags
    - 임의 작성
    '''
    ```  

:bulb: 본 문서는 Post 작성 방법을 정리한다.  
아래 글은 ***로렘 임숨(lorem ipsum)***  
여단이라 등 이로 칠월에서 사람이 종류를 확충과 대한다. 표면은 내인가를 가한, 압수만큼 취하고, 모습은 보인다. 제정이나 의심에서, 거미를, 행위의 싶으라. 어떤 회장은 필요하라 두 저질화에 소리다 전혀 후보에 없기, 서다. 의장직은 깨끗이 평가와 자리에, 강 투철하여야 알다. "선거다 입시나 분규나 밀매에서 과학이다, 하다" 공통점을 환자라도 수용하고 보내고 간부로 제약할 이기다 국유화론이라 보라. 속도에 기자의 정부에 누구는 산출 늘어나다. 사법의 액세서리를 그렇지 되면서, 따른다.
{: .notice--info}

# [01]  내용분류  

자청으로서 세력을 저온의 대표단은 두 있다 부적합성이 흡수한다 주도 대한다. 일은 강화를 일방적이 있음 처리하다, 지금 위하다. 콜레스테롤의 있고 확보하지 이차의 전하다 시장을 인하한 온 사용하라. 교수를 있은 축산물에 오전에 알다 예방으로 넘다. 정전이어 폭우다 찌꺼기를 조사에, 정치권의 없는 종속은 나는 평화가 대하다. 빌리어 정당이 광역을 대형을 통하다.

## 세부내용1  

또 몇 의미는 용어를 현상이 추진한가. 낫다 요건 지친다 공개념의 장소를 여가 다음은 2026년 특별하다. 마찬가지를 처음과 먼저 부정의 고장으로 확정의 있다. 사고에서 결과도, 아니는 주말과 있어야 예정되다 발행된지 것 곧, 들리다. "건의하기 3일, 있으면 2024년 하라" 정부 예산이지 그림과 관계의 환하는 2026년 데 된다. 2시 보호를 8시간 국내가 볼 의식에 않습니다 장관을 한정을, 내세우다. 도중을 수 지역이든지 정도에 있고 조사할 각 하는 없다 즐겁습니다. "지나게 들다 장시간의 위한 트럭이 보수다, 답변에 대하다"

### 세부내용2

투시경의 대책에 동안이나 정계로, 항공모함을 관리하여야 것 9,630,000원 밝히다. "않도록 이 함께 변칙이 등지 진화하라" 우리나라가 국정에, 중요성에서 보험을, 이에서, 유아가 그해를 한하며 행사밖에 만회하다. 논문이 경찰과 있다 이어받은 문제에 나타난 확정되더라도 거의 보다. 소리다 계통은 영세만 국가다 안으면 받는다면 말하다 있으나 영화부터 발표되다. 앓아 토의다 동작의, 전망이 대동하다.

#### 세부내용3

준비하게 2시간 강력히, 감독을 인력의 밝혀내며 떨어진다 발매되는 아이디어 빌린다. 태아부터 아르바이트로 점포가 크어서 9명 감지하다. 채용의 페어를 3,240,000원 성장을 되어 교수는 골이 대합실이어 규정하더라. 그리고 과제의 수, 외지로 많는 보이어야 및 있는지. 평가하여 미생물이지만 공천은 혼자다 요즘을 지원에 공약에, 있다. "입장에 하다, 사실을 보자 방문하다" "현재 동의의 작업과 연합을 갖은, 기름은 총무의 개선안은 정책이 못지않다"


# [02]  문법

## 줄바꿈  

첫 번째 줄 마지막에 <u>스페이스바 두번, Enter</u>

```python
첫 번째 줄입니다. #Space#Space#Enter
두 번째 줄입니다.
```  

## 강조, 기울임, 취소선, 밑줄

**강조**  `**강조**`  
*기울임*  `*기울임*`  
~~취소선~~  `~~취소선~~`  
<u>밑줄</u>  `<u>밑줄</u>`  


## 코드블록

```python
# 아래와 같이 ```로 Code를 감싸서 작성

# ```
# code
# ```
```  

- 주요 지원언어는 아래와 같다.
  - bash, bat, console,
  - c, cpp, go, java, python, 
  - cmake, console, make, vim 
  - css, html, js, jsp, markdown, r, sass
  - sql, sqlite3, 
  - xml, yaml

- 생성 예)

    ```python
    ### --- 생성, 수정한 파일 이름

    # 주석
    import os

    class Class():
        value1 = 0

        def __str__(self):
            return self.value1
        
        def function(parm1, parm2):
            values = 0
            return

    if __name__ == '__main__':
        main()
    ```  

## 이모지

:bulb: 는 `:bulb:`로 작성  

:small_blue_diamond:참조: [https://gist.github.com/rxaviers/7360908](https://gist.github.com/rxaviers/7360908){:target="_blank"}  

### 주요이모지  

:exclamation:  `:exclamation:`  
:fire:  `:fire:`  
:star:  `:star:`  
:cloud:  `:cloud:`  
:sunny:  `:sunny:`  
:zap:  `:zap:`  
:milky_way:  `:milky_way:`  
:computer:  `:computer:`  
:loudspeaker:  `:loudspeaker:`  
:scroll:  `:scroll:`  
:page_with_curl:  `:page_with_curl:`  
:clipboard:  `:clipboard:`  
:closed_book:	`:closed_book:`  
:green_book:  `:green_book:`  
:memo:  `:memo:`  
:rocket:  `:rocket:`  
:beginner:  `:beginner:`  
:round_pushpin:  `:round_pushpin:`  
:triangular_flag_on_post:  `:triangular_flag_on_post:`  
:arrow_forward:  `:arrow_forward:`  
:arrow_backward:  `:arrow_backward:`  
:arrow_left:  `:arrow_left:`  
:arrow_right:  `:arrow_right:`  
:red_circle:  `:red_circle:`  
:diamonds:  `:diamonds:`  
:large_blue_circle:  `:large_blue_circle:`  
:large_blue_diamond:  `:large_blue_diamond:`  
:large_orange_diamond:  `:large_orange_diamond:`  
:small_blue_diamond:  `:small_blue_diamond:`  
:small_orange_diamond:  `:small_orange_diamond:`  
:ballot_box_with_check:  `:ballot_box_with_check:`  


## 링크  

> 같은창으로 열기  
  
:small_blue_diamond:참조: [같은창으로 열기](http://google.co.kr)  

> 새창으로 열기  
  
:small_blue_diamond:참조: [새창으로 열기](http://google.co.kr){:target="_blank"}  

```python
# 같은 창으로 열기
:small_blue_diamond:참조: [같은창으로 열기](http://google.co.kr)  

# 새 창으로 열기
:small_blue_diamond:참조: [새창으로 열기](http://google.co.kr){:target="_blank"}  
```  

## 이미지   

이미지는 Github의 Issues를 활용한다.  
이 때, Issues 작업을 수행하는 Repository는 *public* 이어야 한다.  

### 이미지 업로드

Issues :arrow_forward: New Issue :arrow_forward: Open a blank issue :arrow_forward: 이미지를 Write 창에 복사  
이후, 생성되는 링크를 Page에 복사하여 붙여넣기  

![2024-02-20 18 15 52](https://github.com/cmaven/cmaven.github.io/assets/76153041/0916505a-27a7-496f-8525-145e8cd32d76)  

![2024-02-20 18 16 11](https://github.com/cmaven/cmaven.github.io/assets/76153041/e1914280-8128-4b96-8e33-b152247a4f6e)  

![2024-02-20 18 17 39](https://github.com/cmaven/cmaven.github.io/assets/76153041/bfc1d8fc-da33-467d-9fe4-b0800c881fb2)  

![2024-02-20 18 18 02](https://github.com/cmaven/cmaven.github.io/assets/76153041/e858e82d-96af-425d-a4c3-9e4d4e588d81)  

- 생성 예)  
![unsplash-image-9](https://github.com/cmaven/cmaven.github.io/assets/76153041/0ed9c920-d723-4edd-8c72-60f58514875f)

### 이미지 내 링크 적용  

이미지를 클릭 시, 다른 웹페이지로 이동할 수 있는 링크 생성
- `설명`은 이미지에 마우스 포인터를 놓았을 때, 나오는 텍스트

[![unsplash-image-9](https://github.com/cmaven/cmaven.github.io/assets/76153041/0ed9c920-d723-4edd-8c72-60f58514875f "설명")](http://google.com){:target="_blank"} 

```python
# 같은 창으로 열기
[![unsplash-image-9](https://github.com/cmaven/cmaven.github.io/assets/76153041/0ed9c920-d723-4edd-8c72-60f58514875f "설명")](http://google.com)

# 새 창으로 열기
[![unsplash-image-9](https://github.com/cmaven/cmaven.github.io/assets/76153041/0ed9c920-d723-4edd-8c72-60f58514875f "설명")](http://google.com){:target="_blank"}  
``` 

### 이미지 크기 변경, 정렬

- 크기변경  

    ```python
    # 크기 조절(html 사용)
    <img src="https://github.com/cmaven/cmaven.github.io/assets/76153041/0ed9c920-d723-4edd-8c72-60f58514875f" width="100px" height="100px">{: .align-center}
    ```

- 정렬  

    ```python
    # 가운데 정렬
    ![unsplash-image-9](https://76153041/0ed9c920-d723-4edd-8c72-60f58514875f)
    {: .align-center} 
    # 왼쪽 정렬
    ![unsplash-image-9](https://76153041/0ed9c920-d723-4edd-8c72-60f58514875f)
    {: .align-left} 
    # 오른쪽 정렬
    ![unsplash-image-9](https://76153041/0ed9c920-d723-4edd-8c72-60f58514875f)
    {: .align-right} 
    ```  

- 사용 예 (300px, 가운데 정렬))
<img src="https://github.com/cmaven/cmaven.github.io/assets/76153041/0ed9c920-d723-4edd-8c72-60f58514875f" width="300px" height="300px">{: .align-center}  



## 리스트

- 리스트
  - 리스트
    - 리스트

1. 리스트
   1. 리스트
      - 리스트
   1. 리스트
   2. 리스트
2. 리스트

- [ ] 체크안함
- [x] 체크

```python
- 리스트
  - 리스트
    - 리스트

1. 리스트
   1. 리스트
      - 리스트
   2. 리스트
   3. 리스트
2. 리스트

- [ ] 체크안함
- [x] 체크
```  


## 인용 (BlockQuote)  

> 연정한 부상에서, 정당이 밝히면 문제화할지. 인근은 일으키어야 터진다 예산이, 않다. 적으라 적다 2024년, 않는, 나아 원칙은 놓은가.  

>> 대한민국은 국제평화의 유지에 노력하고 침략적 전쟁을 부인한다. 국회는 국무총리 또는 국무위원의 해임을 대통령에게 건의할 수 있다. 통신·방송의 시설기준과 신문의 기능을 보장하기 위하여 필요한 사항은 법률로 정한다.

```python
> 연정한 부상에서, 정당이 밝히면 문제화할지. 인근은 일으키어야 터진다 예산이, 않다. 적으라 적다 2024년, 않는, 나아 원칙은 놓은가.

>> 대한민국은 국제평화의 유지에 노력하고 침략적 전쟁을 부인한다. 국회는 국무총리 또는 국무위원의 해임을 대통령에게 건의할 수 있다. 통신·방송의 시설기준과 신문의 기능을 보장하기 위하여 필요한 사항은 법률로 정한다.
```  

## 각주

Here is a simple footnote[^1].

A footnote can also have multiple lines[^2].

[^1]: My reference.
[^2]: To add line breaks within a footnote, prefix new lines with 2 spaces.

This is a second line.

```python
Here is a simple footnote[^1].

A footnote can also have multiple lines[^2].

[^1]: My reference.
[^2]: To add line breaks within a footnote, prefix new lines with 2 spaces.

This is a second line.
```  


