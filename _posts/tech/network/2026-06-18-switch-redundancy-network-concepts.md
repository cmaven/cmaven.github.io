---
title: "스위치 이중화를 위한 핵심 네트워크 개념 정리 — VLAN·SVI·LACP·MLAG/VLT·VRRP/VIP·IPMI·PXE"
description: "Arista/25G 네트워크 구축·검증 글을 이해하는 데 필요한 기반 개념과, 스위치 이중화(고가용성)에 쓰이는 VLAN, SVI, LACP, Port-Channel, MLAG/VLT, STP, VRRP, VIP, FHRP, 서버 본딩, IPMI, PXE를 계층별로 한 번에 정리"
excerpt: "스위치를 두 대로 이중화할 때 등장하는 용어 — VLAN/SVI(L2·L3), LACP/Port-Channel/MLAG·VLT(링크·섀시 이중화), VRRP/VIP·FHRP(게이트웨이 이중화), 서버 bonding, IPMI/BMC, PXE — 를 왜 필요한지·어떻게 엮이는지 중심으로 정리한다"
date: 2026-06-18
categories: Network
tags: [네트워크, 스위치이중화, 고가용성, VLAN, SVI, LACP, PortChannel, MLAG, VLT, STP, VRRP, VIP, FHRP, bonding, IPMI, BMC, PXE, ECMP, VXLAN, Arista]
ref: switch-redundancy-network-concepts
---

:bulb: Arista·25G 구축/검증 시리즈(관리 IP·25G 링크·트랜시버·netplan)를 읽다 보면 **VLAN, SVI, LACP, MLAG/VLT, VRRP, VIP, IPMI, PXE** 같은 용어가 계속 나온다. 이 글은 그 개념들을, 특히 **스위치 이중화(고가용성)** 관점에서 계층별로 정리한다.  
대상: 네트워크 구성/이중화 용어를 처음 정리하는 서버·인프라 엔지니어
{: .notice--info}

# [00] 왜 "이중화"인가 — 단일 장애점 제거

서버 한 대가 스위치 한 대에 케이블 한 가닥으로 붙어 있으면, **스위치·케이블·포트 중 어느 하나만 죽어도 통신이 끊긴다.** 이중화(redundancy, 고가용성/HA)는 이 **단일 장애점(SPOF, Single Point of Failure)** 을 없애기 위해 경로·장비·게이트웨이를 둘 이상으로 만드는 것이다.

이중화는 **계층별로** 따로 설계한다.

| 계층 | 무엇을 이중화 | 핵심 기술 |
|------|-------------|----------|
| 물리/링크 (L1~L2) | 케이블·포트·스위치 섀시 | LACP, Port-Channel, **MLAG/VLT**, STP |
| 네트워크 (L2/L3 경계) | 브로드캐스트 도메인·게이트웨이 | VLAN, **SVI**, **VRRP/VIP**, FHRP |
| L3 라우팅 (코어/스파인) | 상위 경로 | ECMP, OSPF/BGP |
| 서버 측 | NIC·업링크 | **bonding(본딩)** |
| 운영/관리 | 장비 접근 경로·부팅 | **IPMI/BMC**, **PXE** |

아래에서 하나씩 본다.

---

# [01] L2 기반 — VLAN과 SVI

## [01-1] VLAN — 하나의 스위치를 여러 개로 쪼개기

**VLAN(Virtual LAN)** 은 물리적으로 같은 스위치를 **논리적으로 분리된 여러 브로드캐스트 도메인**으로 나누는 기술이다. VLAN 10(서버망)과 VLAN 20(관리망)은 같은 스위치에 있어도 서로 직접 통신하지 못한다(라우팅을 거쳐야 한다).

| 포트 모드 | 의미 |
|----------|------|
| **Access** | 한 VLAN에만 속하는 포트 (보통 서버·PC 연결). 태그 없음 |
| **Trunk** | 여러 VLAN을 한 링크로 실어 나르는 포트 (스위치 간 연결). 802.1Q 태그로 VLAN 구분 |

