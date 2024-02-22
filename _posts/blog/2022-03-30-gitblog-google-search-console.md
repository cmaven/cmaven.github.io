---
title: "Github Blog 구글 검색 엔진에 노출시키기(Google Search Console)"
date: 2022-03-30
categories: Github_Blog
tags: [GoogleSearchConsole]
---

GitBlog 구글 검색 엔진에 노출 시켜, 외부 사용자가 접근할 수 있도록 하기  

:bulb: 본 문서는 Github 블로그의 글을 구글 검색 엔진에 노출시키는 방법을 정리한다.  
{: .notice--info}  

# [01]  Google Search Console?  

> 구글 검색 엔진에서 등록된 웹사이트가 검색되도록 등록하고, 검색 결과를 모니터링 할 수 있는 서비스로, 웹 크롤링 형태로 동작한다.  

- 블로그 게시글이 구글 검색이 가능하게 하려면, 구글 검색 엔진이 블로그 사이트를 읽는 작업이 필요함(크롤링)  
- [Google Search Concole](https://search.google.com/search-console/about){:target="_blank"} 사이트에서 등록 및 모니터링을 수행할 수 있음(구글 계정 필요)


# [02]  Google Search Console 등록


- 구글 계정 로그인 후, 사이트 접속, `시작하기` 선택  

  ![이미지 1](https://user-images.githubusercontent.com/76153041/160787269-37114862-a611-48e2-8be3-b05a8dad44c2.png)  

- GitBlog를 사용할 경우, 이미 URL이 있으므로 `URL 접두어` 부분에 블로그 주소를 입력함  

  ![이미지 2](https://user-images.githubusercontent.com/76153041/160787273-047d4228-b41d-43af-8517-a2373a3155ac.png)    

- 입력한 URL의 사이트가 사용자가 운영하는게 맞는지 `소유권 확인` 작업을 진행함  

  ![이미지 3](https://user-images.githubusercontent.com/76153041/160787274-021c4f7d-1044-4ea6-afb1-0723bfad4db4.png)  

- 팝업 창에 나타난 html 파일을(google675xxxx.html)을 블로그 Root 디텍토리에 복사 한 후, Git Repository에 적용함
- `git add *`, `git commit -m xxx`, `git push`

  ![이미지 20](https://user-images.githubusercontent.com/76153041/160791984-e5f45d05-608a-47ab-9d29-770cb259eb1d.png)  

- 파일 업로드 후, 잠시 기다리면 소유권 확인 팝업을 확인할 수 있음  

  ![이미지 4](https://user-images.githubusercontent.com/76153041/160787277-033ea137-cc95-47d6-a6cf-fbe6a94605fd.png)  
  
  
# [03]  Sitemap.xml 생성 및 적용  

- 소유권 확인으로 구글 검색 엔진이 해당 블로그를 인식할 수 있지만, 블로그 사이트를 읽고(크롤링), 정보를 제공하기 위한 데이터 필요
- `sitemap.xml`은 웹사이트의 모든 페이지의 목록을 나열하여 검색 엔진이 사용자에게 정보를 제공할 수 있도록 함
- sitemap.xml 생성 방법은 두 가지
  - 직접 작성
  - Jekyll의 `jekyll-sitemap` 플러그인을 통해서 생성
- 이 블로그에서 사용 중인 `minimal mistakes` 테마는 jekyll-sitemap 플러그인으로 생성 가능함
  - _config.yml 의 plugins 부분에 `jekyll-sitemap` 명시 확인  
  
    ![이미지 12](https://user-images.githubusercontent.com/76153041/160787294-4786d5ba-2d5f-4de5-9d1d-07f6016cb2da.png)  
  - Gemfile 에 `gem 'jekyll-sitemap` 추가  
  
    ![이미지 5](https://user-images.githubusercontent.com/76153041/160787278-7ecb90f0-ab1b-4b66-bfaa-2d950de598ea.png)  

  - 터미널에서 `bundle install` 수행  
    
    ![이미지 7](https://user-images.githubusercontent.com/76153041/160787284-00f0d880-a94d-40c3-bb10-d0d69ab76ea3.png)  
  
  - Git Repository에 반영 후, `htpps://xxx.github.io/sitemap.xml` 으로 접속하여 보면 아래와 같이 목록이 생성됨을 확인할 수 있음  
  
    ![이미지 11](https://user-images.githubusercontent.com/76153041/160787293-7d14ee0d-3fe9-4eca-ae75-8cddccbc9fab.png)  
  
- Google search console에서 `색인` → `Sitemaps` 선택  
  
  ![이미지 13](https://user-images.githubusercontent.com/76153041/160787299-ded6a8a4-2058-4646-96bd-3124e980759e.png)  

- 새 사이트맵 추가 부분에 `sitemap.xml` 입력 후 제출  
 
  ![이미지 14](https://user-images.githubusercontent.com/76153041/160787302-ca1d0463-ac41-416f-8b8c-a3ed6a311cca.png)
  
  ![이미지 15](https://user-images.githubusercontent.com/76153041/160787304-121e1694-eba1-4ded-ba09-e79aeeee999f.png)  

# [04]  Robots.txt 생성 및 적용  

- 웹 크롤러가 사이트의 정보를 크롤링 할 때, 적용할 정책을 지정하는 파일
- 사이트의 어떤 정보를 참조할지 결정하는 역할 
- 블로그의 Root 디렉토리에 Robots.txt를 생성하고 아래 내용을 작성한다.

```python
# User-agent : 크롤링 규칙이 적용되는 크롤러 지정 (*는 모두 허용)
# - Google은 Googlebot, 네이버는 Yeti 등으로 각 검색엔진의 크롤러는 다르다.
# Allow: 크롤링할 경로 (/는 / 아래 모든 경로를 크롤링 수행)
# Sitemap: Sitemap 지정 위치
# - Sitemap은 해당 사이트의 페이지 목록(사이트 지도)

User-agent: *
Allow: /

Sitemap: https://eona1301.github.io/sitemap.xml
```