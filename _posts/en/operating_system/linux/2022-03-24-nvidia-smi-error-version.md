---
title: "nvidia-smi Error: Driver/library version mismatch"
description: "Analysis and fix for the Driver/library version mismatch error when running nvidia-smi on Ubuntu"
excerpt: "How to resolve the NVIDIA driver version mismatch caused by unattended-upgrade (reload modules, prevent auto-updates)"
categories: Linux
tags: [Ubuntu, NVIDIA, nvidia-smi, GPU, driver-error, unattended-upgrade, version-mismatch]
date: 2022-03-24
ref: nvidia-smi-error-version
---

:bulb: This post describes how to resolve the `Failed to initialize NVML: Driver/library version mismatch` error that appears when running `nvidia-smi` after the NVIDIA driver is installed.
{: .notice--info}

# [01] Situation

- Ubuntu server with an NVIDIA GPU installed
- GPU is in use after installing nvidia-driver
- Running `nvidia-smi` fails with `Failed to initialize NVML: Driver/library version mismatch`

  ![nvidia-error-01](https://user-images.githubusercontent.com/76153041/159899223-2e10ca48-c076-4384-8162-d07eccd9c06d.png)

# [02] Cause

## 2-1. Identify the problem

```shell
dmesg
```

![nvidia-error-02](https://user-images.githubusercontent.com/76153041/159899571-6bd84838-cc76-4ae3-9f9e-391564d4c4a1.png)

- `NVRM: API mismatch ...` error message
- Client version is 470.103.01, but the kernel module version is 470.86
- Linux's unattended-upgrade automatically updated the security-related packages, causing the version gap

## 2-2. Check what unattended-upgrade ran

```shell
cat /var/log/apt/history.log
```

![nvidia-error-03](https://user-images.githubusercontent.com/76153041/159901192-57d1870e-d0ce-4870-8dd8-35b597c89f91.png)

```shell
view /var/log/unattended-upgrades/unattended-upgrades.log.1.gz
```

![nvidia-error-04](https://user-images.githubusercontent.com/76153041/159901243-4a9784c3-69ad-485e-be1d-15e1ece17b76.png)

![nvidia-error-05](https://user-images.githubusercontent.com/76153041/159901195-00637157-36e7-4bc4-b490-278201990596.png)

- The log shows that `libnvidia-*` packages were automatically updated on 2022-02-08.

:bulb: If you can't find the relevant entries in `unattended-upgrades.log`, check the older log files (e.g. `log.1.gz`).
{: .notice--info}

# [03] Solution 1: Prevent unattended-upgrade

Exclude the NVIDIA-related packages from the unattended-upgrade target list.

Edit `/etc/apt/apt.conf.d/50unattended-upgrades`:

```shell
# Based on Ubuntu 24.04
# Add the following block to /etc/apt/apt.conf.d/50unattended-upgrades

Unattended-Upgrade::Package-Blacklist {
  "nvidia-*.";
}
```

![Image 41](https://user-images.githubusercontent.com/76153041/183000202-374ce1b1-ae1e-46d2-8374-63c91c2ddae4.png)

:small_blue_diamond: Reference: [link](https://blog.ggaman.com/1029){:target="_blank"}

# [04] Solution 2: Remove the NVIDIA module (without rebooting)

If the update has already been installed automatically, removing the existing module resolves the problem.

## 4-1. Check the NVIDIA kernel modules

```shell
lsmod |grep nvidia
```

![nvidia-error-06](https://user-images.githubusercontent.com/76153041/159901287-a51e2c73-38ea-490d-9638-9cbc9e92ad61.png)

## 4-2. Remove the modules

```shell
# Remove the listed modules
rmmod $module_name

# ex)
rmmod nvidia_uvm
```

:warning: If you see an error like `ERROR: Module nvidia_drm is in use`, terminate the processes that are using it.
{: .notice--warning}

![nvidia-error-07](https://user-images.githubusercontent.com/76153041/159902947-16947caf-9940-42f2-8f37-34aad3c1d7ab.png)

```shell
# Find and kill processes using NVIDIA
lsof /dev/nvidia*
kill -9 $PID

# ex)
kill -9 449143
```

![nvidia-error-08](https://user-images.githubusercontent.com/76153041/159903271-b8e198b2-077b-4bd5-8499-046846713f0d.png)

## 4-3. Verify

The modules are automatically reloaded, and `nvidia-smi` works again.

![nvidia-error-09](https://user-images.githubusercontent.com/76153041/159903143-af2f7b1e-3098-4322-b79d-8ae6808b0dc0.png)
