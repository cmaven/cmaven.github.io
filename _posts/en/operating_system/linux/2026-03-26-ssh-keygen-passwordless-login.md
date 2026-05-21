---
title: "Passwordless SSH Login with Key Authentication"
description: "How to generate a key pair with ssh-keygen and register it on a remote server with ssh-copy-id for passwordless SSH login"
excerpt: "SSH key generation (ssh-keygen), public key registration (ssh-copy-id), permission settings, and using the config file"
date: 2026-03-26
categories: Linux
tags: [SSH, ssh-keygen, ssh-copy-id, public-key-authentication, passwordless-login, authorized_keys, ssh-config]
ref: ssh-keygen-passwordless-login
---

:bulb: This post covers how to set up SSH key authentication on Ubuntu to log in to a remote server without a password.
{: .notice--info}

# [01] How SSH Key Authentication Works

SSH key authentication uses a pair of a **public key** and a **private key**.

```
┌─────────────────┐                    ┌─────────────────┐
│   Local PC      │                    │  Remote Server  │
│                 │                    │                 │
│  ~/.ssh/id_rsa  │ ── private (kept) ── │                 │
│  ~/.ssh/id_rsa  │                    │ ~/.ssh/         │
│         .pub    │ ── copy public ───→ │ authorized_keys │
└─────────────────┘                    └─────────────────┘
```

| Key | Location | Role |
|---|---|---|
| **Private key** (`id_rsa`) | Local PC | Proves your identity. Never share externally |
| **Public key** (`id_rsa.pub`) | Remote server | When registered on the server, only the holder of the private key can connect |

:warning: Never copy the private key (`id_rsa`) to another person or server. Only the public key (`.pub`) is registered on the server.
{: .notice--warning}

---

# [02] Generating the SSH Key

## 2-1. Run ssh-keygen

```bash
ssh-keygen -t rsa -b 4096
```

| Option | Description |
|---|---|
| `-t rsa` | Use the RSA algorithm |
| `-b 4096` | 4096-bit key length (default is 3072; 4096 recommended for security) |

## 2-2. Interactive Prompts

```
Generating public/private rsa key pair.
Enter file in which to save the key (/home/user/.ssh/id_rsa):    ← Enter (use default path)
Enter passphrase (empty for no passphrase):                      ← Enter (no passphrase)
Enter same passphrase again:                                     ← Enter
```

| Question | Recommended input |
|---|---|
| Save path | Enter (default `~/.ssh/id_rsa`) |
| passphrase | Enter (leave empty for no extra prompt on connection) |

:bulb: Setting a passphrase encrypts the key file itself for stronger security, but you must enter it on every connection. Leave it blank if your goal is automation.
{: .notice--info}

## 2-3. Verify Generation

```bash
ls -la ~/.ssh/
```

```
-rw-------  1 user user  3381  Mar 26 10:00  id_rsa        ← private key (600 perms)
-rw-r--r--  1 user user   741  Mar 26 10:00  id_rsa.pub    ← public key
```

---

# [03] Registering the Public Key on the Server

## 3-1. Use ssh-copy-id (Recommended)

```bash
ssh-copy-id user@xxx.xxx.xxx
```

**Execution result:**

```
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s)
user@xxx.xxx.xxx's password:          ← Enter the server password (the last time)

Number of key(s) added: 1
```

This single command automatically registers the public key in the server's `~/.ssh/authorized_keys`.

## 3-2. Manual Registration (when ssh-copy-id is unavailable)

```bash
# Append the public key contents to authorized_keys on the server
cat ~/.ssh/id_rsa.pub | ssh user@xxx.xxx.xxx "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

---

# [04] Connection Test

```bash
ssh user@xxx.xxx.xxx
```

If you log in without entering a password, it succeeded.

```
Welcome to Ubuntu 22.04.x LTS
Last login: Wed Mar 26 10:05:00 2026 from 192.168.x.x
user@server:~$
```

---

# [05] Checking Permissions

The most common reason SSH key authentication fails is **file permission issues**.

## 5-1. Local PC

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

## 5-2. Remote Server

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

| Target | Permissions | Description |
|---|---|---|
| `~/.ssh/` | `700` (drwx------) | Owner-only access |
| `id_rsa` | `600` (-rw-------) | Owner read/write only |
| `id_rsa.pub` | `644` (-rw-r--r--) | Public key — read access allowed |
| `authorized_keys` | `600` (-rw-------) | Owner read/write only |

:warning: If permissions are too open (e.g., 644 on the private key), SSH refuses to use the key file.
{: .notice--warning}

---

# [06] Convenient Connections via SSH config

Instead of typing `ssh user@xxx.xxx.xxx` every time, you can register an alias in the `~/.ssh/config` file.

```bash
vi ~/.ssh/config
```

```
Host myserver
    HostName xxx.xxx.xxx
    User user
    IdentityFile ~/.ssh/id_rsa
    Port 22
```

After that, connect using the alias.

```bash
ssh myserver
```

**Example with multiple servers:**

```
Host dev
    HostName 10.254.202.91
    User kcloud

Host prod
    HostName 10.254.202.92
    User deploy
    Port 2222

Host gpu
    HostName 10.254.203.10
    User ml
    IdentityFile ~/.ssh/id_rsa_gpu
```

```bash
ssh dev     # → kcloud@10.254.202.91:22
ssh prod    # → deploy@10.254.202.92:2222
ssh gpu     # → ml@10.254.203.10 (uses a separate key)
```

:bulb: SSH-based commands such as `scp` and `rsync` can use config aliases as well.
{: .notice--info}

```bash
scp file.txt myserver:~/
rsync -avz ./project/ myserver:~/project/
```

---

# [07] Troubleshooting

## 7-1. When the Password Is Still Requested

```bash
# Check SSH debug output
ssh -v user@xxx.xxx.xxx
```

In the output, look for the following.

```
debug1: Offering public key: /home/user/.ssh/id_rsa RSA
debug1: Server accepts key: /home/user/.ssh/id_rsa RSA     ← If this line appears, the key is recognized
```

If the key is rejected, check the following.

| Check item | Verification command |
|---|---|
| Local private key permissions | `ls -la ~/.ssh/id_rsa` → must be 600 |
| Server authorized_keys permissions | `ls -la ~/.ssh/authorized_keys` → must be 600 |
| Server .ssh directory permissions | `ls -la -d ~/.ssh` → must be 700 |
| Server home directory permissions | `ls -la -d ~` → must be 755 or stricter |
| Server sshd configuration | Confirm `PubkeyAuthentication yes` |

## 7-2. When Public Key Authentication Is Disabled on the Server

```bash
# Check on the server
sudo grep PubkeyAuthentication /etc/ssh/sshd_config
```

```
PubkeyAuthentication yes     ← must be yes
```

If it's set to `no`, change it to `yes` and restart SSH.

```bash
sudo vi /etc/ssh/sshd_config
sudo systemctl restart sshd
```

---

# [08] Full Process Summary

```bash
# 1. Generate the key (local)
ssh-keygen -t rsa -b 4096

# 2. Register the public key (send to the server)
ssh-copy-id user@xxx.xxx.xxx

# 3. Connection test
ssh user@xxx.xxx.xxx

# 4. (Optional) Register config
echo "Host myserver
    HostName xxx.xxx.xxx
    User user" >> ~/.ssh/config

# 5. Connect via alias
ssh myserver
```
