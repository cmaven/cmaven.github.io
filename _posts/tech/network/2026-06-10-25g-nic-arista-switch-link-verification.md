---
title: "25G 네트워크 구성 검증 — 서버-Arista 스위치-서버 링크 호환성 테스트"
description: "신규 구매한 25G NIC와 Arista 스위치 간 호환성을 검증하기 위한 단계별 테스트 가이드. 링크/속도, 트랜시버 인식, FEC 일치, 에러 카운터, iperf3 처리량까지 명령어·출력예·결과 해석 포함"
excerpt: "서버A 25G NIC ↔ Arista 25G 포트 ↔ 서버B 25G NIC 구성에서 링크 협상, 트랜시버 인식, FEC 모드 일치, 에러 카운터, 처리량/지연을 step by step으로 검증하는 방법. 신규 25G 카드와 스위치의 호환성 확인이 목적"
date: 2026-06-10
categories: Network
tags: [25G, SFP28, Arista, EOS, NIC, FEC, ethtool, iperf3, 트랜시버, 호환성, 링크검증, DAC, RS-FEC, Mellanox, Intel]
ref: 25g-nic-arista-switch-link-verification
---

:bulb: **신규로 구매한 25G NIC와 Arista 스위치가 정상적으로 호환되는지** 검증하는 테스트를 단계별로 정리한다.  
구성: `서버A(25G NIC) ── Arista 스위치(25G 포트) ── 서버B(25G NIC)`  
검증 핵심: 링크 속도(25G), 트랜시버 인식, **FEC 모드 일치**, 에러 카운터, 실측 처리량
{: .notice--info}

# [00] 전체 구성도

```
서버 A                         Arista 스위치                       서버 B
┌──────────────┐              ┌──────────────────┐              ┌──────────────┐
│ 25G NIC      │  SFP28 DAC   │ Ethernet1 (25G)  │  SFP28 DAC   │ 25G NIC      │
│ ens1f0       ├──────────────┤                  ├──────────────┤ ens1f0       │
│ 10.0.0.1/24  │              │ Ethernet2 (25G)  │              │ 10.0.0.2/24  │
└──────────────┘              └──────────────────┘              └──────────────┘
       │                              │                                │
   ethtool / iperf3            show interfaces             ethtool / iperf3
```

:warning: 25G 링크의 호환성 문제는 대부분 **① 트랜시버/케이블 미인식, ② FEC 모드 불일치, ③ 속도 자동협상 실패** 세 가지에서 발생한다. 이 글은 그 세 가지를 집중적으로 점검한다.
{: .notice--warning}

# [01] 테스트 목적과 합격 기준

| 검증 항목 | 합격 기준 |
|-----------|-----------|
| 링크 속도 | 양쪽 모두 **25 Gbps**, `up` 상태 |
| 트랜시버 인식 | 스위치/서버가 SFP28 트랜시버를 정상 식별, 벤더/시리얼 표시 |
| FEC 모드 | 스위치·서버 **양쪽 동일 모드**(RS-FEC 권장), uncorrected = 0 |
| 에러 카운터 | CRC/symbol/FEC uncorrected 오류 **증가 없음** |
| 처리량 | 다중 스트림 기준 **23 Gbps 이상**(오버헤드 감안) |
| 지연 | 동일 스위치 경유 RTT 수십 µs 수준, 손실 0% |

# [02] 사전 준비물 및 정보 수집

| 항목 | 내용 |
|------|------|
| 서버 A/B | OS(예: Ubuntu 22.04/RHEL 9), 25G NIC 모델, 슬롯(PCIe Gen3 x8 이상) |
| 25G NIC | 예: Mellanox ConnectX-4 Lx / ConnectX-5, Intel E810/XXV710, Broadcom |
| 케이블 | **SFP28** DAC(≤3m) 또는 AOC/광 트랜시버 — 25G 전용인지 확인(10G SFP+ 아님) |
| 스위치 | Arista EOS, 25G 지원 포트(예: 7050X3/7060X 계열) |
| 테스트 도구 | `ethtool`, `iperf3`, `ping`, (옵션) `sockperf`, `lspci` |

```bash
# 서버에 도구 설치 (Ubuntu)
sudo apt-get install -y ethtool iperf3 pciutils
# RHEL/Rocky
sudo dnf install -y ethtool iperf3 pciutils
```

