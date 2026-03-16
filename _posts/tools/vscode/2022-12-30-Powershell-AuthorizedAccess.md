---
title: "VS Code 터미널 명령 실행 시, UnauthorizedAccess"
description: "VS Code PowerShell 터미널에서 스크립트 실행 시 UnauthorizedAccess 오류를 ExecutionPolicy 변경으로 해결하는 방법"
excerpt: "PowerShell ExecutionPolicy를 RemoteSigned로 변경하여 스크립트 실행 권한 오류 해결하기"
date: 2022-12-13
categories: VScode
tags: [VSCode, PowerShell, ExecutionPolicy, UnauthorizedAccess, 권한오류, Windows, troubleshooting]
---

:bulb: Visual Studio Code의 Terminal(PowerShell)에서 명령어 실행 시, 권한 오류 해결 방법을 작성한다.
{: .notice--info}

# [01] 오류

- 이 시스템에서 스크립트를 실행할 수 없으므로..
- 보안 오류, PSSecurityException
- FullyQualifiedErrorID, UnauthorizedAccess

```shell
PS D:\Code\Python> .\.venv-doit-django\Scripts\activate
.\.venv-doit-django\Scripts\activate : 이 시스템에서 스크립트를 실행할 수 없으므로 ...
    + CategoryInfo          : 보안 오류: (:) [], PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess
```

![2022-12-30 16 36 45](https://user-images.githubusercontent.com/76153041/210055346-6e9599f6-b157-433f-9ca5-2c399580a6ec.png)

# [02] 원인 및 해결방안

- `PowerShell`은 Script 파일을 실행할 수 없도록 기본 설정되어 있다.
- 설정 가능한 값

| 값 | 설명 |
|---|---|
| `Restricted` | default, Script 파일 실행 불가 |
| `AllSigned` | 서명된(승인된) Script 파일만 실행 |
| `RemoteSigned` | 현 시스템에서 사용자가 생성한 Script와 서명된 Script 파일만 실행 |
| `Unrestricted` | 모든 Script 파일 실행 가능 |
| `ByPass` | 경고 및 차단 없이 모든 Script 파일 실행 |
| `Undefined` | 권한 설정 안함 |

## 2-1. Windows 10 경우

> 검색창 → `PowerShell` → 관리자 권한 실행 → Script 실행 권한 변경

![2022-12-30 16 38 34](https://user-images.githubusercontent.com/76153041/210047358-081a290a-c342-4cec-ac83-cacc327f45ba.png)

```shell
# 현재 권한 확인
get-ExecutionPolicy

# 권한 설정(RemoteSigned)
Set-ExecutionPolicy RemoteSigned
```

![2022-12-30 16 40 26](https://user-images.githubusercontent.com/76153041/210047361-49250795-b471-410e-9bce-f0b5d736a761.png)

# [03] 변경 후, 실행 확인

- Script 파일 (여기에선 Python 가상환경)이 정상 동작하는 것을 확인할 수 있다.

![2022-12-30 16 44 13](https://user-images.githubusercontent.com/76153041/210047352-3af31350-b906-4c24-90c6-52876b544dff.png)
