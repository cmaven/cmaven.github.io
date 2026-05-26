---
title: "How to Tell If Ubuntu Is Desktop or Server"
description: "Commands to check whether the installed Ubuntu is Desktop or Server, plus how to check OS version, kernel version, and hardware architecture from the terminal."
excerpt: "Use dpkg -l ubuntu-desktop to distinguish Ubuntu Desktop from Server, and inspect OS and kernel versions with cat /etc/*release and uname -a."
categories: Linux
tags: [Ubuntu, Desktop, Server, dpkg, uname, version-check, os-info, kernel, architecture]
date: 2022-10-27
last_modified_at: 2026-05-26
ref: ubuntu-desktop-server-check
---

:bulb: This post describes how to check the installed Ubuntu variant (Desktop vs. Server), the OS version, and the kernel version — all from the terminal without a GUI.
{: .notice--info}

**Environment**: Ubuntu 20.04 / 22.04 / 24.04

---

# [01] Check Ubuntu Desktop vs. Server

Ubuntu Desktop and Ubuntu Server share the same base packages. The easiest way to tell them apart is to query whether the `ubuntu-desktop` meta-package is installed.

```shell
dpkg -l ubuntu-desktop
```

**When it is Ubuntu Desktop:**

```text
root@gedgeworker1:~# dpkg -l ubuntu-desktop
Desired=Unknown/Install/Remove/Purge/Hold
| Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
|/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)
||/ Name           Version      Architecture Description
+++-==============-============-============-=================================
ii  ubuntu-desktop 1.450.2      amd64        The Ubuntu desktop system
```

The `ii` prefix in the first column means the package is **installed and configured**.

**When it is Ubuntu Server:**

```text
root@gedgemaster:~# dpkg -l ubuntu-desktop
dpkg-query: no packages found matching ubuntu-desktop
```

No output (or the "no packages found" message) means the `ubuntu-desktop` meta-package is absent — this is a Server install.

![Ubuntu Desktop dpkg result](https://user-images.githubusercontent.com/76153041/198195538-29a5408f-38b8-4f7a-a365-ac9c6061aaf7.png)

*Figure 1. `dpkg -l ubuntu-desktop` on a Desktop install — note the `ii` status prefix.*

![Ubuntu Server dpkg result](https://user-images.githubusercontent.com/76153041/198195542-2f340929-f0a7-404b-828d-aeb6ea75fd71.png)

*Figure 2. The same command on a Server install — the package is not found.*

| Result | Meaning |
|---|---|
| `ii  ubuntu-desktop ...` | Ubuntu Desktop |
| `dpkg-query: no packages found` | Ubuntu Server |

:bulb: This check works because `ubuntu-desktop` is a **meta-package** — it has no files of its own but pulls in all Desktop-specific packages (GNOME, display manager, etc.). Its presence or absence is the canonical marker.
{: .notice--info}

---

# [02] Check the Installed OS Version

To see the full Ubuntu version, codename, and distribution information, read the release files:

```shell
cat /etc/*release
```

Sample output (Ubuntu 24.04):

```text
root@gedgeworker1:~# cat /etc/*release
DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=24.04
DISTRIB_CODENAME=noble
DISTRIB_DESCRIPTION="Ubuntu 24.04.1 LTS"
NAME="Ubuntu"
VERSION="24.04.1 LTS (Noble Numbat)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 24.04.1 LTS"
VERSION_ID="24.04"
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
VERSION_CODENAME=noble
UBUNTU_CODENAME=noble
```

Key fields to note:

| Field | Value | Meaning |
|---|---|---|
| `DISTRIB_RELEASE` | `24.04` | Major release version |
| `DISTRIB_CODENAME` | `noble` | Release codename |
| `PRETTY_NAME` | `Ubuntu 24.04.1 LTS` | Human-readable label |
| `ID_LIKE` | `debian` | Parent distribution |

Alternatively, use `lsb_release` for a shorter summary:

```shell
lsb_release -a
```

```text
No LSB modules are available.
Distributor ID: Ubuntu
Description:    Ubuntu 24.04.1 LTS
Release:        24.04
Codename:       noble
```

---

# [03] Check the Kernel Version

The `uname` command reports the running kernel version and system architecture:

```shell
uname -a
```

Sample output:

```text
root@gedgeworker1:~# uname -a
Linux gedgeworker1 5.4.0-125-generic #141-Ubuntu SMP Wed Aug 10 13:42:03 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux
```

| Field (positional) | Example value | Meaning |
|---|---|---|
| Kernel name | `Linux` | OS type |
| Hostname | `gedgeworker1` | Machine name |
| Kernel release | `5.4.0-125-generic` | Kernel version string |
| Build info | `#141-Ubuntu SMP ...` | Build number and date |
| Architecture | `x86_64` | CPU architecture (repeated for machine / processor / platform) |

To show only the kernel version string:

```shell
uname -r
# 5.4.0-125-generic
```

---

# [04] Quick Reference

| Goal | Command |
|---|---|
| Desktop vs. Server | `dpkg -l ubuntu-desktop` |
| OS version (detailed) | `cat /etc/*release` |
| OS version (short) | `lsb_release -a` |
| Kernel version (full) | `uname -a` |
| Kernel version (short) | `uname -r` |
| CPU architecture | `uname -m` |
| Hostname | `hostname` |
