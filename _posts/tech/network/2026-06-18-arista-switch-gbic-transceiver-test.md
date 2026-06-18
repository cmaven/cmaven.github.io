---
title: "Arista 스위치 GBIC(SFP28) 모듈 테스트 — xcvr-unsupported 진단과 결론 도출"
description: "Arista EOS 스위치에 장착한 25G SFP28 트랜시버(GBIC)를 명령어로 테스트해 링크 미연결 원인을 진단하는 방법. transceiver 광파워, errdisabled 사유, inventory 모듈 식별, 서버 ethtool 교차 확인으로 xcvr-unsupported 결론을 도출하는 전체 절차"
excerpt: "25G 링크가 올라오지 않을 때 스위치 GBIC 모듈을 어떻게 테스트하고 결론을 내리는가. Tx/Rx 광파워와 Bias Current, errdisabled reason, show inventory, 서버 ethtool을 교차 분석해 OEM/타사 트랜시버가 unsupported로 차단된 상황을 단계별로 진단한다"
date: 2026-06-18
categories: Network
tags: [Arista, EOS, SFP28, GBIC, 트랜시버, transceiver, 25G, errdisabled, xcvr-unsupported, 광모듈, 호환성, 링크진단, FEC]
ref: arista-switch-gbic-transceiver-test
---

:bulb: 25G 링크가 올라오지 않을 때, **스위치에 장착한 GBIC(SFP28 트랜시버) 모듈을 직접 테스트해 원인을 진단하고 결론을 도출**하는 절차를 정리한다.  
구성: `서버(25G NIC) ── 광케이블 ── Arista 스위치(SFP28 포트)`  
핵심 진단 포인트: **Tx/Rx 광파워**, **Bias Current**, **errdisabled reason**, **inventory 모듈 식별**, **서버 ethtool 교차 확인**
{: .notice--info}

> 이 글의 CLI 출력은 실제 장비(`DCS-7050SX3-48YC8C-F` / EOS 4.30.4M, 호스트명 `sw-core-01`)에서 25G SFP28 트랜시버를 테스트한 기록을 참조 예시로 사용했다. 시리얼 번호·MAC 주소 등 장비 식별 정보는 마스킹(`xxxx`)했고, IP는 문서화 예시값을 사용한다. 실제 진단 시 본인 환경의 값으로 바꿔서 본다.

# [00] 테스트 목적과 구성

신규 25G NIC를 Arista 스위치에 연결했는데 링크가 올라오지 않는 상황에서, **원인이 트랜시버(GBIC)에 있는지**를 가려내는 것이 목표다. 테스트 대상은 여러 포트에 장착된 25G SFP28 광모듈이다.

| 항목 | 값 |
|------|-----|
| 스위치 | `sw-core-01` (DCS-7050SX3-48YC8C-F / EOS 4.30.4M) |
| 테스트 포트 | `Ethernet21`, `Ethernet23`, `Ethernet35`, `Ethernet37` |
| 트랜시버 | OEM `25GBASE-SR`, MikroTik `XS+31LC10D`(`25GBASE-LR`) |
| 서버 NIC | `ens801f0np0` (25G SFP28) |

> 한두 포트만 보면 "그 모듈만 불량"이라 오판하기 쉽다. **서로 다른 모듈을 장착한 여러 포트를 교차 테스트**해야 개별 모듈 문제인지 정책 문제인지 구분된다.

# [01] 테스트 방법 — 무엇을 어떤 명령으로 보는가

GBIC 모듈 진단은 다음 4가지를 순서대로 확인한다.

| 단계 | 확인 항목 | 명령 |
|---:|------|------|
| 1 | 포트 상태 / 트랜시버 타입 | `show interfaces EthernetN status` |
| 2 | 광파워(Tx/Rx)·Bias | `show interfaces EthernetN transceiver` |
| 3 | errdisabled 사유 | `show interfaces status errdisabled` |
| 4 | 모듈 제조사/모델/시리얼 | `show inventory` |

핵심은 **광파워 3종 값**이다.

- **Bias Current(mA)** — 송신 레이저 구동 전류. `0.00 mA`면 송신부가 꺼진 것.
- **Tx Power(dBm)** — 스위치가 내보내는 광 출력. `-30.00 dBm`이면 사실상 송신 없음.
- **Rx Power(dBm)** — 상대편(서버)에서 들어오는 광 신호. 정상 범위면 케이블·상대 송신은 살아 있다는 뜻.

# [02] 포트별 트랜시버 상태 수집

## [02-1] Ethernet21 — 포트 상태

