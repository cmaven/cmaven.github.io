---
title: "Claude Code 'API error · Retrying'의 진짜 원인 — 단일 엣지 IP 차단 추적기"
description: "Claude Code가 API error · Retrying을 반복할 때 DNS → MTU → conntrack → tcpdump 순서로 계층별 소거 진단을 진행해, api.anthropic.com의 엣지 IP 하나만 방화벽에 차단된 것을 찾아내고 /etc/hosts로 우회한 과정. 재사용 가능한 진단 체크리스트와 자동화 스크립트 포함"
excerpt: "Claude Code가 API error · Retrying을 반복하면 클라이언트부터 의심하기 쉽다. 하지만 한 겹씩 벗겨보니 범인은 방화벽이 콕 집어 막은 목적지 IP 단 하나였다"
date: 2026-07-03
categories: Claude
tags: [Claude Code, API error, Retrying, 네트워크진단, tcpdump, conntrack, MTU, DNS, etc-hosts, SNI, 방화벽, curl, api.anthropic.com]
ref: claude-code-api-error-single-edge-ip-block
---

:bulb: Claude Code가 `API error · Retrying in 0s · attempt 1/10`을 반복하며 느려졌다. 처음엔 클라이언트 버그를 의심했지만, DNS → MTU → conntrack → 경로 → 목적지 정책 순서로 한 겹씩 벗겨보니 범인은 사내 방화벽이 콕 집어 막은 **목적지 IP 단 하나**였다. 가설을 세우고 깨뜨린 과정과, 같은 증상을 만났을 때 빠르게 좁혀 들어갈 수 있는 체크리스트를 정리한다.
{: .notice--info}

먼저 결론부터.

- **증상**: Claude Code가 `API error · Retrying`을 반복하며 응답이 눈에 띄게 느려짐
- **진짜 원인**: `api.anthropic.com`의 여러 엣지 IP 중 **하나만** 사내 방화벽에서 차단/불안정. 그런데 사내 DNS가 하필 그 IP만 반환
- **해결**: 같은 대역의 살아있는 IP를 `/etc/hosts`에 고정해 막힌 정문을 우회
- **교훈**: "특정 서비스만 됐다 안 됐다"는 거의 항상 **목적지 단위 정책**의 신호다. 그리고 진단 중 잘못 박은 테스트 IP 하나가 한참을 헤매게 만들 수 있다

---

# [01] 증상 — 재시도 끝에 되긴 하는데, 너무 느리다

평소 잘 쓰던 Claude Code가 어느 날부터 다음 메시지를 반복했다.

```
✻ API error · Retrying in 0s · attempt 1/10
```

응답이 눈에 띄게 느려졌고, 재시도 끝에 결국 되긴 했다. 환경은 Ubuntu 22.04, 노드 두 대. 흥미롭게도 지난주까지는 멀쩡했고, 같은 망의 다른 환경에서는 멀쩡해 보였다. "클라이언트 문제인가?" 싶었지만, 이 가설은 곧 깨진다.

---

# [02] 진단 — 가설을 세우고 깨뜨리기

## 2-1. 우선 연결 자체를 의심하다

`curl`로 API 엔드포인트를 직접 때려봤다.

```bash
curl -I https://api.anthropic.com
# 처음엔: SSL_connect: 상대편이 연결을 끊음
# 잠시 후: HTTP/2 404  ← 정상 (루트 경로엔 페이지가 없어 404가 정상 응답)
```

`404`는 **연결·TLS가 모두 성공**했다는 뜻이다(루트 경로에 콘텐츠가 없을 뿐). 그런데 연속으로 때려보니 결과가 들쭉날쭉했다.

```bash
for i in $(seq 1 10); do
  curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" https://api.anthropic.com
done
# 000 94s  (타임아웃)
# 404 63s
# 000 94s
# ...간헐적으로 성공/실패가 섞임
```

`94초`라는 일정한 타임아웃 값과 `000`(연결 실패)의 반복 — **간헐적 연결 단절**이다. 같은 머신에서 `curl`도 똑같이 실패하니 Claude Code 코드 문제는 배제됐다. 문제는 더 아래 계층에 있었다.

## 2-2. DNS·IPv6 가설 → 부분적으로 빗나감

