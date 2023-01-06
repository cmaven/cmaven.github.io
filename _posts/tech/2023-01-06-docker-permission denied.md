---
title: "Docker 명령어 수행 시, permission denied"
date: 2023-01-06
categories: Docker
tags: [Permission, Docker]
---

Docker 명령어 수행 시, permission denied 오류 수정 방법
------  

### 상황  

- 명령어 수행 시, `dial unix /var/run/docker.sock: connect: permission denied` 오류 발생


```shell
# ex
aiswtool@medge02:~/22_aiswtool/1_apps$ sudo docker version
Client: Docker Engine - Community
 Version:           20.10.22
 API version:       1.41
 Go version:        go1.18.9
 Git commit:        3a2c30b
 Built:             Thu Dec 15 22:28:08 2022
 OS/Arch:           linux/amd64
 Context:           default
 Experimental:      true

Server: Docker Engine - Community
 Engine:
  Version:          20.10.22
  API version:      1.41 (minimum version 1.12)
  Go version:       go1.18.9
  Git commit:       42c8b31
  Built:            Thu Dec 15 22:25:58 2022
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          1.6.14
  GitCommit:        9ba4b250366a5ddde94bb7c9d1def331423aa323
 runc:
  Version:          1.1.4
  GitCommit:        v1.1.4-0-g5fd4c4d
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0
aiswtool@medge02:~/22_aiswtool/1_apps$ docker version
Client: Docker Engine - Community
 Version:           20.10.22
 API version:       1.41
 Go version:        go1.18.9
 Git commit:        3a2c30b
 Built:             Thu Dec 15 22:28:08 2022
 OS/Arch:           linux/amd64
 Context:           default
 Experimental:      true
Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/version": dial unix /var/run/docker.sock: connect: permission denied
```  

![2023-01-05 16 31 49](https://user-images.githubusercontent.com/76153041/210955601-02b102ed-4c7b-442b-8121-3a49debd16e5.png)  

### 원인
- 명령어를 수행하는 사용자가 `/var/run/docker.sock`에 대한 접근 권한이 있어야 함
- 일반적으로 `root` 권한이 아닌 상태로, `docker` 명령어 수행 시 발생

```shell
# 사용자 권한 확인
id

# ex)
aiswtool@medge02:~$ id
uid=1001(aiswtool) gid=1001(aiswtool) groups=1001(aiswtool),27(sudo),
```  

- 현재는 docker 명령어에 대한 권한이 없음

![2023-01-06 16 55 30](https://user-images.githubusercontent.com/76153041/210956002-0db0cee3-73c6-4cb3-9703-06243e20eb96.png)  

### 수정

```shell
# 현재 사용자를 docker 그룹에 추가 
sudo usermod -aG docker $USER
# docker 재시작
systemctl restart docker
# docker 그룹 변경사항 적용
newgrp docker
```  





