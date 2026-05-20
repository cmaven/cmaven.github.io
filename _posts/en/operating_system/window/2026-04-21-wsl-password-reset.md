---
title: "WSL Password Reset (Windows 11)"
description: "How to reset a user password in WSL by logging in as root when you've forgotten the password"
excerpt: "Log in as root with wsl -u root, then reset the password using passwd"
date: 2026-04-21
categories: Windows
tags: [WSL, Ubuntu, password, passwd, root, Windows11, password-reset]
ref: wsl-password-reset
---

:bulb: When you forget your WSL user password, log in as root and reset it. This guide walks through the steps.
{: .notice--info}

---

# [01] Run WSL as Root

In PowerShell or CMD:

```powershell
wsl -u root
```

For a specific distribution:

```powershell
wsl -d Ubuntu-22.04 -u root
```

| Option | Description |
|--------|-------------|
| `-u root` | Log in as root (no password required) |
| `-d Ubuntu-22.04` | Specify a particular distribution |

---

# [02] Check User List (optional)

You can see which user accounts exist.

```bash
cat /etc/passwd | grep -E ":/home/"
```

```
cha:x:1000:1000::/home/cha:/bin/bash
```

UID 1000 is typically the first user you created.

---

# [03] Reset the Password

```bash
passwd <username>
```

Example:

```bash
passwd cha
```

```
New password:
Retype new password:
passwd: password updated successfully
```

:bulb: When run as root, you can set a new password **without entering the old one**.
{: .notice--info}

---

# [04] Verify and Exit

```bash
exit
```

Then log in as the regular user and confirm the new password works.

```powershell
wsl
```

---

# [05] Troubleshooting

## 5-1. `wsl -u root` fails

Open PowerShell **as Administrator** and try again.

```powershell
# Open PowerShell as Administrator, then run:
wsl -u root
```

## 5-2. Don't know the distribution name

```powershell
wsl -l -v
```

```
  NAME            STATE           VERSION
* Ubuntu-22.04    Running         2
  Ubuntu-20.04    Stopped         2
```

The `*` marks the default distribution.

---

# [06] Summary

| Step | Command |
|------|---------|
| Log in as root | `wsl -u root` |
| List users | `cat /etc/passwd \| grep :/home/` |
| Reset password | `passwd <username>` |
| Exit | `exit` |

:bulb: WSL doesn't have a default password. The user sets one when the distribution is first installed, and root can change it without knowing the old one.
{: .notice--info}
