---
title: "Arista ZTP 오류 해결: cannot copy to startup-config when ZeroTouch is enabled"
description: "Arista EOS 스위치 초기 설정 중 write memory 시 'cannot copy to startup-config when ZeroTouch is enabled' 오류나 %ZTP-6-RETRY 로그가 반복될 때 zerotouch cancel로 ZTP를 비활성화해 해결하는 방법"
excerpt: "공장 초기 상태의 Arista 스위치에서 발생하는 'cannot copy to startup-config when ZeroTouch is enabled' 오류와 ZTP 재시도 로그의 원인, zerotouch cancel을 통한 해결, 이후 관리 계정·Management IP·SSH 설정과 저장·확인까지 step by step 가이드"
date: 2026-06-19
categories: Network
tags: [Arista, EOS, 스위치, ZTP, ZeroTouch, startup-config, 프로비저닝, 네트워크, 콘솔, CLI]
ref: arista-ztp-zerotouch-troubleshooting
---

:bulb: 공장 초기 상태의 Arista EOS 스위치를 수동으로 설정하려다 만나는 `cannot copy to startup-config when ZeroTouch is enabled` 오류와 `%ZTP-6-RETRY` 반복 로그를 `zerotouch cancel`로 해결하는 방법을 단계별로 정리한다.  
환경: 공장 초기 상태(또는 startup-config 없는) Arista 스위치(EOS) + 콘솔 케이블
{: .notice--info}

> 이 글의 호스트명(`sw-core-01`)·관리 IP(`192.0.2.110/24`)·게이트웨이(`192.0.2.1`)는 문서화 예시 대역(RFC 5737)으로 치환했고, 비밀번호 등 민감 정보는 마스킹했다. 실제 적용 시 본인 환경의 값으로 바꿔서 사용한다.

# [00] 상황 개요

Arista 스위치를 초기 설정하면서 관리 계정·관리 IP·SSH 접속 등을 입력한 뒤 설정을 저장하려고 하면 다음과 같은 오류가 발생할 수 있다.

```text
cannot copy to startup-config when ZeroTouch is enabled
```

또한 콘솔/터미널에 아래 로그가 지속적으로 출력될 수 있다.

```text
%ZTP-6-RETRY: Retrying Zero Touch Provisioning from the beginning
```

예를 들어 다음과 같이 계정을 만들고 설정을 저장하려는 상황이다.

```
sw-core-01# configure terminal
sw-core-01(config)# username admin privilege 15 role network-admin secret ********
sw-core-01(config)# end
sw-core-01# write memory
```

하지만 스위치가 Zero Touch Provisioning(ZTP) 모드에 남아 있으면 `startup-config`로 설정을 저장하지 못하거나 ZTP 재시도 로그가 계속 발생한다.

:warning: ZTP 모드에서는 사용자가 직접 입력한 설정을 `startup-config`에 **저장할 수 없다.** 저장이 막혀 있으므로 재부팅하면 입력한 설정이 모두 사라진다.
{: .notice--warning}

# [01] 원인

Arista EOS 스위치는 **공장 초기 상태이거나 `startup-config`가 없는 상태**로 부팅되면 Zero Touch Provisioning 모드로 동작한다.

ZTP는 DHCP·HTTP·TFTP·CloudVision 등을 통해 스위치 설정을 자동으로 받아와 초기 프로비저닝을 수행하는 기능이다. 즉, 스위치는 다음 흐름에 갇혀 있다.

```text
스위치 부팅
   │
   ▼
startup-config 없음
   │
   ▼
ZeroTouch Provisioning 활성화
   │
   ▼
DHCP / TFTP / HTTP / CloudVision 등으로 설정 자동 수신 시도
   │
   ▼
설정 수신 실패 → 처음부터 반복 재시도 (%ZTP-6-RETRY)
```

이 상태에서는 스위치가 아직 수동 설정 모드로 완전히 전환되지 않았다. 그래서 사용자가 직접 설정을 입력하더라도 `write memory` 또는 `copy running-config startup-config` 수행 시 다음 오류가 발생한다.

