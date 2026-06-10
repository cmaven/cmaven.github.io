---
title: "Arista 스위치에 관리 IP 할당하고 SSH·웹으로 접속하기"
description: "Arista EOS 스위치의 Management 인터페이스에 IP를 할당하고, 같은 망의 PC에서 SSH와 웹(eAPI)으로 접근하는 전체 절차를 단계별로 정리"
excerpt: "콘솔 최초 접속부터 Management1 IP 할당, VRF 확인, 관리자 계정 생성, SSH·eAPI(HTTPS) 활성화, 설정 저장, PC에서의 SSH·웹 접속 테스트까지 step by step 가이드"
date: 2026-06-10
categories: Network
tags: [Arista, EOS, 스위치, ManagementIP, SSH, eAPI, HTTPS, VRF, 네트워크, 콘솔, CLI]
ref: arista-switch-management-ip-ssh-web-access
---

:bulb: Arista EOS 스위치에 관리용 IP를 할당하고, 같은 네트워크에 있는 PC에서 SSH와 웹(eAPI)으로 접속하는 방법을 단계별로 정리한다.  
환경: Arista 스위치(EOS) + 콘솔 케이블 + 같은 서브넷의 PC
{: .notice--info}

# [00] 전체 구성도

```
관리 PC (192.168.1.20/24)
  │
  ├── SSH   ssh admin@192.168.1.10
  └── HTTPS https://192.168.1.10   (eAPI Explorer)
        │
        ▼
  같은 L2 스위치 / 같은 서브넷 (192.168.1.0/24)
        │
        ▼
Arista 스위치
  └── interface Management1 : 192.168.1.10/24
        ├── management ssh          (SSH 데몬)
        └── management api http-commands  (eAPI / 웹 UI, HTTPS)
```

:warning: **Management1은 데이터 포트(Ethernet1~)와 분리된 전용 관리(out-of-band) 포트**다. 처음에는 PC를 Management1 포트가 속한 같은 서브넷에 직접 연결하거나, 같은 L2 스위치에 물려서 통신한다.
{: .notice--warning}

# [01] 사전 준비물

| 항목 | 설명 |
|------|------|
| 콘솔 케이블 | RJ45-to-USB 또는 시리얼(DB9) 콘솔 케이블 |
| 터미널 프로그램 | PuTTY, Tera Term, `screen`, `minicom` 등 |
| 관리 PC | 스위치와 **같은 서브넷**에 둘 IP를 가진 PC |
| 할당할 IP | 예) 스위치 `192.168.1.10/24`, PC `192.168.1.20/24` |

# [02] 콘솔 포트로 최초 접속

스위치 전면/후면의 **Console 포트**에 콘솔 케이블을 연결하고, 터미널에서 아래 시리얼 설정으로 접속한다.

```
Baud rate : 9600
Data bits : 8
Parity    : None
Stop bits : 1
Flow ctrl : None
```

> 9600 8N1. 리눅스/macOS라면 다음과 같이 접속할 수 있다.

```bash
# 장치 이름은 환경에 따라 다름 (예: /dev/ttyUSB0, /dev/tty.usbserial-XXXX)
screen /dev/ttyUSB0 9600
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
sw-core-01# show vrf
```

출력에 `MGMT` 같은 VRF가 보이고 Management1이 그 VRF에 속해 있으면 **VRF 경로**를, 아무 VRF도 없으면 **기본(default) 경로**를 따른다. 아래 단계에서는 두 경우를 모두 표기한다.

# [05] 관리 IP 할당 (Management1)

```
sw-core-01# configure terminal
sw-core-01(config)# interface Management1
sw-core-01(config-if-Ma1)# ip address 192.168.1.10/24
sw-core-01(config-if-Ma1)# no shutdown
sw-core-01(config-if-Ma1)# exit
```

:bulb: Arista는 서브넷 마스크를 **CIDR 표기(`/24`)**로 입력한다. (`255.255.255.0`가 아님)
{: .notice--info}

# [06] 기본 게이트웨이 설정

같은 서브넷의 PC에서만 접근한다면 게이트웨이 없이도 통신되지만, 다른 망에서 접근하려면 기본 경로를 설정한다.

**VRF를 쓰지 않는 경우(default):**

```
sw-core-01(config)# ip route 0.0.0.0/0 192.168.1.1
```

**Management1이 MGMT VRF에 속한 경우:**

```
sw-core-01(config)# ip route vrf MGMT 0.0.0.0/0 192.168.1.1
```

# [07] 관리자 계정 및 비밀번호 생성

SSH·웹 로그인을 위해 비밀번호가 있는 계정이 필요하다.