```text
! Arista EOS 예시
vlan 10
   name SERVER
vlan 20
   name MGMT
interface Ethernet1
   switchport mode access
   switchport access vlan 10
interface Ethernet48
   switchport mode trunk
   switchport trunk allowed vlan 10,20
```

> 이중화 관점: VLAN 자체는 이중화 기술이 아니라 **분할** 기술이다. 하지만 뒤의 SVI·VRRP·MLAG가 모두 VLAN 위에서 동작하므로 출발점이 된다.

## [01-2] SVI — VLAN에 IP를 주는 L3 인터페이스

스위치 포트는 기본적으로 L2(스위칭)만 한다. **VLAN 간 라우팅**을 하려면 그 VLAN에 **게이트웨이 IP**가 있어야 한다. 그 IP를 갖는 가상 인터페이스가 **SVI(Switched Virtual Interface)** 다. Arista/Cisco에서는 `interface Vlan10` 형태로 만든다.

```text
interface Vlan10
   ip address 10.0.10.1/24      ! VLAN 10 서버들의 게이트웨이
interface Vlan20
   ip address 10.0.20.1/24      ! VLAN 20 관리망의 게이트웨이
```

- VLAN 10에 속한 서버는 게이트웨이를 `10.0.10.1`(SVI)로 설정한다.
- SVI는 **물리 포트가 아니라 VLAN에 묶인 논리 L3 인터페이스**다. 그 VLAN에 멤버 포트가 하나라도 up이면 SVI도 up 된다.

> 참고: 앞선 [Arista 관리 IP 글](/Network/arista-switch-management-ip-ssh-access/)의 `Management1`은 SVI가 아니라 **전용 관리 포트**다. SVI는 데이터 VLAN의 게이트웨이, Management 인터페이스는 OOB(out-of-band) 관리용으로 역할이 다르다.

---

# [02] 링크·섀시 이중화 — LACP, Port-Channel, MLAG/VLT

## [02-1] LACP와 Port-Channel — 여러 링크를 하나로 묶기

**Port-Channel(=LAG, Link Aggregation Group)** 은 여러 물리 링크를 **하나의 논리 링크**로 묶는 것이다. 효과는 두 가지.

1. **대역폭 합산** — 25G × 2 = 약 50G
2. **이중화** — 한 링크가 끊겨도 나머지로 계속 통신

**LACP(Link Aggregation Control Protocol, 802.3ad)** 는 이 묶음을 **자동 협상·관리**하는 프로토콜이다. 양쪽이 LACP 패킷(LACPDU)을 주고받아 묶음을 형성하고, 죽은 링크를 자동으로 뺀다.

| 모드 | 동작 |
|------|------|
| `active` | 먼저 LACP 협상을 시작 |
| `passive` | 상대가 시작하면 응답 |
| `static`(on) | 협상 없이 강제 묶음 (권장하지 않음 — 장애 감지 약함) |

```text
! Arista: Et1, Et2를 Port-Channel 1로 LACP 묶음
interface Ethernet1-2
   channel-group 1 mode active
interface Port-Channel1
   switchport mode trunk
```

## [02-2] MLAG / VLT — "두 대의 스위치를 한 대처럼"

LACP 묶음은 보통 **한 대의 스위치**에 묶인다. 그러면 그 스위치가 통째로 죽으면 끝이다. 이를 해결하는 것이 **MLAG/VLT** — 서로 다른 **두 대의 물리 스위치**를 논리적으로 한 대처럼 보이게 해서, 서버가 **두 스위치에 각각 한 가닥씩** 연결하고도 하나의 LACP 묶음으로 동작하게 한다.

| 벤더 | 명칭 |
|------|------|
| **Arista** | **MLAG** (Multi-chassis Link Aggregation) |
| **Dell** | **VLT** (Virtual Link Trunking) |
| Cisco | vPC (virtual Port Channel) |

> 즉 **VLT는 Dell, MLAG는 Arista의 같은 개념**이다. 이름만 다르고 목적은 동일하다: *섀시(스위치 본체) 단위 이중화*.

