---
title: "Running Git Pull, Commit, Push Without Re-authenticating (SSH, Credential)"
description: "How to register an SSH key or configure Git Credential so that Git operations run without re-authentication every time"
excerpt: "How to simplify Git authentication via ssh-keygen / SSH key registration and git config credential.helper store/cache"
date: 2024-02-22
categories: Git
tags: [Git, SSH, Credential, Authentication, Token, credential-helper, ssh-keygen]
ref: git-credential
---

:bulb: This note summarizes the credentials (authentication) needed for Git operations.  
Typically `pull`, `commit`, and `push` prompt for a user ID and password (or token); here we look at how to streamline that process.
{: .notice--info}

# [01]  Ways to Store User Credentials in the Local Git

1. Using an SSH key
   - Generate an SSH key on the development machine and register it with Git.
   - Use repositories via SSH.
2. Using Git Config (Credential)
   - Permanent storage on the system.
   - Cache-based storage for a limited time.


# [02]  Register and Use an SSH Key  

## 2-1. Generate an SSH Key

```bash
# Accept the defaults (Enter) for any prompts.
ssh-keygen -t rsa -C "Git" -b 4096

# Copy and paste the printed key into the SSH Key field on GitLab.
cat ~/.ssh/id_rsa.pub

# Sample output
root@cmaven:~# cat ~/.ssh/id_rsa.pub
ssh-rsa AAAA124123QABAAACAQCbKx1YXw8bUIWUb39eLkm7+AMVT92PhMCo...
```  

## 2-2. Register the SSH Key with Git  

Profile :arrow_right: Settings :arrow_right: SSH and GPG Keys  :arrow_right:  New SSH Key  :arrow_right:  Paste the key  :arrow_right:  Add SSH Key  

![figure1](https://github.com/cmaven/cmaven.github.io/assets/76153041/cb7654b1-1c4e-4522-8144-2f1d2905902a)  

![figure2](https://github.com/cmaven/cmaven.github.io/assets/76153041/bf6d3bc7-4b6f-4de3-ad09-1289cd56f9d1)  



## 2-3. Clone the target repository over SSH  

![2024-02-22 13 52 04](https://github.com/cmaven/cmaven.github.io/assets/76153041/8fdfd3d3-5f26-4a44-8258-ec53188b365e)  

From this point onward, Pull/Commit/Push run without authentication prompts.


# [03]  Using Git Config (Credential)  

- Run from the Git repository on the development machine.  
- Apply one of the methods below and authenticate once with your ID and password (or token); subsequent Pull/Commit/Push operations run without re-authentication.

## 3-1. Permanent storage  

```bash
git config credential.helper store

# verify changes
git config --list
```  

## 3-2. Cache storage  

```bash
# default 15 minutes
git config credential.helper cache

# specify time (timeout 3600 sec = 1 hour)
git config credential.helper `cache --timeout=3600`
```  


## 3-3. Apply to all projects  

```bash
git config credential.helper store --global
```
