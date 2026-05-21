---
title: "VS Code Terminal — UnauthorizedAccess on Command Execution"
description: "How to resolve UnauthorizedAccess errors when running scripts in the VS Code PowerShell terminal by changing the ExecutionPolicy"
excerpt: "Fix the PowerShell script execution permission error by setting ExecutionPolicy to RemoteSigned"
date: 2022-12-13
categories: VScode
tags: [VSCode, PowerShell, ExecutionPolicy, UnauthorizedAccess, permission-error, Windows, troubleshooting]
ref: Powershell-AuthorizedAccess
---

:bulb: This post explains how to fix the permission error you get when running commands in the Visual Studio Code Terminal (PowerShell).
{: .notice--info}

# [01] The Error

- "Cannot be loaded because running scripts is disabled on this system..."
- Security error, PSSecurityException
- FullyQualifiedErrorID, UnauthorizedAccess

```shell
PS D:\Code\Python> .\.venv-doit-django\Scripts\activate
.\.venv-doit-django\Scripts\activate : 이 시스템에서 스크립트를 실행할 수 없으므로 ...
    + CategoryInfo          : 보안 오류: (:) [], PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess
```

![2022-12-30 16 36 45](https://user-images.githubusercontent.com/76153041/210055346-6e9599f6-b157-433f-9ca5-2c399580a6ec.png)

# [02] Cause and Solution

- `PowerShell` is configured by default to disallow running script files.
- Possible values

| Value | Description |
|---|---|
| `Restricted` | default, scripts cannot be run |
| `AllSigned` | only signed (trusted) scripts run |
| `RemoteSigned` | locally created scripts and signed scripts run |
| `Unrestricted` | all scripts can run |
| `ByPass` | all scripts run with no warning or block |
| `Undefined` | no policy set |

## 2-1. On Windows 10

> Search bar → `PowerShell` → Run as Administrator → Change script execution policy

![2022-12-30 16 38 34](https://user-images.githubusercontent.com/76153041/210047358-081a290a-c342-4cec-ac83-cacc327f45ba.png)

```shell
# Check the current policy
get-ExecutionPolicy

# Set the policy (RemoteSigned)
Set-ExecutionPolicy RemoteSigned
```

![2022-12-30 16 40 26](https://user-images.githubusercontent.com/76153041/210047361-49250795-b471-410e-9bce-f0b5d736a761.png)

# [03] Verifying After the Change

- You can confirm that the script file (here, a Python virtual environment) now runs correctly.

![2022-12-30 16 44 13](https://user-images.githubusercontent.com/76153041/210047352-3af31350-b906-4c24-90c6-52876b544dff.png)
