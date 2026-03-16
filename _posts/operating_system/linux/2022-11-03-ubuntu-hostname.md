---
title: "우분투(Linux)에서 호스트 이름(hostname) 변경"
description: "Ubuntu에서 hostnamectl 명령어로 호스트 이름(hostname)을 변경하는 방법"
excerpt: "hostnamectl set-hostname 명령으로 Ubuntu 호스트 이름을 변경하는 방법"
categories: Linux
tags: [Ubuntu, hostname, hostnamectl, 호스트이름변경]
date: 2022-11-02
---

:bulb: 우분투의 호스트 이름(hostname)을 변경하는 방법을 작성한다.
{: .notice--info}

# [01] 호스트 이름 확인

```shell
hostname

# ex
root@gmaster:~# hostname
gmaster
```

# [02] 호스트 이름 변경

```shell
hostnamectl set-hostname ${호스트이름}

# ex
root@gmaster:~# hostnamectl set-hostname gworker01
root@gmaster:~# hostname
gworker01
```

이 후, 터미널을 종료 후 재시작 또는 시스템을 재부팅하면 변경되어 있다.

:small_blue_diamond:참조: [reboot 없이 하는 방법 (askubuntu)](https://askubuntu.com/questions/87665/how-do-i-change-the-hostname-without-a-restart){:target="_blank"}