```text
sw-core-01#show interfaces Ethernet21 status
Port       Name   Status       Vlan     Duplex Speed  Type         Flags Encapsulation
Et21              errdisabled  1        full   25G    25GBASE-SR
```

트랜시버 타입은 `25GBASE-SR`, 속도 `25G`로 **정상 인식**된다. 그러나 상태가 `errdisabled`다. 케이블이 빠진 `notconnect`가 아니라, 스위치가 특정 오류 조건을 감지해 포트를 강제 비활성화한 상태다.

## [02-2] Ethernet21 — 광파워

```text
sw-core-01#show interfaces Ethernet21 transceiver
                               Bias      Optical   Optical
          Temp       Voltage   Current   Tx Power  Rx Power
Port      (Celsius)  (Volts)   (mA)      (dBm)     (dBm)     Last Update
-----     ---------  --------  --------  --------  --------  -------------------
Et21       31.11      3.31      0.00     -30.00    -0.28     0:00:01 ago
```

| 항목 | 값 | 의미 |
|---|---:|---|
| Bias Current | `0.00 mA` | 송신 레이저 구동 전류 없음 |
| Tx Power | `-30.00 dBm` | 스위치 송신 광 출력이 사실상 없음 |
| Rx Power | `-0.28 dBm` | 상대(서버)에서 오는 광 신호는 감지됨 |

즉 **스위치는 받기는 하지만 보내지 않는** 상태다. 이 비대칭이 핵심 단서다.

## [02-3] Ethernet21 — 상세 카운터

```text
sw-core-01#show interfaces Ethernet21
Ethernet21 is down, line protocol is down (errdisabled)
  Hardware is Ethernet, address is xxxx.xxxx.5f06 (bia xxxx.xxxx.5f06)
  Ethernet MTU 9214 bytes, BW 25000000 kbit
  Full-duplex, 25Gb/s, auto negotiation: off, uni-link: n/a
  ...
     0 input errors, 0 CRC, 0 alignment, 0 symbol, 0 input discards
     0 output errors, 0 collisions
```

CRC·symbol·alignment 에러가 **모두 0**이다. 링크가 올라온 뒤 품질 저하로 에러가 쌓인 것이 아니라, **정상 동작 단계에 진입하기 전에 차단**됐다는 뜻이다.

## [02-4] Ethernet23 — 동일 패턴(25GBASE-SR)

```text
sw-core-01#show interfaces Ethernet23 transceiver
Port      ...  Current(mA)  Tx Power(dBm)  Rx Power(dBm)  Last Update
Et23      ...  0.00         -30.00         -0.38          0:00:01 ago
```

`Et23`도 `Bias 0.00 mA / Tx -30.00 dBm / Rx -0.38 dBm`으로 `Et21`과 똑같다. 포트 두 개가 동일 증상이면 **개별 포트 고장보다 모듈/정책 문제** 쪽으로 무게가 실린다.

# [03] 교차 테스트 — 다른 모듈에서도 재현되는가

같은 결론을 내리려면 **다른 트랜시버**에서도 같은 증상이 나오는지 봐야 한다.

## [03-1] Ethernet35 — 다른 OEM SR 모듈

```text
sw-core-01#show interfaces Ethernet35 transceiver
Et35      ...  0.00(mA)   -30.00(Tx dBm)   -0.74(Rx dBm)
```

`transceiver detail`로 임계값과 비교하면 더 명확하다.

```text
sw-core-01#show interfaces Ethernet35 transceiver detail
           Tx Power      Low Alarm   Low Warn
Port       (dBm)         (dBm)       (dBm)
-------    ------------  ----------  ----------
Et35       -30.00        -11.40      -8.40
           Rx Power
Et35       -0.75         (정상 범위)
```

현재 `Tx Power -30.00 dBm`은 Low Alarm 기준 `-11.40 dBm`보다 훨씬 낮다. 반면 `Rx Power`는 정상 범위다. → **스위치가 송신 레이저를 구동하지 않는** 결과로 해석된다.

## [03-2] Ethernet37 — MikroTik 25GBASE-LR 모듈

SR 계열만이 아니라 **LR 모듈**도 테스트한다.

```text
sw-core-01#show interfaces Ethernet37 status
Et37              errdisabled  1        full   25G    25GBASE-LR

sw-core-01#show interfaces Ethernet37 transceiver detail
           Current   Low Alarm
Et37       0.00 mA   1.00 mA
           Tx Power  Low Alarm
Et37       -30.00    -7.00 dBm
           Rx Power  Low Alarm
Et37       1.05      -19.00 dBm   (정상 범위)
```

