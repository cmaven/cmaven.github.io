---
title: "Arista 스위치에 관리 IP 할당하고 SSH로 접속하기"
description: "Arista EOS 스위치의 Management 인터페이스에 IP를 할당하고, 같은 망의 PC에서 SSH로 접근하는 전체 절차를 실제 작업 출력과 함께 단계별로 정리"
excerpt: "콘솔 최초 접속부터 Management1 IP 할당, VRF 확인, 관리자 계정 생성, SSH 활성화 확인, 설정 저장, PC에서의 SSH 접속 테스트까지 실제 장비 출력을 곁들인 step by step 가이드"
date: 2026-06-10
categories: Network
tags: [Arista, EOS, 스위치, ManagementIP, SSH, VRF, 네트워크, 콘솔, CLI]
ref: arista-switch-management-ip-ssh-access
---

:bulb: Arista EOS 스위치에 관리용 IP를 할당하고, 같은 네트워크에 있는 PC에서 SSH로 접속하는 방법을 실제 작업 출력과 함께 단계별로 정리한다.  
환경: Arista 스위치(EOS) + 콘솔 케이블 + 같은 서브넷의 PC
{: .notice--info}

> 이 글의 CLI 출력은 실제 장비(`DCS-7050SX3-48YC8C-F`, 호스트명 `sw-core-01`)에서 `Management1`에 IP를 할당해 관리망에서 SSH 접근이 되도록 작업한 기록을 참조 예시로 사용했다. 본문의 IP(`192.0.2.110/24`)·서브넷(`192.0.2.0/24`)은 문서화 예시 대역(RFC 5737)으로 치환했고, 비밀번호 등 민감 정보는 마스킹했다. 실제 적용 시 본인 환경의 주소로 바꿔서 사용한다.

# [00] 전체 구성도

```
관리 PC (192.0.2.20/24)
  │
  └── SSH   ssh admin@192.0.2.110
        │
        ▼
  같은 L2 스위치 / 같은 서브넷 (192.0.2.0/24)
        │
        ▼
Arista 스위치 (sw-core-01)
  └── interface Management1 : 192.0.2.110/24
        └── management ssh   (SSH 데몬, Default VRF)
```

:warning: **Management1은 데이터 포트(Ethernet1~)와 분리된 전용 관리(out-of-band) 포트**다. 처음에는 PC를 Management1 포트가 속한 같은 서브넷에 직접 연결하거나, 같은 L2 스위치에 물려서 통신한다.
{: .notice--warning}

# [01] 사전 준비물

| 항목 | 설명 |
|------|------|
| 콘솔 케이블 | RJ45-to-USB 또는 시리얼(DB9) 콘솔 케이블 |
| 터미널 프로그램 | PuTTY, Tera Term, `screen`, `tio` 등 |
| 관리 PC | 스위치와 **같은 서브넷**에 둘 IP를 가진 PC |
| 할당할 IP | 예) 스위치 `192.0.2.110/24`, PC `192.0.2.20/24` |

# [02] 콘솔 포트로 최초 접속

스위치 전면/후면의 **Console 포트**에 콘솔 케이블을 연결하고, 터미널에서 아래 시리얼 설정으로 접속한다.

```
Baud rate : 9600
Data bits : 8
Parity    : None
Stop bits : 1
Flow ctrl : None
```

> 9600 8N1. 윈도우라면 PuTTY/Tera Term을 쓰고, 리눅스(Ubuntu)/macOS라면 아래 절차로 `screen` 또는 `tio`를 사용한다.

## [02-1] Ubuntu에서 USB 시리얼 장치 확인

USB-to-시리얼(콘솔) 케이블을 PC에 꽂으면 보통 `/dev/ttyUSB0`(FTDI/PL2303 계열) 또는 `/dev/ttyACM0`(CDC-ACM 계열)로 잡힌다. 어떤 이름으로 잡혔는지 먼저 확인한다.