# [03] 물리 결선 및 인터페이스 식별

서버 A의 NIC를 스위치 `Ethernet1`, 서버 B의 NIC를 `Ethernet2`에 SFP28 케이블로 연결한다. 서버에서 25G 인터페이스 이름을 먼저 확인한다.

```bash
# 인터페이스 목록과 속도/상태
ip -br link
```

출력 예:

```
lo               UNKNOWN        00:00:00:00:00:00
eno1             UP             a0:36:9f:xx:xx:xx
ens1f0           UP             b8:ce:f6:xx:xx:xx
```

```bash
# NIC 모델과 PCIe 위치 확인
lspci | grep -i ethernet
```

출력 예:

```
01:00.0 Ethernet controller: Mellanox Technologies MT27710 Family [ConnectX-4 Lx]
```

> `ens1f0`가 테스트 대상 25G 인터페이스다. 양 서버 모두 동일하게 확인한다.

# [04] 스위치 측 — 링크/속도 확인

Arista 콘솔(또는 SSH)에서 포트 상태를 본다.

```
sw-core-01# show interfaces Ethernet1 status
```

출력 예:

```
Port       Name   Status       Vlan     Duplex Speed  Type            Flags
Et1               connected    1        full   25G    25GBASE-CR
```

| 필드 | 의미 |
|------|------|
| `Status: connected` | 물리 링크 정상 (`notconnect`이면 미연결/협상 실패) |
| `Speed: 25G` | 25 Gbps로 협상됨 (`10G`로 떨어지면 케이블/포트 설정 문제) |
| `Type: 25GBASE-CR` | DAC 동축(Copper). 광이면 `25GBASE-SR` 등 |

여러 포트를 한 번에 보려면:

```
sw-core-01# show interfaces status | include 25G
```

**포트가 25G로 "설정"되어 있는지 확인 (협상 결과 ≠ 설정값):**

`show interfaces ... status`의 `Speed`는 *협상된(negotiated)* 결과다. 포트에 어떤 속도가 *설정(configured)*되어 있는지는 running-config로 따로 확인해야 한다. 자동협상이 잘 안 붙는 환경에서는 포트를 25G로 **강제 고정**해 두는 것이 안전하다.

```
sw-core-01# show running-config interfaces Ethernet1
```

출력 예 (기본 — 자동협상):

```
interface Ethernet1
   ! speed 설정 줄이 없으면 auto (자동협상)
```

출력 예 (25G 강제 설정):

```
interface Ethernet1
   speed forced 25gfull
```

현재 동작 속도와 함께 보려면:

```
sw-core-01# show interfaces Ethernet1 status | include 25G
sw-core-01# show interfaces Ethernet1 | include -i -E 'Speed|BW|bandwidth'
```

| 확인 | 의미 |
|------|------|
| running-config에 `speed` 줄 없음 | 자동협상(auto) — 트랜시버가 25G면 25G로 협상됨 |
| `speed forced 25gfull` | 25G로 강제 고정 (자동협상 실패/플랫폼 호환성 이슈 시 사용) |
| `status`의 Speed가 `25G` | 실제로 25G로 링크업된 상태 |

**25G로 강제 설정(필요 시):**

```
sw-core-01(config)# interface Ethernet1
sw-core-01(config-if-Et1)# speed forced 25gfull
```

:bulb: 일부 플랫폼은 포트가 40G/100G **브레이크아웃 그룹**(예: 4x10G / 4x25G)으로 묶여 있어 25G 단독으로 안 잡힐 수 있다. 이 경우 해당 포트 그룹을 25G 브레이크아웃 모드로 먼저 분리해야 `Ethernet1/1` 같은 25G 서브포트가 나타난다.
{: .notice--info}

# [05] 스위치 측 — 트랜시버 인식 확인 (호환성 핵심)

신규 트랜시버/케이블을 스위치가 정상 식별하는지 본다. Arista는 미지원/타사 트랜시버에 경고를 남기는 경우가 있다.

```
sw-core-01# show interfaces Ethernet1 transceiver
```

출력 예:

```
Port    Vendor          Part Number    Serial Number    Type
Et1     Arista Networks CAB-D-D-25G-3M  XYZ123456789    25GBASE-CR
```