<pre class="mermaid">
graph TD
    SRV["서버 A<br/>bond0 (802.3ad LACP)"]
    SW1["스위치1<br/>MLAG peer"]
    SW2["스위치2<br/>MLAG peer"]
    SRV -->|eth0| SW1
    SRV -->|eth1| SW2
    SW1 <-->|"Peer-Link + Keepalive"| SW2
    style SRV fill:#e8f5e9,stroke:#2e7d32
    style SW1 fill:#e3f2fd,stroke:#1565c0
    style SW2 fill:#e3f2fd,stroke:#1565c0
</pre>

서버는 두 스위치에 한 가닥씩 연결하지만 **하나의 LACP 본딩(bond0)** 으로 동작하고, 스위치1·2는 MLAG 피어로 묶여 한 대처럼 보인다. 스위치1이 죽어도 서버는 eth1(스위치2)로 무중단 통신한다.

**MLAG 내부 — 두 스위치를 묶는 두 개의 채널**

MLAG가 두 스위치를 한 대처럼 보이게 하려면 둘 사이에 두 종류의 채널이 필요하다.

- **Peer-Link**: 데이터·상태(MAC 테이블, ARP) 동기화 경로. 보통 고대역 Port-Channel로 구성.
- **Peer-Keepalive**: 상대 생존 확인용 별도 경로. 보통 관리망을 통해 구성.
- **Split-brain(스플릿 브레인)**: Peer-Link가 끊겨 두 스위치가 서로 죽은 줄 알고 **둘 다 Master로 행동**하는 위험 상태. Keepalive 경로로 이를 감지·방지한다.

## [02-3] STP — 루프 방지(보조 개념)

이중 경로를 만들면 **L2 루프(브로드캐스트 폭주)** 위험이 생긴다. **STP(Spanning Tree Protocol)** 는 중복 경로 중 하나를 논리적으로 차단해 루프를 막는다. 단, MLAG 환경에서는 두 업링크를 **둘 다 active**로 쓰므로(STP가 막지 않음) 대역폭을 온전히 활용한다 — 이것이 MLAG의 장점 중 하나다.

---

# [03] 게이트웨이 이중화 — VRRP와 VIP

스위치/링크를 이중화해도, 서버가 바라보는 **게이트웨이 IP가 한 장비에만 있으면** 그 장비가 죽을 때 외부 통신이 끊긴다. 게이트웨이 자체를 이중화하는 것이 **VRRP**다.

## [03-1] VIP — 떠다니는 가상 IP

**VIP(Virtual IP)** 는 특정 물리 장비에 고정되지 않고 **현재 활성(Master) 장비가 떠안는 가상의 IP 주소**다. 서버는 실제 스위치 IP가 아니라 이 VIP를 게이트웨이로 바라본다.

## [03-2] VRRP — VIP를 누가 들고 있을지 자동 선출

**VRRP(Virtual Router Redundancy Protocol)** 는 여러 라우터/L3 스위치가 **하나의 VIP와 가상 MAC**을 공유하고, 그중 **Master 하나만 VIP를 응답**하게 한다. Master가 죽으면 Backup이 즉시 VIP를 넘겨받아(failover) 서버는 게이트웨이가 바뀐 줄도 모르고 계속 통신한다.

```text
! 스위치1 (Master 우선)
interface Vlan10
   ip address 10.0.10.2/24
   vrrp 10 ip 10.0.10.1          ! ← VIP (서버의 게이트웨이)
   vrrp 10 priority 200          ! 높을수록 Master

! 스위치2 (Backup)
interface Vlan10
   ip address 10.0.10.3/24
   vrrp 10 ip 10.0.10.1          ! ← 같은 VIP 공유
   vrrp 10 priority 100
```

| 항목 | 값 | 의미 |
|------|-----|------|
| VIP | `10.0.10.1` | 서버가 보는 게이트웨이 (떠다님) |
| 스위치1 실 IP | `10.0.10.2` | priority 200 → Master |
| 스위치2 실 IP | `10.0.10.3` | priority 100 → Backup |

