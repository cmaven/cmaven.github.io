---
title: "격리된 BMC/IPMI 망에서 서버 하드웨어 원격 모니터링 구축기 — bastion·VLAN·채널·읽기전용 계정"
description: "온프레미스 베어메탈 클러스터의 BMC/IPMI를 하나의 관리망으로 표준화하고, bastion(관문) leg를 통해 외부 협력기관에 읽기전용(ipmitool USER 권한)으로 하드웨어 상태(온도·팬·전력·SEL)를 열어주기까지 — BMC IP 중복, 격리망 접근 불가, 스위치 VLAN 격리, LAN 채널·cipher suite, BMC 펌웨어 hang 문제를 하나씩 푼 과정"
excerpt: "'계정 하나 만들고 IP 주면 끝'일 줄 알았던 BMC 읽기전용 개방 작업 — BMC IP 중복/미설정, 격리망에 발 걸친 호스트 부재, 스위치 VLAN 격리, 다른 LAN 채널에 물린 케이블, hang한 BMC 펌웨어까지 층층이 쌓인 문제를 in-band 설정·bastion leg·LLDP 진단·USER 권한 계정·AC 전원 차단으로 푼 기록"
date: 2026-07-29
categories: Network
tags: [BMC, IPMI, ipmitool, OOB, bastion, VLAN, LLDP, tcpdump, 하드웨어모니터링, 읽기전용, CipherSuite, SEL, Prometheus, ipmi-exporter]
ref: bmc-ipmi-remote-hardware-monitoring
---

:bulb: 온프레미스 베어메탈 클러스터의 서버 하드웨어 상태(전원·온도·팬·전력)를 외부 협력기관에 **읽기전용**으로 열어주는 작업을 하면서 겪은 개념·문제·해결 과정을 정리한다. 실제 IP·MAC·기관명 등 식별 정보는 문서용 대역/가명으로 바꿨다 — IPMI 관리망 `10.20.0.0/24`, 노드 내부망 `10.10.0.0/24`, 외부 협력망 `203.0.113.0/29`, 모니터링 계정 `hwmon`, 협력기관 "PartnerOrg".  
대상: 베어메탈 서버의 OOB(out-of-band) 관리를 처음 뚫어보는 서버·인프라 엔지니어
{: .notice--info}

# [00] 배경 개념 — BMC·IPMI·in-band/OOB·bastion

작업을 이해하려면 용어 네 개만 잡으면 된다.

## [00-1] BMC (Baseboard Management Controller)

서버 메인보드에 붙은 **별도의 초소형 관리 컴퓨터**다. 서버 본체(OS)와 독립적으로, **대기전원(standby)만 들어와도 항상 켜져** 있다. 벤더별 상표명이 iDRAC(Dell), iLO(HPE), BMC(Intel/Supermicro) 등으로 다르지만 하는 일은 같다 — 전원 on/off·리셋, 온도·팬·전압·전력 센서 읽기, 하드웨어 이벤트 로그(SEL), 원격 콘솔. **OS가 죽어 있어도** 이 모든 게 된다.

## [00-2] IPMI (Intelligent Platform Management Interface)

BMC와 대화하는 **표준 프로토콜**이다. `ipmitool`이 사실상 표준 클라이언트다.

## [00-3] in-band vs out-of-band(OOB) — BMC에 접근하는 두 길

| 방식 | 경로 | 특징 |
|---|---|---|
| in-band | 그 서버 **OS 안에서** 메인보드 내부 버스(KCS)로 자기 BMC 접근 (`/dev/ipmi0`) | IP·계정 불필요. 단 OS가 켜져 있어야 함 |
| out-of-band | **네트워크로** BMC의 IP에 접속 (RMCP+, UDP 623) | BMC IP·계정·경로 필요. 노드 OS가 꺼져 있어도 됨 |

핵심 성질 하나 — **BMC는 OS 밖의 물건이라 리눅스 `ip addr`에 안 보인다.** 전용 관리 NIC(데이터 NIC와 물리적으로 다른 포트)를 통해 자기만의 IP로만 접근된다.

