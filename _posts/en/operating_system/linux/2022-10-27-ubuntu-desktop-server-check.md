---
title: "How to Tell If Ubuntu Is Desktop or Server"
description: "Commands to check whether the installed Ubuntu is Desktop or Server, plus how to check OS and kernel versions"
excerpt: "Use dpkg -l ubuntu-desktop to distinguish Ubuntu Desktop from Server, and inspect the OS and kernel versions"
categories: Linux
tags: [Ubuntu, Desktop, Server, dpkg, uname, version-check]
date: 2022-10-27
ref: ubuntu-desktop-server-check
---

:bulb: This post describes how to check the installed Ubuntu version and whether it is Ubuntu Desktop or Ubuntu Server.
{: .notice--info}

# [01] Check Ubuntu Desktop vs. Server

```shell
dpkg -l ubuntu-desktop

# When it is ubuntu-desktop
root@gedgeworker1:~# dpkg -l ubuntu-desktop
Desired=Unknown/Install/Remove/Purge/Hold
| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
|/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)
||/ Name           Version      Architecture Description
+++-==============-============-============-=================================
ii  ubuntu-desktop 1.450.2      amd64        The Ubuntu desktop system

# When it is ubuntu-server
root@gedgemaster:~# dpkg -l ubuntu-desktop
dpkg-query: no packages found matching ubuntu-desktop
```

![2022-10-27 13 54 57](https://user-images.githubusercontent.com/76153041/198195538-29a5408f-38b8-4f7a-a365-ac9c6061aaf7.png)

![2022-10-27 13 55 07](https://user-images.githubusercontent.com/76153041/198195542-2f340929-f0a7-404b-828d-aeb6ea75fd71.png)

# [02] Check the Installed OS

```shell
cat /etc/*release

# Sample output
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

# [03] Check the Kernel Version

```shell
uname -a

# Sample output
root@gedgeworker1:~# uname -a
Linux gedgeworker1 5.4.0-125-generic #141-Ubuntu SMP Wed Aug 10 13:42:03 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux
```
