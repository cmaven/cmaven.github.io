---
title: "Docker에 Ubuntu 컨테이너 생성 후, Nginx 서버 접근하기"
date: 2024-05-10
categories: Docker
tags: [Docker, Ubuntu]
---

:bulb: Docker 환경에서 Ubuntu 컨테이너를 Dockerfile로 생성하고, 실행하는 방법을 작성한다.  
컨테이너 내부에 nginx 서버를 구동시켜 외부에서 접근해본다.
{: .notice--info}

# [01]  Dockerfile 작성 및 이미지 생성, 컨테이너 실행

## Dockerfile  

```shell
# Dockerfile.ubuntu.22.04
vim Dockerfile.ubuntu.22.04

FROM ubuntu:22.04
ARG VERSION=latest
WORKDIR /root
RUN apt-get update ; apt-get install -y nginx net-tools vim iperf3

CMD service nginx start && tail -f /dev/null
```  

- RUN의 `apt-get install` 다음에 설치 원하는 패키지명 입력
- CMD의 `tail -f /dev/null` 은 컨테이너가 시작 후, 자동 종료 방지  


## 이미지 생성  

```shell
# 명령은 생성한 Dockerfile과 동일한 경로에서 실행
sudo docker build -f Dockerfile.ubuntu.22.04 -t test/ubuntu22.04 .
```  

## 생성 이미지 활용 컨테이너 실행  

- `-p`: Port Forward 지정
  - 아래는 Host에 8800 포트에 대한 Request를 컨테이너 내부의 80 포트로 전달함을 의미
- `--restart`: Docker 서비스가 재실행될 때, 생성한 컨테이너의 동작 지정
  - always는 항상 재시작 된다. = 항상 실행 상태를 유지한다.

```shell
docker run -d -p 8800:80 --name medge_ubuntu --restart always test/ubuntu22.04
```

# [02]  (선택)컨테이너 내부 Nginx 설정  

## 내부 접근

- 실행 중인 컨테이너에 bash Shell 터미널 접근

```shell
# test_ubuntu는 위에서 생성한 컨테이너 명

docker exec -it test_ubuntu /bin/bash
```

## 컨테이너 내부 Nginx index.html 수정

- Nginx Web Server의 Homepage로 접근했을 때, 컨테이너 내부로의 진입인지 확인하기 위함
- `/var/www/html/index.nginx-debian.html` 파일

```html
<!-- /var/www/html/index.nginx-debian.html <h1> 태그 부분 수정(제목) -->
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>
</head>
<body>
<!-- 내용 추가: -Con(8800) -->
<h1>Welcome to nginx!-Con(8800)</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```  

# [03]  접근확인

- ServerIP + Docker Port
  - ex) 111.111.111.111:8800  
  - [01]에서 설정한 8800 포트 활용
  - [02]에서 작성한 `<h1>Welcome to nginx!-Con(8800)</h1>` 출력 확인  

  ![2024-05-13 16 14 07](https://github.com/cmaven/cmaven.github.io/assets/76153041/7a6a6278-816b-4931-adc0-a81868ceea69)