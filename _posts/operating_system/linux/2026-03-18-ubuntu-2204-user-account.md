---
title: "Ubuntu 22.04 사용자 계정 생성 및 관리"
description: "Ubuntu 22.04에서 adduser 명령어로 사용자 계정을 생성하고, sudo 권한 부여 및 계정 삭제하는 방법"
excerpt: "Ubuntu 22.04 LTS에서 adduser를 이용한 사용자 계정 생성, sudo 그룹 추가를 통한 관리자 권한 부여, 계정 삭제까지 사용자 관리 방법 정리"
date: 2026-03-18
categories: Linux
tags: [Ubuntu, Ubuntu-22.04, adduser, useradd, deluser, sudo, 사용자계정, 계정생성, 계정삭제, 사용자관리]
---

:bulb: Ubuntu 환경에서 새로운 사용자 계정을 생성하고, 관리자 권한을 부여하며, 계정을 삭제하는 방법을 작성한다. Ubuntu Server와 Desktop 모두에 적용 가능하다.
{: .notice--info}

# [01] 요약

| 항목 | 내용 |
|---|---|
| 사용자 생성 | `adduser` 또는 `useradd` 명령어 사용 |
| 홈 디렉토리 | `adduser` 사용 시 `/home/사용자이름` 자동 생성 |
| 관리자 권한 | `sudo` 그룹에 추가하여 부여 |
| 권한 확인 | `groups` 또는 `sudo whoami` 명령어로 확인 |

# [02] 사용자 생성

`adduser` 명령어를 사용하면 홈 디렉토리 생성, 기본 쉘 설정, 비밀번호 설정까지 한 번에 처리된다.

```bash
sudo adduser 사용자이름
```

실행 시 아래 항목이 자동으로 처리된다.

| 항목 | 설명 |
|---|---|
| 홈 디렉토리 | `/home/사용자이름` 자동 생성 |
| 기본 쉘 | `/bin/bash` 설정 |
| 그룹 | 사용자 이름과 동일한 그룹 자동 생성 |
| 비밀번호 | 설정 프롬프트 출력 |

> `useradd`는 홈 디렉토리를 자동으로 생성하지 않으므로, 일반적인 사용자 생성에는 `adduser`를 권장한다.
{: .notice--warning}

# [03] 관리자 권한 부여

생성한 사용자에게 `sudo` 권한을 부여하려면 `sudo` 그룹에 추가한다.

```bash
sudo usermod -aG sudo 사용자계정
```

| 옵션 | 설명 |
|---|---|
| `-a` | 기존 그룹을 유지하면서 추가 (append) |
| `-G` | 추가할 그룹 지정 |

# [04] 권한 및 생성 확인

## 4-1. 홈 디렉토리 확인

```bash
ls -ld /home/사용자계정
```

## 4-2. 그룹 확인

```bash
groups 사용자이름
```

출력 예시:
```
사용자이름 : 사용자이름 sudo
```

`sudo`가 포함되어 있으면 관리자 권한이 정상적으로 부여된 것이다.

## 4-3. sudo 권한 동작 확인

해당 사용자로 전환 후 확인한다.

```bash
su - 사용자이름
sudo whoami
```

`root`가 출력되면 정상이다.

# [05] 사용자 삭제

```bash
# 사용자만 삭제 (홈 디렉토리 유지)
sudo deluser 사용자이름

# 홈 디렉토리 포함 삭제
sudo deluser --remove-home 사용자이름
```

| 명령어 | 설명 |
|---|---|
| `deluser 사용자이름` | 계정만 삭제, `/home/사용자이름` 디렉토리는 유지 |
| `deluser --remove-home 사용자이름` | 계정과 홈 디렉토리 모두 삭제 |

:small_blue_diamond:참조: [https://cmaven.tistory.com/12](https://cmaven.tistory.com/12){:target="_blank"}