리졸버를 확인하니 `systemd-resolved`(stub `127.0.0.53`)를 거치고 있었고, `api.anthropic.com`이 IPv4와 IPv6를 모두 반환했다. 한때 "IPv6 폴백 지연"을 의심했지만, IPv4를 강제(`curl -4`)해도, 심지어 **IP를 직접 박아(`--resolve`) DNS를 우회해도** 실패했다.

```bash
curl -4 --resolve api.anthropic.com:443:160.79.104.10 -o /dev/null -s \
  -w "%{http_code}\n" https://api.anthropic.com
# 그래도 타임아웃(000)이 섞여 나옴
```

DNS는 범인이 아니다. IPv6도 아예 연결성이 없어 폴백 가설도 폐기했다.

## 2-3. MTU·conntrack 가설 → 둘 다 무죄

- **MTU 블랙홀?** 큰 패킷(`ping -M do -s 1472`)이 손실 없이 통과 → MTU 정상
- **conntrack 포화?** 테이블은 한가했고(`nf_conntrack_count`가 한도의 1% 미만), `insert_failed`/`drop` 카운터 전부 0 → conntrack 무죄

```bash
sysctl net.netfilter.nf_conntrack_count net.netfilter.nf_conntrack_max
conntrack -S | grep -E "insert_failed|drop"   # 전부 0
```

## 2-4. 결정적 증거 — SYN은 나가는데 SYN-ACK이 안 온다

`tcpdump`로 실패하는 순간을 잡았다.

```bash
sudo tcpdump -ni any host 160.79.104.10 and tcp port 443
# 실패 케이스:
#  Out ... > 160.79.104.10.443: Flags [S]      ← SYN 발송
#  Out ... > 160.79.104.10.443: Flags [S]      ← 1초 후 재전송
#  (SYN-ACK 응답 없음 → connect timeout)
# 성공 케이스:
#  Out ... [S]  →  In ... [S.]  →  정상 핸드셰이크
```

우리 쪽 SYN은 NIC 밖으로 정상 송출되는데, 응답(SYN-ACK)이 안 돌아온다. 즉 드롭 지점은 **클라이언트 바깥의 경로/장비**다. 정량화하면 이렇다.

```
나간 SYN: 48   →   돌아온 SYN-ACK: 37   (약 23% 유실)
```

OS도 무관했다. 같은 망의 Windows에서 `Test-NetConnection`을 30회 돌려도 비슷한 비율로 실패했다(약 13%). "Windows는 잘 된다"고 느낀 건, 당시 측정 방식의 아티팩트와 다른 경로를 타는 환경을 비교했기 때문이었다.

## 2-5. 함정 — 잘못 박은 테스트 IP

목적지를 여러 개 동시에 비교하다가 큰 혼선을 겪었다. `--resolve`로 google IP를 임의로 박았는데, 그게 해당 망에서 맞지 않는 IP라 **google이 100% 실패**하는 것처럼 보였다. 하마터면 "전면 차단"이라는 틀린 결론을 낼 뻔했다.

:warning: IP를 손으로 박을 땐 그게 실제 유효한 IP인지부터 의심하자. DNS가 주는 IP로 다시 재니 google·amazon·github는 100% 정상이었다. 잘못된 대조군 하나가 전체 진단을 엉뚱한 방향으로 끌고 간다.
{: .notice--warning}

## 2-6. 진짜 원인 — 목적지 IP 단위 차단

여러 목적지를 **같은 라운드에서 동시에** 측정하는 스크립트(부록 A)를 돌리자 그림이 또렷해졌다. DNS가 주는 정상 IP 기준으로:

| 목적지 | 결과 |
|--------|------|
| google / amazon / github | 100% 성공 |
| `api.anthropic.com` (`160.79.104.10`) | 거의 100% 실패 |

그리고 결정타. **같은 대역의 바로 옆 IP는 멀쩡했다.**

```bash
for ip in 160.79.104.10 160.79.104.11 160.79.104.12 160.79.104.13; do
  # .10 → 9/10 실패
  # .11 → 10/10 성공
  # .12 → 10/10 성공
  # .13 → 10/10 성공
done
```

`160.79.104.10` 하나만 막혀 있고, `.11`~`.13`은 완벽하게 동작했다. 랜덤한 망 장애라면 이렇게 IP 단위로 0%/100%가 깔끔하게 갈릴 수 없다. 이건 **방화벽/IPS가 특정 목적지 IP 하나를 차단**하고 있다는 강력한 신호다.

