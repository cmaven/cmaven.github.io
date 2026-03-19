---
title: "우분투(Ubuntu)가 데스크탑(Desktop), 서버(Server) 중 어느 버전으로 설치되었는지 확인하기"
description: "설치된 Ubuntu가 Desktop인지 Server인지 확인하는 방법과 운영체제 버전, 커널 버전 확인 명령어"
excerpt: "dpkg -l ubuntu-desktop 명령으로 Ubuntu Desktop/Server 구분 및 운영체제, 커널 버전 확인법"
categories: Linux
tags: [Ubuntu, Desktop, Server, dpkg, uname, 버전확인]
date: 2022-10-27
---

:bulb: 설치된 우분투 버전과 해당 버전이 Ubuntu-Desktop인지, Ubuntu-Server인지 확인하는 방법을 작성한다.
{: .notice--info}

# [01] Ubuntu Desktop / Server 확인

```shell
dpkg -l ubuntu-desktop

# ubuntu-desktop일 경우
root@gedgeworker1:~# dpkg -l ubuntu-desktop
Desired=Unknown/Install/Remove/Purge/Hold
| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
|/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)
||/ Name           Version      Architecture Description
+++-==============-============-============-=================================
ii  ubuntu-desktop 1.450.2      amd64        The Ubuntu desktop system

# ubuntu-server일 경우
root@gedgemaster:~# dpkg -l ubuntu-desktop
dpkg-query: no packages found matching ubuntu-desktop
```

![2022-10-27 13 54 57](https://user-images.githubusercontent.com/76153041/198195538-29a5408f-38b8-4f7a-a365-ac9c6061aaf7.png)

![2022-10-27 13 55 07](https://user-images.githubusercontent.com/76153041/198195542-2f340929-f0a7-404b-828d-aeb6ea75fd71.png)

# [02] 설치된 운영체제 확인

```shell
cat /etc/*release

# 출력 예
root@gedgeworker1:~# cat /etc/*release
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=24.04
DISTRIB_CODENAME=noble
DISTRIB_DESCRIPTION="Ubuntu 24.04.1 LTS"
NAME="Ubuntu"
VERSION="24.04.1 LTS (Noble Numbat)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 24.04.1 LTS"
VERSION_ID="24.04"
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
VERSION_CODENAME=noble
UBUNTU_CODENAME=noble
```

# [03] 설치된 커널 버전 확인

```shell
uname -a

# 출력 예
root@gedgeworker1:~# uname -a
Linux gedgeworker1 5.4.0-125-generic #141-Ubuntu SMP Wed Aug 10 13:42:03 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux
```
