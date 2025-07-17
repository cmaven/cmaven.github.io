---
title: "Ubuntu 저장소(Repository) 한국 미러로 변경"
date: 2025-07-17
categories: Linux
tags: [Ubuntu, apt, kakao]
---

:bulb: Ubuntu 환경에서 패키지 설치 시, 다운로드 속도를 높이기 위해 기본 다운로드 경로(미러 사이트)를 변경하는 방법을 작성한다.
{: .notice--info}

# [01]  Ubuntu Repository 한국 미러 경로로 변경하기

📘 Ubuntu 22.04 기준

- kakao 미러
  - http://mirror.kakao.com/ubuntu
- kaist 미러
  - http://ftp.kaist.ac.kr

```shell
##-- Kakao
sudo sed -i 's|http://.*.ubuntu.com/ubuntu|http://mirror.kakao.com/ubuntu|g' /etc/apt/sources.list

##-- Kaist
sudo sed -i 's|http://.*.ubuntu.com/ubuntu|http://ftp.kaist.ac.kr/ubuntu|g' /etc/apt/sources.list
```  

위를 수행한 후, `sudo apt update` 후, 필요한 패키지를 설치하는데 활용한다.

# [02]  복구

- 기본 Ubuntu 미러 사이트로 복구하기

```shell
##-- Kakao
sudo sed -i 's|http://[^ ]*ubuntu|http://archive.ubuntu.com/ubuntu|g' /etc/apt/sources.list

##-- Kaist
sudo sed -i 's|http://security.ubuntu.com/ubuntu|http://security.ubuntu.com/ubuntu|g' /etc/apt/sources.list
```