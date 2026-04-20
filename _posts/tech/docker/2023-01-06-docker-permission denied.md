---
title: "Docker 명령어 수행 시, permission denied"
description: "일반 사용자로 Docker 명령어 실행 시 permission denied 오류의 원인과 docker 그룹 추가로 해결하는 방법"
excerpt: "docker.sock permission denied 오류를 usermod docker 그룹 추가로 해결하기"
date: 2023-01-06
categories: Docker
tags: [Docker, Permission, docker.sock, usermod, 권한오류, Ubuntu, troubleshooting]
---

:bulb: Docker 명령어 수행 시, permission denied 오류 수정 방법을 작성한다.
{: .notice--info}

# [01] 상황

- 명령어 수행 시, `dial unix /var/run/docker.sock: connect: permission denied` 오류 발생

```shell
# ex
aiswtool@medge02:~/22_aiswtool/1_apps$ docker version
Client: Docker Engine - Community
 Version:           20.10.22
...
Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/version": dial unix /var/run/docker.sock: connect: permission denied
```

![2023-01-05 16 31 49](https://user-images.githubusercontent.com/76153041/210955601-02b102ed-4c7b-442b-8121-3a49debd16e5.png)

# [02] 원인

- 명령어를 수행하는 사용자가 `/var/run/docker.sock`에 대한 접근 권한이 있어야 함
- 일반적으로 `root` 권한이 아닌 상태로, `docker` 명령어 수행 시 발생

```shell
# 사용자 권한 확인
id

# ex)
aiswtool@medge02:~$ id
uid=1001(aiswtool) gid=1001(aiswtool) groups=1001(aiswtool),27(sudo),
```

![2023-01-06 16 55 30](https://user-images.githubusercontent.com/76153041/210956002-0db0cee3-73c6-4cb3-9703-06243e20eb96.png)

# [03] 수정

```shell
# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
# docker 재시작
systemctl restart docker
# docker 그룹 변경사항 적용
newgrp docker
```

# [04] 확인

- 사용자의 명령어 권한 확인 후, docker 명령어를 수행하면 해당 오류가 사라짐을 확인할 수 있음

![2023-01-05 16 41 52](https://user-images.githubusercontent.com/76153041/210956441-bb8175b9-e1e7-41da-84dd-6add1d9db05e.png)