```bash
# 케이블을 꽂은 직후, 새로 생성된 시리얼 장치 확인
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null

# 케이블을 꽂는 순간의 커널 메시지로 장치 이름 확인 (가장 확실)
dmesg | grep -iE 'ttyUSB|ttyACM|usb' | tail -n 20

# USB 장치 목록에서 시리얼 칩(FTDI, Prolific 등) 확인
lsusb
```

> `dmesg`에 `FTDI USB Serial Device converter now attached to ttyUSB0` 같은 줄이 보이면 그 장치가 콘솔 케이블이다. 꽂기 전/후로 `ls`를 비교하면 새로 생긴 장치를 바로 알 수 있다.

:warning: 일반 사용자 계정은 시리얼 포트 접근 권한이 없어 `Permission denied`가 날 수 있다. 사용자를 `dialout` 그룹에 추가하면 sudo 없이 접속할 수 있다(재로그인 필요).
{: .notice--warning}

```bash
# 현재 사용자를 dialout 그룹에 추가 후 로그아웃→로그인(또는 재부팅)
sudo usermod -aG dialout $USER

# 임시로는 sudo로 실행해도 된다
```

## [02-2] screen으로 접속

가장 가볍게 쓸 수 있는 방법이다.

```bash
# 설치 (Ubuntu/Debian)
sudo apt update
sudo apt install -y screen

# 접속: screen <장치> <baud>
screen /dev/ttyUSB0 9600
```

