---
title: "로컬 환경(Host)에서 깃 원격 저장소(Git Remote Repository) 생성하기"
date: 2022-08-25
categories: Git
tags: [RemoteRepository]
---

로컬 환경(Host Windows 또는 Linux)에서 깃 원격 저장소(Git Remote Repository)에 신규 저장소 생성하기
------

> Github page의 UI를 사용하지 않고 Host CLI로 원격 저장소를 생성한다.

### 필요정보

- `curl`을 사용하여 `Github API`로 Remote Repository를 생성함
- 원격에서 Github API를 사용하기 위해, 사용자 토큰(User Token)을 Github에서 발급 필요  

#### Token 생성  
- 사용자 Profile → Settings → Developer settings → Personal access tokens  
- 신규 토큰 생성은 `Generate new token`
  - Select scopes는 `repo` 부분만 전체 체크
- 기존 토큰 재생성은 토큰명 선택후, `Regenerate token`  
- 생성된 토큰을 API Call에 사용함
- 참조 스크린샷  
  ![doit_django_09](https://user-images.githubusercontent.com/76153041/186601949-d98457be-e591-4cd0-88ba-d1b5afbcdcb3.png){: width="200px" }
  ![doit_django_02](https://user-images.githubusercontent.com/76153041/186601994-d07dbb55-5450-443e-9862-2e62249a0a4d.png)
  ![doit_django_03](https://user-images.githubusercontent.com/76153041/186602003-bb8e12d7-deb6-463b-a97a-c3a348a4572f.png)
  ![doit_django_04](https://user-images.githubusercontent.com/76153041/186602019-ec0fa3f2-2ecb-4ee7-9fa4-9c0f6f83ce3a.png)


### API 사용  
[참조][githubapi-Create an organization repository](https://docs.github.com/en/rest/repos/repos#create-an-organization-repository){: target="_blank"}   

- API 동작 확인  

```shell
curl -i -u cmaven:${user_token} https://api.github.com/user

'''
example
'''
E:\Coding\Python\doit_djngo>curl -i -u cmaven:${user_token} https://api.github.com/user
HTTP/1.1 200 OK
Server: GitHub.com
Date: Thu, 25 Aug 2022 03:01:21 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 1264
Cache-Control: private, max-age=60, s-maxage=60
Vary: Accept, Authorization, Cookie, X-GitHub-OTP
# ...
```  

- Remote Repository 생성
  - `name`은 생성할 저장소 이름
  - `private`는 `true`로 설정 시, 비공개 저장소를 생성함

```shell
'''
Windows 환경의 cmd
'''
curl -i -u cmaven:${user_token} https://api.github.com/user/repos -d "{\"name\":\"doit_django\", \"private\":\"true\"}"

'''
Linux 환경의 bash-shell
'''
curl -i -u cmaven:${user_token} https://api.github.com/user/repos -d '{"name":"doit_django", "private":"true"}'
```  
- 생성 예  
![doit_django_07](https://user-images.githubusercontent.com/76153041/186605224-99d9d71f-70ad-4016-81b9-8f725886ec50.png)

- 생성모습
![doit_django_07](https://user-images.githubusercontent.com/76153041/186604838-32cbd253-9b55-4eb2-b924-b345b6fbeaf0.png)