상세 진단(광 트랜시버의 광 파워 등):

```
sw-core-01# show interfaces Ethernet1 transceiver detail
```

| 확인 포인트 | 의미 |
|-------------|------|
| Vendor/Part/Serial 표시됨 | 트랜시버 EEPROM 정상 인식 |
| `Type`이 25GBASE-* | 25G 전용 케이블 (10G로 표시되면 잘못된 케이블) |
| 광이면 Rx Power 범위 내 | 광 신호 레벨 정상 |

:warning: Arista에서 타사(third-party) 트랜시버는 기본 정책에 따라 차단될 수 있다. 필요 시 `show logging | include transceiver`로 거부 로그를 확인하고, 정책상 허용 모델인지 점검한다.
{: .notice--warning}

# [06] FEC 모드 확인 및 일치 (가장 중요)

25G에서 **FEC(Forward Error Correction) 모드가 양쪽에서 다르면 링크가 올라오지 않거나, 올라와도 에러가 폭증**한다. 신규 카드 호환성 검증의 핵심 단계다.

- **RS-FEC (CL91, Reed-Solomon)**: 25GBASE-CR(3m 초과 DAC), SR 광에서 일반적으로 요구
- **FC-FEC (CL74, Fire-code / BASE-R)**: 짧은 DAC에서 사용 가능
- **None(disabled)**: 매우 짧은 패시브 케이블 한정

**스위치 측 FEC 확인:**

```
sw-core-01# show interfaces Ethernet1 phy detail | include -i fec
```

또는 인터페이스 설정에서:

```
sw-core-01# show running-config interfaces Ethernet1
```

출력 예:

```
interface Ethernet1
   error-correction encoding reed-solomon
```

**스위치 측 FEC 설정(필요 시):**

```
sw-core-01(config)# interface Ethernet1
sw-core-01(config-if-Et1)# error-correction encoding reed-solomon
```

> 옵션: `reed-solomon`(RS-FEC), `fire-code`(FC-FEC), `disabled`. 서버 측과 **반드시 동일하게** 맞춘다.

**서버 측 FEC 확인:**

```bash
ethtool --show-fec ens1f0
```

출력 예:

```
FEC parameters for ens1f0:
Configured FEC encodings: Auto
Active FEC encoding: RS
```

| 필드 | 의미 |
|------|------|
| `Active FEC encoding: RS` | 현재 RS-FEC 동작 중 (스위치와 일치해야 함) |
| `Auto` | 자동 협상. 한쪽이 고정이면 양쪽 고정 권장 |

**서버 측 FEC 강제 설정(불일치 시):**

```bash
# RS-FEC로 고정
sudo ethtool --set-fec ens1f0 encoding rs
# 옵션: rs | baser(=FC-FEC) | off | auto
```

:bulb: **양쪽을 동일 모드로 고정**하는 것이 가장 안정적이다. 한쪽 `auto`, 다른 쪽 `rs`처럼 섞이면 간헐적 링크 플랩이 발생할 수 있다.
{: .notice--info}

# [07] 서버 측 — 링크/속도 확인

```bash
ethtool ens1f0
```

출력 예(요약):

```
Settings for ens1f0:
        Supported link modes:   25000baseCR/Full
        Speed: 25000Mb/s
        Duplex: Full
        Auto-negotiation: on
        Link detected: yes
```

| 필드 | 의미 |
|------|------|
| `Speed: 25000Mb/s` | 25 Gbps 링크 정상 |
| `Link detected: yes` | 물리 링크 up |
| `Auto-negotiation: on` | 자동협상 사용 (양쪽 정책 일치 필요) |

양 서버(A/B) 모두 동일하게 `25000Mb/s`, `Link detected: yes`여야 한다.

# [08] 서버 측 — 드라이버/펌웨어 확인

신규 카드라면 드라이버·펌웨어 버전이 호환성에 직접 영향을 준다.

```bash
ethtool -i ens1f0
```

출력 예:

```
driver: mlx5_core
version: 5.15.0-xx
firmware-version: 14.32.1010 (MT_0000000080)
bus-info: 0000:01:00.0
```

| 필드 | 의미 |
|------|------|
| `driver` | 커널 NIC 드라이버 (예: `mlx5_core`, `ice`, `i40e`, `bnxt_en`) |
| `firmware-version` | NIC 펌웨어 — 벤더 권장 최신 버전인지 확인 |