```text
cannot copy to startup-config when ZeroTouch is enabled
```

# [02] 해결 방법 요약

수동으로 Arista 스위치를 설정하려면 먼저 ZTP를 취소해야 한다. 핵심 명령은 단 하나다.

```
zerotouch cancel
```

일반적인 해결 순서는 다음과 같다.

```text
1. admin 계정으로 콘솔 로그인
2. enable 모드 진입
3. zerotouch cancel 실행
4. 스위치 재부팅 (자동으로 진행될 수 있음)
5. 재부팅 후 수동 설정 진행
6. write memory 또는 copy running-config startup-config 실행
```

:bulb: `zerotouch cancel`은 ZTP 모드를 비활성화하고 빈 `startup-config`를 생성해, 이후 정상적으로 설정을 저장할 수 있게 만든다.
{: .notice--info}

# [03] ZTP 취소 절차

초기 상태의 Arista 스위치에 콘솔로 접속한 뒤 다음 명령을 수행한다(초기 계정은 보통 `admin`, 비밀번호 없음).

```
localhost login: admin

localhost> enable
localhost# zerotouch cancel
```

`zerotouch cancel` 명령을 실행하면 스위치가 재부팅될 수 있다. 재부팅 후 다시 로그인한다.

```
localhost login: admin

localhost> enable
localhost#
```

이후부터는 일반적인 수동 설정을 진행하면 된다.

# [04] 관리 계정·Management IP·SSH 설정 예시

ZTP를 취소한 뒤 기본적인 관리 설정을 적용하는 예시다. 환경에 맞게 `<password>`, `<관리IP>`, `<prefix>`, `<gateway>` 값을 변경한다.

```
localhost# configure terminal

localhost(config)# hostname sw-core-01

sw-core-01(config)# username admin privilege 15 role network-admin secret <password>

sw-core-01(config)# interface Management1
sw-core-01(config-if-Ma1)# ip address <관리IP>/<prefix>
sw-core-01(config-if-Ma1)# no shutdown
sw-core-01(config-if-Ma1)# exit

sw-core-01(config)# ip route 0.0.0.0/0 <gateway>

sw-core-01(config)# management ssh
sw-core-01(config-mgmt-ssh)# no shutdown
sw-core-01(config-mgmt-ssh)# exit

sw-core-01(config)# end
```

실제 값을 채운 예시는 다음과 같다.

```
sw-core-01# configure terminal

sw-core-01(config)# username admin privilege 15 role network-admin secret ********

sw-core-01(config)# interface Management1
sw-core-01(config-if-Ma1)# ip address 192.0.2.110/24
sw-core-01(config-if-Ma1)# no shutdown
sw-core-01(config-if-Ma1)# exit

sw-core-01(config)# ip route 0.0.0.0/0 192.0.2.1

sw-core-01(config)# management ssh
sw-core-01(config-mgmt-ssh)# no shutdown
sw-core-01(config-mgmt-ssh)# exit

sw-core-01(config)# end
```

:bulb: Management IP 할당·SSH 접속의 전체 절차(VRF 확인, 접속 테스트 포함)는 별도 글 "Arista 스위치에 관리 IP 할당하고 SSH로 접속하기"에서 더 자세히 다룬다.
{: .notice--info}

# [05] 설정 저장

ZTP를 취소한 뒤에는 정상적으로 설정 저장이 가능해야 한다.

```
sw-core-01# write memory
```

또는 동일한 명령을 풀어서 쓸 수 있다.

```
sw-core-01# copy running-config startup-config
```

정상적으로 저장되면 다음 메시지가 출력된다.

```text
Copy completed successfully.
```

- `write memory` = `copy running-config startup-config`
- 저장하지 않으면 재부팅 시 설정이 사라진다.

# [06] 확인 명령

## [06-1] startup-config 확인

```
sw-core-01# show startup-config
```

