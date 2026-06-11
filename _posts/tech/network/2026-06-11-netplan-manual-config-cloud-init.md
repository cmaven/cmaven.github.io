<!-- 2026-06-11-netplan-manual-config-cloud-init.md: cloud-init 자동 생성 환경에서 netplan을 직접 수정해 인터페이스 IP/게이트웨이/DNS를 설정하는 가이드 | 생성일: 2026-06-11 -->
---
title: "cloud-init 자동 생성 환경에서 netplan 직접 수정해 NIC에 IP·게이트웨이·DNS 설정하기"
description: "Ubuntu에서 50-cloud-init.yaml이 자동 생성되어 netplan apply가 먹지 않을 때, cloud-init의 네트워크 관리를 끄고 추가 NIC에 IP/게이트웨이/DNS를 영구 설정하는 방법과 기존 파일 처리 3가지 선택지"
excerpt: "인터페이스 이름 확인 → cloud-init 네트워크 비활성화 → netplan yaml 작성 → netplan try로 안전 적용까지. 기존 50-cloud-init.yaml을 삭제할지 말지에 대한 3가지 선택지(추가/통합/비활성화)와 default route 충돌 주의점 정리"
date: 2026-06-11
categories: Network
tags: [netplan, cloud-init, Ubuntu, 네트워크, IP설정, 게이트웨이, DNS, NIC, ConnectX, Mellanox, 리눅스, 서버]
ref: netplan-manual-config-cloud-init
---

:bulb: Ubuntu 서버에서 `/etc/netplan/50-cloud-init.yaml`이 cloud-init에 의해 **자동 생성**되는 환경일 때, 추가 NIC에 IP·게이트웨이·DNS를 **영구적으로** 설정하는 방법을 단계별로 정리한다.
환경: Ubuntu(netplan + cloud-init) + 여러 개의 NIC가 장착된 서버
{: .notice--info}

# [00] 문제 상황

기존에는 `/etc/netplan/` 아래 yaml 파일을 작성하고 `netplan apply`만 하면 됐는데, 어느 순간부터 설정이 잘 안 먹거나 **재부팅하면 사라지는** 경우가 있다. 파일 상단을 보면 다음과 같은 주석이 있다.

```
# This file is generated from information provided by the datasource. Changes
# to it will not persist across an instance reboot. To disable cloud-init's
# network configuration capabilities, write a file
# /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg with the following:
# network: {config: disabled}
```

즉 이 파일은 **cloud-init이 부팅 때마다 자동 생성**한다. 직접 수정해도 재부팅 시 cloud-init이 덮어써서 날아갈 수 있다. 이 글에서는 cloud-init의 네트워크 관리를 끄고 netplan을 직접 관리하는 방법을 다룬다.

# [01] (가장 중요) 설정할 인터페이스 이름부터 정확히 확인

설정 전에 **실제 인터페이스 이름**을 반드시 확인한다. 이름이 한 글자라도 틀리면 `netplan apply`가 적용되지 않는다. (예: `ens801f0np0` vs `ens810f0np0`처럼 숫자 순서를 헷갈리기 쉽다.)

```bash
# 인터페이스 목록과 상태 (가장 간단)
ip -br link

# 하드웨어와 매핑해서 확인
sudo lshw -c network -short

# PCI 디바이스로 확인
lspci | grep -i ethernet
```

`ip -br link` 출력 예시:

```
lo               UNKNOWN        00:00:00:00:00:00 <LOOPBACK,UP,LOWER_UP>
ens259f0         UP             aa:bb:cc:00:11:01 <BROADCAST,MULTICAST,UP,LOWER_UP>
ens801f0np0      DOWN           aa:bb:cc:00:11:0a <BROADCAST,MULTICAST>
ens801f1np1      DOWN           aa:bb:cc:00:11:0b <BROADCAST,MULTICAST>
```

여기서 새로 설정할 인터페이스를 **이름과 MAC 주소로 특정**해 둔다. 이 글에서는 `ens801f0np0`(현재 `DOWN` 상태인 추가 NIC)을 설정한다고 가정한다.

:warning: `ens259f0`처럼 이미 `UP` 상태이고 SSH가 그 인터페이스로 들어오고 있다면 **그 인터페이스 설정은 건드리지 않는다.** 잘못 건드리면 접속이 끊긴다.
{: .notice--warning}

# [02] 현재 netplan 상태 확인

```bash
ls /etc/netplan/
cat /etc/netplan/50-cloud-init.yaml
```

자동 생성된 `50-cloud-init.yaml` 예시(개인정보 치환):

```yaml
network:
    ethernets:
        ens259f0:
            addresses:
            - 192.168.0.108/24
            nameservers:
                addresses:
                - 192.168.0.10
                search: []
            routes:
            -   to: default
                via: 192.168.0.1
    version: 2
```

