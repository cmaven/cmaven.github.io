---
title: "Bypassing BAD PASSWORD: contains the user name"
description: "How to bypass the BAD PASSWORD error in Ubuntu and set a password containing the user name (pwquality.conf)"
excerpt: "How to change the password validation policy via the usercheck setting in pwquality.conf"
date: 2023-09-21
last_modified_at: 2026-05-26
categories: Linux
tags: [Ubuntu, password, pwquality, pam, password-policy, security-config]
ref: password-check
---

:bulb: This post covers how to work around the `BAD PASSWORD: The password contains the user name in some form` error that prevents you from setting the desired password on Linux (Ubuntu).
{: .notice--info}

# [01] Situation

- On Linux (Ubuntu), when entering a password you hit `BAD PASSWORD: The password contains the user name in some form` and cannot set the desired password
- ex) Test server
  - username: testuser
  - password: testuser

# [02] Disabling the Validation

:warning: Modifying this is not recommended in security-sensitive environments.
{: .notice--warning}

## 2-1. Locate the Password Configuration File

On Debian (Ubuntu), `/etc/pam.d/common-password` references the `pam_pwquality.so` configuration.

```shell
# requires root
# /etc/pam.d/common-password
# here are the per-package modules (the "Primary" block)
password        requisite                       pam_pwquality.so retry=3
password        [success=2 default=ignore]      pam_unix.so obscure use_authtok try_first_pass yescrypt
```

## 2-2. Change the Password Validation Setting

In `/etc/security/pwquality.conf`, change to `usercheck = 0`.

```shell
# requires root
# /etc/security/pwquality.conf
# Whether to check if it contains the user name in some form.
# The check is enabled if the value is not 0.
usercheck = 0
#
```

:small_blue_diamond: Reference: [Password validation settings reference](https://www.networkworld.com/article/2726217/how-to-enforce-password-complexity-on-linux.html){:target="_blank"}
