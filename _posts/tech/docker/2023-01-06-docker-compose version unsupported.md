---
title: "docker-compose 명령어 수행 시, docker-compose.yml is unsupported"
description: "docker-compose up 실행 시 Version is unsupported 오류의 원인과 최신 버전 재설치로 해결하는 방법"
excerpt: "docker-compose.yml version unsupported 오류 원인 및 재설치 해결 방법"
date: 2023-01-06
categories: Docker
tags: [Docker, Docker-compose, 버전오류, Ubuntu, 재설치, troubleshooting]
---

:bulb: docker-compose 명령어 수행 시, version ... is unsupported 해결 방법을 작성한다.
{: .notice--info}

# [01] 상황

- `docker-compose up -d` 명령어 수행
  - `Version in "./docker-compose.yml" is unsupported` 오류 발생

```shell
# ex)
aiswtool@medge02:~/22_aiswtool/1_apps/medicalmgr-etri$ sudo docker-compose up -d
ERROR: Version in "./docker-compose.yml" is unsupported. You might be seeing this error because you're using the wrong Compose file version. Either specify a supported version (e.g "2.2" or "3.3") and place your service definitions under the `services` key, or omit the `version` key and place your service definitions at the root of the file to use version 1.
For more on the Compose file format versions, see https://docs.docker.com/compose/compose-file/
```

![2023-01-05 17 27 42](https://user-images.githubusercontent.com/76153041/210957113-f7b109a7-b03c-4101-b2a4-97e332b9dd0f.png)

# [02] 원인

- 실행하는 docker-compose 의 버전을 현재 운영체제(Ubuntu 24.04)에서 지원하지 않음
  - [참조: Version in docker-compose.yml is unsupported](https://github.com/datahub-project/datahub/issues/2020){:target="_blank"}

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

# [03] 수정

- `docker-compose` 재설치
  - `23.01.06` 기준 `Ubuntu 24.04`에서는 `2.14.2` 버전이 설치됨

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
```

![2023-01-05 17 33 48](https://user-images.githubusercontent.com/76153041/210959033-e25306e2-c530-4db8-a26e-f04088125d09.png)
