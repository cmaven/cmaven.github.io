---
title: "WSL 삭제 방법 — 배포판 제거부터 전체 초기화까지 (Windows 11)"
description: "WSL에서 특정 Linux 배포판 삭제, WSL 기능 자체 제거, 완전 초기화 후 재설치하는 방법 정리"
excerpt: "wsl --unregister로 배포판 삭제, wsl --uninstall로 전체 제거, Windows 기능에서 WSL 비활성화까지"
date: 2026-04-21
categories: Windows
tags: [WSL, Ubuntu, 삭제, unregister, uninstall, Windows11, 초기화, 재설치]
---

:bulb: WSL 삭제는 특정 배포판만 삭제하는 것과 WSL 기능 자체를 제거하는 것으로 구분된다. 각 방법을 정리한다.
{: .notice--info}

---

# [01] 설치된 배포판 확인

삭제 전에 현재 설치된 배포판을 확인한다.

```powershell
wsl -l -v
```

```
  NAME            STATE           VERSION
* Ubuntu-22.04    Running         2
  Ubuntu-20.04    Stopped         2
```

---

# [02] 특정 배포판 삭제

```powershell
wsl --unregister Ubuntu-22.04
```

:warning: 해당 배포판의 **모든 데이터(파일, 설정, 사용자 정보)가 삭제**된다. 필요한 데이터는 미리 백업한다.
{: .notice--warning}

삭제 확인:

```powershell
wsl -l -v
```

삭제된 배포판이 목록에서 사라졌으면 성공이다.

---

# [03] WSL 전체 제거

## 3-1. 방법 1: PowerShell 사용

```powershell
wsl --uninstall
```

## 3-2. 방법 2: Windows 기능에서 제거

1. `Win + R` → `optionalfeatures` 입력 → 실행
2. 아래 항목의 체크를 해제한다:
   - **Windows Subsystem for Linux**
   - **Virtual Machine Platform**
3. **확인** 클릭 후 시스템 재부팅

| 항목 | 설명 |
|------|------|
| Windows Subsystem for Linux | WSL 핵심 기능 |
| Virtual Machine Platform | WSL 2의 가상화 기반 |

---

# [04] 완전 초기화 후 재설치

기존 배포판을 완전히 삭제하고 새로 설치하는 경우:

```powershell
# 1. 기존 배포판 삭제
wsl --unregister Ubuntu

# 2. 새로 설치
wsl --install
```

특정 버전으로 재설치:

```powershell
wsl --install -d Ubuntu-22.04
```

---

# [05] 정리

| 작업 | 명령어 | 범위 |
|------|--------|------|
| 배포판 목록 확인 | `wsl -l -v` | 조회 |
| 특정 배포판 삭제 | `wsl --unregister Ubuntu-22.04` | 해당 배포판만 |
| WSL 전체 제거 | `wsl --uninstall` | WSL 기능 전체 |
| 초기화 후 재설치 | `wsl --unregister` → `wsl --install` | 완전 초기화 |

:bulb: Microsoft Store에서 설치한 Ubuntu는 앱 제거로도 삭제할 수 있지만, `wsl --unregister` 방식이 더 확실하다.
{: .notice--info}