- 화면이 비어 있으면 **Enter**를 한 번 쳐서 프롬프트를 깨운다.
- 종료: `Ctrl + a` 누른 뒤 `k` → `y` (또는 `Ctrl + a`, `\`).
- 분리(세션 유지): `Ctrl + a` 뒤 `d`, 재접속은 `screen -r`.

## [02-3] tio로 접속

현대적인 시리얼 터미널로, 명령행 옵션이 깔끔하고 **장치가 빠졌다 다시 꽂히면 자동 재연결**된다. 장비 콘솔을 자주 붙일 때 편하다.

```bash
# 설치 (Ubuntu 22.04+ 기본 저장소 제공)
sudo apt update
sudo apt install -y tio

# 접속: tio 기본 baud는 115200이므로 9600을 명시한다
tio -b 9600 /dev/ttyUSB0
```

- 화면이 비어 있으면 **Enter**를 한 번 쳐서 프롬프트를 깨운다.
- 모든 단축키는 `Ctrl + t`가 접두키다. 종료: `Ctrl + t` 뒤 `q`.
- 단축키 목록 보기: `Ctrl + t` 뒤 `?`.
- 자주 쓰는 설정은 프로필로 저장할 수 있다(`/etc/tio/config` 또는 `~/.config/tio/config`).

```ini
# 예) ~/.config/tio/config — "tio arista"로 바로 접속
[arista]
device = /dev/ttyUSB0
baudrate = 9600
```

접속되면 기본 계정 `admin`으로 로그인한다(초기 비밀번호 없음). 프롬프트가 `switch>` 또는 `switch login:` 형태로 나타난다.

```
switch login: admin
switch>
```

# [03] enable 모드 진입 및 호스트명 설정

```
switch> enable
switch# configure terminal
switch(config)# hostname sw-core-01
sw-core-01(config)#
```

- `enable` : 특권(EXEC) 모드 진입
- `configure terminal` : 전역 설정 모드 진입

# [04] VRF 확인 (중요)

최신 EOS는 Management1 인터페이스가 별도 VRF(보통 이름 `MGMT`)에 속하는 경우가 많다. **VRF 사용 여부에 따라 라우트와 서비스 활성화 위치가 달라지므로 먼저 확인한다.**

```
sw-core-01# show ip route vrf MGMT
% IP Routing table for VRF MGMT does not exist.
```

이번 장비에서는 위처럼 `MGMT` VRF 라우팅 테이블이 **존재하지 않았다.** 즉 `Management1`이 별도 관리 VRF가 아니라 **Default VRF**에서 동작하는 구성이다. 같은 `192.0.2.0/24` 대역에서 접근하는 경우에는 별도 라우트 없이 connected route로 통신된다.

> 반대로 `show vrf` 출력에 `MGMT` 같은 VRF가 보이고 Management1이 그 VRF에 속해 있으면 **VRF 경로**를, 아무 VRF도 없으면 **기본(default) 경로**를 따른다. 아래 단계에서는 두 경우를 모두 표기한다.

# [05] 관리 IP 할당 (Management1)

먼저 작업 전 `Management1` 상태를 확인하면, 물리 링크는 up이지만 IP가 할당되어 있지 않은 것을 볼 수 있다.

```
sw-core-01# show ip interface Management1
Management1 is up, line protocol is up (connected)
  No Internet protocol address assigned
  IPv6 Interface Forwarding : None
  IP MTU 1500 bytes
```

> 핵심은 `No Internet protocol address assigned` 줄이다. 물리 링크(`up, line protocol is up (connected)`)는 정상이므로 IP만 할당하면 된다.

이제 IP를 할당하고 인터페이스를 활성화한다.

```
sw-core-01# configure terminal
sw-core-01(config)# interface Management1
sw-core-01(config-if-Ma1)# ip address 192.0.2.110/24
sw-core-01(config-if-Ma1)# no shutdown
sw-core-01(config-if-Ma1)# exit
```

:bulb: Arista는 서브넷 마스크를 **CIDR 표기(`/24`)**로 입력한다. (`255.255.255.0`가 아님)
{: .notice--info}

설정 후 다시 확인하면 IP가 정상 반영된다.

```
sw-core-01# show ip interface Management1
Management1 is up, line protocol is up (connected)
  Internet address is 192.0.2.110/24
  Broadcast address is 255.255.255.255
  IPv6 Interface Forwarding : None
  Proxy-ARP is disabled
  Local Proxy-ARP is disabled
  Gratuitous ARP is ignored
  IP MTU 1500 bytes

sw-core-01# show running-config interfaces Management1
interface Management1
   ip address 192.0.2.110/24
```

# [06] 기본 게이트웨이 설정

같은 서브넷의 PC에서만 접근한다면 게이트웨이 없이도 통신된다(이번 작업이 그 경우다). 다른 망에서 접근하려면 기본 경로를 설정한다.

**VRF를 쓰지 않는 경우(default):**

```
sw-core-01(config)# ip route 0.0.0.0/0 192.0.2.1
```

**Management1이 MGMT VRF에 속한 경우:**

```
sw-core-01(config)# ip route vrf MGMT 0.0.0.0/0 192.0.2.1
```

:warning: 위 게이트웨이 주소(`192.0.2.1`)는 예시다. **실제 관리망 게이트웨이 주소를 확인한 뒤** 적용한다.
{: .notice--warning}

# [07] 관리자 계정 및 비밀번호 생성

SSH 로그인을 위해 비밀번호가 있는 계정이 필요하다.

```
sw-core-01# configure terminal
sw-core-01(config)# username admin privilege 15 role network-admin secret ********
sw-core-01(config)# end
sw-core-01# write memory
Copy completed successfully.
```

- `privilege 15` : 최고 권한
- `role network-admin` : 모든 명령 사용 가능 역할
- `secret` : 암호화 저장되는 비밀번호 (위 출력에서는 보안상 `********`로 마스킹)

# [08] SSH 활성화 확인

EOS는 보통 SSH가 기본 활성화되어 있다. 실제로 이번 장비도 별도 설정 없이 Default VRF에서 SSHD가 켜져 있었다.

```
sw-core-01# show management ssh
SSHD status for Default VRF is enabled
SSH connection limit is 50
SSH per host connection limit is 20
FIPS status: disabled
```

> 핵심은 `SSHD status for Default VRF is enabled` 줄이다. 이 상태면 `Management1` IP와 로컬 계정만 준비되면 바로 SSH 접속 테스트가 가능하다.

만약 SSH가 꺼져 있거나, 명시적으로 켜고 싶거나, VRF 환경을 반영해야 한다면 아래처럼 설정한다.

**default VRF:**

```
sw-core-01(config)# management ssh
sw-core-01(config-mgmt-ssh)# no shutdown
sw-core-01(config-mgmt-ssh)# exit
```

**MGMT VRF 환경(관리 트래픽이 MGMT VRF로 들어올 때):**

```
sw-core-01(config)# management ssh
sw-core-01(config-mgmt-ssh)# no shutdown
sw-core-01(config-mgmt-ssh)# vrf MGMT
sw-core-01(config-mgmt-ssh-vrf-MGMT)# no shutdown
sw-core-01(config-mgmt-ssh-vrf-MGMT)# exit
```

# [09] 설정 저장

```
sw-core-01(config)# end
sw-core-01# write memory
Copy completed successfully.
```

- `write memory` = `copy running-config startup-config`
- 저장하지 않으면 재부팅 시 설정이 사라진다.

# [10] PC에서 접속 테스트 (같은 망)

먼저 관리 PC의 IP를 스위치와 같은 대역으로 설정한다(예: `192.0.2.20/24`).

**연결 확인(ping):**

```bash
ping 192.0.2.110
```

**SSH 접속:**

```bash
ssh admin@192.0.2.110
```

→ `admin` 계정 비밀번호를 입력하면 `sw-core-01>` 프롬프트로 로그인된다. privilege 15 계정이면 로그인 직후부터 상위 권한이 적용될 수 있다.

# [11] 스위치에서 상태 확인 명령

```
# 관리 IP 확인
show ip interface brief
show ip interface Management1

# 인터페이스 물리/링크 상태
show interfaces Management1

# SSH 서비스 상태
show management ssh

# VRF 구성 확인
show vrf
show ip route vrf MGMT
```

# [12] 트러블슈팅

| 증상 | 점검 포인트 |
|------|-------------|
| ping 안 됨 | PC와 스위치가 **같은 서브넷**인지, Management1에 `no shutdown` 했는지, 케이블이 Management 포트에 꽂혔는지, IP 충돌이 없는지 |
| SSH 거부됨 | `username ... secret`으로 비밀번호 설정했는지, `show management ssh`에서 활성 상태인지, VRF 환경이면 해당 VRF에서 `no shutdown` 했는지, SSH 접근 ACL이 막고 있지 않은지 |
| 다른 망에서 접근 불가 | 기본 게이트웨이(`ip route ...`)를 올바른 VRF에 설정했는지, `show ip route` / `show vrf`로 실제 라우팅 구성 확인 |
| 재부팅 후 설정 사라짐 | `write memory`로 startup-config 저장했는지 |

# [13] 요약

| 단계 | 작업 위치 | 내용 |
|------|-----------|------|
| STEP 02 | 콘솔 | 9600 8N1로 최초 접속, `admin` 로그인 |
| STEP 04 | 스위치 CLI | `show ip route vrf MGMT` / `show vrf`로 MGMT VRF 사용 여부 확인 (이번 장비는 Default VRF) |
| STEP 05 | 스위치 CLI | Management1에 `ip address 192.0.2.110/24` + `no shutdown` |
| STEP 06 | 스위치 CLI | 기본 게이트웨이(`ip route`) 설정 (다른 망 접근 시, 필요하면 VRF 지정) |
| STEP 07 | 스위치 CLI | `username admin ... secret`로 비밀번호 계정 생성 |
| STEP 08 | 스위치 CLI | `show management ssh`로 SSHD 활성 확인 (필요 시 `management ssh` 활성화) |
| STEP 09 | 스위치 CLI | `write memory`로 설정 저장 |
| STEP 10 | 관리 PC | `ssh admin@192.0.2.110` 접속 테스트 |