문제를 키운 건 DNS였다. 사내·외부 DNS 모두 `api.anthropic.com`에 대해 **하필 막힌 `.10`만 반환**하고 있었다. 그래서 클라이언트는 늘 막힌 정문으로만 향했고, 실패율이 시점마다 출렁인 건 `.10`이 "부분 차단/불안정" 경계에 걸쳐 있었기 때문이다.

:memo: **왜 IP가 여러 개인가?** `api.anthropic.com` 같은 도메인 뒤에는 여러 대의 엣지 서버가 있고, 각기 다른 IP가 붙는다. 모두 같은 서비스로 들어가는 "여러 개의 정문"이다. 평소엔 DNS가 그중 하나를 골라준다. 지금은 그 선택이 하필 막힌 문에 고정돼 있었다.
{: .notice--warning}

---

# [03] 해결 — 살아있는 엣지 IP를 /etc/hosts에 고정

## 3-1. 원리 — IP를 바꿔도 안전한 이유 (SNI)

HTTPS는 목적지를 IP가 아니라 **도메인 이름(SNI)으로 식별**한다. 어느 엣지 IP로 접속하든 연결 시 "나는 `api.anthropic.com`을 찾는다"는 이름을 함께 보내고, 서버는 그 이름에 맞는 인증서와 콘텐츠로 응답한다. 따라서 `.10` 대신 `.11`로 붙어도 같은 건물의 다른 정문일 뿐, 인증서 검증도 도메인 기준이라 그대로 통과한다.

## 3-2. /etc/hosts로 살아있는 IP 고정

이름→IP 변환은 `/etc/hosts`가 DNS보다 먼저 참조된다. 여기에 살아있는 IP를 적으면 DNS 질의를 건너뛰고 곧장 그 IP로 향한다. 이 서버 한 대에만 적용되고, 사내 DNS/방화벽 설정은 건드리지 않는다.

```bash
echo "160.79.104.11 api.anthropic.com" | sudo tee -a /etc/hosts
sudo resolvectl flush-caches
```

## 3-3. 적용/롤백 자동화

`/etc/hosts`는 민감 파일이라, 적용 전 자동 백업·중복 방지·사전 연결 검증·원클릭 롤백을 갖춘 스크립트로 다뤘다. 핵심 동작은 다음과 같다(전체 코드는 부록 B).

- `apply [IP]` — 지정 IP를 먼저 5회 테스트해 살아있을 때만 hosts에 고정(백업 후)
- `rollback` — 추가했던 항목만 정확히 제거하고 캐시 flush
- `status` — 현재 해석 IP와 연결 결과 확인
- `probe` — `.11`~`.20` 중 살아있는 대체 IP 자동 탐색

우리가 넣은 줄에 식별 마커를 달아, 여러 번 실행해도 줄이 쌓이지 않고 롤백 시 그 줄만 안전하게 지운다(다른 hosts 항목은 보존).

## 3-4. 주의 — 기존 세션은 재시작해야 갈아탄다

`/etc/hosts`는 **새 연결을 시작할 때 한 번만** 참조된다. 이미 막힌 IP로 맺어진 연결이나 프로그램 내부 DNS 캐시는 그대로 남을 수 있으므로, 캐시 flush와 함께 **해당 프로그램을 재시작**해야 새 IP로 확실히 붙는다.

---

# [04] 결과 — 네 단계로 검증

`.11`로 고정한 뒤 네 단계로 검증했다.

```bash
# 1) hosts 항목
grep anthropic /etc/hosts
#  160.79.104.11 api.anthropic.com

# 2) 이름 해석
getent ahostsv4 api.anthropic.com
#  160.79.104.11  STREAM api.anthropic.com

# 3) 실제 연결 (remote_ip 확인)
curl -4 -o /dev/null -s -w "%{remote_ip} → %{http_code} (%{time_total}s)\n" https://api.anthropic.com
#  160.79.104.11 → 404 (0.06s)   ← .11로 빠르게 붙음

# 4) 살아있는 세션 — 가장 중요
ss -tnp | grep 160.79.104
#  ESTAB ... 160.79.104.11:443  users:(("claude",pid=...))   (연결 다수, 전부 .11)
#  → .10은 하나도 없음
```