<pre class="mermaid">
graph TD
    SRV["서버<br/>gateway = 10.0.10.1 (VIP)"]
    VIP{{"VIP 10.0.10.1<br/>가상 IP/MAC"}}
    M["스위치1 (Master)<br/>10.0.10.2 · priority 200"]
    B["스위치2 (Backup)<br/>10.0.10.3 · priority 100"]
    SRV --> VIP
    VIP -->|"평상시 응답"| M
    VIP -.->|"Master 장애 시 인수 (failover)"| B
    M <-->|"VRRP advertisement"| B
    style SRV fill:#e8f5e9,stroke:#2e7d32
    style VIP fill:#f3e5f5,stroke:#6a1b9a
    style M fill:#e3f2fd,stroke:#1565c0
    style B fill:#fff3e0,stroke:#e65100
</pre>

> MLAG(L2 섀시 이중화) + VRRP(L3 게이트웨이 이중화)를 **함께** 쓰면 링크·스위치·게이트웨이가 모두 이중화된다. 이것이 일반적인 이중화 토폴로지다.

## [03-3] FHRP 가족 — VRRP만 있는 게 아니다

게이트웨이 이중화 프로토콜을 통칭 **FHRP(First Hop Redundancy Protocol)** 라 한다. VRRP는 그중 하나다.

| 프로토콜 | 벤더 | 특징 |
|---|---|---|
| **VRRP** | 표준(개방) | 가장 범용. Master 1 + Backup N |
| **HSRP** | Cisco 전용 | VRRP와 유사, Active/Standby 용어 사용 |
| **GLBP** | Cisco 전용 | 여러 게이트웨이가 **동시에** 트래픽 분담(로드밸런싱) |

> Arista는 표준 **VRRP**를 쓴다. 멀티벤더 환경에선 표준 VRRP가 무난하다.

---

# [04] 서버 측 이중화 — 본딩(bonding)

스위치 쪽 MLAG에 대응해, **서버도 NIC 두 장을 하나로 묶어야** 한다. 리눅스에서는 이를 **본딩(bonding) / 팀밍(teaming)** 이라 한다. 스위치 MLAG와 짝을 이루려면 **802.3ad(LACP) 모드**를 쓴다.

```yaml
# netplan 예시 (LACP 본딩) — 두 NIC를 bond0으로
network:
  version: 2
  ethernets:
    ens801f0np0: {}
    ens801f1np1: {}
  bonds:
    bond0:
      interfaces: [ens801f0np0, ens801f1np1]
      parameters:
        mode: 802.3ad          # LACP
        lacp-rate: fast
        mii-monitor-interval: 100
      addresses: [10.0.10.50/24]
      routes:
        - to: default
          via: 10.0.10.1       # ← VRRP VIP
```

> netplan으로 NIC를 직접 설정하는 방법은 [netplan 수동 설정 글](/Network/netplan-manual-config-cloud-init/)을 참고한다. 본딩 모드는 **반드시 스위치 측 LACP/MLAG 설정과 일치**해야 링크가 정상적으로 묶인다.

| bonding 모드 | 특징 | 스위치 요구 |
|---|---|---|
| `802.3ad` (LACP) | 표준 LACP, 대역폭+이중화 | 스위치 Port-Channel/MLAG 필요 |
| `active-backup` | 한 NIC만 사용, 죽으면 전환 | 스위치 설정 불필요 (가장 단순한 이중화) |
| `balance-xor` 등 | 정적 해시 분산 | static LAG |

---

# [05] 운영·관리 이중화 — IPMI/BMC와 PXE

## [05-1] IPMI / BMC — OS와 무관한 별도 관리 경로

**IPMI(Intelligent Platform Management Interface)** 는 서버의 **BMC(Baseboard Management Controller)** 칩이 제공하는 **대역 외(out-of-band) 관리** 표준이다. 핵심은 **OS·메인 NIC와 완전히 분리**되어 있다는 점이다.

- 전용 관리 LAN 포트와 **자체 IP**를 가진다 (서버 OS가 꺼져 있어도 동작).
- 원격 전원 on/off/리셋, 하드웨어 센서(온도·팬·전압), **원격 콘솔(SOL/KVM)** 제공.
- 벤더 구현: Dell **iDRAC**, HPE **iLO**, Supermicro **IPMI**, Lenovo **XCC** 등.