`25GBASE-LR`인 MikroTik `XS+31LC10D`에서도 `Bias 0.00 mA / Tx -30.00 dBm`이고 `Rx`만 정상이다. **SR이든 LR이든 동일 증상**이라는 점이 결정적이다.

# [04] errdisabled 사유 확인 — 결정적 근거

```text
sw-core-01#show interfaces status errdisabled
   Port       Name             Status         Reason
---------- ---------------- ----------------- ----------------
   Et21                        errdisabled    xcvr-unsupported
   Et23                        errdisabled    xcvr-unsupported
   Et35                        errdisabled    xcvr-unsupported
   Et37                        errdisabled    xcvr-unsupported
   ... (Et1, Et3, ... 다수 포트 동일)
```

네 포트 모두 — 그리고 다수의 다른 포트까지 — 사유가 `xcvr-unsupported`다. **스위치가 장착된 트랜시버를 "지원되지 않는 모듈"로 분류해 포트를 차단**한 것이다.

`xcvr-unsupported`는 보통 다음 상황에서 발생한다.

- Arista 인증/호환 목록에 없는 SFP28 모듈 사용
- 타 벤더 전용으로 코딩된 광모듈 사용
- EEPROM 정보가 Arista 장비와 맞지 않는 모듈
- EOS 정책상 unsupported transceiver 차단이 활성화된 상태

# [05] inventory로 모듈 식별

차단된 모듈이 무엇인지 `show inventory`로 확인한다.

```text
sw-core-01#show inventory
System has 56 switched transceiver slots
  Port Manufacturer     Model            Serial Number    Rev
  ---- ---------------- ---------------- ---------------- ----
  21   OEM              25GBASE-SR       PS3Hxxxxxx       0002
  23   OEM              25GBASE-SR       PS3Hxxxxxx       0002
  35   OEM              25GBASE-SR       PS3Hxxxxxx       0002
  37   MikroTik         XS+31LC10D       OLxxxxxxxxxx     1.0
```

여기서 중요한 포인트: **스위치가 제조사/모델/시리얼/리비전을 정상적으로 읽고 있다**는 것이다.

```text
37   MikroTik   XS+31LC10D   OLxxxxxxxxxx   1.0
```

즉 EEPROM을 **못 읽는** 상태가 아니다. 정보는 읽지만 **Arista 호환 모듈로 인정하지 않아** `xcvr-unsupported`로 차단한 것이다.

# [06] 서버 측 교차 확인 (ethtool)

스위치 측 진단을 서버에서 한 번 더 확인한다.

```text
root@server-a:~# ethtool ens801f0np0
        Supported link modes:   25000baseSR/Full ...
        Supported FEC modes: None        RS      BASER
        Speed: Unknown!
        Duplex: Unknown! (255)
        Link detected: no (No cable)
```

서버 NIC는 25G SR(`25000baseSR/Full`)과 RS-FEC를 **지원**한다. 그런데 `Link detected: no (No cable)`다.

스위치가 `Tx Power -30.00 dBm` / `Bias 0.00 mA`로 송신을 끈 상태이므로, 서버 입장에서 "케이블 없음"으로 보이는 것은 **자연스러운 귀결**이다. 서버 NIC 기능 문제가 아니다.

```text
root@server-a:~# ethtool --show-fec ens801f0np0
Configured FEC encodings: Auto
Active FEC encoding: None
```

`Active FEC: None`도 링크가 안 올라온 결과일 뿐, FEC 불일치의 증거가 아니다.

# [07] 결과 해석 — 링크의 물리 상태

수집값을 종합하면 광 경로의 상태는 다음과 같다.

```text
서버 NIC Tx  ─────────────▶  스위치 Rx 감지됨 (Rx Power 정상)
서버 NIC Rx  ◀────────────X  스위치 Tx 비활성화 (Bias 0mA, Tx -30dBm)
```

| 근거 | 값 |
|------|-----|
| 스위치 Rx Power | Et21 -0.28 / Et23 -0.38 / Et35 -0.74 / Et37 1.05 dBm (감지됨) |
| 스위치 Tx Power | 네 포트 모두 `-30.00 dBm` (송신 없음) |
| 스위치 Bias | 네 포트 모두 `0.00 mA` (레이저 미구동) |
| errdisabled reason | 네 포트 모두 `xcvr-unsupported` |
| 서버 | `Link detected: no (No cable)` |

# [08] 원인 결론