```
sw-core-01(config)# username admin privilege 15 role network-admin secret <원하는비밀번호>
```

- `privilege 15` : 최고 권한
- `role network-admin` : 모든 명령 사용 가능 역할
- `secret` : 암호화 저장되는 비밀번호

# [08] SSH 활성화

EOS는 보통 SSH가 기본 활성화되어 있지만, 명시적으로 켜고 VRF 환경을 반영한다.

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

# [09] 웹(eAPI / HTTPS) 활성화

Arista의 웹 UI는 **eAPI(Command API)** 기반이며, HTTPS로 켜는 것을 권장한다.

**default VRF:**

```
sw-core-01(config)# management api http-commands
sw-core-01(config-mgmt-api-http-cmds)# protocol https
sw-core-01(config-mgmt-api-http-cmds)# no shutdown
sw-core-01(config-mgmt-api-http-cmds)# exit
```

**MGMT VRF 환경:**

```
sw-core-01(config)# management api http-commands
sw-core-01(config-mgmt-api-http-cmds)# protocol https
sw-core-01(config-mgmt-api-http-cmds)# no shutdown
sw-core-01(config-mgmt-api-http-cmds)# vrf MGMT
sw-core-01(config-mgmt-api-http-cmds-vrf-MGMT)# no shutdown
sw-core-01(config-mgmt-api-http-cmds-vrf-MGMT)# exit
```

:warning: HTTPS는 기본 자체 서명(self-signed) 인증서를 사용하므로 브라우저에서 보안 경고가 뜬다. 내부 관리망에서는 예외 처리 후 진행하면 된다.
{: .notice--warning}

# [10] 설정 저장

```
sw-core-01(config)# end
sw-core-01# write memory
```

- `write memory` = `copy running-config startup-config`
- 저장하지 않으면 재부팅 시 설정이 사라진다.

# [11] PC에서 접속 테스트 (같은 망)

먼저 관리 PC의 IP를 스위치와 같은 대역으로 설정한다(예: `192.168.1.20/24`).

**연결 확인(ping):**

```bash
ping 192.168.1.10
```

**SSH 접속:**

```bash
ssh admin@192.168.1.10
```

**웹(eAPI Explorer) 접속:**

브라우저에서 아래 주소로 접속한다.

```
https://192.168.1.10
```

→ 자체 서명 인증서 경고를 통과하면 `admin` 계정 로그인 후, 명령을 직접 실행하고 JSON 응답을 확인할 수 있는 **eAPI Explorer** 화면이 열린다.

# [12] 스위치에서 상태 확인 명령

```
# 관리 IP 확인
show ip interface brief

# SSH 서비스 상태
show management ssh

# eAPI(웹) 서비스 상태 — 활성 프로토콜/포트/VRF 확인
show management api http-commands

# VRF 구성 확인
show vrf
```

# [13] 트러블슈팅

| 증상 | 점검 포인트 |
|------|-------------|
| ping 안 됨 | PC와 스위치가 **같은 서브넷**인지, Management1에 `no shutdown` 했는지, 케이블이 Management 포트에 꽂혔는지 |
| SSH 거부됨 | `username ... secret`으로 비밀번호 설정했는지, `show management ssh`에서 활성 상태인지, VRF 환경이면 해당 VRF에서 `no shutdown` 했는지 |
| 웹 접속 안 됨 | `show management api http-commands`에서 `protocol https` 활성/포트 확인, VRF 환경이면 VRF에서 `no shutdown` 했는지 |
| 다른 망에서 접근 불가 | 기본 게이트웨이(`ip route ...`)를 올바른 VRF에 설정했는지 |
| 재부팅 후 설정 사라짐 | `write memory`로 startup-config 저장했는지 |

# [14] 요약

| 단계 | 작업 위치 | 내용 |
|------|-----------|------|
| STEP 02 | 콘솔 | 9600 8N1로 최초 접속, `admin` 로그인 |
| STEP 04 | 스위치 CLI | `show vrf`로 MGMT VRF 사용 여부 확인 |
| STEP 05 | 스위치 CLI | Management1에 `ip address <IP>/24` + `no shutdown` |
| STEP 06 | 스위치 CLI | 기본 게이트웨이(`ip route`) 설정 (필요 시 VRF 지정) |
| STEP 07 | 스위치 CLI | `username admin ... secret`로 비밀번호 계정 생성 |
| STEP 08 | 스위치 CLI | `management ssh` 활성화 |
| STEP 09 | 스위치 CLI | `management api http-commands` + HTTPS 활성화 |
| STEP 10 | 스위치 CLI | `write memory`로 설정 저장 |
| STEP 11 | 관리 PC | `ssh admin@IP` / `https://IP` 접속 테스트 |
