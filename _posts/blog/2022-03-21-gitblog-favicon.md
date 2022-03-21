---
title: "GitBlog 파비콘(Favicon) 생성 및 적용하기"
date: 2022-03-21
categories: Gitblog
tags: [Favicon]
---

GitBlog 에 파비콘(Favicon) 생성 및 적용하는 방법
------

### Favicon? 
> "Favorites + Icon"의 합성어로 인터넷 웹 브라우저의 주소창, 탭에 표시되는 대표 아이콘

아래 블로그 왼쪽 편의 아이콘을 변경하려 한다.  
 
![favicon 설정이 안되어 있는 상태](https://user-images.githubusercontent.com/76153041/159212163-a60549fa-e776-454a-bb03-a1c9d7de688b.png)

### 이미지 준비 및 파비콘 생성

- 사용할 이미지  
      
  정사각형 이미지를 사용하는 것이 좋음  

  ![favicon용 이미지](https://user-images.githubusercontent.com/76153041/159210308-0e238928-1658-4216-bfcd-aa0df9f463cb.png){: width="20%" height="20%"}  

   
- 파비콘 생성  
  
  [(링크) favicon-generator](https://www.favicon-generator.org/){:target="_blank"}
  
  
  사용할 이미지 파일을 업로드하고 (파일선택) → 파비콘을 생성함 (Create Favicon)  

  ![favicon-generator](https://user-images.githubusercontent.com/76153041/159210975-16270ef4-88b8-47d6-8a3b-41426ad20374.png)  
    
  생성된 파일을 다운로드 받음 (Download the generated favicon)
  아래 HTML document의 내용은 블로그 설정 파일에 입력해야함 (따로 복사)  
  

  ![favicon-generator-02](https://user-images.githubusercontent.com/76153041/159210983-4ea54f53-5f99-437a-a0fd-de3664433f08.png)  
  
  다운로드 받은 파일의 이름을 변경 (선택사항)  
  이 때, ico 확장자는 유지하여야 함  
  ex) ed00c6... 파일을 favicon.ico 파일로 변경함  
      
  ![favicon-파일 만들기](https://user-images.githubusercontent.com/76153041/159211993-91ae9936-55da-40ce-8a29-f9c973a00f67.png)  

### 블로그에 생성한 파비콘 적용하기  

- 생성한 파일의 압축을 풀고, 블로그의 `/assets/` 폴더 아래로 복사  

  ![favicon-ico 폴더 업로드](https://user-images.githubusercontent.com/76153041/159212363-25f845a9-0804-4a28-b939-040b5aab36df.png)  

- 파비콘 생성 시, 출력되었던 HTML document의 내용을 `_includes/head/custom/html` 에 입력  
  
  `minimal-mistakes` 테마 기준  
  생성한 파일의 경로를 `herf` 태그 경로에 추가하여 준다 (/assets/favicon.ico/)  
  
  ![_includes_head_custom html 경로에 favicon ico 설정](https://user-images.githubusercontent.com/76153041/159212365-3d2f69cd-28dc-4d6e-84c3-7e0910994404.png)  


### 적용된 모습  
![favicon-update 된 상태](https://user-images.githubusercontent.com/76153041/159212719-0bfccb72-1cca-4d16-ae90-491a39c4d55e.png)  