## [00-4] bastion(관문 호스트)

BMC들은 보통 **외부와 분리된 전용망**(IPMI 네트워크)에만 물려 있다. 보안·안정성 때문에 일부러 격리한 것이라 바깥에서 직접 못 들어간다. bastion은 그 격리망으로 통하는 **유일한 관문 서버**다 — 한 발은 사용자가 접속하는 망에, 다른 발은 IPMI 격리망에 담근다. 사용자는 bastion까지만 들어오고, bastion 위에서 `ipmitool`을 실행해 BMC와 대화한다.

> IPMI/BMC가 전체 인프라에서 차지하는 위치(관리 경로 이중화)는 [스위치 이중화 개념 글](/Network/switch-redundancy-network-concepts/)의 IPMI/BMC 절도 참고.

---

# [01] 필요성 — 왜 BMC 모니터링인가

외부 협력기관(PartnerOrg)이 우리 물리 노드의 **하드웨어 상태를 직접 확인**하고 싶어 했다. VM/컨테이너 지표(k8s·OpenStack)는 이미 Prometheus로 보이지만, 그건 **소프트웨어 레벨**이다. 정작 필요한 건 그 아래 — **물리 서버의 온도·팬·전력·전원 상태·하드웨어 이벤트**였다.

이 정보의 출처가 바로 BMC다. 그리고 요구는 **읽기전용**이었다. 전원제어나 콘솔 같은 위험한 권한은 주지 않고, 센서 값만 보게 한다.

두 가지 방식이 가능했다.

- **in-band exporter**: 각 노드가 자기 BMC를 로컬로 읽어 Prometheus에 올림. BMC 네트워크·계정 불필요. 단 노드 OS가 꺼지면 끊김.
- **out-of-band(원격)**: 수집기가 BMC IP로 접속해 읽음. 노드가 꺼져 있어도 수집. 대신 BMC망·계정 필요.

협력기관이 **자기 손으로 `ipmitool`을 돌려 확인**하고 싶어 했기 때문에, OOB 경로 + 읽기전용 계정을 준비하기로 했다. 이 결정이 이후 문제의 대부분을 불러왔다 — OOB는 "격리된 BMC망에 실제로 닿아야" 하기 때문이다.

---

# [02] 현상황 — 파보니 나온 문제들

"계정 하나 만들고 IP 주면 끝"일 줄 알았다. 실제로는 층층이 문제가 쌓여 있었다.

**(1) BMC IP가 제각각·중복이었다.**
노드 15대의 BMC IP를 조사하니, 상당수가 **같은 IP(중복)** 로 설정돼 있거나 아예 미설정이었다. 서로 다른 서브넷(`10.20.0.x`와 `10.30.0.x`)이 섞여 있기도 했다. 이 상태로는 하나의 관리망으로 묶을 수 없다.

**(2) 격리된 IPMI망에 "접속할 호스트"가 없었다.**
BMC들은 전부 **전용(dedicated) 관리 NIC**로 격리 스위치에만 물려 있었다. 결정적으로, **그 격리망에 발을 걸친 서버 OS가 하나도 없었다.** 노드가 자기 BMC조차 ping이 안 됐다(전용 NIC라 OS와 분리). 즉 BMC IP를 아무리 잘 맞춰도 **어디서도 접근할 수 없는** 상태였다.

**(3) 스위치가 조용히 VLAN으로 갈라놓고 있었다.**
bastion 후보 노드의 남는 랜포트를 격리 스위치에 물리고 IP를 줬는데도 BMC가 전혀 안 잡혔다. 링크 LED는 켜져 있었다. 원인은 **스위치의 VLAN 격리** — 관문 포트와 BMC 포트가 서로 다른 VLAN에 있었다.

**(4) 어떤 서버는 BMC가 "다른 채널"에 물려 있었다.**
대부분 노드는 BMC LAN이 채널 1에 있었는데, 한 서버(Intel 보드)는 **케이블이 채널 3(전용 관리포트)에 물려 있었다.** 채널 1에 IP를 넣어봐야 응답이 없다. 게다가 그 채널은 **암호 스위트(cipher suite) 표준값(suite 3)이 비활성**이라, IP를 옳게 넣어도 인증 세션이 안 열렸다.

