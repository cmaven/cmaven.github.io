---
title: "Checking RAID Environment Disks on Ubuntu — MegaRAID + smartctl Guide"
description: "How to verify RAID Controller, Virtual Disk, and Physical Disk status on an Ubuntu server using lsblk/lspci/smartctl, including SSD SMART check on MegaRAID"
excerpt: "The disk visible to the OS may be a Virtual Disk — use smartctl with the megaraid option to inspect Physical Disks behind the RAID Controller"
date: 2026-05-06
categories: Storage
tags: [Ubuntu, RAID, MegaRAID, smartctl, smartmontools, SSD, lsblk, lspci, RAID1, SMART, Physical-Disk]
ref: ubuntu-raid-disk-check-megaraid
---

:bulb: How to verify disk devices, RAID Controller, and the SMART status of Physical Disks hidden behind RAID on Ubuntu.
{: .notice--info}

**Environment**: Ubuntu 22.04 + LSI MegaRAID SAS3108 (Intel RMS3CC080 OEM) + 2× Intel SSD S4510 480GB + RAID1

---

# [01] Understanding the Overall Structure

The disk the OS sees may differ from the actual Physical Disk. When a RAID Controller sits in between, the OS sees only the Virtual Disk.

<pre class="mermaid">
graph TD
    OS["Ubuntu OS<br/>/dev/sda (446GiB)"] --> VD["Virtual Disk<br/>(RAID1 Mirror)"]
    VD --> CTRL["LSI MegaRAID SAS3108<br/>RAID Controller"]
    CTRL --> PD1["Physical Disk 8<br/>Intel SSD 480GB"]
    CTRL --> PD2["Physical Disk 9<br/>Intel SSD 480GB"]

    style OS fill:#e3f2fd,stroke:#1565c0
    style VD fill:#fff3e0,stroke:#e65100
    style CTRL fill:#fce4ec,stroke:#c62828
    style PD1 fill:#e8f5e9,stroke:#2e7d32
    style PD2 fill:#e8f5e9,stroke:#2e7d32
</pre>

---

# [02] Disk Device and Slot Check

## 2-1. Basic Disk List

```bash
lsblk -d -o NAME,SIZE,MODEL,SERIAL
```

**Sample output:**

```
NAME    SIZE MODEL     SERIAL
sda   446.1G RMS3CC080 008348090b453e172b10c13010b00506
```

| Field | Description |
|-------|-------------|
| NAME | Device name |
| SIZE | Disk capacity |
| MODEL | Disk model (may be the Virtual Disk model) |
| SERIAL | Serial number |

## 2-2. SCSI Device Check

```bash
lsscsi -g
```

**Sample output:**

```
[0:2:0:0]    disk    Intel    RMS3CC080        4.65  /dev/sda   /dev/sg0
```

| Field | Description |
|-------|-------------|
| disk | Device type |
| RMS3CC080 | RAID Controller or Virtual Disk |
| /dev/sda | Virtual Disk exposed to OS |
| /dev/sg0 | Generic SCSI Device |

## 2-3. RAID Controller via PCI

```bash
lspci | grep -i -E 'raid|sas|scsi|lsi|broadcom'
```

**Sample output:**

```
5e:00.0 RAID bus controller: Broadcom / LSI MegaRAID SAS-3 3108 [Invader] (rev 02)
```

## 2-4. RAID Driver Check

```bash
lsmod | grep megaraid
```

**Sample output:**

```
megaraid_sas          188416  3
```

---

# [03] RAID Configuration Check

## 3-1. Linux Software RAID (mdadm)

```bash
cat /proc/mdstat
```

**Sample output:**

```
Personalities : [raid1] [raid5] [raid6]
unused devices: <none>
```

:bulb: `unused devices: <none>` means no mdadm-based Software RAID is in use. Normal for Hardware RAID (MegaRAID) environments like above.
{: .notice--info}

## 3-2. Install smartmontools

To check Physical Disk status, install `smartmontools`.

```bash
sudo apt update
sudo apt install smartmontools -y
```

## 3-3. Scan Physical Disks Behind RAID

```bash
sudo smartctl --scan
```

**Sample output:**

```
/dev/sda -d scsi
/dev/bus/0 -d megaraid,8
/dev/bus/0 -d megaraid,9
```

| Item | Description |
|------|-------------|
| `megaraid,8` | Physical Disk index 8 |
| `megaraid,9` | Physical Disk index 9 |

`/dev/bus/0` is the direct access path to the RAID Controller, and `-d megaraid,N` selects each Physical Disk.