이 파일 안에는 **현재 관리용 인터페이스 `ens259f0`의 설정**이 들어 있다. 이 점을 기억해 둔다(뒤의 [05]에서 중요).

# [03] cloud-init 네트워크 관리 끄기

파일 상단 주석이 알려준 그대로, cloud-init이 더 이상 netplan을 건드리지 못하게 막는다.

```bash
sudo tee /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg <<'EOF'
network: {config: disabled}
EOF
```

:bulb: 이 작업은 **파일을 삭제하는 게 아니라** 비활성화 설정 파일을 하나 추가하는 것이다. 이걸 해두면 재부팅해도 cloud-init이 `50-cloud-init.yaml`을 다시 생성/덮어쓰지 않는다.
{: .notice--info}

# [04] netplan yaml 작성

기존 파일을 직접 고치기보다 **별도 파일**을 만드는 것을 권장한다. netplan은 `/etc/netplan/` 안의 모든 `.yaml`을 **파일명 숫자 순서로 병합**하므로, 새 인터페이스만 따로 적으면 된다.

```bash
sudo vim /etc/netplan/60-custom.yaml
```

내용(값은 본인 환경에 맞게 수정):

```yaml
# 60-custom.yaml: 추가 NIC(ens801f0np0) 고정 IP 설정 | 생성일: 2026-06-11
network:
  version: 2
  ethernets:
    ens801f0np0:                   # ← [01]에서 확인한 정확한 이름
      addresses:
        - 192.168.10.50/24         # 원하는 IP/프리픽스 길이
      nameservers:
        addresses: [8.8.8.8, 1.1.1.1]
      routes:
        - to: default
          via: 192.168.10.1        # 게이트웨이
```

## default route(기본 게이트웨이)는 보통 하나만

:warning: 기본 게이트웨이(`to: default`)는 **인터페이스 한 곳에만** 두는 것이 안전하다. 이미 `ens259f0`에 default route가 있는데 `ens801f0np0`에도 default를 주면 라우팅이 꼬일 수 있다.
{: .notice--warning}

추가 NIC를 **특정 대역 통신 전용**으로만 쓸 거라면 default 대신 특정 라우트만 준다.

```yaml
    ens801f0np0:
      addresses:
        - 192.168.10.50/24
      routes:
        - to: 192.168.20.0/24      # 이 대역만 이 NIC로
          via: 192.168.10.1
```

굳이 두 인터페이스 모두 default가 필요하면 `metric`으로 우선순위를 구분한다(숫자가 작을수록 우선).

```yaml
      routes:
        - to: default
          via: 192.168.10.1
          metric: 200
```

# [05] (핵심) 기존 50-cloud-init.yaml은 삭제해야 하나? — 3가지 선택지

cloud-init을 껐으니 기존 파일을 지워도 되는지 헷갈린다. **그냥 삭제하면 안 된다.** 그 안에는 현재 관리망(`ens259f0`)의 IP/게이트웨이/DNS가 들어 있어서, 무턱대고 지우면 `netplan apply` 순간 **SSH가 끊겨 서버에 접속하지 못할 수 있다.** 상황에 맞춰 아래 셋 중 하나를 고른다.

## 선택지 1 — 기존 파일은 그대로 두고 새 파일만 추가 (가장 안전 ✅, 원격 서버 권장)

```
/etc/netplan/
├── 50-cloud-init.yaml      ← 그대로 둠 (ens259f0 관리망 설정 유지)
└── 60-custom.yaml          ← ens801f0np0 만 새로 추가
```

netplan이 두 파일을 병합하므로 기존 관리망은 전혀 안 건드린다. 접속이 끊길 위험이 없어 **원격 서버라면 이 방법을 추천**한다. [03]에서 cloud-init을 비활성화했으므로 재부팅해도 `50-cloud-init.yaml`이 덮어써지지 않는다.

## 선택지 2 — 하나로 통합하고 기존 파일 삭제 (정리 우선)

설정 파일을 한 곳으로 모으고 싶다면, 기존 `ens259f0` 설정을 **새 파일로 옮겨 적은 뒤에** 기존 파일을 지운다. **순서가 중요하다.**

```bash
# 1) 먼저 백업
sudo cp /etc/netplan/50-cloud-init.yaml /root/50-cloud-init.yaml.bak

# 2) 새 파일에 ens259f0 + ens801f0np0 둘 다 작성
sudo vim /etc/netplan/60-custom.yaml
```

```yaml
# 60-custom.yaml: 전체 NIC 고정 IP 통합 설정 | 생성일: 2026-06-11
network:
  version: 2
  ethernets:
    ens259f0:                      # 기존 관리망 — 50-cloud-init.yaml에서 그대로 옮김
      addresses:
        - 192.168.0.108/24
      nameservers:
        addresses: [192.168.0.10]
      routes:
        - to: default
          via: 192.168.0.1
    ens801f0np0:                   # 새로 추가하는 NIC
      addresses:
        - 192.168.10.50/24
      nameservers:
        addresses: [8.8.8.8, 1.1.1.1]
      routes:
        - to: 192.168.20.0/24
          via: 192.168.10.1
```

