---
title: "docker-compose 명령어 수행 시, docker-compose.yml is unsupported"
date: 2023-01-06
categories: Docker
tags: [Docker-compose]
---

docker-compose 명령어 수행 시, version ... is unsupported 해결 방법
------  

### 상황  

- `docker-compose up -d` 명령어 수행
  - `Version in "./docker-compose.yml" is unsupported` 오류 발생


```shell
# ex)
aiswtool@medge02:~/22_aiswtool/1_apps/medicalmgr-etri$ sudo docker-compose up -d
ERROR: Version in "./docker-compose.yml" is unsupported. You might be seeing this error because you're using the wrong Compose file version. Either specify a supported version (e.g "2.2" or "3.3") and place your service definitions under the `services` key, or omit the `version` key and place your service definitions at the root of the file to use version 1.
For more on the Compose file format versions, see https://docs.docker.com/compose/compose-file/

```  

![2023-01-05 17 27 42](https://user-images.githubusercontent.com/76153041/210957113-f7b109a7-b03c-4101-b2a4-97e332b9dd0f.png)  


### 원인  

- 실행하는 docker-compose 의 버전을 현재 운영체제(Ubuntu 20.04)에서 지원하지 않음
  - [참조][Version in docker-compose.yml is unsupported](https://github.com/datahub-project/datahub/issues/2020){: target="_blank"}  

- 현 시스템의 docker-compose 버전은 `1.25.0`

  ```shell
  docker-compose version

  #ex)
  aiswtool@medge02:~$ docker-compose version
  docker-compose version 1.25.0, build unknown
  docker-py version: 4.1.0
  CPython version: 3.8.10
  OpenSSL version: OpenSSL 1.1.1f  31 Mar 2020
  ```  

### 수정

- `docker-compose` 재설치
  - `23.01.06` 기준 `Ubuntu 20.04`에서는 `2.14.2` 버전이 설치됨

```shell
# docker-compose의 최신 버전 값을 얻는데 사용하는 패키지 설치
sudo apt-get install jq

# docker-compose의 최신 버전 값, 설치 경로를 변수에 저장
VERSION=$(curl --silent https://api.github.com/repos/docker/compose/releases/latest | jq .name -r)
DESTINATION=/usr/bin/docker-compose

# docker-compose 바이너리 다운로드 및 지정 경로에 설치
sudo curl -L https://github.com/docker/compose/releases/download/${VERSION}/docker-compose-$(uname -s)-$(uname -m) -o $DESTINATION

# 바이너리에 권한 설정(root 권한 아닌 사용자가 접근할 수 있게)
sudo chmod 755 $DESTINATION

# 명령어 설치 확인
which docker-compose

# 설치된 docker-compose version 확인
docker-compose version

#ex)
aiswtool@medge02:~$ sudo apt-get install jq -y
Reading package lists... Done
Building dependency tree
Reading state information... Done
The following additional packages will be installed:
  libjq1 libonig5
The following NEW packages will be installed:
  jq libjq1 libonig5
0 upgraded, 3 newly installed, 0 to remove and 71 not upgraded.
Need to get 313 kB of archives.
After this operation, 1,062 kB of additional disk space will be used.
Get:1 http://kr.archive.ubuntu.com/ubuntu focal/universe amd64 libonig5 amd64 6.9.4-1 [142 kB]
Get:2 http://kr.archive.ubuntu.com/ubuntu focal-updates/universe amd64 libjq1 amd64 1.6-1ubuntu0.20.04.1 [121 kB]
Get:3 http://kr.archive.ubuntu.com/ubuntu focal-updates/universe amd64 jq amd64 1.6-1ubuntu0.20.04.1 [50.2 kB]
Fetched 313 kB in 2s (146 kB/s)
Selecting previously unselected package libonig5:amd64.
(Reading database ... 154047 files and directories currently installed.)
Preparing to unpack .../libonig5_6.9.4-1_amd64.deb ...
Unpacking libonig5:amd64 (6.9.4-1) ...
Selecting previously unselected package libjq1:amd64.
Preparing to unpack .../libjq1_1.6-1ubuntu0.20.04.1_amd64.deb ...
Unpacking libjq1:amd64 (1.6-1ubuntu0.20.04.1) ...
Selecting previously unselected package jq.
Preparing to unpack .../jq_1.6-1ubuntu0.20.04.1_amd64.deb ...
Unpacking jq (1.6-1ubuntu0.20.04.1) ...
Setting up libonig5:amd64 (6.9.4-1) ...
Setting up libjq1:amd64 (1.6-1ubuntu0.20.04.1) ...
Setting up jq (1.6-1ubuntu0.20.04.1) ...
Processing triggers for man-db (2.9.1-1) ...
Processing triggers for libc-bin (2.31-0ubuntu9.7) ...
aiswtool@medge02:~$ VERSION=$(curl --silent https://api.github.com/repos/docker/compose/releases/latest | jq .name -r)
aiswtool@medge02:~$ DESTINATION=/usr/bin/docker-compose
aiswtool@medge02:~$ sudo curl -L https://github.com/docker/compose/releases/download/${VERSION}/docker-compose-$(uname -s)-$(uname -m) -o $DESTINATION
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
100 42.8M  100 42.8M    0     0  4709k      0  0:00:09  0:00:09 --:--:-- 3957k
aiswtool@medge02:~$ sudo chmod 755 $DESTINATION
aiswtool@medge02:~$ which docker-compose
/usr/local/bin/docker-compose
aiswtool@medge02:~$ docker-compose version
Docker Compose version v2.14.2
```  

![2023-01-05 17 33 48](https://user-images.githubusercontent.com/76153041/210959033-e25306e2-c530-4db8-a26e-f04088125d09.png)



