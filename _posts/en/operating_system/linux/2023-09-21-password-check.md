---
title: "Bypassing BAD PASSWORD: contains the user name"
description: "How to bypass the BAD PASSWORD error in Ubuntu and set a password containing the user name by adjusting the usercheck setting in pwquality.conf."
excerpt: "Change usercheck = 0 in /etc/security/pwquality.conf to allow passwords that contain the username — useful for test and dev environments."
date: 2023-09-21
last_modified_at: 2026-05-26
categories: Linux
tags: [Ubuntu, password, pwquality, pam, password-policy, security-config, usercheck, passwd]
ref: password-check
---

:bulb: This post covers how to work around the `BAD PASSWORD: The password contains the user name in some form` error that prevents you from setting the desired password on Linux (Ubuntu).
{: .notice--info}

:warning: Weakening password policy is only appropriate for isolated test or development environments. Do **not** apply this change on production or internet-facing systems.
{: .notice--warning}

**Environment**: Ubuntu 20.04 / 22.04 / 24.04 (requires root)

---

# [01] Situation

When setting a password with `passwd` on Linux, you may encounter this error:

```text
Changing password for testuser.
Current password:
New password:
BAD PASSWORD: The password contains the user name in some form
New password:
```

The system rejects the new password because the PAM `pwquality` module detects that the password string resembles the username.

**Typical scenario — test server:**

| Item | Value |
|---|---|
| Username | `testuser` |
| Desired password | `testuser` (or similar) |
| Error | `BAD PASSWORD: The password contains the user name in some form` |

This is intentional security behaviour in production, but on a local test server or CI environment it is an unnecessary obstacle.

---

# [02] How the Check Works

Ubuntu's password validation chain looks like this:

```text
passwd command
    └─► PAM stack (/etc/pam.d/common-password)
            └─► pam_pwquality.so
                    └─► /etc/security/pwquality.conf  ← policy lives here
```

The relevant PAM stack entry:

```shell
# /etc/pam.d/common-password  (requires root to view)
# here are the per-package modules (the "Primary" block)
password        requisite                       pam_pwquality.so retry=3
password        [success=2 default=ignore]      pam_unix.so obscure use_authtok try_first_pass yescrypt
```

`pam_pwquality.so` reads its policy from `/etc/security/pwquality.conf`. One of those policy flags is `usercheck`, which controls whether the password is tested against the username.

---

# [03] Disabling the Validation

## 3-1. Locate the Password Configuration File

Open the pwquality configuration file with a text editor (root required):

```shell
sudo nano /etc/security/pwquality.conf
```

Find the `usercheck` line (it may be commented out, defaulting to `1`):

```shell
# /etc/security/pwquality.conf
# Whether to check if it contains the user name in some form.
# The check is enabled if the value is not 0.
# usercheck = 1
```

## 3-2. Change the Password Validation Setting

Set `usercheck` to `0` to disable the username-similarity check:

```shell
# /etc/security/pwquality.conf
# Whether to check if it contains the user name in some form.
# The check is enabled if the value is not 0.
usercheck = 0
```

Save and close the file. The change takes effect immediately — no service restart required.

## 3-3. Verify

Try setting the previously rejected password:

```shell
passwd testuser
# New password: testuser
# Retype new password: testuser
# passwd: password updated successfully
```

---

# [04] Other Common pwquality Settings

While you have `pwquality.conf` open, here are other frequently adjusted settings for test environments:

| Setting | Default | Meaning |
|---|---|---|
| `minlen` | `8` | Minimum password length |
| `usercheck` | `1` | Reject passwords containing the username |
| `dictcheck` | `1` | Reject passwords found in a dictionary |
| `maxrepeat` | `0` (disabled) | Max consecutive identical characters |
| `minclass` | `0` (disabled) | Minimum number of character classes required |

To disable all quality checks for a test machine, set:

```shell
minlen = 1
usercheck = 0
dictcheck = 0
```

:warning: Reset these to defaults before promoting a test machine to any production role.
{: .notice--warning}

---

# [05] Reverting the Change

To re-enable the username check, set `usercheck` back to `1` (or comment the line out to restore the default):

```shell
# /etc/security/pwquality.conf
usercheck = 1
```

---

# [06] Reference

:small_blue_diamond: [Password validation settings reference — NetworkWorld](https://www.networkworld.com/article/2726217/how-to-enforce-password-complexity-on-linux.html){:target="_blank"}

:small_blue_diamond: [`pam_pwquality` man page](https://manpages.ubuntu.com/manpages/jammy/man8/pam_pwquality.8.html){:target="_blank"}
