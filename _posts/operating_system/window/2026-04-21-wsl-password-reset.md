---
title: "WSL 비밀번호 재설정 방법 (Windows 11)"
description: "WSL에서 사용자 비밀번호를 잊어버렸을 때 root 계정으로 접속하여 비밀번호를 재설정하는 방법"
excerpt: "wsl -u root로 root 접속 후 passwd 명령어로 비밀번호 재설정하기"
date: 2026-04-21
categories: Windows
tags: [WSL, Ubuntu, 비밀번호, passwd, root, Windows11, 비밀번호재설정]
---

:bulb: WSL에서 사용자 비밀번호를 잊어버린 경우, root 계정으로 접속하여 비밀번호를 재설정하는 방법을 정리한다.
{: .notice--info}

---

# [01] root 사용자로 WSL 실행

PowerShell 또는 CMD에서 아래 명령어를 실행한다.

```powershell
wsl -u root
```

특정 배포판을 지정해야 하는 경우:

```powershell
wsl -d Ubuntu-22.04 -u root
```

| 옵션 | 설명 |
|------|------|
| `-u root` | root 사용자로 접속 (비밀번호 불필요) |
| `-d Ubuntu-22.04` | 특정 배포판 지정 |

---

# [02] 사용자 목록 확인 (선택)

어떤 사용자 계정이 있는지 확인할 수 있다.

```bash
cat /etc/passwd | grep -E ":/home/"
```

```
cha:x:1000:1000::/home/cha:/bin/bash
```

일반적으로 UID 1000번이 최초 생성한 사용자이다.

---

# [03] 비밀번호 재설정

```bash
passwd 사용자이름
```

예시:

```bash
passwd cha
```

```
New password:
Retype new password:
passwd: password updated successfully
```

:bulb: root 계정에서 실행하면 **기존 비밀번호 입력 없이** 바로 새 비밀번호를 설정할 수 있다.
{: .notice--info}

---

# [04] 변경 확인 후 종료

```bash
exit
```

이후 일반 사용자로 WSL에 접속하여 새 비밀번호가 적용되었는지 확인한다.

```powershell
wsl
```

---

# [05] 트러블슈팅

## 5-1. wsl -u root 실행이 안 되는 경우

**관리자 권한 PowerShell**로 실행한다.

```powershell
# PowerShell을 관리자 권한으로 열고
wsl -u root
```

## 5-2. 배포판 이름을 모르는 경우

```powershell
wsl -l -v
```

```
  NAME            STATE           VERSION
* Ubuntu-22.04    Running         2
  Ubuntu-20.04    Stopped         2
```

`*` 표시가 기본 배포판이다.

---

# [06] 정리

| 단계 | 명령어 |
|------|--------|
| root 접속 | `wsl -u root` |
| 사용자 확인 | `cat /etc/passwd \| grep :/home/` |
| 비밀번호 변경 | `passwd 사용자이름` |
| 종료 | `exit` |

:bulb: WSL에는 기본 비밀번호가 존재하지 않는다. 최초 설치 시 사용자가 직접 설정하며, root 계정에서는 기존 비밀번호 없이 변경 가능하다.
{: .notice--info}