---

# [04] Physical Disk SMART Check

## 4-1. Single Disk Detail

```bash
sudo smartctl -a -d megaraid,8 /dev/bus/0
```

**Sample output (key fields):**

```
Device Model:     INTEL SSDSC2KB480G8
Serial Number:    BTYF2083027D480BGN
User Capacity:    480,103,981,056 bytes [480 GB]
SMART overall-health self-assessment test result: PASSED
```

## 4-2. Batch Check Multiple Disks

```bash
for i in 8 9; do
  echo "========================="
  echo "Physical Disk $i"
  sudo smartctl -a -d megaraid,$i /dev/bus/0 | \
    grep -E "Product|Model|Serial|User Capacity|SMART overall"
done
```

**Sample output:**

```
=========================
Physical Disk 8
Device Model:     INTEL SSDSC2KB480G8
Serial Number:    BTYF2083027D480BGN
User Capacity:    480 GB
SMART overall-health self-assessment test result: PASSED

=========================
Physical Disk 9
Device Model:     INTEL SSDSC2KB480G8
Serial Number:    BTYF20830230480BGN
User Capacity:    480 GB
SMART overall-health self-assessment test result: PASSED
```

---

# [05] Inferring RAID Configuration

For the current example:

| Item | Value |
|------|-------|
| Physical Disk | 480GB SSD × 2 |
| OS-visible capacity | 446GiB (≈ 480GB) |
| Inferred | **RAID1 (Mirror)** |

:bulb: If the OS saw ~960GB, it would be RAID0/JBOD. If somewhat less than 960GB, RAID5/6.
{: .notice--info}

---

# [06] SSD Status Key Checkpoints

## 6-1. Temperature

```bash
sudo smartctl -a -d megaraid,8 /dev/bus/0 | grep Temperature
```

**Sample output:**

```
Temperature_Celsius     21
```

| Range | Status |
|-------|--------|
| 0–40°C | Normal |
| 40–60°C | Caution (review workload) |
| 60°C+ | Critical (check cooling/failure) |

## 6-2. Wear Level (Lifespan)

```bash
sudo smartctl -a -d megaraid,8 /dev/bus/0 | grep -i wear
```

**Sample output:**

```
Workld_Media_Wear_Indic
Media_Wearout_Indicator
```

SSD lifespan indicator. Counts down from 100 toward 0 — closer to 0 means time to replace.

## 6-3. Bad Block Check

```bash
sudo smartctl -a -d megaraid,8 /dev/bus/0 | \
  grep -E "Reallocated|Pending|CRC"
```

**Healthy output:**

```
Reallocated_Sector_Ct   0
Pending_Sector_Count    0
CRC_Error_Count         0
```

:warning: If `Reallocated_Sector_Ct` or `Pending_Sector_Count` is **non-zero**, consider replacing the disk. Accumulated CRC errors may indicate a cabling/connection issue.
{: .notice--warning}

---

# [07] Quick Start — Step by Step

```bash
# Step 1. Check disks
lsblk -d -o NAME,SIZE,MODEL,SERIAL

# Step 2. Identify RAID Controller
lspci | grep -i -E 'raid|sas|scsi|lsi|broadcom'

# Step 3. Confirm RAID driver
lsmod | grep megaraid

# Step 4. Install smartmontools
sudo apt update && sudo apt install smartmontools -y

# Step 5. Scan Physical Disks
sudo smartctl --scan

# Step 6. Check Physical Disk status
sudo smartctl -a -d megaraid,8 /dev/bus/0

# Step 7. Batch check all disks
for i in 8 9; do
  echo "========================="
  echo "PD $i"
  sudo smartctl -a -d megaraid,$i /dev/bus/0 | \
    grep -E "Model|Serial|User Capacity|SMART overall"
done
```

---

# [08] Summary

| Key point | Description |
|-----------|-------------|
| OS disk ≠ Physical Disk | With a RAID Controller, the OS sees only the Virtual Disk |
| Hardware RAID ID | `lspci` for RAID Controller model; `/proc/mdstat` for Software RAID |
| Physical Disk access | `smartctl -d megaraid,N /dev/bus/0` required |
| Infer RAID config | OS-visible capacity ÷ Physical Disk count gives RAID Level hint |
| SMART check | Temperature, Wear Level, Reallocated/Pending Sector, CRC errors |

:bulb: In RAID environments, checking only the OS-visible disk isn't enough. Verify SMART status of each Physical Disk behind the RAID Controller to catch failures early.
{: .notice--info}
