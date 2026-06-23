<!-- 2026-06-23-homeserver-https-dns01-country-block.md: iptime 국가별 접속 제한 회선에서 DNS-01 와일드카드로 HTTPS 붙이기 | 생성일: 2026-06-23 -->
---
title: "국내만 열린 홈서버에 HTTPS 붙이기 — Let's Encrypt DNS-01 + DuckDNS 와일드카드"
description: "iptime 국가별 접속 제한(국내만 허용) 때문에 HTTP-01 인증서 발급이 실패하는 홈서버에서, 포트를 열지 않는 DNS-01 + DuckDNS 와일드카드로 HTTPS를 붙이는 방법"
excerpt: "해외 인바운드 차단(국가별 접속 제한·CGNAT)으로 80포트 HTTP-01이 막힐 때, certbot DNS-01 + DuckDNS TXT hook으로 와일드카드 인증서를 받아 서브도메인 여러 개를 HTTPS로 노출하는 step-by-step 가이드"
date: 2026-06-23
categories: Network
tags: [iptime, DuckDNS, HTTPS, "Let's Encrypt", Certbot, DNS-01, 와일드카드, 국가별접속제한, Nginx, Docker, 홈서버]
ref: homeserver-https-dns01-country-block
---

:bulb: iptime **"국가별 접속 제한(대한민국만 허용)"** 을 켜둔 홈서버는 해외 인바운드가 막혀 **HTTP-01(80포트) 인증서 발급이 실패**한다. 포트를 열 필요 없는 **DNS-01(DuckDNS TXT)** 로 **와일드카드 인증서**를 받으면, 보안 설정을 유지한 채 HTTPS를 붙일 수 있다.
{: .notice--info}

이 글은 [iptime 공유기에서 DuckDNS + HTTPS 설정하기](/Network/iptime-duckdns-https-guide/) 의 **후속편**이다. DuckDNS 도메인 등록·IP 자동 갱신·포트포워딩·Docker Compose 기본 구성은 앞 글에서 다뤘으니, 여기서는 **HTTP-01이 막히는 환경의 진단과 DNS-01 전환**만 집중해서 다룬다.

이 글의 예시 환경:
- 서버 LAN IP `192.168.0.22`, 도메인 접두어 `mydomain` (→ `mydomain.duckdns.org`)
- 서비스 3개: `engwrite`(Django), `birthplanner`(Vite SPA), `cdocs`(VitePress) — 호스트 포트 8000/8100/8200
- 목표: `https://engwrite.mydomain.duckdns.org` 처럼 **서브도메인**으로 노출

