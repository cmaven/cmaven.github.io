---
title: "WSL에 특정 Ubuntu 버전 설치하기 (Windows 11)"
description: "WSL에서 Ubuntu 20.04, 22.04, 24.04 등 특정 버전을 선택하여 설치하고 기본 배포판으로 설정하는 방법"
excerpt: "wsl --install -d Ubuntu-22.04로 원하는 버전 설치, 기본 배포판 설정, Microsoft Store 대안까지"
date: 2026-04-21
categories: Windows
tags: [WSL, Ubuntu, 설치, wsl-install, Windows11, Ubuntu-22.04, Ubuntu-24.04, 배포판]
---

:bulb: WSL에서 여러 Ubuntu 버전을 선택하여 설치하고, 기본 배포판을 설정하는 방법을 정리한다.
{: .notice--info}

---

# [01] 설치 가능한 배포판 확인

```powershell
wsl --list --online
```

```
NAME                  FRIENDLY NAME
Ubuntu                Ubuntu
Ubuntu-20.04          Ubuntu 20.04 LTS
Ubuntu-22.04          Ubuntu 22.04 LTS
Ubuntu-24.04          Ubuntu 24.04 LTS
Debian                Debian GNU/Linux
...
```

---

# [02] 특정 Ubuntu 버전 설치

```powershell
wsl --install -d Ubuntu-22.04
```

다른 버전 예시:

```powershell
wsl --install -d Ubuntu-20.04
wsl --install -d Ubuntu-24.04
```

기본 Ubuntu(최신 LTS) 설치:

```powershell
wsl --install -d Ubuntu
```

| 버전 | 특징 |
|------|------|
| Ubuntu-20.04 | 안정성 중심, 레거시 환경 |
| Ubuntu-22.04 | 표준 (권장) |
| Ubuntu-24.04 | 최신 환경 |

---

# [03] 설치 후 초기 설정

설치가 완료되면 자동으로 배포판이 실행되며, 아래 항목을 설정한다.

```
Enter new UNIX username: cha
New password:
Retype new password:
```

| 항목 | 설명 |
|------|------|
| 사용자 이름 | 영문 소문자 (sudo 권한 자동 부여) |
| 비밀번호 | `sudo` 실행 시 입력하는 비밀번호 |

---

# [04] 설치된 배포판 확인

```powershell
wsl -l -v
```

```
  NAME            STATE           VERSION
* Ubuntu-22.04    Running         2
  Ubuntu-20.04    Stopped         2
```

| 표시 | 의미 |
|------|------|
| `*` | 기본 배포판 |
| STATE `Running` | 현재 실행 중 |
| VERSION `2` | WSL 2 사용 중 |

---

# [05] 특정 배포판 실행

```powershell
wsl -d Ubuntu-22.04
```

여러 배포판이 설치된 경우, `-d` 옵션으로 원하는 배포판을 지정하여 실행한다.

---

# [06] 기본 배포판 설정

```powershell
wsl --set-default Ubuntu-22.04
```

이후 `wsl` 명령만 입력하면 지정한 배포판이 실행된다.

---

# [07] Microsoft Store로 설치 (대안)

명령어 대신 GUI로 설치할 수도 있다.

1. **Microsoft Store** 실행
2. **"Ubuntu 22.04"** 검색
3. 원하는 버전 선택 → **설치**

:bulb: 명령어 방식(`wsl --install -d`)과 Microsoft Store 방식 모두 동일한 결과이다. 명령어 방식이 더 빠르고 자동화에 유리하다.
{: .notice--info}

---

# [08] 트러블슈팅

## 8-1. 설치 오류 발생 시

**BIOS에서 가상화(Virtualization)가 비활성화**되어 있을 수 있다.

1. PC 재시작 → BIOS 진입 (F2, DEL 등)
2. **Intel VT-x** 또는 **AMD-V** 항목 활성화
3. 저장 후 재부팅

## 8-2. WSL 상태 확인

```powershell
wsl --status
```

```
Default Version: 2
WSL version: 2.x.x
Kernel version: 5.x.x
```

## 8-3. WSL 업데이트

```powershell
wsl --update
```

---

# [09] 정리

| 작업 | 명령어 |
|------|--------|
| 설치 가능 목록 | `wsl --list --online` |
| 특정 버전 설치 | `wsl --install -d Ubuntu-22.04` |
| 배포판 목록 확인 | `wsl -l -v` |
| 특정 배포판 실행 | `wsl -d Ubuntu-22.04` |
| 기본 배포판 설정 | `wsl --set-default Ubuntu-22.04` |
| WSL 상태 확인 | `wsl --status` |
| WSL 업데이트 | `wsl --update` |