> 이중화 관점: 데이터망/OS가 다운돼도 IPMI 경로로 서버를 진단·복구할 수 있다 — **관리 경로의 이중화**다. 앞선 [관리 IP/SSH 글](/Network/arista-switch-management-ip-ssh-access/)의 "관리망"이 바로 이런 OOB 관리 트래픽이 흐르는 망이다.

```text
관리망 (VLAN 20 / OOB)
  ├── 스위치 Management1   (장비 관리 SSH)
  ├── 서버1 IPMI/BMC       (전원·콘솔, OS와 별개 IP)
  └── 서버2 IPMI/BMC
```

## [05-2] PXE — 네트워크로 OS를 부팅

**PXE(Preboot eXecution Environment)** 는 서버가 로컬 디스크가 아니라 **네트워크에서 부팅 이미지를 받아 부팅**하게 하는 표준이다. 대량 서버 프로비저닝·무디스크 노드·자동 OS 설치에 쓴다.

동작 흐름:

```text
1. NIC가 PXE로 부팅 → DHCP 요청 (IP + next-server + 부트파일명 수신)
2. TFTP/HTTP로 부트로더(예: iPXE, GRUB) 다운로드
3. 부트로더가 커널·initrd·킥스타트/프리시드 받아 OS 설치·부팅
```

**PXE를 위한 DHCP Relay**

PXE 클라이언트와 DHCP 서버가 **다른 VLAN**에 있으면, 브로드캐스트인 DHCP가 라우터를 못 넘는다. SVI에 **DHCP relay(`ip helper-address`)** 를 걸어 DHCP 요청을 서버로 중계한다.

```text
interface Vlan30
   ip address 10.0.30.1/24
   ip helper-address 10.0.99.10   ! DHCP/PXE 서버 주소
```

> 이중화 관점: PXE 인프라(DHCP·TFTP) 자체를 이중화하면 프로비저닝 경로의 단일 장애점을 없앤다. PXE는 **VLAN·SVI(게이트웨이)** 위에서 동작하므로, 부팅용 VLAN과 DHCP relay 설계가 함께 필요하다.

---

# [06] 전체 그림 — 개념이 어떻게 한 토폴로지로 엮이는가

<pre class="mermaid">
graph TD
    CORE["외부망 / 코어"]
    VIP{{"VRRP VIP 10.0.10.1<br/>게이트웨이 이중화"}}
    SW1["스위치1<br/>SVI Vlan10 · MLAG"]
    SW2["스위치2<br/>SVI Vlan10 · MLAG"]
    S1["서버1<br/>bond0 (802.3ad)"]
    S2["서버2<br/>bond0 (802.3ad)"]
    MGMT["관리망 VLAN 20 (OOB)<br/>IPMI/BMC · Management1"]
    CORE --> VIP
    VIP --> SW1
    VIP --> SW2
    SW1 <-->|"Peer-Link"| SW2
    SW1 ---|LACP| S1
    SW2 ---|LACP| S1
    SW1 ---|LACP| S2
    SW2 ---|LACP| S2
    S1 -.->|OOB| MGMT
    S2 -.->|OOB| MGMT
    style CORE fill:#eceff1,stroke:#455a64
    style VIP fill:#f3e5f5,stroke:#6a1b9a
    style SW1 fill:#e3f2fd,stroke:#1565c0
    style SW2 fill:#e3f2fd,stroke:#1565c0
    style S1 fill:#e8f5e9,stroke:#2e7d32
    style S2 fill:#e8f5e9,stroke:#2e7d32
    style MGMT fill:#fff3e0,stroke:#e65100
</pre>

