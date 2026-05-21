---
title: "Securely Erasing a Hard Disk (HDD) on Ubuntu (Linux)"
description: "How to securely erase a hard disk (low-level format) on Ubuntu using shred, badblocks, and dd"
excerpt: "How to securely erase a Linux hard disk (unrecoverable) using shred, badblocks, and dd"
date: 2023-01-02
categories: Linux
tags: [Ubuntu, shred, badblocks, dd, HDD, disk-erase, low-level-format, data-wipe]
ref: ubuntu-disk-erase
---

:bulb: This guide describes how to securely erase a hard disk on Ubuntu (so the data cannot be recovered).
{: .notice--info}

Based on Ubuntu 24.04.

# [01] Summary

```shell
sudo shred -v -z -n3 /dev/sdx
sudo badblocks -w -c 600 /dev/sdx
dd if=/dev/urandom of=/dev/sdx bs=1M
```

# [02] shred

> A command that repeatedly writes and erases real data (3 passes by default) to make data recovery difficult.

## 2-1. Install

```shell
apt-get install coreutils
```

## 2-2. Prepare the Disk for Erasure

Check the disks:

```shell
lsblk

# ex) Targeting sdg and sdf for erasure
root@gedgem01:~# lsblk
NAME                      MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
loop0                       7:0    0  55.6M  1 loop /snap/core18/2654
sda                         8:0    0 953.9G  0 disk
├─sda1                      8:1    0   512M  0 part /boot/efi
├─sda2                      8:2    0     1G  0 part /boot
└─sda3                      8:3    0 952.4G  0 part
  └─ubuntu--vg-ubuntu--lv 253:0    0 952.4G  0 lvm  /
sdb                         8:16   0 931.5G  0 disk
sdc                         8:32   0   3.7T  0 disk
sdd                         8:48   0   3.7T  0 disk
└─sdd1                      8:49   0   3.7T  0 part /mnt/sdd
sdf                         8:80   0   1.8T  0 disk
├─sdf1                      8:81   0   2.4G  0 part
├─sdf2                      8:82   0     2G  0 part
├─sdf3                      8:83   0     1K  0 part
└─sdf5                      8:85   0   1.8T  0 part
sdg                         8:96   0   1.8T  0 disk
```

If partitions exist, delete them first:

```shell
# sdx is the disk holding the partitions you want to remove
fdisk /dev/sdx

# ex)
# Print partitions command (p)
# Delete partition command (d)
# Save changes command (w)
root@gedgem01:~# fdisk /dev/sdf

Welcome to fdisk (util-linux 2.34).
Changes will remain in memory only, until you decide to write them.
Be careful before using the write command.


Command (m for help): p
Disk /dev/sdf: 1.84 TiB, 2000398934016 bytes, 3907029168 sectors
Disk model: 001-1CM164
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
Disklabel type: dos
Disk identifier: 0x00014c49

Device     Boot   Start        End    Sectors  Size Id Type
/dev/sdf1          2048    4982527    4980480  2.4G fd Linux raid autodetect
/dev/sdf2       4982528    9176831    4194304    2G fd Linux raid autodetect
/dev/sdf3       9437184 3907015007 3897577824  1.8T  f W95 Ext'd (LBA)
/dev/sdf5       9453280 3906822239 3897368960  1.8T fd Linux raid autodetect

Command (m for help): d
Partition number (1-3,5, default 5): 5

Partition 5 has been deleted.

Command (m for help): d
Partition number (1-3, default 3): 3

Partition 3 has been deleted.

Command (m for help): d
Partition number (1,2, default 2): 2

Partition 2 has been deleted.

Command (m for help): d
Selected partition 1
Partition 1 has been deleted.

Command (m for help): p
Disk /dev/sdf: 1.84 TiB, 2000398934016 bytes, 3907029168 sectors
Disk model: 001-1CM164
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 4096 bytes
I/O size (minimum/optimal): 4096 bytes / 4096 bytes
Disklabel type: dos
Disk identifier: 0x00014c49

Command (m for help): w
The partition table has been altered.
Calling ioctl() to re-read partition table.
Syncing disks.
```

## 2-3. Erase the Disk

- `-v` : show progress
- `-n1` : number of write/erase iterations to perform (default is 3)
- `-z` : overwrite with zeros on the final pass

```shell
sudo shred -v -z -n3 /dev/sdx
```

:small_blue_diamond:Reference: [How can I securely erase a hard drive?](https://askubuntu.com/questions/17640/how-can-i-securely-erase-a-hard-drive){:target="_blank"}
:small_blue_diamond:Reference: [shred - Linux man page](https://linux.die.net/man/1/shred){:target="_blank"}

# [03] badblocks

> A command used to find bad blocks (physically damaged areas) on a disk. It writes random values to the disk and reads them back to detect bad blocks, and we leverage that behavior for secure erasure.

## 3-1. Install

```shell
apt-get install e2fsprogs
```

## 3-2. Erase the Disk

- `-w` : write random values (0xaa, 0x55, 0xff, 0x00) to every block on the device, read them back, and compare to determine whether bad blocks exist
- `-c` : the number of blocks tested at once (default is 64)

```shell
# Typical block sizes are 512, 4096, 32768, etc.
sudo badblocks -w -c 600 /dev/sdx
```

# [04] dd

> Commonly used on Linux for low-level formatting. Writes random data to the device.

```shell
dd if=/dev/urandom of=/dev/sdx bs=1M
```
