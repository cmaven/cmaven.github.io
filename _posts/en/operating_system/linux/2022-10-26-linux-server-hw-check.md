---
title: "Checking Linux Server Hardware Info - CPU, Memory, Disk, Network"
description: "Commands for inspecting CPU, memory, disk, network, and GPU information on an Ubuntu server"
excerpt: "How to inspect Linux server hardware using dmidecode, lscpu, lshw, lsblk, and friends"
categories: Linux
tags: [Ubuntu, CPU, Memory, Disk, Network, GPU, dmidecode, lscpu, lshw, hardware-check]
date: 2022-10-26
ref: linux-server-hw-check
---

:bulb: This post collects commands for inspecting the hardware installed on a server: CPU, memory, disks, network interface cards, GPU, and so on.
{: .notice--info}

:book: Based on Ubuntu 24.04 Server

# [01] Related Commands

| Command | Description |
|---|---|
| `dmidecode` | Print hardware info from the system DMI (SMBIOS) tables |
| `free` | Show available and used memory |
| `lshw` | Extract hardware config such as memory settings, firmware version, CPU speed, and bus speed |
| `lsblk` | List block device info, derived from the `sysfs` filesystem |
| `lscpu` | Print CPU info: architecture, cores/threads, sockets, etc. |

# [02] CPU Information

```shell
lscpu

# Extract only the relevant fields
# Architecture, number of processors, threads per core, cores per socket, sockets, model name, NUMA info
# Processors = Cores * threads-per-core * sockets
lscpu |grep -E 'Archi|On-line|Thread|socket|Socket|Model |NUMA'
```

![2022-10-27 13 40 43](https://user-images.githubusercontent.com/76153041/198193272-fca3526b-c86a-4dc6-a1ac-a958f9d9cc3b.png)

# [03] Memory Information

```shell
# Show the size of installed memory (including empty slots)
dmidecode -t memory |grep -i size

# Show only the slots that actually have memory installed
dmidecode -t memory |grep -i size | egrep -Ev No

# Count the number of populated memory slots
dmidecode -t memory |grep -i size | egrep -Ev No | wc -l

# Show total memory capacity
free -mh

# When `dmidecode -t memory` output includes lines like "Volatile Size"
# Count total slots = (slots with GB value) + (No Module Installed) - (Volatile Size lines)
dmidecode -t memory | egrep "Size: ([0-9]+ GB|No Module Installed)" |grep -v "Volatile Size:" | wc -l

# List installed memory modules and count them
dmidecode -t memory | egrep "Size: [0-9]+ GB" | grep -v "Volatile Size:"
dmidecode -t memory | egrep "Size: [0-9]+ GB" | grep -v "Volatile Size:"| wc -l

# List empty slots and count them
dmidecode -t memory | egrep "Size: No Module Installed"
dmidecode -t memory | egrep "Size: No Module Installed" | wc -l

# Check the DDRx generation of the installed memory
lshw -short -C memory
```

![2022-10-27 13 15 45](https://user-images.githubusercontent.com/76153041/198190125-d0cf6441-4bc3-4acd-b5eb-f4c6acc96fc2.png)

![Image](https://github-production-user-asset-6210df.s3.amazonaws.com/76153041/445567781-4e1a1825-c315-43c1-9e8b-97f68cb54b7d.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAVCODYLSA53PQK4ZA%2F20250520%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250520T105847Z&X-Amz-Expires=300&X-Amz-Signature=161f1921bc2d12cc40c6c37e3186d2cb3cf453b044d40ce982dc73f9064ea1db&X-Amz-SignedHeaders=host)

# [04] Disk Information

```shell
# Show disk devices
lsblk

# Show disk devices with bus info
lshw -c disk -businfo
```

# [05] Network Information

```shell
# Show network devices with bus info
lshw -c network -businfo
```

![2022-10-27 13 44 10](https://user-images.githubusercontent.com/76153041/198193433-2e10005b-9618-4583-a2af-9b49607e5d90.png)

# [06] GPU Information

```shell
# Show display/GPU devices
lshw -C display

# When using an NVIDIA GPU with the driver installed
nvidia-smi
```