| 이중화 대상 | 담당 개념 |
|------------|----------|
| 케이블·포트 | LACP / Port-Channel |
| 스위치 섀시 | **MLAG(Arista) / VLT(Dell)** |
| L2 루프 방지 | STP (MLAG에선 보조) |
| 게이트웨이(L3) | **VRRP + VIP** (FHRP) |
| 서버 업링크 | bonding(802.3ad) |
| 관리 경로 | IPMI/BMC + 관리 VLAN |
| 프로비저닝 | PXE (DHCP/TFTP 이중화) |

---

# [07] L3 라우팅 이중화 — ECMP와 BGP/OSPF

게이트웨이까지는 VRRP로 이중화했다면, 그 **위(코어/스파인) 구간은 동적 라우팅으로 이중화**한다. VRRP가 "게이트웨이 한 홉"의 이중화라면, 이쪽은 "그 너머 경로"의 이중화다.

- **ECMP(Equal-Cost Multi-Path)**: 비용이 같은 경로 여러 개로 트래픽을 분산하고, 한 경로가 죽으면 자동 우회한다. 대역폭과 이중화를 동시에 얻는다.
- **OSPF / BGP**: 경로를 동적으로 학습하고 장애 시 재수렴(reconverge)한다. 현대 데이터센터(leaf-spine fabric)는 L2 MLAG 대신 **L3 + BGP/EVPN**으로 가는 추세다.

<pre class="mermaid">
graph TD
    LEAF["Leaf 스위치"]
    SP1["Spine 1"]
    SP2["Spine 2"]
    DST["목적지 대역"]
    LEAF -->|"경로 A · cost 10"| SP1
    LEAF -->|"경로 B · cost 10"| SP2
    SP1 --> DST
    SP2 --> DST
    style LEAF fill:#e8f5e9,stroke:#2e7d32
    style SP1 fill:#e3f2fd,stroke:#1565c0
    style SP2 fill:#e3f2fd,stroke:#1565c0
    style DST fill:#eceff1,stroke:#455a64
</pre>

비용이 같은 두 경로를 **동시에** 쓰며(ECMP 부하분산), 한 경로(Spine)가 죽으면 라우팅이 재수렴해 나머지 경로로 자동 우회한다.

> 소규모는 MLAG+VRRP(L2 중심), 대규모는 L3 라우팅(ECMP+BGP) 중심으로 설계가 갈린다.

---

# [08] 물리계층에서 함께 맞춰야 할 값 — MTU/Jumbo·FEC·트랜시버

이중화 자체는 아니지만, 25G 링크를 **정상 동작**시키려면 물리·링크 계층에서 양단이 맞아야 하는 값들이다. 이 값이 어긋나면 이중화 이전에 링크 품질·연결 자체가 깨진다.

- **Jumbo Frame (MTU 9000+)**: 대용량 전송 효율을 높인다. **경로 전체**(서버 NIC·본딩·스위치 포트·SVI)가 동일 MTU여야 한다. 한 곳만 다르면 단편화·블랙홀이 발생한다.
- **FEC(RS-FEC)**: 25G 이상 고속 링크의 비트 오류를 정정한다. **양단 FEC 모드가 일치**해야 링크가 안정적으로 올라온다 → [25G 검증 글](/Network/25g-nic-arista-switch-link-verification/) 참조.
- **트랜시버 호환성**: 스위치가 모듈을 `xcvr-unsupported`로 차단하면 링크 자체가 안 온다 → [GBIC 테스트 글](/Network/arista-switch-gbic-transceiver-test/) 참조.

---

# [09] 대규모 환경의 현대적 대안 — VXLAN/EVPN과 Anycast Gateway

대규모 환경에선 VLAN의 한계(ID 4094개, L2 도메인 확장의 어려움)를 넘기 위해 **VXLAN**(L3 위에 L2를 터널링)과 **EVPN**(그 컨트롤 플레인)을 쓴다.

이때 게이트웨이는 VRRP 대신 **Anycast Gateway** — 모든 leaf 스위치가 **동일한 게이트웨이 IP/MAC을 동시에** 보유해, 서버가 어디에 붙어도 가장 가까운 스위치가 게이트웨이가 되는 방식 — 로 이중화한다.

> 본 글의 주제(소~중규모 스위치 이중화)에서는 MLAG+VRRP로 충분하다. VXLAN/EVPN은 "더 큰 그림"으로 개념만 알아두면 된다.