전체 구성 요소(iptime · DuckDNS · Let's Encrypt · nginx · 서버)의 관계는 다음과 같다.

<pre class="mermaid">
graph TD
    USER["국내 사용자<br/>브라우저"] -->|"https://*.mydomain.duckdns.org<br/>(443)"| DUCK
    LE["Let's Encrypt<br/>(해외 검증 서버)"] -.->|"DNS-01: TXT 조회<br/>_acme-challenge"| DUCK
    OVERSEAS["해외 인바운드<br/>(80/443)"] -.->|"국가별 접속 제한<br/>으로 차단"| IPTIME

    DUCK["DuckDNS<br/>(DNS + TXT 레코드)"] -->|"도메인 → 공유기 공인 IP"| IPTIME

    IPTIME["iptime 공유기<br/>국가별 접속 제한: 한국만 허용<br/>포트포워딩 443"] -->|"443 → 192.168.0.22"| NGINX

    subgraph SERVER["리눅스 서버 (192.168.0.22)"]
        NGINX["nginx<br/>리버스 프록시 + 와일드카드 TLS 종단"]
        CERTBOT["certbot (DNS-01)<br/>duckdns-hook.sh 로 TXT 갱신"]
        NGINX -->|":8000"| A["engwrite (Django)"]
        NGINX -->|":8100"| B["birthplanner (Vite SPA)"]
        NGINX -->|":8200"| C["cdocs (VitePress)"]
    end

    CERTBOT -->|"TXT add/clean"| DUCK
    CERTBOT -->|"와일드카드 인증서 발급<br/>*.mydomain.duckdns.org"| NGINX

    style USER fill:#e3f2fd,stroke:#1565c0
    style DUCK fill:#fff3e0,stroke:#e65100
    style IPTIME fill:#fce4ec,stroke:#c62828
    style NGINX fill:#e8f5e9,stroke:#2e7d32
    style CERTBOT fill:#ede7f6,stroke:#5e35b1
    style LE fill:#f3e5f5,stroke:#8e24aa
    style OVERSEAS fill:#ffebee,stroke:#b71c1c,stroke-dasharray: 5 5
</pre>

핵심은 **해외 인바운드는 차단(점선)** 한 채로, 인증서 검증은 서버 접속이 필요 없는 **DNS-01(TXT 조회)** 로 처리한다는 점이다.

---

# [00] 왜 흔한 가이드대로 하면 막히나

블로그에 흔한 방법은 **Let's Encrypt HTTP-01** 이다. certbot이 `/.well-known/acme-challenge/` 에 파일을 두고, Let's Encrypt가 **외부에서 80포트로 그 파일을 읽어** 도메인 소유를 검증한다([앞 글의 STEP 06](/Network/iptime-duckdns-https-guide/) 방식).

그런데 한국 가정용 회선(특히 KT)이나 iptime 보안 설정에 따라 **외부(해외) 인바운드가 막혀 있으면**, Let's Encrypt의 검증 서버(전부 해외)가 우리 서버 80포트에 접속하지 못해 발급이 실패한다.

```
Certbot failed to authenticate some domains (authenticator: webroot).
  Detail: <공인IP>: Fetching http://<도메인>/.well-known/acme-challenge/...:
          Timeout during connect (likely firewall problem)
```

:warning: 이 에러를 보면 보통 포트포워딩을 의심하지만, 포트포워딩은 멀쩡한데 **해외 IP만 차단**되는 경우가 많다. 먼저 원인부터 정확히 진단하자.
{: .notice--warning}

---

# [01] 진단 — "정말 외부에서 안 들어오나"

## 1-1. DNS와 공인 IP가 맞는지

```bash
curl -s ifconfig.me; echo            # 내 공인 IP
dig +short mydomain.duckdns.org          # 위와 같아야 정상
dig +short engwrite.mydomain.duckdns.org # DuckDNS는 서브도메인도 같은 IP로 응답
```

## 1-2. 해외에서 포트가 열리나 — 가장 중요

국내에서 `nc`로 테스트하면 **될 수도** 있다(국내는 허용). 반드시 **해외 노드** 기준으로 봐야 한다. [check-host.net](https://check-host.net){:target="_blank"} 이 다국적 노드에서 한 번에 확인해 준다.

```bash
# 80 포트를 해외 8개 노드에서 검사
RID=$(curl -s -H 'Accept: application/json' \
  "https://check-host.net/check-tcp?host=mydomain.duckdns.org:80&max_nodes=8" \
  | grep -oE '"request_id":"[^"]+"' | cut -d'"' -f4)
sleep 12
curl -s -H 'Accept: application/json' "https://check-host.net/check-result/$RID"
```

해외 노드가 **전부 `Connection timed out`** 이고 국내만 되면 → **지역(해외 IP) 기반 인바운드 차단**. 포트포워딩·CGNAT 문제가 아니다.

:memo: **구별 팁**: 80/443뿐 아니라 **임의 고포트**(이미 포워딩된 포트가 있으면)도 해외에서 timeout이면 "특정 포트 차단"이 아니라 "지역 차단"이다.
{: .notice--info}

## 1-3. 범인 확인 — iptime 국가별 접속 제한

iptime 관리페이지 → **보안 기능 → 국가별 접속 제한** 을 보자. 아래처럼 **"국가허용"에 South Korea(대한민국)만** 들어 있으면, 나머지 전 세계 인바운드가 차단된다(예시에선 84,856개 차단).

![iptime 국가별 접속 제한 — 대한민국만 허용](/assets/images/iptime-country-block.png)

이 설정은 **보안상 유용**하므로 끄지 말고 유지하자. 대신 인증서 발급 방식을 바꾼다.

---

# [02] 해법 선택 — 해외 접근이 필요한가?

| 상황 | 해법 |
|------|------|
| **국내에서만 쓰면 됨** (대부분의 개인 홈서버) | **국가별 제한 유지 + DNS-01** ← 이 글 |
| 해외에서도 접근 필요 | 국가별 제한 해제(해외 허용) 후 HTTP-01, 또는 Cloudflare Tunnel/Tailscale |

DNS-01은 Let's Encrypt가 우리 서버에 **접속하지 않고** DNS TXT 레코드만 읽으므로, 인바운드가 막혀 있어도 발급/자동갱신이 된다. 서빙(443)은 국내 사용자만 받으면 되므로 국가 제한과 공존한다.

:bulb: DuckDNS는 도메인당 TXT 슬롯이 **1개** 뿐이라, 서브도메인이 여러 개면 각각 발급하지 말고 **와일드카드 `*.mydomain.duckdns.org` 1장**으로 받는 것이 정석이다. 와일드카드는 `_acme-challenge.mydomain.duckdns.org` TXT 하나로 검증된다.
{: .notice--info}

---

# [03] 사전 준비

1. **DuckDNS 도메인 + 토큰**: 앞 글의 [STEP 02](/Network/iptime-duckdns-https-guide/) 참고 (도메인 `mydomain` 추가 → 상단 **token** 복사).
2. **iptime 포트포워딩**: 외부 `443` → `192.168.0.22:443`. **DNS-01은 80 불필요**. 단 국내 사용자 HTTPS 접속용 443은 필요하다.
   - 국가별 접속 제한이 켜져 있어도 **국내 IP**는 이 443으로 들어올 수 있다.
3. 서버에 `docker` + `docker compose`(v2), `curl`, `dig`.

---

# [04] 인증서 발급 — certbot DNS-01 + DuckDNS hook

핵심은 certbot의 `--manual` 모드에 **DuckDNS TXT를 설정/해제하는 hook**을 붙이는 것이다.

## 4-1. DuckDNS hook 스크립트

`~/myserver/scripts/duckdns-hook.sh` (실행권한 부여):

```sh
#!/bin/sh
set -eu
action="${1:-}"
: "${DUCKDNS_DOMAIN:?}"; : "${DUCKDNS_TOKEN:?}"
base="https://www.duckdns.org/update?domains=${DUCKDNS_DOMAIN}&token=${DUCKDNS_TOKEN}"
case "$action" in
  add)   url="${base}&txt=${CERTBOT_VALIDATION}" ;;
  clean) url="${base}&txt=removed&clear=true" ;;
  *) echo "usage: duckdns-hook.sh add|clean" >&2; exit 2 ;;
esac
resp="$(curl -fsS "$url" || wget -qO- "$url")"
echo "duckdns-hook($action) -> $resp" >&2
[ "$action" = add ] && [ "$resp" != OK ] && exit 1
[ "$action" = add ] && sleep "${DUCKDNS_PROPAGATION:-30}"   # TXT 전파 대기
exit 0
```

:memo: `CERTBOT_DOMAIN`/`CERTBOT_VALIDATION`은 certbot이 hook 실행 시 자동으로 넣어 주는 환경변수다.
{: .notice--info}

## 4-2. docker compose (certbot 서비스)

[앞 글의 docker-compose.yml](/Network/iptime-duckdns-https-guide/) 의 certbot 서비스에 hook 스크립트와 토큰을 주입한다.

```yaml
  certbot:
    image: certbot/certbot
    container_name: certbot
    restart: unless-stopped
    env_file:
      - ./duckdns.env          # DUCKDNS_DOMAIN / DUCKDNS_TOKEN / DUCKDNS_PROPAGATION
    volumes:
      - ./data/certbot/conf:/etc/letsencrypt
      - ./data/certbot/www:/var/www/certbot
      - ./scripts:/scripts:ro
    # 12시간마다 자동 갱신 (저장된 manual hook 을 재사용)
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

`~/myserver/duckdns.env` (권한 600):

```ini
DUCKDNS_DOMAIN=mydomain
DUCKDNS_TOKEN=여기에-토큰
DUCKDNS_PROPAGATION=30
```

## 4-3. 발급 (먼저 staging으로 리허설)

Let's Encrypt 운영 인증서는 **주 5회** 한도가 있으니, 먼저 `--dry-run`(staging)으로 검증한다.

```bash
cd ~/myserver
docker compose run --rm --entrypoint certbot certbot certonly \
  --manual --preferred-challenges dns \
  --manual-auth-hook   "/scripts/duckdns-hook.sh add" \
  --manual-cleanup-hook "/scripts/duckdns-hook.sh clean" \
  --cert-name mydomain.duckdns.org \
  -d '*.mydomain.duckdns.org' \
  --email you@example.com --agree-tos --no-eff-email --non-interactive \
  --dry-run
```

`The dry run was successful.` 가 나오면 `--dry-run`만 빼고 다시 실행 → 실제 발급.

```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/mydomain.duckdns.org/fullchain.pem
```

:warning: **흔한 함정 1 — entrypoint**: 위 compose처럼 certbot에 자동갱신용 `entrypoint`(무한 renew 루프)가 있으면, `docker compose run certbot certonly ...` 는 entrypoint가 인자를 삼켜서 `certonly`가 실행되지 않는다(`No renewals were attempted` 후 멈춤). 반드시 **`--entrypoint certbot`** 으로 오버라이드한다.<br><br>**흔한 함정 2 — 와일드카드 cert 경로**: `--cert-name mydomain.duckdns.org`로 lineage 이름을 고정하면 `live/mydomain.duckdns.org/` 에 저장돼 nginx 설정 경로와 맞추기 쉽다.
{: .notice--danger}

---

# [05] nginx — 서브도메인별 443 + 와일드카드 인증서

`~/myserver/nginx/nginx.conf` (요지):

```nginx
events {}
http {
  map $http_upgrade $connection_upgrade { default upgrade; '' close; }
  client_max_body_size 50m;
  ssl_protocols TLSv1.2 TLSv1.3;     # certonly 는 options-ssl-nginx.conf 를 안 만드므로 인라인

  # 80 → 443 리다이렉트 (국내 사용자용)
  server {
    listen 80;
    server_name mydomain.duckdns.org *.mydomain.duckdns.org;
    location / { return 301 https://$host$request_uri; }
  }

  # 서브도메인마다 443 server — 전부 같은 와일드카드 인증서 사용
  server {
    listen 443 ssl;
    server_name engwrite.mydomain.duckdns.org;
    ssl_certificate     /etc/letsencrypt/live/mydomain.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mydomain.duckdns.org/privkey.pem;
    location / {
      proxy_pass http://192.168.0.22:8000;     # 끝 '/' 없음 = 루트 그대로 전달
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
  }
  # birthplanner(:8100), cdocs(:8200) 도 같은 형태로 server 블록 추가
}
```

```bash
cd ~/myserver && docker compose down && docker compose up -d
```

:memo: HTTP-01 방식과 달리 `certonly`는 `options-ssl-nginx.conf`와 `ssl-dhparams.pem`을 생성하지 않는다. nginx에 `ssl_protocols` 등을 **인라인**으로 넣어야 기동 실패를 피한다.
{: .notice--info}

---

# [06] 백엔드 앱은 "루트('/')" 기준으로 — 서브도메인의 장점

서브도메인 방식은 각 앱이 **자기 루트**에서 동작하므로 base-path를 건드릴 필요가 없다. (경로 방식 `/engwrite/` 처럼 base를 바꾸면 정적파일·리다이렉트가 깨지기 쉽다.) 단, 이전에 경로 방식을 시도했다면 그 잔재를 **루트로 되돌려야** 한다.

- **Django(engwrite)**: `.env`
  - `DJANGO_ALLOWED_HOSTS=engwrite.mydomain.duckdns.org,127.0.0.1,localhost`
  - `CSRF_TRUSTED_ORIGINS=https://engwrite.mydomain.duckdns.org`
  - `USE_HTTPS=true`, `FORCE_SCRIPT_NAME=` (비움 — 루트 서빙)
  - settings: `SECURE_SSL_REDIRECT=False` (외부 nginx가 HTTPS 종단)
- **Vite SPA(birthplanner)**: `vite.config.ts`의 `base` 제거(기본 `/`), React Router `basename` 제거, 재빌드.
- **VitePress(cdocs)**: config의 `base: '/cdocs/'` 제거(기본 `/`), 그리고 **dev 서버가 아니라 prod 정적 빌드**로 서빙(dev 서버는 외부 노출 금지·라우팅 깨짐).

---

# [07] 검증

```bash
# 국내망에서 각 서브도메인 (200/301 정상)
for s in engwrite birthplanner cdocs; do
  curl -Iks "https://$s.mydomain.duckdns.org/" | head -1
done

# 인증서가 와일드카드인지
echo | openssl s_client -servername engwrite.mydomain.duckdns.org \
  -connect mydomain.duckdns.org:443 2>/dev/null | openssl x509 -noout -subject -enddate
# subject= CN = *.mydomain.duckdns.org

# 자동 갱신 리허설 (저장된 hook 으로)
cd ~/myserver && docker compose run --rm --entrypoint certbot certbot renew --dry-run
# Congratulations, all simulated renewals succeeded
```

브라우저로 `https://engwrite.mydomain.duckdns.org/` → 자물쇠 + 정상 화면이면 끝.

---

# [08] 트러블슈팅

| 증상 | 원인 / 해결 |
|------|-------------|
| `Timeout during connect (likely firewall problem)` | 해외 인바운드 차단(국가별 제한/ISP). HTTP-01 대신 **DNS-01** 사용 (이 글) |
| `No renewals were attempted` 후 멈춤 | certbot 서비스 entrypoint가 `certonly`를 삼킴 → `--entrypoint certbot` 추가 |
| nginx 기동 실패: `options-ssl-nginx.conf 없음` | `certonly`는 이 파일을 안 만든다 → nginx에 `ssl_protocols` 등 **인라인** 설정 |
| 호스트에서 `live/...` 접근 거부 | certbot이 root 0700으로 생성. `[ -f ]` 검사를 컨테이너 안(`docker compose run --entrypoint test ...`)에서 하거나 sudo |
| DNS-01 발급은 됐는데 외부 접속 안 됨 | 443도 막혔는지 확인. 국내만 쓰면 OK, 해외 필요하면 국가 제한 해제 또는 터널 |
| rate limit (주 5회) | 실패 디버깅은 반드시 `--dry-run`(staging)으로 |

---

# [09] 정리

- 한국 홈서버에서 HTTPS가 안 붙는 흔한 진짜 원인은 **포트포워딩 실수가 아니라 "해외 인바운드 차단"**(ISP 또는 iptime 국가별 접속 제한)인 경우가 많다.
- 이때 **DNS-01 + DuckDNS 와일드카드**면 포트를 더 열지 않고, 국가별 접속 제한(보안)을 유지한 채 HTTPS를 붙일 수 있다.
- 서브도메인 방식은 앱을 루트에서 그대로 두므로 base-path 함정을 피한다.

:bulb: 해외 접근이 막히지 않은 일반 환경이라면, 더 간단한 **HTTP-01(80포트 webroot)** 방식인 [iptime 공유기에서 DuckDNS + HTTPS 설정하기](/Network/iptime-duckdns-https-guide/) 를 먼저 보자.
{: .notice--info}