| 우선순위 | 원인 후보 | 판단 |
|---:|------|------|
| 1 | Arista 트랜시버 호환성/지원 정책 | **매우 높음** |
| 2 | OEM/타사 25G SR·LR 모듈이 EOS에서 unsupported로 분류 | **매우 높음** |
| 3 | unsupported transceiver unlock/license 미적용 | 높음 |
| 4 | 광케이블 문제 | 낮음 (Rx 신호 감지됨) |
| 5 | 서버 NIC 설정 문제 | 낮음 (25G·RS-FEC 지원) |
| 6 | FEC 불일치 | 후순위 (링크 차단이 선행) |
| 7 | MTU/IP 설정 | 링크 up 이후 검증 항목 |

**결론**: SR/LR 케이블 종류나 서버 설정 이전에, **Arista 스위치가 현재 장착된 타사/OEM 25G SFP28 트랜시버 전반을 unsupported로 차단하는 문제**다. 특정 모듈 하나의 불량이 아니다(서로 다른 SR·LR 모듈이 모두 동일 증상).

# [09] 권장 조치

## [09-1] Arista 호환 25G SFP28 모듈로 교체 (권장)

가장 안정적인 해결책. 교체 전 모듈 정보를 확보해 호환 목록과 대조한다.

```text
show interfaces Ethernet21 transceiver detail
show interfaces transceiver detail
```

확인 항목: `Vendor name`, `Vendor PN`, `Vendor SN`, `Identifier`, `Connector`, `Nominal bitrate`.

## [09-2] 테스트 목적의 unsupported transceiver 허용

테스트 환경이고 정책상 허용 가능하면 검토한다.

```text
configure terminal
service unsupported-transceiver
end
```

이후 포트 재활성화:

```text
configure terminal
interface Ethernet21
   shutdown
   no shutdown
end
```

:warning: 본 장비(EOS 4.30.4M / 7050SX3)에서 `service unsupported-transceiver`가 `% Incomplete command`로 응답한 이력이 있어, 추가 인자 또는 unlock/license key가 필요할 수 있다. 임의 추측 대신 **납품사/Arista에 확인**한다. 운영망에서는 벤더 지원 범위에서 제외될 수 있으므로 검증/임시 용도로만 사용한다.
{: .notice--warning}

## [09-3] 링크 복구 후 FEC 명시 설정

트랜시버 문제가 풀리면 25G 안정성을 위해 양쪽 RS-FEC를 맞춘다.

```text
# 스위치
interface Ethernet21
   speed forced 25gfull
   error-correction encoding reed-solomon
   no shutdown
```

```bash
# 서버
sudo ethtool --set-fec ens801f0np0 encoding rs
```

# [10] 복구 후 검증 절차

| 순서 | 항목 | 명령 | 기대 결과 |
|---:|------|------|------|
| 1 | errdisabled 해소 | `show interfaces status errdisabled` | 해당 포트가 목록에서 사라짐 |
| 2 | Tx 광 출력 정상화 | `show interfaces Ethernet21 transceiver` | `Tx Power`가 `-30 dBm`이 아님, `Bias`가 `0 mA`가 아님 |
| 3 | 서버 링크 | `ethtool ens801f0np0` | `Speed: 25000Mb/s`, `Link detected: yes` |
| 4 | FEC | `ethtool --show-fec ens801f0np0` | `Active FEC encoding: RS` |
| 5 | IP 통신 | `ping -c 5 10.0.0.2` | packet loss 0% |
| 6 | 처리량 | `iperf3 -c 10.0.0.2 -P 8 -t 30` | 약 23Gbps 이상 |

# [11] 결론

`Et21`·`Et23`(OEM 25GBASE-SR)에 이어 `Et35`(OEM SR), `Et37`(MikroTik XS+31LC10D 25GBASE-LR) 교차 테스트에서도 모두 `errdisabled / xcvr-unsupported`가 확인됐다.

```text
Arista DCS-7050SX3-48YC8C-F / EOS 4.30.4M 환경에서
장착한 OEM 25GBASE-SR 및 MikroTik 25GBASE-LR 트랜시버가
모두 unsupported로 분류되어 포트가 errdisabled 처리됨.
```

스위치 포트가 송신 광을 내보내지 않으므로(`Bias 0 mA / Tx -30 dBm / Rx 감지됨`) 서버에서는 `No cable`로 보이지만, **실제 원인은 스위치의 unsupported transceiver 차단**이다. 우선 조치는 (1) Arista 호환 25G SFP28(SR/LR) 모듈 교체, 또는 (2) 납품사/Arista를 통한 `unsupported-transceiver` unlock/license 확보이며, 그 후 FEC·케이블·MTU·IP·iperf3 검증을 진행한다.