**(5) BMC 펌웨어가 통째로 멈춰 있기도 했다.**
한 노드는 in-band `ipmitool mc info`조차 타임아웃이었다. `/dev/ipmi0`도 있고 커널모듈도 정상인데 BMC 칩이 응답을 안 했다. **BMC 펌웨어 자체가 hang**한 것. BMC는 대기전원으로 계속 돌기 때문에, 서버를 재부팅해도 풀리지 않는다.

---

# [03] 개선 1 — BMC IP 표준화 (in-band)

전 노드 BMC IP를 하나의 서브넷 `10.20.0.0/24`로 통일했다. 여기서 중요한 성질 — **BMC IP 설정은 네트워크 없이 in-band로 된다.** 각 노드에서:

```bash
sudo ipmitool lan set 1 ipsrc static
sudo ipmitool lan set 1 ipaddr 10.20.0.1X       # 노드별
sudo ipmitool lan set 1 netmask 255.255.255.0
sudo ipmitool lan set 1 access on
```

BMC망에 아직 못 닿는 상태에서도, 서버 안에서(KCS) BMC 설정을 바꿀 수 있다는 게 핵심이었다.

---

# [04] 개선 2 — bastion에 격리망 진입로(leg) 만들기

격리망에 발을 걸친 호스트가 없다는 문제는, **관문 노드의 남는 NIC 하나를 IPMI 스위치에 물리고** 그 위에 IP(`10.20.0.254`)를 얹어 해결한다. 이 leg가 유일한 진입로가 된다.

```bash
sudo ip addr add 10.20.0.254/24 dev <유휴 NIC> && sudo ip link set <유휴 NIC> up
# 재부팅 영속화는 netplan/systemd로
```

> 주의: 관문이 쿠버네티스 노드라면 `ip_forward=0`을 강제하지 말 것(파드 라우팅이 깨진다). 외부↔BMC 직접 라우팅 차단은 방화벽으로 한다.

---

# [05] 진단 기법 — "링크는 되는데 안 잡힐 때"

가장 배운 게 많은 부분이다. leg를 꽂았는데 BMC가 안 보일 때, **스위치에게 직접 물어보는** 방법들.

## [05-1] 누가 이 L2에 있나 — 패시브 캡처

```bash
sudo tcpdump -i <leg> -ne not stp
```

스위치 STP만 잡히고 BMC 프레임이 0이면, BMC가 같은 브로드캐스트 도메인에 없다는 뜻이다.

## [05-2] 이 포트가 무슨 VLAN인가 — LLDP

스위치는 30초마다 각 포트로 자기 이름·포트·PVID를 광고한다.

```bash
sudo tcpdump -i <leg> -v ether proto 0x88cc
```

여기서 `Port VLAN Id (PVID): 40` 같은 값이 튀어나온다. 추측이 아니라 **스위치가 직접 불러주는 값**이다. 이걸로 "관문 포트가 VLAN 40, BMC는 다른 VLAN"임을 확정했다.

## [05-3] 어느 채널의 포트가 실제 케이블에 물렸나

BMC 전용 포트는 OS에 안 보인다. 각 채널에 구분 IP를 임시로 주고 bastion에서 ARP로 확인하면, **응답이 오는 IP의 채널이 실제 물린 포트**다.

VLAN 문제는 스위치에서 관문 포트와 BMC 포트를 같은 VLAN으로 맞춰 풀었고, 채널 문제는 IP를 실제 물린 채널(3번)로 옮기고 그 채널의 cipher suite를 표준값으로 되살려 풀었다.

---

# [06] 개선 3 — 읽기전용 계정과 권한 모델

`ipmitool`은 도구일 뿐, 실제 가능한 동작은 **BMC 계정의 권한(privilege)** 이 정하고 BMC 펌웨어가 강제한다.

