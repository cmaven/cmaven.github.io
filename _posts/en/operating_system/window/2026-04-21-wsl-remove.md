---
title: "How to Remove WSL - From Deleting a Distribution to a Full Reset (Windows 11)"
description: "How to delete a specific Linux distribution from WSL, uninstall the WSL feature itself, or perform a full reset and reinstall"
excerpt: "Use wsl --unregister to delete a distribution, wsl --uninstall to remove WSL entirely, or disable WSL from Windows Features"
date: 2026-04-21
categories: Windows
tags: [WSL, Ubuntu, remove, unregister, uninstall, Windows11, reset, reinstall]
ref: wsl-remove
---

:bulb: Removing WSL is split into two cases: deleting a specific distribution, and removing the WSL feature itself. This guide covers both.
{: .notice--info}

---

# [01] Check Installed Distributions

Before removing, confirm which distributions are currently installed.

```powershell
wsl -l -v
```

```
  NAME            STATE           VERSION
* Ubuntu-22.04    Running         2
  Ubuntu-20.04    Stopped         2
```

---

# [02] Delete a Specific Distribution

```powershell
wsl --unregister Ubuntu-22.04
```

:warning: **All data (files, settings, user information)** for that distribution is deleted. Back up anything you need beforehand.
{: .notice--warning}

Verify the deletion:

```powershell
wsl -l -v
```

If the deleted distribution is no longer listed, it was removed successfully.

---

# [03] Remove WSL Entirely

## 3-1. Method 1: Using PowerShell

```powershell
wsl --uninstall
```

## 3-2. Method 2: Remove via Windows Features

1. `Win + R` -> type `optionalfeatures` -> Run
2. Uncheck the following items:
   - **Windows Subsystem for Linux**
   - **Virtual Machine Platform**
3. Click **OK** and reboot the system

| Item | Description |
|------|------|
| Windows Subsystem for Linux | Core WSL functionality |
| Virtual Machine Platform | Virtualization base for WSL 2 |

---

# [04] Full Reset and Reinstall

To completely wipe an existing distribution and install it fresh:

```powershell
# 1. Remove the existing distribution
wsl --unregister Ubuntu

# 2. Install fresh
wsl --install
```

Reinstall a specific version:

```powershell
wsl --install -d Ubuntu-22.04
```

---

# [05] Summary

| Task | Command | Scope |
|------|--------|------|
| List distributions | `wsl -l -v` | Query |
| Delete a specific distribution | `wsl --unregister Ubuntu-22.04` | That distribution only |
| Remove WSL entirely | `wsl --uninstall` | The entire WSL feature |
| Full reset and reinstall | `wsl --unregister` -> `wsl --install` | Complete reset |

:bulb: Ubuntu installed from the Microsoft Store can be uninstalled like a regular app, but `wsl --unregister` is the more reliable method.
{: .notice--info}