> 펌웨어가 오래되면 25G/FEC 협상 버그가 있을 수 있으므로 벤더 릴리스 노트와 대조한다.

# [09] PCIe 대역폭 확인 (병목 점검)

25G(≈3.125 GB/s)를 내려면 PCIe Gen3 x8 이상이 필요하다.

```bash
sudo lspci -vv -s 01:00.0 | grep -i -E 'LnkCap|LnkSta'
```

출력 예:

```
LnkCap: ... Speed 8GT/s, Width x8
LnkSta: ... Speed 8GT/s, Width x8
```

| 확인 | 의미 |
|------|------|
| `LnkSta` Width가 `x8` | 슬롯이 x8로 동작 (x4로 떨어지면 처리량 저하) |
| Speed `8GT/s`(Gen3) 이상 | 25G 라인레이트 수용 가능 |

# [10] IP 설정 및 기본 연결 확인

```bash
# 서버 A
sudo ip addr add 10.0.0.1/24 dev ens1f0
sudo ip link set ens1f0 up
# 서버 B
sudo ip addr add 10.0.0.2/24 dev ens1f0
sudo ip link set ens1f0 up
```

연결 확인:

```bash
# 서버 A에서 B로
ping -c 4 10.0.0.2
```

출력 예:

```
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=0.045 ms
...
4 packets transmitted, 4 received, 0% packet loss
```

> `0% packet loss`와 µs 단위 RTT면 L2/L3 경로 정상.

# [11] MTU / Jumbo Frame 설정 및 검증

고처리량 테스트 전 Jumbo Frame(9000)을 맞추면 CPU 부하가 줄고 처리량이 오른다. **서버 양쪽과 스위치 포트/VLAN 모두 동일 MTU**여야 한다.

```bash
# 서버 양쪽
sudo ip link set ens1f0 mtu 9000
```

```
# 스위치 (Arista) — 포트 L2 MTU
sw-core-01(config)# interface Ethernet1
sw-core-01(config-if-Et1)# l2 mtu 9214
```

Jumbo 경로 검증(단편화 없이 9000B 전송):

```bash
ping -M do -s 8972 -c 4 10.0.0.2
```

| 결과 | 의미 |
|------|------|
| 성공(loss 0%) | 9000 MTU 경로 정상 |
| `Message too long` / 100% loss | 중간 구간 MTU 불일치 → 스위치/서버 MTU 재확인 |

# [12] 처리량(Throughput) 테스트 — iperf3

단일 TCP 스트림은 단일 CPU 코어 한계로 25G를 못 채울 수 있다. **다중 스트림(`-P`)**으로 라인레이트에 근접시킨다.

**서버 B(수신, 서버 역할):**

```bash
iperf3 -s
```

**서버 A(송신, 클라이언트):**

```bash
# 8개 병렬 스트림, 30초
iperf3 -c 10.0.0.2 -P 8 -t 30
```

출력 예(요약):

```
[SUM]   0.00-30.00  sec  82.1 GBytes  23.5 Gbits/sec   0   sender
[SUM]   0.00-30.00  sec  82.0 GBytes  23.5 Gbits/sec       receiver
```

| 필드 | 의미 |
|------|------|
| `23.5 Gbits/sec` | 실측 처리량 — 25G 대비 ~94%, TCP/헤더 오버헤드 감안 시 정상 |
| `Retr`(재전송) 0 또는 소량 | 0에 가까울수록 좋음. 급증하면 FEC/혼잡/버퍼 문제 |

**역방향(B→A)도 테스트:**

```bash
iperf3 -c 10.0.0.2 -P 8 -t 30 -R
```

> 양방향 모두 23 Gbps 이상이면 호환성·성능 합격. 한 방향만 낮으면 해당 송신측 NIC/케이블 점검.

UDP로 라인레이트 손실률을 보려면:

```bash
iperf3 -c 10.0.0.2 -u -b 25G -t 20
```

`Lost/Total Datagrams`가 0%에 가까워야 한다.

# [13] 종단간(PC A → 스위치 → PC B) 25G 검증

