---
title: "Mounting a Large Disk on Ubuntu (Linux)"
description: "How to create a GPT partition with parted and mount a disk larger than 2TB on Ubuntu"
excerpt: "Use parted instead of fdisk to format disks larger than 2TB as GPT and mount them"
categories: Linux
tags: [Ubuntu, parted, GPT, mount, fstab, large-disk, disk-mount]
date: 2022-10-28
last_modified_at: 2026-05-26
ref: ubuntu-largedisk-mount
---

:bulb: This post describes how to format and mount a disk larger than 2TB on Ubuntu.
{: .notice--info}

:warning: The traditional `fdisk` command only recognizes up to `2TB`. For disks larger than 2TB you must use `parted`.
{: .notice--warning}

# [01] Check the Disk

On the following system, we will format and mount a disk reported as 3.7TB.

```shell
root@test:~# lsblk
NAME                      MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
loop0                       7:0    0  55.6M  1 loop /snap/core18/2560
loop1                       7:1    0  55.6M  1 loop /snap/core18/2566
sda                         8:0    0 953.9G  0 disk
├─sda1                      8:1    0   512M  0 part /boot/efi
├─sda2                      8:2    0     1G  0 part /boot
└─sda3                      8:3    0 952.4G  0 part
  └─ubuntu--vg-ubuntu--lv 253:0    0 952.4G  0 lvm  /
sdb                         8:16   0 931.5G  0 disk
sdc                         8:32   0   3.7T  0 disk
sdd                         8:48   0   3.7T  0 disk
```

# [02] parted - Partition Setup

`parted` is a disk partitioning and re-partitioning utility.

```shell
# At the (parted) prompt, press Enter or type commands
# mklabel gpt - yes - mkpart - (enter) - ext4 - 1 - 3.7TB - q
root@test:~# parted /dev/sdd
GNU Parted 3.3
Using /dev/sdd
Welcome to GNU Parted! Type 'help' to view a list of commands.
(parted) mklabel gpt
Warning: The existing disk label on /dev/sdd will be destroyed and all data on this disk will be lost. Do you want to continue?
Yes/No? yes
(parted)
(parted) mkpart
Partition name?  []?
File system type?  [ext2]? ext4
Start? 1
End? 3.7TB
(parted) q
Information: You may need to update /etc/fstab.
```

After creating the partition:

![fdisk-01](https://user-images.githubusercontent.com/76153041/199198008-4bcc8161-fd47-4b7e-a6a2-7f5c614501c1.png)

# [03] mkfs - Format

```shell
root@test:~# mkfs.ext4 /dev/sdd1
mke2fs 1.45.5 (07-Jan-2020)
/dev/sdd1 contains a ext4 file system
        created on Tue Nov  1 08:25:01 2022
Proceed anyway? (y,N) y
Creating filesystem with 976754176 4k blocks and 244195328 inodes
Filesystem UUID: a0ce91ce-e19f-4266-80bd-09868c4faafc
Superblock backups stored on blocks:
        32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208,
        4096000, 7962624, 11239424, 20480000, 23887872, 71663616, 78675968,
        102400000, 214990848, 512000000, 550731776, 644972544

Allocating group tables: done
Writing inode tables: done
Creating journal (262144 blocks): done
Writing superblocks and filesystem accounting information: done
```

# [04] Mount

```shell
# Create the mount point
root@test:~# mkdir /mnt/sdd
# Mount
root@test:~# mount /dev/sdd1 /mnt/sdd
# Set read/write permissions on the mounted directory
root@test:~# chmod 775 /mnt/sdd
```

After mounting, verify the result:

- `/dev/sdd1` is mounted at `/mnt/sdd` with a capacity larger than 2TB

```shell
root@test:~# df -h
Filesystem                         Size  Used Avail Use% Mounted on
udev                                24G     0   24G   0% /dev
tmpfs                              4.7G  2.1M  4.7G   1% /run
/dev/mapper/ubuntu--vg-ubuntu--lv  937G  156G  734G  18% /
tmpfs                               24G     0   24G   0% /dev/shm
tmpfs                              5.0M  4.0K  5.0M   1% /run/lock
tmpfs                               24G     0   24G   0% /sys/fs/cgroup
/dev/sda2                          974M  318M  589M  36% /boot
/dev/sda1                          511M  5.3M  506M   2% /boot/efi
/dev/loop0                          56M   56M     0 100% /snap/core18/2560
tmpfs                              4.7G   24K  4.7G   1% /run/user/128
tmpfs                              4.7G     0  4.7G   0% /run/user/0
/dev/sdd1                          3.6T   28K  3.4T   1% /mnt/sdd
```

# [05] Auto-mount at Boot

Add the following line to `/etc/fstab`.

```shell
# /etc/fstab

/dev/sdd1 /mnt/sdd ext4 defaults 0 0
```

![2022-11-01 17 43 12](https://user-images.githubusercontent.com/76153041/199199148-7378ae07-310b-42b1-979d-73f015066de3.png)