---

# [10] 용어 빠른 정리표

| 용어 | 한 줄 정의 | 계층 | 이중화 역할 |
|------|-----------|------|------------|
| **VLAN** | 스위치를 논리적으로 분할한 브로드캐스트 도메인 | L2 | 분할(기반) |
| **SVI** | VLAN에 IP를 부여하는 가상 L3 인터페이스(게이트웨이) | L3 | VRRP의 토대 |
| **LACP** | 여러 링크를 자동 협상해 하나로 묶는 프로토콜(802.3ad) | L2 | 링크 이중화 |
| **Port-Channel/LAG** | LACP로 묶인 논리 링크 | L2 | 대역폭+이중화 |
| **MLAG / VLT** | 두 스위치를 한 대처럼 — 섀시 단위 이중화 (Arista/Dell) | L2 | 스위치 이중화 |
| **Peer-Link/Keepalive** | MLAG 두 스위치의 상태 동기화·생존 확인 경로 | L2 | MLAG 안정 |
| **STP** | L2 루프 차단 | L2 | 루프 방지 |
| **VRRP** | VIP를 Master/Backup이 자동 인수인계하는 프로토콜 | L3 | 게이트웨이 이중화 |
| **VIP** | 활성 장비가 떠안는 가상 게이트웨이 IP | L3 | 게이트웨이 이중화 |
| **FHRP (HSRP/GLBP)** | 게이트웨이 이중화 프로토콜 통칭 (VRRP 포함) | L3 | 게이트웨이 이중화 |
| **bonding** | 서버 NIC 여러 장을 묶기(LACP/active-backup) | 서버 | 서버 업링크 이중화 |
| **ECMP** | 동일 비용 다중경로 분산·우회 | L3 | 경로 이중화 |
| **OSPF/BGP** | 동적 라우팅 학습·재수렴 | L3 | 경로 이중화 |
| **IPMI/BMC** | OS와 분리된 OOB 하드웨어 관리(전원·콘솔) | 관리 | 관리 경로 이중화 |
| **PXE** | 네트워크 부팅(DHCP+TFTP) | 부팅 | 프로비저닝 |
| **DHCP relay** | 다른 VLAN의 DHCP로 중계(`ip helper-address`) | L3 | PXE 지원 |
| **Jumbo/MTU** | 큰 프레임; 경로 전체 동일해야 함 | L2/L3 | (성능) |
| **FEC(RS-FEC)** | 고속 링크 비트오류 정정, 양단 일치 | L1 | (링크 안정) |
| **VXLAN/EVPN** | L2 over L3 + Anycast Gateway | overlay | 대규모 이중화 |

---

# [11] 정리

스위치 이중화는 **한 가지 기술이 아니라 계층별 기술의 조합**이다.

1. **VLAN/SVI** 로 망을 나누고 게이트웨이를 만든다.
2. **LACP/Port-Channel** 로 링크를, **MLAG/VLT** 로 스위치 섀시를 이중화한다(Peer-Link/Keepalive로 동기화·Split-brain 방지).
3. **VRRP/VIP**(FHRP) 로 게이트웨이를, **ECMP/BGP** 로 상위 경로를 이중화한다.
4. 서버는 **bonding(802.3ad)** 으로 두 스위치에 동시에 붙는다.
5. **IPMI/BMC** 로 OS와 무관한 관리 경로를, **PXE** 로 프로비저닝 경로를 갖춘다.

물리계층에서는 **MTU·FEC·트랜시버 호환성**을 양단에 맞춰야 링크가 정상 동작하고, 대규모로 가면 **VXLAN/EVPN + Anycast Gateway** 가 대안이 된다. 이 개념들을 머리에 넣고 보면, Arista 관리 IP·25G 링크·트랜시버·netplan 글에서 등장하는 `Management1`, `Port-Channel`, `VLAN`, `게이트웨이`, `본딩` 같은 용어가 **하나의 이중화 그림** 안에서 어디에 위치하는지 보이게 된다.
