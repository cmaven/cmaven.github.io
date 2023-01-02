---
title: "우분투(Linux)에서 하드디스크(HDD) 완전 삭제"
category: Linux
tags: [Ubuntu, Shred]
date: 2023-01-02
---

우분투에서 하드디스크 완전 삭제
------

> shred?  

- 데이터 복구가 어렵도록, 실제 데이터를 쓰고/지우는 것을 반복하는(default 3) 명령어

### 설치  
- Ubuntu 20.04

```shell
apt-get install coreutils
```  

### 디스크 삭제 준비

- 디스크 확인

```shell
lsblk

# ex) sdg, sdf 를 삭제하고자 함
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

- 파티션이 존재하면 삭제

```shell
# sdx는 삭제하려는 파티션이 존재하는 디스크 
fdisk /dev/sdx

# ex) 
# 파티션 확인 command (p)
# 파티션 삭제 command (d)
# 실행 내용 저장 command (w)
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

### 디스크 삭제

- 사용할 옵션
  - `-v` : 진행사항을 보여줌
  - `-n1` : 반복하여 쓰기/지우기를 수행할 횟 수(default 3)
  - `-z` : 마지막 쓰기 시, Zero 값으로 덮어쓰기

```shell
sudo shred -v -z -n3 /dev/sdx
```  

[참조][How can I seurely erase a hard drive?](https://askubuntu.com/questions/17640/how-can-i-securely-erase-a-hard-drive){: target="_blank"} 
[참조][shred - Linux man page](https://linux.die.net/man/1/shred){: target="_blank"} 
