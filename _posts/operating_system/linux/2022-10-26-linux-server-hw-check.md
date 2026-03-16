---
title: "서버에 장착된 CPU,메모리,디스크,네트워크 장치 상태(슬롯별 용량,제조사 등) 확인하기"
description: "Ubuntu 서버에서 CPU, 메모리, 디스크, 네트워크, GPU 등 하드웨어 정보를 확인하는 명령어 모음"
excerpt: "dmidecode, lscpu, lshw, lsblk 등을 활용한 Linux 서버 하드웨어 정보 확인 방법"
categories: Linux
tags: [Ubuntu, CPU, Memory, Disk, Network, GPU, dmidecode, lscpu, lshw, 하드웨어확인]
date: 2022-10-26
---

:bulb: 서버에 장착된 CPU, Memory, Disk, Network Interface Card, GPU 등 하드웨어 정보를 확인하는 방법을 작성한다.
{: .notice--info}

📘 Ubuntu 20.04 Server 기준

# [01] 관련 명령어

| 명령어 | 설명 |
|---|---|
| `dmidecode` | 시스템 DMI(SMBIOS) 테이블의 하드웨어 정보를 출력 |
| `free` | 시스템 메모리의 사용 가능/사용 중인 양을 출력 |
| `lshw` | 메모리 설정, 펌웨어 버전, CPU 속도, 버스 스피드 등 하드웨어 설정 정보 추출 |
| `lsblk` | 블럭 디바이스 정보를 `sysfs` 파일 시스템에서 정제하여 출력 |
| `lscpu` | CPU 아키텍처, 코어/스레드 수, 소켓 수 등 CPU 정보 출력 |

# [02] CPU 정보 확인

```shell
lscpu

# 필요 정보만 추출
# Architecture, Processor 수, Core당 Thread 수, Socket 당 Core 수, Socket 수, 모델명, NUMA 정보
# Processer = Core * Core 당 Thread 수 * Socket 수
lscpu |grep -E 'Archi|On-line|Thread|socket|Socket|Model |NUMA'
```

![2022-10-27 13 40 43](https://user-images.githubusercontent.com/76153041/198193272-fca3526b-c86a-4dc6-a1ac-a958f9d9cc3b.png)

# [03] 메모리 정보 확인

```shell
# 장착된 메모리 사이즈 보기 (비어있는 슬롯까지 확인)
dmidecode -t memory |grep -i size

# 메모리가 장착된 총 슬롯의 메모리 사이즈만 확인
dmidecode -t memory |grep -i size | egrep -Ev No

# 메모리가 장착된 총 슬롯의 수 확인
dmidecode -t memory |grep -i size | egrep -Ev No | wc -l

# 메모리 전체 용량 보기
free -mh

# dmidecode -t memory 결과에 Volatile Size 등의 결과가 포함될 경우
# 서버의 총 메모리 수 확인 (Size에 GB값이 있는 부분 + No Module(설치안된 부분) - Volatile Size 부분 제외)
dmidecode -t memory | egrep "Size: ([0-9]+ GB|No Module Installed)" |grep -v "Volatile Size:" | wc -l

# 서버에 장착된 메모리 확인 및 수 확인
dmidecode -t memory | egrep "Size: [0-9]+ GB" | grep -v "Volatile Size:"
dmidecode -t memory | egrep "Size: [0-9]+ GB" | grep -v "Volatile Size:"| wc -l

# 서버에 장착되지 않은 슬롯 및 수 확인
dmidecode -t memory | egrep "Size: No Module Installed"
dmidecode -t memory | egrep "Size: No Module Installed" | wc -l

# 서버에 장착된 메모리의 DDRx 확인
lshw -short -C memory
```

![2022-10-27 13 15 45](https://user-images.githubusercontent.com/76153041/198190125-d0cf6441-4bc3-4acd-b5eb-f4c6acc96fc2.png)

![Image](https://github-production-user-asset-6210df.s3.amazonaws.com/76153041/445567781-4e1a1825-c315-43c1-9e8b-97f68cb54b7d.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAVCODYLSA53PQK4ZA%2F20250520%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250520T105847Z&X-Amz-Expires=300&X-Amz-Signature=161f1921bc2d12cc40c6c37e3186d2cb3cf453b044d40ce982dc73f9064ea1db&X-Amz-SignedHeaders=host)

# [04] 디스크 정보 확인

```shell
# 디스크 장치 정보 보기
lsblk

# 디스크 장치 정보 보기
lshw -c disk -businfo
```

# [05] 네트워크 정보 확인

```shell
# 네트워크 장치 정보 보기
lshw -c network -businfo
```

![2022-10-27 13 44 10](https://user-images.githubusercontent.com/76153041/198193433-2e10005b-9618-4583-a2af-9b49607e5d90.png)

# [06] GPU 정보 확인

```shell
# gpu display 확인
lshw -C display

# nvidia-gpu 이며, driver 설치된 경우
nvidia-smi
```