| priv | 이름 | 가능 |
|---|---|---|
| 2 | USER | 센서·SDR·SEL·상태 **읽기만** |
| 3 | OPERATOR | + 전원제어 |
| 4 | ADMIN | + 계정/채널 설정, 원격 콘솔 |

협력기관에는 **USER(2) 계정 `hwmon`** 을 각 BMC에 만들어줬다. 읽기전용이라 `ipmitool`로 접속은 되지만 `chassis power off` 같은 제어 명령은 BMC가 거부한다 — "도구 실행 가능"과 "전원제어 불가"가 공존한다. 추가로 무인증 암호 스위트(cipher 0)는 비활성 상태를 확인했다.

```bash
# 읽기전용 계정 생성 (각 노드 in-band)
sudo ipmitool user set name    <slot> hwmon
sudo ipmitool user set password <slot> '<강한비번>'   # 화면 노출 없이 파일에서 주입
sudo ipmitool user priv        <slot> 2 1             # 2 = USER
sudo ipmitool user enable      <slot>
```

사용 시 반드시 `-L USER`를 붙인다(안 붙이면 도구가 ADMIN 세션을 요청해 실패).

```bash
ipmitool -I lanplus -H 10.20.0.1X -U hwmon -f <비번파일> -L USER sdr type Temperature
```

---

# [07] 개선 4 — 멈춘 BMC 되살리기: AC 전원 차단

펌웨어가 hang한 BMC는 OS 재부팅으로 안 풀린다(BMC는 대기전원으로 계속 도니까). 유일한 방법은 **AC 전원을 완전히 끊는 것** — 전원코드를 뽑거나(이중전원이면 둘 다) PDU에서 내려 대기전원까지 방전(30초~수 분)한 뒤 재투입한다. 그러면 BMC 펌웨어가 콜드 부팅으로 리셋된다.

> 이때 그 노드에 살아있는 서비스가 있으면 먼저 안전하게 내려야 한다. 우리 경우 그 노드에 게스트 클러스터 VM이 돌고 있어서, VM을 정상 종료하고 오케스트레이터(자동복구)를 일시중지한 뒤 전원을 내렸다. AC 리셋 후 BMC는 정상 응답했다.

---

# [08] 결과와 교훈

- 대상 노드 **전부** BMC IP를 `10.20.0.0/24`로 통일하고, 읽기전용 계정 `hwmon`을 심었다.
- 관문(bastion)에 격리망 leg를 영속화해, 협력기관이 관문에 SSH로 들어와 `ipmitool`로 각 BMC의 온도·팬·전력·SEL을 조회할 수 있게 됐다. 권한은 읽기전용으로 못 박혀 있다.
- 상시 대시보드가 필요하면 `prometheus-ipmi-exporter`(원격 모드)를 leg 있는 호스트에서 돌려 target에 BMC들을 넣으면 된다. 수동 확인과 같은 데이터를 자동·주기화하는 것뿐이다.

얻은 교훈 몇 가지:

- **"IP 설정 성공 ≠ 도달 가능."** BMC IP가 맞아도 격리망에 발 걸친 호스트가 없거나, 스위치 VLAN이 다르거나, 케이블이 다른 채널에 물려 있으면 안 통한다.
- **스위치에게 직접 물어라.** 링크는 되는데 안 잡힐 때 LLDP(`0x88cc`) 한 방이면 포트·VLAN을 확정할 수 있다. 눈으로 케이블 뽑아보며 추측하는 것보다 빠르다.
- **BMC도 결국 컴퓨터라 hang한다.** 그리고 대기전원으로 도니까 OS 재부팅과 무관하다 — AC 차단만이 리셋이다.
- **읽기전용은 도구가 아니라 계정 권한으로 강제한다.** `ipmitool`을 쥐여줘도 USER 권한이면 전원제어는 못 한다.

BMC/IPMI는 평소엔 존재를 잊고 지내는 계층이지만, 물리 인프라를 다룰 때 가장 밑바닥에서 가장 확실한 정보를 준다. 한 번 제대로 뚫어두면, 노드가 꺼져 있어도 그 안이 지금 뜨거운지 팬이 도는지 알 수 있다.
