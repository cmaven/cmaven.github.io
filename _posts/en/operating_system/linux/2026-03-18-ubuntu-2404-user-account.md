---
title: "Creating and Managing User Accounts on Ubuntu 24.04"
description: "How to create user accounts with the adduser command on Ubuntu 24.04, grant sudo privileges, and delete accounts"
excerpt: "User management on Ubuntu 24.04 LTS — creating accounts with adduser, granting admin privileges via the sudo group, and deleting accounts"
date: 2026-03-18
categories: Linux
tags: [Ubuntu, Ubuntu-24.04, adduser, useradd, deluser, sudo, user-account, account-creation, account-deletion, user-management]
ref: ubuntu-2404-user-account
---

:bulb: This post covers creating new user accounts, granting administrator privileges, and deleting accounts in an Ubuntu environment. Applicable to both Ubuntu Server and Desktop.
{: .notice--info}

# [01] Summary

| Item | Content |
|---|---|
| User creation | Use the `adduser` or `useradd` command |
| Home directory | Auto-created as `/home/username` when using `adduser` |
| Admin privileges | Granted by adding to the `sudo` group |
| Privilege verification | Check with `groups` or `sudo whoami` |

# [02] Creating a User

Using `adduser` handles home directory creation, default shell setup, and password configuration in one step.

```bash
sudo adduser username
```

When executed, the following are handled automatically.

| Item | Description |
|---|---|
| Home directory | `/home/username` is created automatically |
| Default shell | Set to `/bin/bash` |
| Group | A group with the same name as the user is auto-created |
| Password | A prompt is shown to set it |

> `useradd` does not automatically create a home directory, so `adduser` is recommended for ordinary user creation.
{: .notice--warning}

# [03] Granting Admin Privileges

To grant `sudo` privileges to the user you created, add them to the `sudo` group.

```bash
sudo usermod -aG sudo username
```

| Option | Description |
|---|---|
| `-a` | Append while keeping existing groups (append) |
| `-G` | Specify the group to add |

# [04] Verifying Privileges and Creation

## 4-1. Verify the Home Directory

```bash
ls -ld /home/username
```

## 4-2. Verify Groups

```bash
groups username
```

Example output:
```
username : username sudo
```

If `sudo` is included, admin privileges have been granted correctly.

## 4-3. Verify sudo Privileges

Switch to the user and verify.

```bash
su - username
sudo whoami
```

If `root` is printed, it's working correctly.

# [05] Deleting a User

```bash
# Delete only the user (keep the home directory)
sudo deluser username

# Delete including the home directory
sudo deluser --remove-home username
```

| Command | Description |
|---|---|
| `deluser username` | Delete the account only; `/home/username` is preserved |
| `deluser --remove-home username` | Delete both the account and the home directory |

:small_blue_diamond: Reference: [https://cmaven.tistory.com/12](https://cmaven.tistory.com/12){:target="_blank"}