특히 4번이 결정적이었다. Claude Code의 실제 연결이 전부 `.11`로 맺어졌고 `.10`은 완전히 사라졌다. 막힌 정문을 완전히 벗어난 것이다. 이후 `API error · Retrying`는 사라졌고 응답 속도도 정상으로 돌아왔다.

## 남은 일

- **다른 노드에도 동일 적용** — 같은 망의 두 번째 노드도 같은 방식으로 처리
- **다른 anthropic 도메인 점검** — 클라이언트가 쓰는 보조 도메인이 막힌 IP를 받으면 같은 증상이 재발할 수 있으니, 이상 징후 시 동일하게 확인
- **근본 해결은 관리자 몫** — `/etc/hosts` 우회는 임시방편이다. 엣지 IP는 바뀔 수 있으므로, 방화벽에서 해당 IP 차단 해제 또는 도메인 대역 허용을 받아두면 hosts 관리에서 자유로워진다

---

# [05] 진단 체크리스트 (재사용용)

비슷한 "간헐적 API 연결 실패"를 만났을 때 빠르게 좁히는 순서.

1. **클라이언트 vs 시스템** — 같은 목적지를 `curl`로도 재현되나? 되면 클라이언트 무죄
2. **DNS** — IP를 직접 박아도(`--resolve`) 실패하나? 실패하면 DNS 무죄
3. **MTU** — 큰 패킷(`ping -M do -s 1472`)이 통과하나? 통과하면 MTU 무죄
4. **conntrack** — `nf_conntrack_count`가 한도에 닿았나? `insert_failed/drop`이 0인가?
5. **경로** — `tcpdump`로 SYN은 나가는데 SYN-ACK이 안 오나? 그러면 외부 드롭
6. **목적지 단위** — 여러 목적지를 **동시에** 재라. 특정 IP만 갈리면 목적지 정책
7. **대역 내 이웃 IP** — 같은 대역의 옆 IP(`.11`, `.12`)는 되나? 되면 개별 IP 차단 확정

:bulb: 그리고 무엇보다, 손으로 박는 테스트 IP가 유효한지 항상 의심하라. 잘못된 대조군 하나가 전체 진단을 엉뚱한 방향으로 끌고 갈 수 있다.
{: .notice--info}

---

# 부록 A. 다중 목적지 동시 진단 스크립트 (conn_check.sh)

여러 목적지를 같은 라운드에서 동시에 측정해, 막히는/풀리는 구간이 목적지 공통인지(=경로/게이트웨이 전면) vs 특정 목적지인지를 시계열로 판별한다. 2~3회 반복 실행하면 평균 실패율과 주기가 또렷해진다.

