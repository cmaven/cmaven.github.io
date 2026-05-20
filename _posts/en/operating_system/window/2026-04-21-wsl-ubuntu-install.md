---
title: "Installing a Specific Ubuntu Version on WSL (Windows 11)"
description: "How to choose and install specific Ubuntu versions (20.04, 22.04, 24.04) on WSL and set the default distribution"
excerpt: "Use wsl --install -d Ubuntu-22.04 to install the version you want, set the default distribution, with a Microsoft Store alternative"
date: 2026-04-21
categories: Windows
tags: [WSL, Ubuntu, install, wsl-install, Windows11, Ubuntu-22.04, Ubuntu-24.04, distribution]
ref: wsl-ubuntu-install
---

:bulb: How to install multiple Ubuntu versions on WSL and configure the default distribution.
{: .notice--info}

---

# [01] List Available Distributions

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

# [02] Install a Specific Ubuntu Version

```powershell
wsl --install -d Ubuntu-22.04
```

Other versions:

```powershell
wsl --install -d Ubuntu-20.04
wsl --install -d Ubuntu-24.04
```

Install the default Ubuntu (latest LTS):

```powershell
wsl --install -d Ubuntu
```

| Version | Notes |
|---------|-------|
| Ubuntu-20.04 | Stability-focused, legacy support |
| Ubuntu-22.04 | Standard (recommended) |
| Ubuntu-24.04 | Latest environment |

---

# [03] Initial Setup After Installation

After installation, the distribution starts automatically and prompts:

```
Enter new UNIX username: cha
New password:
Retype new password:
```

| Field | Description |
|-------|-------------|
| Username | Lowercase ASCII (sudo permissions granted automatically) |
| Password | Used when running `sudo` |

---

# [04] Verify Installed Distributions

```powershell
wsl -l -v
```

```
  NAME            STATE           VERSION
* Ubuntu-22.04    Running         2
  Ubuntu-20.04    Stopped         2
```

| Marker | Meaning |
|--------|---------|
| `*` | Default distribution |
| STATE `Running` | Currently running |
| VERSION `2` | Running on WSL 2 |

---

# [05] Run a Specific Distribution

```powershell
wsl -d Ubuntu-22.04
```

With multiple distributions installed, use `-d` to specify which one to launch.

---

# [06] Set the Default Distribution

```powershell
wsl --set-default Ubuntu-22.04
```

After this, running plain `wsl` will launch the specified distribution.

---

# [07] Install via Microsoft Store (Alternative)

You can also install through the GUI.

1. Open **Microsoft Store**
2. Search for **"Ubuntu 22.04"**
3. Select a version → click **Install**

:bulb: Both the command-line method (`wsl --install -d`) and the Microsoft Store method yield the same result. CLI is faster and better for automation.
{: .notice--info}

---

# [08] Troubleshooting

## 8-1. Installation errors

**Virtualization** may be disabled in your BIOS.

1. Restart PC → enter BIOS (F2, DEL, etc.)
2. Enable **Intel VT-x** or **AMD-V**
3. Save and reboot

## 8-2. Check WSL status

```powershell
wsl --status
```

```
Default Version: 2
WSL version: 2.x.x
Kernel version: 5.x.x
```

## 8-3. Update WSL

```powershell
wsl --update
```

---

# [09] Summary

| Task | Command |
|------|---------|
| List available distributions | `wsl --list --online` |
| Install a specific version | `wsl --install -d Ubuntu-22.04` |
| List installed distributions | `wsl -l -v` |
| Run a specific distribution | `wsl -d Ubuntu-22.04` |
| Set default distribution | `wsl --set-default Ubuntu-22.04` |
| Check WSL status | `wsl --status` |
| Update WSL | `wsl --update` |
