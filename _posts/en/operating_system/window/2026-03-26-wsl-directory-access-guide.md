---
title: "Complete WSL Directory Access Guide - Windows <-> Ubuntu File Sharing"
description: "How to find WSL Ubuntu files from Windows and access Windows files from Ubuntu - bidirectional paths"
excerpt: "Five ways to access WSL files: \\wsl$ and /mnt/c paths, network drive mapping, VS Code integration, and more"
date: 2026-03-26
categories: Windows
tags: [WSL, WSL2, file-access, directory, mnt, wsl$, VS-Code, network-drive, explorer]
ref: wsl-directory-access-guide
---

:bulb: This guide covers bidirectional paths and practical techniques for finding WSL Ubuntu files from Windows, and Windows files from Ubuntu.
{: .notice--info}

# [01] WSL and Windows Filesystem Structure

Once WSL is installed, Windows and Ubuntu each maintain their own filesystem while being able to access one another.

```
+--------------------------------------------------+
| Windows (C:\Users\...)                           |
|                                                  |
|   Accessing WSL Ubuntu files:                    |
|   \\wsl$\Ubuntu\home\{username}\                 |
|                                                  |
+--------------------------------------------------+
| Ubuntu (WSL)                                     |
|                                                  |
|   Accessing Windows files:                       |
|   /mnt/c/Users/{windows-username}/               |
|                                                  |
+--------------------------------------------------+
```

---

# [02] Windows -> Ubuntu File Access

## 2-1. Path format

```
\\wsl$\Ubuntu\home\{username}
```

In recent versions of WSL2, the following path also works:

```
\\wsl.localhost\Ubuntu\home\{username}
```

## 2-2. Key directory mappings

| Ubuntu path | Access path from Windows |
|---|---|
| `/home/{user}` | `\\wsl$\Ubuntu\home\{user}` |
| `/etc` | `\\wsl$\Ubuntu\etc` |
| `/root` | `\\wsl$\Ubuntu\root` |
| `/tmp` | `\\wsl$\Ubuntu\tmp` |

---

# [03] Ubuntu -> Windows File Access

From Ubuntu, Windows drives are automatically mounted under `/mnt/`.

| Windows path | Access path from Ubuntu |
|---|---|
| `C:\Users\{user}\Desktop` | `/mnt/c/Users/{user}/Desktop` |
| `D:\Projects` | `/mnt/d/Projects` |
| `C:\Program Files` | `/mnt/c/Program Files` |

---

# [04] Five Easy Ways to Access WSL Files

## 4-1. Type the path directly in File Explorer (simplest)

Open Windows File Explorer and enter `\\wsl$` in the address bar to see all installed WSL distributions as folders.

```
\\wsl$
```

Click the Ubuntu folder to browse the entire filesystem.

## 4-2. Open Explorer directly from the Ubuntu terminal (fastest)

In an Ubuntu shell, navigate to the desired directory and run the following to open it in Windows Explorer.

```bash
# Open the current directory in Explorer
explorer.exe .

# Open a specific directory in Explorer
explorer.exe /home/kcloud/projects
```

## 4-3. Map a network drive (for frequent access)

If you access certain WSL paths often, mapping them to a Windows drive letter is convenient.

1. Right-click **"This PC"** in File Explorer
2. Select **"Map network drive"**
3. Choose a drive letter (e.g., `Z:`)
4. Enter `\\wsl$\Ubuntu\home\{username}` in the folder field
5. Check **"Reconnect at sign-in"**

After that, `Z:\` takes you straight to your Ubuntu home directory.

## 4-4. Open in VS Code

This is the cleanest way to edit WSL files with VS Code.

```bash
# Run from the Ubuntu terminal
code .                    # Open the current directory in VS Code
code ~/projects/myapp     # Open a specific project
```

The VS Code Remote - WSL extension automatically connects to the WSL environment.

## 4-5. Create a shortcut

You can place a shortcut on the Windows desktop too.

1. Right-click the desktop -> **"New"** -> **"Shortcut"**
2. Enter `\\wsl$\Ubuntu\home\{username}` as the location
3. Name it and finish

---

# [05] Relationship with Remote Servers

:warning: WSL directory sharing applies only to the **local WSL environment**. If you SSH into a remote server from WSL Ubuntu, the remote server's files are NOT reachable via `\\wsl$`.
{: .notice--warning}

To handle remote server files from Windows, use `scp`, `rsync`, or the Remote - SSH extension in VS Code.

```bash
# Copy a file from the remote server to local
scp user@10.254.202.91:/home/user/file.txt ~/

# Copy a file from local to the remote server
scp ~/file.txt user@10.254.202.91:/home/user/
```

---

# [06] Performance Considerations

File operations in WSL have notable performance differences.

| Scenario | Performance | Recommended |
|---|---|---|
| Working with Ubuntu files inside Ubuntu | Fast | Yes - do development here |
| Accessing via `\\wsl$` from Windows | Moderate | Yes - for browsing, light edits |
| Working with Windows files via `/mnt/c/` from Ubuntu | Slow | No - don't put dev projects here |

:bulb: **Key principle:** Keep development projects under the Ubuntu filesystem (`/home/{user}/`), and only reach in from Windows via `\\wsl$` or `explorer.exe .` when you need to view them. This is the most efficient pattern.
{: .notice--info}

---

# [07] Summary

```bash
# Windows -> Ubuntu
\\wsl$\Ubuntu\home\{username}

# Ubuntu -> Windows
/mnt/c/Users/{windows-username}

# Open Explorer directly from Ubuntu
explorer.exe .
```

WSL filesystem sharing is bidirectional, but for performance, the recommended pattern is **work inside Ubuntu, view from Windows**.
