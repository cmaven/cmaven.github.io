---
title: "Windows 11에서 WSL로 Ubuntu 22.04 설치 및 구성"
description: "Windows 11에서 WSL2를 활성화하고 Ubuntu 22.04 LTS를 설치하여 Linux 개발 환경을 구성하는 방법"
excerpt: "WSL2 활성화, Ubuntu 22.04 설치, 초기 설정, Windows Terminal 연동까지 Windows 11에서 WSL 기반 Linux 환경 구성 방법 정리"
date: 2026-03-19
categories: Windows
tags: [Windows-11, WSL, WSL2, Ubuntu, Ubuntu-22.04, Linux, 개발환경, Windows-Terminal]
---

:bulb: Windows 11에서 WSL(Windows Subsystem for Linux)을 사용하여 Ubuntu 22.04 LTS를 설치하고 초기 설정하는 방법을 작성한다.
{: .notice--info}

# [01] 요약

| 항목 | 내용 |
|---|---|
| WSL 버전 | WSL2 (권장) |
| 설치 대상 | Ubuntu 22.04 LTS |
| 필요 환경 | Windows 11 (빌드 22000 이상) |
| 소요 시간 | 약 10~15분 |

# [02] WSL 설치

## 2-1. 한 줄 설치 (WSL 미설치 환경)

PowerShell을 **관리자 권한**으로 실행한 후 아래 명령어를 입력한다.

```powershell
wsl --install
```

이 명령어 하나로 아래 항목이 자동 처리된다.

| 항목 | 설명 |
|---|---|
| Virtual Machine Platform | 가상화 플랫폼 기능 활성화 |
| Windows Subsystem for Linux | WSL 기능 활성화 |
| WSL2 커널 | Linux 커널 업데이트 설치 |
| Ubuntu (기본) | 기본 배포판 설치 |

> WSL 기능을 처음 활성화하는 경우 시스템 구성 요소가 변경되므로 **PC 재부팅이 필요**하다. 재부팅 후 Ubuntu 설정이 자동으로 이어진다.
{: .notice--warning}

## 2-2. 배포판 추가 설치 (WSL이 이미 설치된 경우)

WSL이 이미 활성화된 환경에서 Ubuntu 22.04만 추가 설치할 때 사용한다. **재부팅은 필요하지 않다.**

```powershell
# 설치 가능한 배포판 목록 확인
wsl --list --online

# Ubuntu 22.04 설치
wsl --install -d Ubuntu-22.04
```

# [03] WSL 버전 확인 및 설정

## 3-1. WSL 버전 확인

```powershell
wsl -l -v
```

출력 예시:

```
  NAME            STATE           VERSION
* Ubuntu-22.04    Running         2
```

VERSION이 `2`이면 WSL2로 정상 설정된 것이다.

## 3-2. 기본 버전을 WSL2로 설정

```powershell
# 기본 WSL 버전을 2로 설정
wsl --set-default-version 2

# 특정 배포판의 버전 변경
wsl --set-version Ubuntu-22.04 2
```

# [04] Ubuntu 초기 설정

설치 완료 후 Ubuntu를 처음 실행하면 사용자 계정 설정을 요구한다.

```
Enter new UNIX username: 사용자이름
New password: 비밀번호 입력
Retype new password: 비밀번호 재입력
```

## 4-1. 패키지 업데이트

```bash
sudo apt update && sudo apt upgrade -y
```

## 4-2. 한국어 로케일 설정 (선택)

```bash
sudo apt install -y language-pack-ko
sudo update-locale LANG=ko_KR.UTF-8
```

설정 후 WSL을 재시작하면 적용된다.

# [05] WSL 기본 명령어

| 명령어 | 설명 |
|---|---|
| `wsl` | 기본 배포판 실행 |
| `wsl -d Ubuntu-22.04` | 특정 배포판 실행 |
| `wsl -l -v` | 설치된 배포판 목록 및 상태 확인 |
| `wsl --shutdown` | 모든 WSL 인스턴스 종료 |
| `wsl --terminate Ubuntu-22.04` | 특정 배포판 종료 |
| `wsl --update` | WSL 커널 업데이트 |
| `wsl --unregister Ubuntu-22.04` | 배포판 삭제 (데이터 포함) |

# [06] Windows ↔ WSL 파일 접근

## 6-1. WSL에서 Windows 파일 접근

Windows의 C 드라이브는 `/mnt/c`에 마운트된다.

```bash
# Windows 사용자 폴더 접근
cd /mnt/c/Users/사용자이름

# Windows 바탕화면 접근
cd /mnt/c/Users/사용자이름/Desktop
```

## 6-2. Windows에서 WSL 파일 접근

Windows 탐색기 주소창에 아래 경로를 입력한다.

```
\\wsl$\Ubuntu-22.04
```

또는 WSL 터미널에서 아래 명령어로 탐색기를 열 수 있다.

```bash
explorer.exe .
```

# [07] Windows Terminal 연동

Windows 11에는 Windows Terminal이 기본 포함되어 있다. Ubuntu 22.04 설치 후 자동으로 프로필이 추가된다.

- Windows Terminal 실행 → 탭 옆 드롭다운(`∨`) → **Ubuntu 22.04** 선택

## 7-1. 기본 프로필 변경 (선택)

1. Windows Terminal → 설정(`Ctrl + ,`)
2. 시작 → 기본 프로필 → **Ubuntu 22.04** 선택
3. 저장

# [08] WSL 삭제

```powershell
# 배포판 삭제 (모든 데이터 포함)
wsl --unregister Ubuntu-22.04
```

> `--unregister`는 배포판과 내부 데이터를 **모두 삭제**한다. 필요한 데이터는 미리 백업한다.
{: .notice--warning}
