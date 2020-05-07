---
layout: post
title: "Ubuntu 저장소 변경"
date: 2018-01-12 16:00 +0900
categories: Linux
tags: ubuntu
---

우분투 설치 후, 저장소(Repository)를 변경하는 방법을 정리한다.

------

> 기존 파일 백업

```shell
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bp
```

> sources.list 파일 수정(vim editor)

```shell
sudo vim /etc/apt/sources.list
```

>  vim 명령모드 `:` 에서 아래 명령 수행


```powershell
:%s/us.archive.ubuntu.com/ftp.daumkakao.com/g
```

