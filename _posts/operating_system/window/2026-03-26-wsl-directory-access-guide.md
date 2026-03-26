---
title: "WSL 디렉토리 접근 완전 가이드 — Windows ↔ Ubuntu 파일 공유"
description: "WSL Ubuntu의 파일을 Windows에서 찾는 방법과, 반대로 Ubuntu에서 Windows 파일에 접근하는 양방향 경로 정리"
excerpt: "\\wsl$, /mnt/c 경로부터 네트워크 드라이브 매핑, VS Code 연동까지 WSL 파일 접근 5가지 방법"
date: 2026-03-26
categories: Windows
tags: [WSL, WSL2, 파일접근, 디렉토리, mnt, wsl$, VS-Code, 네트워크드라이브, explorer]
---

:bulb: WSL Ubuntu의 파일을 Windows에서 찾고, 반대로 Ubuntu에서 Windows 파일에 접근하는 양방향 경로와 실전 활용법을 정리한다.
{: .notice--info}

# [01] WSL과 Windows의 파일시스템 구조

WSL을 설치하면 Windows와 Ubuntu는 각자의 파일시스템을 가지면서도 서로 접근할 수 있는 구조가 된다.

```
┌──────────────────────────────────────────────────┐
│ Windows (C:\Users\...)                           │
│                                                  │
│   WSL Ubuntu 파일 접근:                           │
│   \\wsl$\Ubuntu\home\{사용자명}\                  │
│                                                  │
├──────────────────────────────────────────────────┤
│ Ubuntu (WSL)                                     │
│                                                  │
│   Windows 파일 접근:                              │
│   /mnt/c/Users/{윈도우사용자명}/                   │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

# [02] Windows → Ubuntu 파일 접근

## 2-1. 경로 형식

```
\\wsl$\Ubuntu\home\{사용자명}
```

최신 WSL2에서는 아래 경로도 사용 가능하다.

```
\\wsl.localhost\Ubuntu\home\{사용자명}
```

## 2-2. 주요 디렉토리 매핑

| Ubuntu 경로 | Windows에서의 접근 경로 |
|---|---|
| `/home/{사용자}` | `\\wsl$\Ubuntu\home\{사용자}` |
| `/etc` | `\\wsl$\Ubuntu\etc` |
| `/root` | `\\wsl$\Ubuntu\root` |
| `/tmp` | `\\wsl$\Ubuntu\tmp` |

---

# [03] Ubuntu → Windows 파일 접근

Ubuntu에서는 Windows 드라이브가 `/mnt/` 아래에 자동 마운트된다.

| Windows 경로 | Ubuntu에서의 접근 경로 |
|---|---|
| `C:\Users\{사용자}\Desktop` | `/mnt/c/Users/{사용자}/Desktop` |
| `D:\Projects` | `/mnt/d/Projects` |
| `C:\Program Files` | `/mnt/c/Program Files` |

---

# [04] 쉽게 접근하는 5가지 방법

## 4-1. 파일 탐색기 주소창에 직접 입력 (가장 간단)

Windows 파일 탐색기를 열고 주소창에 `\\wsl$`을 입력하면 설치된 모든 WSL 배포판이 폴더로 표시된다.

```
\\wsl$
```

여기서 Ubuntu 폴더를 클릭하면 전체 파일시스템을 탐색할 수 있다.

## 4-2. Ubuntu 터미널에서 탐색기 바로 열기 (가장 빠름)

Ubuntu 쉘에서 원하는 디렉토리로 이동한 뒤 아래 명령어를 실행하면 해당 경로가 Windows 탐색기로 바로 열린다.

```bash
# 현재 디렉토리를 탐색기로 열기
explorer.exe .

# 특정 디렉토리를 탐색기로 열기
explorer.exe /home/kcloud/projects
```

## 4-3. 네트워크 드라이브 매핑 (자주 접근할 때)

자주 접근하는 WSL 경로를 Windows 드라이브 문자에 매핑해 두면 편하다.

1. 파일 탐색기에서 **"이 PC"** 우클릭
2. **"네트워크 드라이브 연결"** 선택
3. 드라이브 문자 선택 (예: `Z:`)
4. 폴더에 `\\wsl$\Ubuntu\home\{사용자명}` 입력
5. **"로그인 시 다시 연결"** 체크

이후 `Z:\`로 바로 Ubuntu 홈 디렉토리에 접근할 수 있다.

## 4-4. VS Code로 바로 열기

VS Code에서 WSL 파일을 편집하는 가장 깔끔한 방법이다.

```bash
# Ubuntu 터미널에서 실행
code .                    # 현재 디렉토리를 VS Code로 열기
code ~/projects/myapp     # 특정 프로젝트 열기
```

VS Code의 Remote - WSL 확장이 자동으로 WSL 환경에 연결된다.

## 4-5. 바로가기 만들기

Windows 바탕화면에 바로가기를 만들어 둘 수도 있다.

1. 바탕화면 우클릭 → **"새로 만들기"** → **"바로 가기"**
2. 위치에 `\\wsl$\Ubuntu\home\{사용자명}` 입력
3. 이름 지정 후 완료

---

# [05] 원격 서버와의 관계

:warning: WSL 디렉토리 공유는 **로컬 WSL 환경**에만 해당한다. WSL Ubuntu에서 SSH로 원격 서버에 접속한 경우, 원격 서버의 파일은 `\\wsl$`로 접근할 수 없다.
{: .notice--warning}

원격 서버 파일을 Windows에서 다루려면 `scp`, `rsync`, 또는 VS Code의 Remote - SSH 확장을 사용해야 한다.

```bash
# 원격 서버에서 로컬로 파일 복사
scp user@10.254.202.91:/home/user/file.txt ~/

# 로컬에서 원격으로 파일 복사
scp ~/file.txt user@10.254.202.91:/home/user/
```

---

# [06] 성능 관련 주의사항

WSL에서 파일 작업 시 성능 차이가 있다.

| 시나리오 | 성능 | 권장 |
|---|---|---|
| Ubuntu 안에서 Ubuntu 파일 작업 | 빠름 | O — 개발 작업은 여기서 |
| Windows에서 `\\wsl$` 통해 접근 | 보통 | O — 파일 확인, 간단한 편집 |
| Ubuntu에서 `/mnt/c/` 통해 Windows 파일 작업 | 느림 | X — 개발 프로젝트를 여기 두지 말 것 |

:bulb: **핵심 원칙:** 개발 프로젝트는 Ubuntu 파일시스템(`/home/{사용자}/` 아래)에 두고, Windows에서 확인이 필요할 때만 `\\wsl$`이나 `explorer.exe .`로 접근하는 것이 가장 효율적이다.
{: .notice--info}

---

# [07] 정리

```bash
# Windows → Ubuntu
\\wsl$\Ubuntu\home\{사용자명}

# Ubuntu → Windows
/mnt/c/Users/{윈도우사용자명}

# Ubuntu에서 탐색기 바로 열기
explorer.exe .
```

WSL의 파일시스템 공유는 양방향이지만, 성능을 위해 **작업은 Ubuntu 안에서, 확인은 Windows에서** 하는 패턴을 권장한다.