설정이 저장되어 있다면 hostname, username, Management1 IP, SSH 설정 등이 출력된다. ZTP가 취소되기 전에는 이 출력이 비어 있다.

## [06-2] running-config 확인

```
sw-core-01# show running-config
```

현재 동작 중인 설정을 확인한다.

## [06-3] ZTP 상태 확인

EOS 버전에 따라 지원 명령이 다를 수 있지만, 다음 명령으로 ZTP 상태를 확인할 수 있다.

```
sw-core-01# show zerotouch
```

또는 로그에서 ZTP 관련 메시지를 확인한다.

```
sw-core-01# show logging | include ZTP|ZeroTouch
```

ZTP가 정상적으로 취소되었다면 다음 반복 로그가 더 이상 발생하지 않는다.

```text
%ZTP-6-RETRY: Retrying Zero Touch Provisioning from the beginning
```

# [07] 트러블슈팅 체크리스트

`zerotouch cancel`을 실행했는데도 문제가 계속된다면 아래 항목을 점검한다.

| 증상 | 점검 포인트 |
|------|-------------|
| 저장 시 여전히 ZTP 오류 | `show startup-config`로 startup-config가 생성됐는지 확인. 비어 있으면 `zerotouch cancel` 재실행 후 재부팅 |
| `%ZTP-6-RETRY` 로그 반복 | `show logging \| include ZTP`로 확인 → 여전히 발생하면 `zerotouch cancel` 재실행 |
| 재부팅하니 설정이 사라짐 | `write memory`로 startup-config를 저장했는지, 저장이 `Copy completed successfully.`로 끝났는지 확인 |
| 재부팅 후 다시 ZTP 진입 | startup-config가 비어 있거나 없으면 재부팅 시 다시 ZTP 모드로 진입할 수 있음 → 설정 입력 후 반드시 저장 |

각 점검 명령은 다음과 같다.

```
# startup-config 존재 여부
sw-core-01# show startup-config

# 설정 저장 재시도
sw-core-01# copy running-config startup-config

# ZTP 재활성 여부
sw-core-01# show logging | include ZTP|ZeroTouch

# 다시 발생 시 재취소
sw-core-01# zerotouch cancel

# 재부팅 후 설정 유지 확인
sw-core-01# reload
sw-core-01# show running-config
sw-core-01# show startup-config
```

# [08] 요약

| 단계 | 작업 위치 | 내용 |
|------|-----------|------|
| STEP 03 | 콘솔 | `admin` 로그인 → `enable` → `zerotouch cancel` |
| - | 스위치 | (자동) 재부팅, 빈 startup-config 생성 |
| STEP 04 | 스위치 CLI | hostname / username / Management1 IP / SSH 설정 |
| STEP 05 | 스위치 CLI | `write memory`로 설정 저장 (`Copy completed successfully.`) |
| STEP 06 | 스위치 CLI | `show startup-config` / `show zerotouch`로 ZTP 취소·저장 확인 |

핵심은 단순하다. 다음 오류나 로그를 만나면 스위치가 아직 ZTP 모드에 있는 것이다.

```text
cannot copy to startup-config when ZeroTouch is enabled
%ZTP-6-RETRY: Retrying Zero Touch Provisioning from the beginning
```

해결은 `zerotouch cancel` 한 줄이며, 재부팅 후 관리 계정·Management IP·SSH를 설정하고 `write memory`로 저장하면 된다. Arista 스위치를 수동으로 관리할 계획이라면 **초기 설정 단계에서 ZTP를 먼저 취소**하는 것이 가장 중요하다.

# [09] 참고 명령 모음

```
enable
zerotouch cancel
configure terminal
hostname sw-core-01
username admin privilege 15 role network-admin secret <password>
interface Management1
ip address <관리IP>/<prefix>
no shutdown
exit
ip route 0.0.0.0/0 <gateway>
management ssh
no shutdown
exit
end
write memory
show startup-config
show running-config
show zerotouch
show logging | include ZTP|ZeroTouch
```
