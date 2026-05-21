---
title: "Installing and Configuring Ubuntu on WSL (Windows 11)"
description: "How to enable WSL2 on Windows 11 and install Ubuntu to set up a Linux development environment"
excerpt: "Enable WSL2, install Ubuntu, perform initial setup, and integrate with Windows Terminal to build a WSL-based Linux environment on Windows 11"
date: 2026-03-19
categories: Windows
tags: [Windows-11, WSL, WSL2, Ubuntu, Linux, dev-environment, Windows-Terminal]
ref: windows11-wsl-ubuntu
---

:bulb: This guide covers how to install Ubuntu using WSL (Windows Subsystem for Linux) on Windows 11 and perform initial configuration.
{: .notice--info}

# [01] Summary

| Item | Details |
|---|---|
| WSL version | WSL2 (recommended) |
| Target | Ubuntu (latest LTS) |
| Requirements | Windows 11 (build 22000 or later) |
| Estimated time | About 10-15 minutes |

# [02] Installing WSL

## 2-1. One-line install (when WSL is not installed)

Open PowerShell as **Administrator** and run the following command.

```powershell
wsl --install
```

This single command automatically handles the following items.

| Item | Description |
|---|---|
| Virtual Machine Platform | Enables the virtualization platform feature |
| Windows Subsystem for Linux | Enables the WSL feature |
| WSL2 kernel | Installs the Linux kernel update |
| Ubuntu (default) | Installs the default distribution |

> When enabling WSL for the first time, system components change, so **a PC reboot is required**. After the reboot, Ubuntu setup continues automatically.
{: .notice--warning}

## 2-2. Installing a specific distribution (when WSL is already installed)

Use this when WSL is already enabled and you want to add Ubuntu. **No reboot is required.**

```powershell
# List available distributions
wsl --list --online
```

Example output:

```
NAME                   FRIENDLY NAME
Ubuntu                 Ubuntu
Ubuntu-24.04           Ubuntu 24.04 LTS
Ubuntu-22.04           Ubuntu 22.04 LTS
Debian                 Debian GNU/Linux
...
```

Install the latest stable version.

```powershell
# Install the latest Ubuntu LTS
wsl --install -d Ubuntu
```

> `wsl --install -d Ubuntu` automatically installs the latest LTS version. If you need a specific version, specify it like `Ubuntu-24.04`.
{: .notice--info}

# [03] Checking and Setting the WSL Version

## 3-1. Check the WSL version

```powershell
wsl -l -v
```

Example output:

```
  NAME            STATE           VERSION
* Ubuntu          Running         2
```

If VERSION shows `2`, WSL2 is configured correctly.

## 3-2. Set the default version to WSL2

```powershell
# Set default WSL version to 2
wsl --set-default-version 2

# Change the version of a specific distribution
wsl --set-version Ubuntu 2
```

# [04] Initial Ubuntu Setup

After installation completes, the first run of Ubuntu prompts for user account setup.

```
Enter new UNIX username: username
New password: password
Retype new password: password again
```

## 4-1. Update packages

```bash
sudo apt update && sudo apt upgrade -y
```

## 4-2. Set locale (optional)

```bash
sudo apt install -y language-pack-en
sudo update-locale LANG=en_US.UTF-8
```

Restart WSL to apply the changes.

# [05] Basic WSL Commands

| Command | Description |
|---|---|
| `wsl` | Run the default distribution |
| `wsl -d Ubuntu` | Run a specific distribution |
| `wsl -l -v` | List installed distributions and their state |
| `wsl --shutdown` | Shut down all WSL instances |
| `wsl --terminate Ubuntu` | Terminate a specific distribution |
| `wsl --update` | Update the WSL kernel |
| `wsl --unregister Ubuntu` | Delete a distribution (including data) |

# [06] Windows <-> WSL File Access

## 6-1. Access Windows files from WSL

The Windows C drive is mounted at `/mnt/c`.

```bash
# Access the Windows user folder
cd /mnt/c/Users/username

# Access the Windows desktop
cd /mnt/c/Users/username/Desktop
```

## 6-2. Access WSL files from Windows

Enter the following path in the Windows File Explorer address bar.

```
\\wsl$\Ubuntu
```

Or open Explorer directly from a WSL terminal:

```bash
explorer.exe .
```

# [07] Windows Terminal Integration

Windows 11 ships with Windows Terminal preinstalled. After installing Ubuntu, a profile is automatically added.

- Launch Windows Terminal -> dropdown next to the tab (`v`) -> select **Ubuntu**

## 7-1. Change the default profile (optional)

1. Windows Terminal -> Settings (`Ctrl + ,`)
2. Startup -> Default profile -> select **Ubuntu**
3. Save

# [08] Removing WSL

```powershell
# Delete a distribution (including all data)
wsl --unregister Ubuntu
```

> `--unregister` **deletes the distribution and all its internal data**. Back up anything you need beforehand.
{: .notice--warning}