```bash
#!/usr/bin/env bash
# conn_check.sh
# 여러 목적지(IP/포트)에 대한 신규 TCP 443 연결 성공/실패를 같은 라운드에서
# 동시 측정하여 "전면 간헐 차단"인지 "특정 목적지만 차단"인지 시계열로 판별한다.
# 사용: ./conn_check.sh   |   ROUNDS=100 ./conn_check.sh   |   TIMEOUT=2 ./conn_check.sh
set -u

ROUNDS="${ROUNDS:-50}"        # 측정 라운드 수
TIMEOUT="${TIMEOUT:-3}"       # connect 타임아웃(초)
SLEEP="${SLEEP:-0.3}"         # 라운드 간 간격(초)

# 측정 대상: "이름|호스트헤더|IP". IP를 직접 박아 DNS 변수를 제거(순수 TCP/TLS 경로만 측정).
# ※ 주의: 여기 박는 IP가 "그 환경에서 실제 유효한 IP"인지 반드시 확인할 것.
#   잘못된 IP를 박으면 해당 목적지가 100% 실패하는 것처럼 보여 진단을 오염시킨다.
#   확실히 하려면 --resolve 없이 도메인으로 직접 재거나, getent ahostsv4 로 실제 IP를 먼저 확인.
TARGETS=(
  "anthropic|api.anthropic.com|160.79.104.10"
  "google|www.google.com|142.250.207.110"
  "cloudflare|one.one.one.one|1.1.1.1"
  "github|github.com|140.82.112.3"
  "amazon|www.amazon.com|54.239.28.85"
)

TS="$(date +%Y%m%d_%H%M%S)"
CSV="./conn_check_${TS}.csv"

NAMES=()
for t in "${TARGETS[@]}"; do NAMES+=("${t%%|*}"); done

declare -A FAILS TOTAL
for n in "${NAMES[@]}"; do FAILS["$n"]=0; TOTAL["$n"]=0; done

{ printf "timestamp,round"
  for n in "${NAMES[@]}"; do printf ",%s_code,%s_time" "$n" "$n"; done
  printf "\n"; } > "$CSV"

echo "측정 시작: ROUNDS=$ROUNDS TIMEOUT=${TIMEOUT}s  로그=$CSV"
printf "%-10s %-3s" "time" "#"
for n in "${NAMES[@]}"; do printf " %-12s" "$n"; done
printf "\n"

probe() {  # 반환: "<http_code> <time_total>" (실패 시 code=000)
  local host="$1" ip="$2"
  curl -4 -o /dev/null -s -w "%{http_code} %{time_total}" \
    --connect-timeout "$TIMEOUT" --resolve "${host}:443:${ip}" \
    "https://${host}" 2>/dev/null || echo "000 0"
}

for ((r=1; r<=ROUNDS; r++)); do
  now="$(date +%H:%M:%S)"; printf "%-10s %-3d" "$now" "$r"; csv_line="$now,$r"
  for t in "${TARGETS[@]}"; do
    name="${t%%|*}"; rest="${t#*|}"; host="${rest%%|*}"; ip="${rest##*|}"
    read -r code time <<< "$(probe "$host" "$ip")"
    TOTAL["$name"]=$(( TOTAL["$name"] + 1 ))
    if [[ "$code" == "000" ]]; then
      FAILS["$name"]=$(( FAILS["$name"] + 1 )); printf " %-12s" "FAIL"
    else
      printf " %-12s" "ok ${time}s"
    fi
    csv_line+=",${code},${time}"
  done
  printf "\n"; echo "$csv_line" >> "$CSV"; sleep "$SLEEP"
done

echo ""; echo "================== 요약 (실패율) =================="
for n in "${NAMES[@]}"; do
  tot="${TOTAL[$n]}"; f="${FAILS[$n]}"
  (( tot > 0 )) && rate=$(( f * 100 / tot )) || rate=0
  printf "  %-12s 실패 %2d/%-2d  (%d%%)\n" "$n" "$f" "$tot" "$rate"
done
echo "==================================================="
echo "CSV 로그: $CSV"
```

**해석 가이드**

- 모든 목적지가 같은 라운드에서 동시에 FAIL/OK → 전면(경로/게이트웨이) 간헐 차단
- 특정 목적지만 FAIL이 두드러짐 → 목적지 특정 차단
- FAIL 구간이 뭉쳐 있으면 → 주기적 차단(세션/NAT 포화 의심)

---

# 부록 B. 적용/롤백 스크립트 (anthropic_ip_fix.sh)

`/etc/hosts`는 민감 파일이므로, 적용 전 자동 백업·중복 방지·사전 연결 검증·원클릭 롤백을 갖췄다. 우리가 넣은 줄에 식별 마커를 달아 여러 번 실행해도 줄이 쌓이지 않고, 롤백 시 그 줄만 정확히 제거한다(다른 hosts 항목은 보존).

