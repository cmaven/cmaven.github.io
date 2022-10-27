---
title: "우분투(Ubuntu)가 데스크탑(Desktop), 서버(Server) 중 어느 버전으로 설치되었는지 확인하기"
category: Linux
tags: [Ubuntu]
date: 2022-10-27
---

설치된 우분투 버전과 해당 버전이 Ubuntu-Desktop 인지, Ubuntu-Server 인지 확인하기
------

### Ubuntu Desktop? Server? 확인방법

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


### (기타) 설치된 운영체제 확인
```shell
cat /etc/*release

# 출력 예
root@gedgeworker1:~# cat /etc/*release
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=20.04
DISTRIB_CODENAME=focal
DISTRIB_DESCRIPTION="Ubuntu 20.04.4 LTS"
NAME="Ubuntu"
VERSION="20.04.4 LTS (Focal Fossa)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 20.04.4 LTS"
VERSION_ID="20.04"
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
VERSION_CODENAME=focal
UBUNTU_CODENAME=focal
```

### (기타) 설치된 커널 버전 확인
```shell
uname -a

# 출력 예
root@gedgeworker1:~# uname -a
Linux gedgeworker1 5.4.0-125-generic #141-Ubuntu SMP Wed Aug 10 13:42:03 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux
```