여기까지 각 구간(서버A, 스위치 포트, 서버B)을 **개별**로 확인했다. 마지막으로 **PC A에서 25G로 패킷을 보냈을 때 PC B가 동일하게 25G로 받는지**를 종단간(end-to-end)으로 확인한다. 이 테스트가 통과하면 경로상의 모든 요소(**서버A NIC → 스위치 포워딩 → 서버B NIC**)가 25G를 만족한다는 것을 한 번에 증명할 수 있다.

**판정 논리:**

| 관찰 | 결론 |
|------|------|
| PC A 송신 ≈ 25G **그리고** PC B 수신 ≈ 25G | 송신 NIC · 스위치 포워딩 · 수신 NIC **모두 25G 정상** |
| PC A는 25G 송신, PC B 수신 < 25G | 스위치 큐 드롭 또는 **수신측 NIC/PCIe 병목** |
| PC A가 25G로 송신 자체를 못 함 | **송신측 NIC/케이블/포트 협상** 문제 |

> 핵심: 한쪽 끝에서 넣은 라인레이트가 반대쪽 끝에서 그대로 나오면, 중간의 스위치와 양쪽 NIC가 모두 25G를 처리한다는 것을 **동시에** 입증한다.

**1) 송신 측정 — PC A:**

```bash
# PC A → PC B, 8 스트림으로 라인레이트에 근접 송신
iperf3 -c 10.0.0.2 -P 8 -t 30
```

**2) 수신 측정 — PC B (송신과 동시에 확인):**

PC B의 `iperf3 -s` 출력에서 `receiver` 라인의 Gbits/sec가 PC A 송신값과 일치하는지 본다. 인터페이스 실시간 수신율을 별도로 보려면:

```bash
# PC B에서 1초 간격 수신 바이트 증가량 → 수신 라인레이트 환산
sar -n DEV 1
# 또는
ifstat -i ens1f0 1
```

**출력 해석:**

```
# PC A (송신) iperf3
[SUM]   0.00-30.00  sec  82.1 GBytes  23.5 Gbits/sec        sender
# PC B (수신) iperf3 서버
[SUM]   0.00-30.00  sec  82.0 GBytes  23.5 Gbits/sec        receiver
# PC B (sar -n DEV)
ens1f0  ...  rxkB/s ≈ 2.9e6   (≈ 23.5 Gbps 수신)
```

| 확인 | 의미 |
|------|------|
| 송신 ≈ 수신 ≈ 23 Gbps+ | **종단간 25G 검증 통과** — 스위치 + 양쪽 NIC 모두 합격 |
| 수신이 송신보다 크게 낮음 | 스위치 드롭/수신 NIC 병목 → `show interfaces Et2 counters`, `ethtool -S`로 drop 확인 |

**3) 양방향 동시(전이중) 확인:**

25G는 전이중(full-duplex)이므로 양방향 동시에 각각 25G가 가능해야 한다.

```bash
# PC A: 송신+수신 동시 부하
iperf3 -c 10.0.0.2 -P 8 -t 30 --bidir
```

출력 예(요약):

```
[SUM][TX]  0.00-30.00  sec  81.9 GBytes  23.4 Gbits/sec        sender
[SUM][RX]  0.00-30.00  sec  81.8 GBytes  23.4 Gbits/sec        receiver
```

> 양방향 각각 ~23 Gbps가 유지되면 전이중 25G까지 검증 완료. 이로써 "PC A에서 25G로 보낸 트래픽을 PC B가 25G로 수신"이 실측으로 확인되어, **스위치와 양쪽 PC의 NIC 모두 25G를 만족**한다고 판단할 수 있다.

# [14] 지연(Latency) 테스트

```bash
# 빠른 간격으로 RTT 분포 확인
sudo ping -i 0.2 -c 50 10.0.0.2
```

출력 예:

```
rtt min/avg/max/mdev = 0.038/0.046/0.071/0.008 ms
```

| 지표 | 의미 |
|------|------|
| `avg` 수십 µs | 동일 스위치 경유 정상 |
| `mdev`(지터) 작음 | 안정적. 크게 튀면 FEC 재시도/버퍼 문제 의심 |

# [15] 에러 카운터 확인 (테스트 전후 비교)

처리량 테스트 **전후로** 카운터를 떠서 증가분을 본다. 호환성 문제는 여기서 드러난다.

**서버 측:**

