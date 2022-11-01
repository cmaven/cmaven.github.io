---
title: "우분투(Linux)에서 대용량 디스크 마운트하기"
category: Linux
tags: [Ubuntu]
date: 2022-10-28
---

우분투 환경에서, 2TB 이상의 디스크를 마운트하기
------

### 디스크 정보 확인  
- 아래 시스템에서, 3.7TB로 인식되는 디스크를 포맷하고 마운트한다.
  - 일반적인 `fdisk` 명령어로 포맷 및 마운트 시, `2TB`까지만 인식

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

### parted - 파티션 설정  

- 디스크 파티션 및 파티션 재설정 프로그램  

```shell
# (parted) 엔터 혹은 명령어 입력
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

- 파티션 생성 후
![fdisk-01(자르기)](https://user-images.githubusercontent.com/76153041/199198008-4bcc8161-fd47-4b7e-a6a2-7f5c614501c1.png)  


### mkfs - 포맷  
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

### 마운트  

```shell
# 마운트 위치 생성
root@test:~# mkdir /mnt/sdd
# 마운트
root@test:~# mount /dev/sdd1 /mnt/sdd
# 마운트된 디렉토리 읽기,쓰기 권한 설정
root@test:~# chmod 775 /mnt/sdd
```  

- 마운트 완료 후, 결과 확인  
  - `/dev/sdd1` 이, 2TB 넘는 용량으로 `/mnt/sdd` 에 마운트 됨을 확인
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

### 부팅 시, 자동으로 마운트 시키기  
- `/etc/fstab` 파일을 아래와 같이 수정

```shell
# /etc/fstab

/dev/sdd1 /mnt/sdd ext4 defaults 0 0 
```  

![2022-11-01 17 43 12](https://user-images.githubusercontent.com/76153041/199199148-7378ae07-310b-42b1-979d-73f015066de3.png)