---
title: "VS Code 터미널 명령 실행 시, UnauthorizedAccess"
date: 2022-12-13 12:00
categories: VScode
tags: [Powershell]
---

Visual Studio Code의 Terminal(Powershell)에서 명령어 실행 시, 권한 오류 해결 방법

------

### 오류 
- 이 시스템에서 스크립트를 실행할 수 없으므로..
- 보안 오류, PSSecurityException
- FullyQualifiedErrorID, UnauthorizedAccess

```shell
PS D:\Code\Python> .\.venv-doit-django\Scripts\activate
.\.venv-doit-django\Scripts\activate : 이 시스템에서 스크립트를 실행할 수 없으므로 D:\Code\Python\.venv-doit-django\Scdjango\Scripts\                                                                                              k/?LinkID
Activate.ps1 파일을 로드할 수 없습니다. 자세한 내용은 about_Execution_Policies(https://go.microsoft.com/fwlink/?LinkID=13517
0)를 참조하십시오.
위치 줄:1 문자:1
+ .\.venv-doit-django\Scripts\activate
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : 보안 오류: (:) [], PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess
```  

![2022-12-30 16 36 45](https://user-images.githubusercontent.com/76153041/210055346-6e9599f6-b157-433f-9ca5-2c399580a6ec.png)

### 원인 및 해결방안  
- `Powershell`은 Script 파일을 실행할 수 없도록 기본 설정되어 있다.
- 설정 가능한 값
  - `Restricted`: default, Script 파일 실행 불가
  - `AllSigned`: 서명된(승인된) Script 파일만 실행
  - `RemoteSigned`: 현 시스템에서 사용자가 생성한 Script와 서명된(승인된) Script 파일만 실행
  - `Unrestricted`: 모든 Script 파일 실행 가능
  - `ByPass`: 경고 및 차단 없이 모든 Script 파일 실행
  - `Undefined`: 권한 설정 안함

#### Windows 10 경우
> 검색창 → `Powershell` → 관리자 권한 실행 → Script 실행 권한 변경  


![2022-12-30 16 38 34](https://user-images.githubusercontent.com/76153041/210047358-081a290a-c342-4cec-ac83-cacc327f45ba.png)   

```shell
# 현재 권한 확인
get-ExecutionPolicy

# 권한 설정(RemoteSigned)
Set-ExecutionPolicy RemoteSigned

# ex)
Windows PowerShell
Copyright (C) Microsoft Corporation. All rights reserved.

새로운 크로스 플랫폼 PowerShell 사용 https://aka.ms/pscore6

PS C:\Windows\system32> get-ExecutionPolicy
Restricted
PS C:\Windows\system32> Set-ExecutionPolicy RemoteSigned

실행 규칙 변경
실행 정책은 신뢰하지 않는 스크립트로부터 사용자를 보호합니다. 실행 정책을 변경하면 about_Execution_Policies 도움말
항목(https://go.microsoft.com/fwlink/?LinkID=135170)에 설명된 보안 위험에 노출될 수 있습니다. 실행 정책을
변경하시겠습니까?
[Y] 예(Y)  [A] 모두 예(A)  [N] 아니요(N)  [L] 모두 아니요(L)  [S] 일시 중단(S)  [?] 도움말 (기본값은 "N"): y
PS C:\Windows\system32> get-ExecutionPolicy
RemoteSigned
```  


![2022-12-30 16 40 26](https://user-images.githubusercontent.com/76153041/210047361-49250795-b471-410e-9bce-f0b5d736a761.png)  

### 변경 후, 실행 확인
- Script 파일 (여기에선 Python 가상환경)이 정상 동작하는 것을 확인할 수 있다.  

![2022-12-30 16 44 13](https://user-images.githubusercontent.com/76153041/210047352-3af31350-b906-4c24-90c6-52876b544dff.png)  