```bash
ethtool -S ens1f0 | grep -i -E 'err|drop|fec|crc'
```

출력 예:

```
     rx_crc_errors_phy: 0
     rx_corrected_bits_phy: 1024
     rx_symbol_err_phy: 0
     fec_uncorrectable_blocks: 0
```

| 카운터 | 의미 |
|--------|------|
| `rx_crc_errors_phy` | CRC 오류 — **증가하면 안 됨** (케이블/FEC 문제) |
| `fec_corrected_*` | FEC가 정정한 비트 — 소량 증가는 정상(FEC 정상 동작 증거) |
| `fec_uncorrectable_*` | **정정 실패 — 0이어야 함**. 증가 시 링크 품질/FEC 불일치 |
| `rx_symbol_err_phy` | 심볼 오류 — 0 권장 |

**스위치 측:**

```
sw-core-01# show interfaces Ethernet1 counters errors
```

출력 예:

```
Port    FCS Err  Align Err  Symbol Err  Rx Err  Tx Err
Et1     0        0          0           0       0
```

```
# FEC 통계 (corrected/uncorrected codeword)
sw-core-01# show interfaces Ethernet1 phy detail | include -i -A2 fec
```

| 확인 | 의미 |
|------|------|
| FCS/Symbol Err 0 유지 | 링크 품질 양호 |
| FEC uncorrected = 0 | **합격 필수 조건** |

# [16] 호환성 트러블슈팅

| 증상 | 원인/조치 |
|------|-----------|
| 링크 안 올라옴(`notconnect`/`Link detected: no`) | FEC 모드 불일치 → 스위치·서버를 동일 모드(RS-FEC)로 고정. 케이블이 25G SFP28인지 확인 |
| 25G가 아닌 10G로 협상 | 케이블이 10G SFP+거나 포트 강제 속도 설정 → 스위치 `speed forced 25gfull` 또는 자동협상 정렬 |
| 트랜시버 미인식/거부 로그 | 타사 트랜시버 차단 정책 → `show logging | include transceiver` 확인, 허용 모델/정책 점검 |
| 링크 플랩(간헐 끊김) | 한쪽 FEC `auto`, 다른 쪽 고정 → 양쪽 동일 고정. 펌웨어 업데이트 검토 |
| 처리량이 10G 수준 | PCIe x4 강등(`LnkSta` 확인), 단일 스트림 한계 → `-P` 다중 스트림, IRQ/RSS 튜닝 |
| FEC corrected 급증 + uncorrected 발생 | 케이블 품질/길이 한계 → 케이블 교체, 더 강한 FEC(RS) 적용 |

# [17] 요약 체크리스트

| 단계 | 위치 | 확인 |
|------|------|------|
| STEP 04 | 스위치 | `show interfaces Et1 status` → `connected`, `25G` |
| STEP 04 | 스위치 | `show running-config interfaces Et1` → 포트 25G 설정(auto/`forced 25gfull`) 확인 |
| STEP 05 | 스위치 | `show interfaces Et1 transceiver` → 트랜시버 인식 |
| STEP 06 | 스위치+서버 | FEC 모드 **양쪽 동일**(RS 권장) |
| STEP 07 | 서버 | `ethtool ens1f0` → `25000Mb/s`, `Link: yes` |
| STEP 08 | 서버 | `ethtool -i` → 드라이버/펌웨어 최신 |
| STEP 09 | 서버 | `lspci` → PCIe x8 / Gen3+ |
| STEP 11 | 양쪽 | MTU 9000 일치, `ping -M do -s 8972` 성공 |
| STEP 12 | 서버 | `iperf3 -P 8` → 양방향 23 Gbps+ |
| STEP 13 | 양쪽 | **종단간**: PC A 송신 ≈ PC B 수신 ≈ 23 Gbps+ (`--bidir` 전이중 포함) |
| STEP 15 | 양쪽 | CRC/FEC uncorrected **증가 0** |

> 위 항목이 모두 통과하면, 신규 25G NIC와 Arista 스위치 간 **호환성·성능 검증 완료**로 판단한다. 특히 STEP 13(종단간)에서 PC A가 보낸 25G를 PC B가 그대로 수신하면, 스위치와 양쪽 PC NIC 모두 25G를 만족함이 한 번에 입증된다.
