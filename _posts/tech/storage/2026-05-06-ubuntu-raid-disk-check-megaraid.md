---
title: "Ubuntu에서 RAID 환경 디스크 확인하기 — MegaRAID + smartctl 가이드"
description: "Ubuntu 서버의 RAID Controller, Virtual Disk, Physical Disk 상태를 lsblk/lspci/smartctl로 확인하는 방법과 MegaRAID 환경에서 실제 SSD 상태 점검 절차"
excerpt: "OS에 보이는 디스크는 Virtual Disk일 수 있다 — RAID Controller 뒤의 Physical Disk를 smartctl megaraid 옵션으로 확인하기"
date: 2026-05-06
categories: Storage
tags: [Ubuntu, RAID, MegaRAID, smartctl, smartmontools, SSD, lsblk, lspci, RAID1, SMART, Physical-Disk]
---

:bulb: Ubuntu 서버 환경에서 디스크 장치, RAID Controller, 그리고 RAID 뒤에 숨겨진 Physical Disk의 상태(SMART)를 확인하는 방법을 정리한다.
{: .notice--info}

**환경**: Ubuntu 22.04 + LSI MegaRAID SAS3108 (Intel RMS3CC080 OEM) + Intel SSD S4510 480GB x2 + RAID1

---

# [01] 전체 구조 이해

OS가 보는 디스크와 실제 Physical Disk는 다를 수 있다. RAID Controller가 중간에 끼면 OS는 Virtual Disk만 본다.

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

# [02] 디스크 장치 및 슬롯 확인

## 2-1. 기본 디스크 목록

```bash
lsblk -d -o NAME,SIZE,MODEL,SERIAL
```

**출력 예시:**

```
NAME    SIZE MODEL     SERIAL
sda   446.1G RMS3CC080 008348090b453e172b10c13010b00506
```

| 항목 | 설명 |
|---|---|
| NAME | 디스크 장치명 |
| SIZE | 디스크 용량 |
| MODEL | 디스크 모델 (Virtual Disk 모델로 표시될 수 있음) |
| SERIAL | 디스크 시리얼 |

## 2-2. SCSI 장치 확인

```bash
lsscsi -g
```

**출력 예시:**

```
[0:2:0:0]    disk    Intel    RMS3CC080        4.65  /dev/sda   /dev/sg0
```

| 항목 | 설명 |
|---|---|
| disk | 디스크 타입 |
| RMS3CC080 | RAID Controller 또는 Virtual Disk |
| /dev/sda | OS에 노출된 Virtual Disk |
| /dev/sg0 | Generic SCSI Device |

## 2-3. PCI 장치로 RAID Controller 확인

```bash
lspci | grep -i -E 'raid|sas|scsi|lsi|broadcom'
```

**출력 예시:**

```
5e:00.0 RAID bus controller: Broadcom / LSI MegaRAID SAS-3 3108 [Invader] (rev 02)
```

## 2-4. RAID 드라이버 확인

```bash
lsmod | grep megaraid
```

**출력 예시:**

```
megaraid_sas          188416  3
```

---

# [03] RAID 구성 확인

## 3-1. Linux Software RAID (mdadm)

```bash
cat /proc/mdstat
```

**출력 예시:**

```
Personalities : [raid1] [raid5] [raid6]
unused devices: <none>
```

:bulb: `unused devices: <none>`이면 mdadm 기반 Software RAID는 사용 중이지 않다. 위 환경처럼 Hardware RAID(MegaRAID)인 경우 정상이다.
{: .notice--info}

## 3-2. smartmontools 설치

Physical Disk 상태를 확인하려면 `smartmontools` 패키지가 필요하다.

```bash
sudo apt update
sudo apt install smartmontools -y
```

## 3-3. RAID 뒤 Physical Disk 검색

```bash
sudo smartctl --scan
```

**출력 예시:**

```
/dev/sda -d scsi
/dev/bus/0 -d megaraid,8
/dev/bus/0 -d megaraid,9
```

| 항목 | 설명 |
|---|---|
| `megaraid,8` | Physical Disk index 8 |
| `megaraid,9` | Physical Disk index 9 |

`/dev/bus/0`은 RAID Controller에 대한 직접 접근 경로이고, `-d megaraid,N` 옵션으로 각 Physical Disk를 지정한다.

---

# [04] Physical Disk SMART 확인

## 4-1. 단일 디스크 상세 확인