```bash
#!/usr/bin/env bash
# anthropic_ip_fix.sh
# api.anthropic.com 이 차단된 엣지 IP 대신 살아있는 IP로 붙도록 /etc/hosts 에
# 항목을 고정(apply)하거나 원상복구(rollback)한다. 적용 전 백업 + 적용 후 검증.
# 사용:
#   sudo ./anthropic_ip_fix.sh apply              (기본 IP 사용)
#   sudo ./anthropic_ip_fix.sh apply 160.79.104.12 (IP 지정)
#   sudo ./anthropic_ip_fix.sh rollback
#   sudo ./anthropic_ip_fix.sh status
#   sudo ./anthropic_ip_fix.sh probe              (대체 IP 후보 자동 탐색)
set -euo pipefail

HOSTS="/etc/hosts"
DOMAIN="api.anthropic.com"
DEFAULT_IP="160.79.104.11"                   # 환경에 맞는 살아있는 IP로 교체
MARK="# added-by-anthropic_ip_fix"
BACKUP_DIR="/var/backups/anthropic_ip_fix"

need_root() {
  [[ "$(id -u)" -eq 0 ]] || { echo "ERROR: root 필요. 'sudo $0 ...'" >&2; exit 1; }
}
flush_dns() { command -v resolvectl >/dev/null 2>&1 && resolvectl flush-caches 2>/dev/null || true; }

show_status() {
  echo "----- 현재 상태 -----"
  echo -n "해석 IP : "; getent ahostsv4 "$DOMAIN" | awk '{print $1}' | sort -u | tr '\n' ' '; echo
  echo -n "연결 결과(5회): "
  for i in $(seq 1 5); do
    curl -4 -o /dev/null -s -w "%{http_code} " --connect-timeout 3 "https://$DOMAIN" || echo -n "000 "
  done; echo
  echo -n "$HOSTS 내 항목: "
  grep -q "$MARK" "$HOSTS" && grep "$MARK" "$HOSTS" || echo "(없음 - DNS 기본값 사용 중)"
  echo "---------------------"
}

probe_ips() {
  echo "대체 IP 후보 탐색 (160.79.104.11 ~ .20):"
  local best=""
  for last in $(seq 11 20); do
    local ip="160.79.104.${last}" ok=0
    for i in $(seq 1 5); do
      code=$(curl -4 -o /dev/null -s -w "%{http_code}" --connect-timeout 3 \
              --resolve "${DOMAIN}:443:${ip}" "https://${DOMAIN}" 2>/dev/null || echo 000)
      [[ "$code" != "000" ]] && ok=$((ok+1))
    done
    printf "  %-16s %d/5 성공\n" "$ip" "$ok"
    [[ -z "$best" && "$ok" -eq 5 ]] && best="$ip"
  done
  [[ -n "$best" ]] && echo ">> 추천 IP: $best"
}

apply_fix() {
  need_root; local ip="${1:-$DEFAULT_IP}"
  [[ "$ip" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]] || { echo "ERROR: 잘못된 IP: $ip" >&2; exit 1; }

  echo "사전 검증: $ip 연결 테스트..."
  local pre_ok=0
  for i in $(seq 1 5); do
    code=$(curl -4 -o /dev/null -s -w "%{http_code}" --connect-timeout 3 \
            --resolve "${DOMAIN}:443:${ip}" "https://${DOMAIN}" 2>/dev/null || echo 000)
    [[ "$code" != "000" ]] && pre_ok=$((pre_ok+1))
  done
  echo "  $ip : $pre_ok/5 성공"
  (( pre_ok >= 3 )) || { echo "ERROR: $ip 불안정. 'probe'로 살아있는 IP를 먼저 찾으세요." >&2; exit 1; }

  mkdir -p "$BACKUP_DIR"
  local backup="${BACKUP_DIR}/hosts.$(date +%Y%m%d_%H%M%S)"
  cp -a "$HOSTS" "$backup"; echo "백업: $backup"

  sed -i "/$MARK/d" "$HOSTS"                      # 기존 우리 항목 제거(중복 방지)
  echo "${ip} ${DOMAIN} ${MARK}" >> "$HOSTS"; echo "추가: ${ip} ${DOMAIN}"
  flush_dns; echo; show_status
}

rollback_fix() {
  need_root
  if ! grep -q "$MARK" "$HOSTS"; then
    echo "롤백할 항목 없음 (이미 기본 상태)"; flush_dns; show_status; return 0
  fi
  mkdir -p "$BACKUP_DIR"
  cp -a "$HOSTS" "${BACKUP_DIR}/hosts.before_rollback.$(date +%Y%m%d_%H%M%S)"
  sed -i "/$MARK/d" "$HOSTS"
  echo "제거 완료: ${DOMAIN} 고정 항목 삭제"; flush_dns; echo; show_status
}

case "${1:-}" in
  apply)    shift; apply_fix "${1:-}";;
  rollback) shift; rollback_fix;;
  status)   show_status;;
  probe)    probe_ips;;
  *)        echo "usage: sudo $0 {apply [IP]|rollback|status|probe}";;
esac
```

**권장 순서**: `status` → `probe` → `apply` → (Claude Code 실행 테스트) → 이상 시 `rollback`. 적용 후엔 캐시 flush와 함께 실행 중이던 클라이언트를 재시작해야 새 IP로 확실히 갈아탄다.

---

*환경: Ubuntu 22.04 / Claude Code. 본문의 사내 IP·호스트명 등 식별 정보는 일반화 처리했으며, `160.79.104.x`는 공개적으로 관측되는 엣지 IP 예시다. 차단 정책과 IP는 환경·시점에 따라 다르다.*
