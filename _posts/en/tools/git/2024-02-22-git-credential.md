---
title: "Running Git Pull, Commit, Push Without Re-authenticating (SSH, Credential)"
description: "How to register an SSH key or configure Git Credential Helper so that Git operations run without re-authentication on every command"
excerpt: "Streamline Git authentication with ssh-keygen SSH key registration or git config credential.helper store/cache"
date: 2024-02-22
last_modified_at: 2026-05-26
categories: Git
tags: [Git, SSH, Credential, Authentication, Token, credential-helper, ssh-keygen]
ref: git-credential
---

:bulb: Every `pull`, `commit`, and `push` prompts for credentials by default — configure SSH keys or a credential helper once to eliminate repeated authentication.
{: .notice--info}

# [01] Two Ways to Store Git Credentials

| Method | How it works | Best for |
|--------|-------------|---------|
| **SSH Key** | Generate a key pair; register the public key with Git host | Permanent, passwordless auth per machine |
| **Git Credential Helper** | Cache credentials after first login | HTTPS-based workflows; temporary or permanent storage |

# [02] Register and Use an SSH Key

## 2-1. Generate an SSH key

```bash
# Accept the defaults (press Enter for each prompt)
ssh-keygen -t rsa -C "Git" -b 4096

# Print the public key to copy
cat ~/.ssh/id_rsa.pub
```

Sample output:

```text
root@cmaven:~# cat ~/.ssh/id_rsa.pub
ssh-rsa AAAA124123QABAAACAQCbKx1YXw8bUIWUb39eLkm7+AMVT92PhMCo...
```

Copy the entire line starting with `ssh-rsa`.

## 2-2. Register the SSH key with your Git host

Navigate to: **Profile → Settings → SSH and GPG Keys → New SSH Key → Paste the key → Add SSH Key**

*Figure 1. SSH Keys settings page*

![figure1](https://github.com/cmaven/cmaven.github.io/assets/76153041/cb7654b1-1c4e-4522-8144-2f1d2905902a)

*Figure 2. Adding a new SSH key*

![figure2](https://github.com/cmaven/cmaven.github.io/assets/76153041/bf6d3bc7-4b6f-4de3-ad09-1289cd56f9d1)

## 2-3. Clone the repository over SSH

When cloning, use the SSH URL (starts with `git@`) instead of HTTPS:

*Figure 3. Selecting the SSH clone URL*

![2024-02-22 13 52 04](https://github.com/cmaven/cmaven.github.io/assets/76153041/8fdfd3d3-5f26-4a44-8258-ec53188b365e)

From this point onward, `pull`, `commit`, and `push` run without authentication prompts.

> If your repository was already cloned via HTTPS, update the remote URL: `git remote set-url origin git@github.com:<user>/<repo>.git`

# [03] Using Git Config (Credential Helper)

Run these commands from inside any Git repository on your development machine. Authenticate once with your ID and password (or token); subsequent operations run without re-authentication.

## 3-1. Permanent storage

Credentials are saved in plain text to `~/.git-credentials`.

```bash
git config credential.helper store

# Verify the change
git config --list
```

## 3-2. Cache storage (time-limited)

Credentials are held in memory only — nothing written to disk.

```bash
# Default: 15 minutes
git config credential.helper cache

# Custom timeout (e.g., 1 hour = 3600 seconds)
git config credential.helper "cache --timeout=3600"
```

## 3-3. Apply globally to all projects

```bash
git config credential.helper store --global
```

## 3-4. Comparison

| Helper | Storage location | Expires | Security |
|--------|-----------------|---------|---------|
| `store` | `~/.git-credentials` (plain text) | Never | Lower |
| `cache` | Memory (tmpfs socket) | After timeout | Higher |
| SSH key | `~/.ssh/` (key file) | Never | Highest |

> On macOS, use `osxkeychain` as the credential helper to store credentials in the system Keychain: `git config --global credential.helper osxkeychain`. On Windows, `wincred` or the Git Credential Manager (GCM) is recommended.
