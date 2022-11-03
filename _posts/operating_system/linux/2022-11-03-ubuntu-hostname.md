---
title: "우분투(Linux)에서 호스트 이름(hostname) 변경"
category: Linux
tags: [Ubuntu]
date: 2022-11-02
---

우분투의 호스트 이름 변경
------

### 호스트 이름 확인  
```shell
hostname

# ex
root@gmaster:~# hostname
gmaster
```

### 호스트 이름 변경  
```shell
hostnamectl set-hostname ${호스트이름}

# ex
root@gmaster:~# hostnamectl set-hostname gworker01
root@gmaster:~# hostname
gworker01
```  
- 이 후, 터미널을 종료 후, 재시작 또는 시스템을 재부팅하면 변경되어 있음

> reboot 없이 하는 방법은?
[참조][askutuntu-how do i change the hostname without a restart](https://askubuntu.com/questions/87665/how-do-i-change-the-hostname-without-a-restart){: target="_blank"} 
