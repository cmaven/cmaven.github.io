---
title: "VS Code Terminal — UnauthorizedAccess on Command Execution"
description: "How to resolve UnauthorizedAccess errors when running scripts in the VS Code PowerShell terminal by changing the ExecutionPolicy"
excerpt: "Fix the PowerShell script execution permission error by setting ExecutionPolicy to RemoteSigned"
date: 2022-12-13
last_modified_at: 2026-05-26
categories: VScode
tags: [VSCode, PowerShell, ExecutionPolicy, UnauthorizedAccess, permission-error, Windows, troubleshooting]
ref: Powershell-AuthorizedAccess
---

:bulb: This post explains how to fix the **`UnauthorizedAccess` / `PSSecurityException`** error you get when running scripts (for example, activating a Python virtual environment) in the **Visual Studio Code Terminal (PowerShell)** on Windows. The fix is to change PowerShell's **ExecutionPolicy** — a one-time setting that takes about 30 seconds.
{: .notice--info}

# [01] The Error

When you open a PowerShell terminal in VS Code on Windows and try to run a script file (`.ps1`), an activation script (`activate.ps1` for a Python virtual environment), or any third-party command that ships as a script, PowerShell refuses to execute it and prints something like the following:

- "Cannot be loaded because running scripts is disabled on this system..."
- Security error, `PSSecurityException`
- `FullyQualifiedErrorID`: `UnauthorizedAccess`

```shell
PS D:\Code\Python> .\.venv-doit-django\Scripts\activate
.\.venv-doit-django\Scripts\activate : File ...\activate.ps1 cannot be loaded
because running scripts is disabled on this system.
For more information, see about_Execution_Policies at
https://go.microsoft.com/fwlink/?LinkID=135170.
    + CategoryInfo          : SecurityError: (:) [], PSSecurityException
    + FullyQualifiedErrorId : UnauthorizedAccess
```

> The same Korean-locale Windows installation shows:
> `이 시스템에서 스크립트를 실행할 수 없으므로 ...` / `보안 오류: (:) [], PSSecurityException`.
> The cause and fix are identical regardless of OS display language.

![2022-12-30 16 36 45 - PowerShell UnauthorizedAccess error in VS Code terminal](https://user-images.githubusercontent.com/76153041/210055346-6e9599f6-b157-433f-9ca5-2c399580a6ec.png)

*Figure 1. The `UnauthorizedAccess` error fires when PowerShell refuses to execute `activate.ps1` for a Python virtual environment.*

# [02] Cause and Solution

`PowerShell` is configured by default to **disallow running script files** as a security precaution against accidentally executing untrusted `.ps1` files downloaded from the internet. The setting that controls this is called **`ExecutionPolicy`**.

There are six possible values for `ExecutionPolicy`. Pick one based on how strict you want PowerShell to be:

| Value | Description |
|---|---|
| `Restricted` | **Default on Windows clients.** No scripts can be run at all — only interactive commands. |
| `AllSigned` | Only scripts signed by a trusted publisher will run. Prompts on every signed script you have not already trusted. |
| `RemoteSigned` | **Recommended for developers.** Scripts created **locally** run without a signature; scripts **downloaded from the internet** must be signed. |
| `Unrestricted` | All scripts can run. PowerShell warns once before running an internet-downloaded script. |
| `Bypass` | All scripts run with no warnings or prompts. Avoid unless you know exactly what you are doing (CI agents, automated installers). |
| `Undefined` | No policy is set at this scope. PowerShell falls back to the next-higher scope (`MachinePolicy`, `UserPolicy`, etc.). |

For day-to-day development work — running Python venv activation, build scripts, package installers — **`RemoteSigned`** is the right balance: your own scripts run freely, but anything downloaded from the internet still needs a signature.

## 2-1. On Windows 10 / 11

> Search bar → `PowerShell` → **Run as Administrator** → change the script execution policy.

Administrator privileges are required because the policy change applies at the **`LocalMachine`** scope (the default scope of `Set-ExecutionPolicy`).

![2022-12-30 16 38 34 - opening PowerShell as Administrator from Start menu](https://user-images.githubusercontent.com/76153041/210047358-081a290a-c342-4cec-ac83-cacc327f45ba.png)

*Figure 2. Right-click PowerShell in the Start menu and choose **Run as Administrator**. Without admin rights, `Set-ExecutionPolicy` will fail with an access-denied error.*

```shell
# Check the current policy
Get-ExecutionPolicy

# Set the policy (RemoteSigned)
Set-ExecutionPolicy RemoteSigned
```

PowerShell prompts you to confirm the change. Press `Y` (or `A` for "Yes to All") to apply it.

![2022-12-30 16 40 26 - running Set-ExecutionPolicy RemoteSigned in elevated PowerShell](https://user-images.githubusercontent.com/76153041/210047361-49250795-b471-410e-9bce-f0b5d736a761.png)

*Figure 3. `Get-ExecutionPolicy` shows the current setting; `Set-ExecutionPolicy RemoteSigned` changes it. The new value persists across reboots and applies to every PowerShell session, including the one embedded in VS Code.*

## 2-2. Per-User Alternative (No Admin Required)

If you cannot run PowerShell as Administrator (corporate-managed laptop, shared workstation), apply the policy only to your own user account using the `-Scope CurrentUser` flag — no elevation needed:

```shell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

This affects only **your** PowerShell sessions and survives without touching the machine-wide policy.

# [03] Verifying After the Change

Reopen the VS Code terminal (or run a new PowerShell tab inside it) and re-run the script that originally failed. You can confirm that the script file — here, a Python virtual environment activation — now runs correctly and the shell prompt is prefixed with the venv name (`(.venv-doit-django)`).

![2022-12-30 16 44 13 - Python venv activation now succeeds after policy change](https://user-images.githubusercontent.com/76153041/210047352-3af31350-b906-4c24-90c6-52876b544dff.png)

*Figure 4. After `Set-ExecutionPolicy RemoteSigned`, `activate.ps1` runs successfully and the venv prefix appears in the prompt.*

# [04] Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Set-ExecutionPolicy` itself returns access-denied | PowerShell not running as Administrator | Close PowerShell, right-click → **Run as Administrator**, retry. Or use `-Scope CurrentUser`. |
| Policy change "succeeded" but the error still appears | Group Policy is overriding the local policy | Run `Get-ExecutionPolicy -List` to see all scopes; if `MachinePolicy` or `UserPolicy` shows a value, contact IT. |
| VS Code's integrated terminal still blocks scripts | VS Code is using a different shell or a different PowerShell version | Open Command Palette → **Terminal: Select Default Profile** → pick the same PowerShell you configured. |
| Error returns after an OS update | Policy preserved, but profile script is missing | Confirm with `Get-ExecutionPolicy` — if the value reset, re-apply `Set-ExecutionPolicy RemoteSigned`. |

# [05] Security Note

`RemoteSigned` is safe for normal development work because it still rejects unsigned scripts downloaded from the internet (the `Zone.Identifier` alternate data stream marks them as remote). If you ever need to run a specific downloaded `.ps1` once, unblock just that file with `Unblock-File path\to\script.ps1` instead of weakening the global policy to `Unrestricted` or `Bypass`.
