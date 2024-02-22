---
title: "Github Blog 방문자 통계 확인하기(Google Analytics) 구글 파비콘(Favicon) 생성 및 적용하기"
date: 2022-03-29
categories: Github_Blog
tags: [GoogleAnalytics]
---  


:bulb: 깃헙 블로그에 Google Analytics(GA4)를 적용하여 방문제 통계를 확인하는 방법을 작성한다.
{: .notice--info}

# [01]  Google Analytics? 

> 구글에서 제공하는 웹사이트 트래픽을 추적하고 보고하는 Web Analytics Service  

사용 중인 블로그에 대해 방문자 통계 정보를 확인할 수 있도록 한다.

# [02]  Google Analytics 설정하기

## 가입 및 계정 생성

- google anlytics 사이트에 접속하여 계정 생성 및 설정 진행
  
  [(링크) google analytics](https://analytics.google.com/analytics/web/){:target="_blank"}
  
  ![01](https://user-images.githubusercontent.com/76153041/160599808-64fb41fd-4fd6-434a-8644-b0c05ccb6f4a.png)  

- 계정 이름은 꼭 구글 아이디와 같을 필요는 없다.  

  ![02](https://user-images.githubusercontent.com/76153041/160599811-2e24ba78-7b77-49e5-99c0-c05729717743.png)  

- 속성 이름은 사용하는 블로그 주소를 입력한다.  
- 보고 시간대 및 통화를 대한민국/원 으로 변경한다.  
  
  ![03](https://user-images.githubusercontent.com/76153041/160599820-648b14d2-62c1-4e85-978d-f2c8a4f69877.png)  

- 비즈니스 정보는 설정 안하여도 무방하다.(추후 변경 가능함)  
  
  ![04](https://user-images.githubusercontent.com/76153041/160599824-5246bf8a-c903-42e9-9a3d-3752094e19a7.png)  

- 서비스 약관 동의  

  ![05](https://user-images.githubusercontent.com/76153041/160599830-496811bb-d455-45c0-9598-8573bb8db175.png)  

- 서비스 약관 동의까지 진행하면 1차적인 설정이 완료된다.
- 실제로 트래픽 데이터를 모니터링하기 위해서는 `데이터 스트림`을 설정하고 `측정 ID`(measurement_id)를 생성해야 한다.
- `측정 ID`는 추후 Gitblog 설정 파일에 입력하여 Google Analytics가 해당 페이지를 추적할 수 있게 한다.
- 현재 Google Analytics는 `GA4` (Google Analytics 4)로 서비스 중이고, `G-XXX` 형태의 ID를 생성하고 활용한다.
- 이전에는 `UA` (Google Analytics 3)로 `UA-XXX` 형태의 ID를 생성하고 활용했다.  

  > Google Anlytics를 활용하여 방문자 통계를 확인하는 방법을 구글링 하면 UA-XXX의 추적 ID를 사용하는 포스팅을 많이 찾아볼 수 있다.. 위의 속성 설정에서 Google 애널리틱스 4 속성으로 생성하였는데, UA-XXX를 사용하는 방법을 활용하면 제대로 동작하지 않는다.  

- Gitblog는 Web 기반으로 구현하였으므로, 플랫폼을 `웹`으로 선택한다.
  ![06](https://user-images.githubusercontent.com/76153041/160599835-d09895c9-6a1d-46e2-a922-7f0912d1faf5.png)  

- 웹사이트 URL에는 Gitblog의 주소, 스트림 이름은 임의로 작성한다.
  ![07](https://user-images.githubusercontent.com/76153041/160599841-c37fe421-2e8d-4fae-8731-848e3548e59c.png)  

- 아래 화면의 `측정 ID`인 `G-4DKPW49KWZ`를 GitBlog에 적용하도록 한다.
  ![08](https://user-images.githubusercontent.com/76153041/160599844-e28d5077-03b5-48c9-aa88-171d0d01f5e2.png)  

## Github Blog 설정

> minimal mistake theme 기준  

- `_config.yml`의 `provider`를 `google-gtag` 입력, `measurement_id`가 없을 경우 생성 후, 위의 `추적 ID` 값을 입력  

  ![이미지 18](https://user-images.githubusercontent.com/76153041/160604837-c3e9941b-2a9c-4216-9c90-f1913e8008b8.png)  

- `_includes>analytics-providers>google-gtag.html` `<script>` 부분에 아래 코드 추가
  ```html
  gtag('config', {{ site.analytics.google.measurement_id }});
  ```
  ![10](https://user-images.githubusercontent.com/76153041/160599852-a8f310a6-4c8d-4abc-b8bb-8801a240933e.png)  


# [03]  결과 확인  

- 정상적으로 동작한다면, 접속을 새로고침하고 Google Analytics 홈 화면에서 바로 통계치를 확인할 수 있다.  
- 
  ![11](https://user-images.githubusercontent.com/76153041/160600107-010c5616-b57e-429f-98e2-f98998ef35e9.png)  