```bash
sudo smartctl -a -d megaraid,8 /dev/bus/0
```

**출력 예시 (주요 항목):**

```
Device Model:     INTEL SSDSC2KB480G8
Serial Number:    BTYF2083027D480BGN
User Capacity:    480,103,981,056 bytes [480 GB]
SMART overall-health self-assessment test result: PASSED
```

## 4-2. 여러 디스크 일괄 확인

```bash
for i in 8 9; do
  echo "========================="
  echo "Physical Disk $i"
  sudo smartctl -a -d megaraid,$i /dev/bus/0 | \
    grep -E "Product|Model|Serial|User Capacity|SMART overall"
done
```

**출력 예시:**

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

# [05] RAID 구성 추론

현재 예시의 경우:

| 항목 | 값 |
|------|---|
| Physical Disk | 480GB SSD x 2 |
| OS 노출 용량 | 446GiB (≈ 480GB) |
| 추론 | **RAID1 (Mirror)** |

:bulb: 만약 OS 노출 용량이 ~960GB였다면 RAID0/JBOD, ~960GB에서 일부 빠진 형태였다면 RAID5/6로 추론할 수 있다.
{: .notice--info}

---

# [06] SSD 상태 핵심 점검 포인트

## 6-1. 온도 확인

```bash
sudo smartctl -a -d megaraid,8 /dev/bus/0 | grep Temperature
```

**출력 예시:**

```
Temperature_Celsius     21
```

| 온도 범위 | 상태 |
|----------|------|
| 0~40°C | 정상 |
| 40~60°C | 주의 (워크로드 점검) |
| 60°C 이상 | 위험 (쿨링/장애 점검) |

## 6-2. Wear Level (수명)

```bash
sudo smartctl -a -d megaraid,8 /dev/bus/0 | grep -i wear
```

**출력 예시:**

```
Workld_Media_Wear_Indic
Media_Wearout_Indicator
```

SSD 수명 지표. 값이 100에서 0으로 줄어들며, 0에 가까울수록 교체 시점이다.

## 6-3. 배드블록 확인

```bash
sudo smartctl -a -d megaraid,8 /dev/bus/0 | \
  grep -E "Reallocated|Pending|CRC"
```

**정상 출력 예시:**

```
Reallocated_Sector_Ct   0
Pending_Sector_Count    0
CRC_Error_Count         0
```

:warning: `Reallocated_Sector_Ct` 또는 `Pending_Sector_Count`가 **0이 아니면** 디스크 교체를 검토해야 한다. CRC 오류가 누적되면 케이블/연결 문제일 수 있다.
{: .notice--warning}

---

# [07] 빠른 시작 — Step by Step

```bash
# Step 1. 디스크 확인
lsblk -d -o NAME,SIZE,MODEL,SERIAL

# Step 2. RAID Controller 확인
lspci | grep -i -E 'raid|sas|scsi|lsi|broadcom'

# Step 3. RAID Driver 확인
lsmod | grep megaraid

# Step 4. smartmontools 설치
sudo apt update && sudo apt install smartmontools -y

# Step 5. Physical Disk 검색
sudo smartctl --scan

# Step 6. Physical Disk 상태 확인
sudo smartctl -a -d megaraid,8 /dev/bus/0

# Step 7. 모든 디스크 상태 일괄 확인
for i in 8 9; do
  echo "========================="
  echo "PD $i"
  sudo smartctl -a -d megaraid,$i /dev/bus/0 | \
    grep -E "Model|Serial|User Capacity|SMART overall"
done
```

---

# [08] 정리

| 핵심 포인트 | 설명 |
|------------|------|
| OS에 보이는 디스크 ≠ Physical Disk | RAID Controller가 있으면 OS는 Virtual Disk만 본다 |
| Hardware RAID 식별 | `lspci`로 RAID Controller 모델 확인, `/proc/mdstat`로 Software RAID 여부 확인 |
| Physical Disk 접근 | `smartctl -d megaraid,N /dev/bus/0` 옵션 필수 |
| RAID 구성 추론 | OS 노출 용량 ÷ Physical Disk 개수로 RAID Level 유추 |
| SMART 점검 | 온도, Wear Level, Reallocated/Pending Sector, CRC 오류 |

:bulb: RAID 환경에서는 OS가 보이는 디스크만 점검하면 안 된다. RAID Controller 뒤의 Physical Disk 각각의 SMART 상태를 확인해야 장애를 미리 발견할 수 있다.
{: .notice--info}