```bash
# 3) 두 인터페이스 설정이 새 파일에 모두 들어간 것을 확인한 뒤에만 기존 파일 삭제
sudo rm /etc/netplan/50-cloud-init.yaml
```

## 선택지 3 — 삭제 대신 확장자만 바꿔 비활성화 (가장 되돌리기 쉬움)

netplan은 `.yaml` 확장자가 아닌 파일은 무시한다. 그래서 삭제 대신 이름만 바꿔 비활성화할 수도 있다.

```bash
sudo mv /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml.disabled
```

문제가 생기면 다시 `.yaml`로 되돌리기만 하면 원상복구된다. 통합 파일([선택지 2]의 `60-custom.yaml`)을 함께 둔 상태에서 안전하게 정리할 때 유용하다.

| 선택지 | 기존 파일 | 추천 상황 | 위험도 |
|--------|-----------|-----------|--------|
| 1. 새 파일만 추가 | 그대로 둠 | **원격 서버**, 관리망 안 건드리고 싶을 때 | 가장 낮음 |
| 2. 통합 후 삭제 | 옮겨 적고 삭제 | 설정을 한 파일로 정리하고 싶을 때 | 중간(순서 주의) |
| 3. 확장자 변경 | `.disabled`로 비활성화 | 삭제는 부담되고 되돌릴 여지를 남기고 싶을 때 | 낮음 |

# [06] 권한 설정 및 문법 검증

netplan은 yaml 파일 권한이 느슨하면 경고를 낸다. 소유자만 읽도록 권한을 좁힌다.

```bash
sudo chmod 600 /etc/netplan/60-custom.yaml
sudo netplan generate          # 문법 검증 (오류 있으면 여기서 출력)
```

# [07] 안전하게 적용 — netplan try

원격 서버에서는 `netplan apply`보다 **`netplan try`를 먼저** 쓴다. 설정을 적용한 뒤 일정 시간(기본 120초) 안에 Enter를 누르지 않으면 **자동으로 이전 설정으로 롤백**한다. 잘못 설정해서 SSH가 끊겨도 스스로 복구되므로 안전하다.

```bash
sudo netplan try
# 화면 지시에 따라, 접속이 유지되면 Enter로 확정
```

정상 동작을 확인했다면 적용한다.

```bash
sudo netplan apply
```

# [08] 적용 결과 확인

```bash
# IP가 붙었는지
ip -br addr show ens801f0np0

# 라우트/게이트웨이 확인
ip route

# DNS 확인
resolvectl status ens801f0np0

# 게이트웨이까지 연결되는지
ping -c2 192.168.10.1
```

`ip -br addr`에서 인터페이스가 `UP` 상태이고 지정한 IP가 보이면 성공이다.

# [09] 트러블슈팅

| 증상 | 점검 포인트 |
|------|-------------|
| 설정이 적용 안 됨 | 인터페이스 **이름 오타** 확인([01]), `netplan generate`에서 yaml 문법/들여쓰기 오류 확인 |
| 재부팅하면 사라짐 | `99-disable-network-config.cfg`로 cloud-init을 껐는지 확인([03]) |
| 인터페이스가 계속 DOWN | 케이블/트랜시버 연결, `ip link set ens801f0np0 up`, 링크 파트너(스위치 포트) 상태 확인 |
| 인터넷이 안 됨 | default route가 엉뚱한 NIC에 잡혔는지 `ip route`로 확인, 게이트웨이 IP가 같은 서브넷인지 확인 |
| DNS만 안 됨 | `nameservers.addresses` 값 확인, `resolvectl status`로 실제 적용 DNS 확인 |
| apply 후 SSH 끊김 | 콘솔로 접속해 백업 파일 복구, 이후엔 `netplan try`로 작업 |
| 권한 경고 | `chmod 600`으로 yaml 권한 좁히기([06]) |

# [10] 요약

| 단계 | 작업 | 내용 |
|------|------|------|
| STEP 01 | 확인 | `ip -br link`로 설정할 인터페이스 **정확한 이름** 확정 |
| STEP 03 | cloud-init | `99-disable-network-config.cfg` 생성해 자동 생성 끄기 |
| STEP 04 | netplan | 별도 yaml에 IP/게이트웨이/DNS 작성 (default route는 하나만) |
| STEP 05 | 기존 파일 | 추가 / 통합 후 삭제 / 확장자 변경 중 선택 (원격은 **추가** 권장) |
| STEP 06 | 검증 | `chmod 600` + `netplan generate`로 문법 확인 |
| STEP 07 | 적용 | `netplan try`로 안전 적용 후 `netplan apply` |
| STEP 08 | 확인 | `ip -br addr` / `ip route` / `resolvectl` / `ping`로 검증 |
