---
title: "서버에 장착된 CPU,메모리,디스크,네트워크 장치 상태(슬롯별 용량,제조사 등) 확인하기"
category: Linux
tags: [CPU,Memory,Disk,Network]
date: 2022-10-26
---

서버에 장착된 하드웨어 정보를 확인한다.

------  

> CPU, Memory, Disk, Network Interface Card 정보 확인  

### 환경
- Ubuntu 20.04 Server

### 관련 명령어  

#### dmidecode
- 시스템에 장착된 하드웨어 정보를 확인할 때 사용
- 컴퓨터의 DMI(Desktop Management Interface, SMBIOS) 테이블의 정보를 사용자가 알아보기 쉽게 변경하여 출력함  

#### free
- 시스템의 메모리의 사용 가능한 양, 사용 중인 양을 출력

#### lshw
- 시스템의 하드웨어 설정 정보를 추출
- 메모리 설정, 펌웨어 버전, 메인보드 설정, CPU 버전/속도, 캐시설정, 버스 스피드 등을 확인 가능함

#### lsblk
- 특정 블럭 디바이스의 정보를 표현함
- `sysfs` 파일 시스템으로 확인 가능한 정보를 정제하여 출력


### CPU 정보 확인
```shell
lscpu

# 필요 정보만 추출
# Architecture, Processor 수, Core당 Thread 수, Socket 당 Core 수, Socket 수, 모델명, NUMA 정보
# Processer = Core * Core 당 Thread 수 * Socket 수
lscpu |grep -E 'Archi|On-line|Thread|socket|Socket|Model |NUMA'
```

![2022-10-27 13 40 43](https://user-images.githubusercontent.com/76153041/198193272-fca3526b-c86a-4dc6-a1ac-a958f9d9cc3b.png)  


### 메모리 정보 확인

```shell
# 장착된 메모리 사이즈 보기 (비어잇는 슬롯까지 확인)
dmidecode -t memory |grep -i size

# 메모리가 장착된 총 슬롯의 메모리 사이즈만 확인
dmidecode -t memory |grep -i size | egrep -Ev No

# 메모리가 장착된 총 슬롯의 수 확인
dmidecode -t memory |grep -i size | egrep -Ev No | wc -l

# 메모리 전체 용량 보기
free -mh
```

![2022-10-27 13 15 45](https://user-images.githubusercontent.com/76153041/198190125-d0cf6441-4bc3-4acd-b5eb-f4c6acc96fc2.png)


### 디스크 정보 확인

```shell
# 디스크 장치 정보 보기
lsblk 

# 디스크 장치 정보 보기
lshw -c disk -businfo
```

### 네트워크 정보 확인  

```shell
# 네트워크 장치 정보 보기
lshw -c network -businfo
```

![2022-10-27 13 44 10](https://user-images.githubusercontent.com/76153041/198193433-2e10005b-9618-4583-a2af-9b49607e5d90.png)