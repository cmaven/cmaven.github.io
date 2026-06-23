---
title: "국내만 열린 홈서버에 HTTPS 붙이기 — Let's Encrypt DNS-01 + DuckDNS 와일드카드"
description: "iptime 국가별 접속 제한(국내만 허용) 때문에 HTTP-01 인증서 발급이 실패하는 홈서버에서, 포트를 열지 않는 DNS-01 + DuckDNS 와일드카드로 HTTPS를 붙이는 방법"
excerpt: "해외 인바운드 차단(국가별 접속 제한·CGNAT)으로 80포트 HTTP-01이 막힐 때, certbot DNS-01 + DuckDNS TXT hook으로 와일드카드 인증서를 받아 서브도메인 여러 개를 HTTPS로 노출하는 방법"
date: 2026-06-23
categories: Network
tags: [iptime, DuckDNS, HTTPS, "Let's Encrypt", Certbot, DNS-01, 와일드카드, 국가별접속제한, Nginx, Docker, 홈서버]
ref: homeserver-https-dns01-country-block
---

:bulb: iptime의 "국가별 접속 제한(대한민국만 허용)"을 켜 두면 해외에서 들어오는 트래픽이 막혀서, 80포트로 검증하는 HTTP-01 방식은 인증서 발급이 안 된다. 이럴 땐 포트를 열 필요가 없는 DNS-01(DuckDNS TXT) 방식으로 와일드카드 인증서를 받으면 된다. 보안 설정은 그대로 두고 HTTPS만 붙일 수 있다.
{: .notice--info}

이 글은 [iptime 공유기에서 DuckDNS + HTTPS 설정하기](/Network/iptime-duckdns-https-guide/)의 후속편이다. 앞 글에서 DuckDNS 도메인 등록, IP 자동 갱신, 포트포워딩, Docker Compose 기본 구성까지 다뤘으니 여기서는 반복하지 않는다. 대신 "분명히 똑같이 따라 했는데 인증서 발급에서 막히는" 상황, 즉 해외 인바운드가 차단된 환경을 진단하고 DNS-01로 갈아타는 부분만 짚는다.

글에서 쓰는 예시 환경은 이렇다.

- 서버 LAN IP `192.168.0.22`, 도메인 접두어 `mydomain` (→ `mydomain.duckdns.org`)
- 서비스 세 개: `engwrite`(Django), `birthplanner`(Vite SPA), `cdocs`(VitePress). 호스트 포트는 각각 8000, 8100, 8200
- 목표는 `https://engwrite.mydomain.duckdns.org`처럼 서브도메인으로 노출하는 것

먼저 전체 그림부터 보자. iptime, DuckDNS, Let's Encrypt, nginx, 서버가 어떻게 얽혀 있는지를 그려 보면 이렇다.

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

요점은 점선으로 표시한 해외 인바운드는 계속 막아 둔 채로, 인증서 검증만 서버에 직접 접속할 필요가 없는 DNS-01(TXT 조회)로 돌린다는 것이다. 보안은 유지하면서 발급 경로만 우회하는 셈이다.

---

# [00] 흔한 가이드대로 했는데 왜 막힐까

블로그에 가장 많이 나오는 방식은 Let's Encrypt의 HTTP-01이다. certbot이 `/.well-known/acme-challenge/` 아래에 검증용 파일을 하나 만들어 두면, Let's Encrypt가 외부에서 80포트로 그 파일을 읽어 보고 "이 도메인 주인이 맞네" 하고 인증서를 내준다. 앞 글의 [STEP 06](/Network/iptime-duckdns-https-guide/)이 바로 이 방식이다.

문제는 한국 가정용 회선(특히 KT)이나 iptime 보안 설정 탓에 해외에서 들어오는 연결이 막혀 있는 경우다. Let's Encrypt 검증 서버는 전부 해외에 있어서, 우리 서버 80포트에 닿질 못하고 그대로 발급이 실패한다.

```
Certbot failed to authenticate some domains (authenticator: webroot).
  Detail: <공인IP>: Fetching http://<도메인>/.well-known/acme-challenge/...:
          Timeout during connect (likely firewall problem)
```

:warning: 이 에러가 뜨면 십중팔구 포트포워딩부터 다시 들여다보게 되는데, 정작 포트포워딩은 멀쩡하고 해외 IP만 차단돼 있는 경우가 꽤 많다. 그러니 원인부터 제대로 가려내자.
{: .notice--warning}

---

# [01] 진단 — 정말 밖에서 못 들어오는 게 맞나

## 1-1. DNS와 공인 IP가 일치하는지

```bash
curl -s ifconfig.me; echo            # 내 공인 IP
dig +short mydomain.duckdns.org          # 위와 같아야 정상
dig +short engwrite.mydomain.duckdns.org # DuckDNS는 서브도메인도 같은 IP로 응답
```

## 1-2. 해외에서 포트가 열려 있나 — 여기가 제일 중요하다

국내에서 `nc`로 찔러 보면 멀쩡히 열린 것처럼 보일 수 있다. 국내는 어차피 허용돼 있으니까. 그래서 반드시 해외 노드 기준으로 봐야 한다. [check-host.net](https://check-host.net){:target="_blank"}을 쓰면 여러 나라 노드에서 한 번에 확인된다.

```bash
# 80 포트를 해외 8개 노드에서 검사
RID=$(curl -s -H 'Accept: application/json' \
  "https://check-host.net/check-tcp?host=mydomain.duckdns.org:80&max_nodes=8" \
  | grep -oE '"request_id":"[^"]+"' | cut -d'"' -f4)
sleep 12
curl -s -H 'Accept: application/json' "https://check-host.net/check-result/$RID"
```

해외 노드가 죄다 `Connection timed out`인데 국내만 된다면, 포트포워딩이나 CGNAT 문제가 아니라 지역(해외 IP) 기반으로 인바운드가 막힌 것이다.

:memo: 구별하는 팁 하나. 80, 443뿐 아니라 이미 포워딩해 둔 아무 고포트나 하나 골라 해외에서 찔러 봤을 때도 timeout이라면, "특정 포트만 막힌 것"이 아니라 "지역 자체가 막힌 것"이다.
{: .notice--info}

## 1-3. 범인은 iptime 국가별 접속 제한

iptime 관리페이지에서 보안 기능 → 국가별 접속 제한을 열어 보자. 아래처럼 허용 목록에 South Korea(대한민국) 하나만 들어 있으면, 나머지 전 세계 인바운드가 전부 막힌다. 아래 예시에서는 84,856개가 차단으로 잡혀 있다.

![iptime 국가별 접속 제한 — 대한민국만 허용](/assets/images/iptime-country-block.png)

이 설정은 보안상 꽤 쓸모가 있으니 끄지 말고 그대로 두자. 끄는 대신 인증서 발급 방식을 바꾸면 된다.

---

# [02] 어떻게 풀까 — 해외 접근이 필요한지부터 정하자

| 상황 | 해법 |
|------|------|
| 국내에서만 쓰면 됨 (개인 홈서버 대부분) | 국가별 제한 유지 + DNS-01 ← 이 글 |
| 해외에서도 접근해야 함 | 국가별 제한을 풀고 HTTP-01, 또는 Cloudflare Tunnel / Tailscale |

DNS-01은 Let's Encrypt가 우리 서버에 직접 접속하지 않는다. DNS에 박아 둔 TXT 레코드만 읽어서 검증하기 때문에, 인바운드가 막혀 있어도 발급도 되고 자동 갱신도 된다. 실제 서비스(443)는 어차피 국내 사용자만 받으면 되니, 국가별 접속 제한과 부딪힐 일도 없다.

:bulb: DuckDNS는 도메인 하나당 TXT 슬롯이 딱 1개뿐이다. 그래서 서브도메인이 여러 개라고 각각 발급하려 들면 슬롯이 모자란다. 이럴 땐 와일드카드 `*.mydomain.duckdns.org` 한 장으로 받는 게 정석이다. 와일드카드는 `_acme-challenge.mydomain.duckdns.org` TXT 하나로 검증되니 슬롯 문제도 없다.
{: .notice--info}

---

# [03] 사전 준비

1. DuckDNS 도메인과 토큰. 앞 글의 [STEP 02](/Network/iptime-duckdns-https-guide/)를 참고해 도메인(`mydomain`)을 추가하고 페이지 상단의 token을 복사해 둔다.
2. iptime 포트포워딩은 외부 `443` → `192.168.0.22:443` 하나면 된다. DNS-01은 80이 필요 없다. 다만 국내 사용자가 HTTPS로 접속하려면 443은 열려 있어야 한다. 국가별 접속 제한이 켜져 있어도 국내 IP는 이 443으로 잘 들어온다.
3. 서버에는 `docker`와 `docker compose`(v2), 그리고 `curl`, `dig` 정도가 있으면 된다.

---

# [04] 인증서 발급 — certbot DNS-01 + DuckDNS hook

핵심은 certbot의 `--manual` 모드에, DuckDNS TXT 레코드를 넣고 빼 주는 hook 스크립트를 물리는 것이다.

## 4-1. DuckDNS hook 스크립트

`~/myserver/scripts/duckdns-hook.sh`를 만들고 실행 권한을 준다.

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

:memo: 스크립트 안의 `CERTBOT_DOMAIN`, `CERTBOT_VALIDATION`은 우리가 채우는 게 아니다. certbot이 hook을 실행할 때 알아서 넣어 주는 환경변수다.
{: .notice--info}

## 4-2. docker compose의 certbot 서비스

[앞 글의 docker-compose.yml](/Network/iptime-duckdns-https-guide/)에서 쓰던 certbot 서비스에, 방금 만든 hook 스크립트와 토큰을 넣어 준다.

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

토큰은 `~/myserver/duckdns.env`에 따로 두고 권한을 600으로 잠가 둔다.

```ini
DUCKDNS_DOMAIN=mydomain
DUCKDNS_TOKEN=여기에-토큰
DUCKDNS_PROPAGATION=30
```

## 4-3. 발급은 staging으로 리허설부터

Let's Encrypt 운영 인증서는 주당 5회 발급 한도가 있다. 설정을 디버깅하다 한도를 까먹으면 곤란하니, 먼저 `--dry-run`(staging)으로 한 번 돌려 본다.

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

`The dry run was successful.`가 보이면 `--dry-run`만 빼고 다시 돌린다. 이번엔 진짜 발급이다.

```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/mydomain.duckdns.org/fullchain.pem
```

:warning: 여기서 두 번 잘 밟는 함정이 있다.<br><br>**하나, entrypoint가 인자를 삼킨다.** 위 compose처럼 certbot에 자동 갱신용 entrypoint(무한 renew 루프)가 걸려 있으면, `docker compose run certbot certonly ...`를 실행해도 entrypoint가 인자를 먹어 버려서 `certonly`가 돌지 않는다. `No renewals were attempted`만 찍고 멈춘다면 이 경우다. 위 명령처럼 `--entrypoint certbot`으로 덮어써 줘야 한다.<br><br>**둘, 와일드카드 인증서 경로.** `--cert-name mydomain.duckdns.org`로 lineage 이름을 고정해 두면 인증서가 `live/mydomain.duckdns.org/`에 저장된다. 그래야 다음 단계 nginx 설정의 경로와 깔끔하게 맞아떨어진다.
{: .notice--danger}

---

# [05] nginx — 서브도메인마다 443, 인증서는 와일드카드 한 장

`~/myserver/nginx/nginx.conf`의 요지만 보면 이렇다.

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

:memo: HTTP-01 때와 달리 `certonly`는 `options-ssl-nginx.conf`나 `ssl-dhparams.pem` 같은 보조 파일을 만들어 주지 않는다. 그걸 `include`하려 들면 nginx가 파일이 없다며 기동에 실패한다. 그래서 위처럼 `ssl_protocols`를 conf 안에 직접 적어 줬다.
{: .notice--info}

---

# [06] 앱은 루트('/')에서 돌리자 — 서브도메인의 진짜 장점

서브도메인 방식의 좋은 점은 각 앱이 자기 루트에서 그냥 돌아간다는 것이다. base-path를 건드릴 일이 없다. 반대로 `/engwrite/` 같은 경로 방식으로 가면 base를 바꿔야 하는데, 그 순간 정적 파일 경로나 리다이렉트가 줄줄이 깨지기 시작한다. 혹시 전에 경로 방식을 시도해 본 적이 있다면, 그 흔적을 루트로 되돌려 놓아야 한다.

- **Django(engwrite)** — `.env`에서
  - `DJANGO_ALLOWED_HOSTS=engwrite.mydomain.duckdns.org,127.0.0.1,localhost`
  - `CSRF_TRUSTED_ORIGINS=https://engwrite.mydomain.duckdns.org`
  - `USE_HTTPS=true`, `FORCE_SCRIPT_NAME=` (비워서 루트 서빙)
  - settings에서 `SECURE_SSL_REDIRECT=False` (HTTPS 종단은 바깥 nginx가 한다)
- **Vite SPA(birthplanner)** — `vite.config.ts`의 `base`를 지워 기본값 `/`로 두고, React Router의 `basename`도 빼고 다시 빌드한다.
- **VitePress(cdocs)** — config의 `base: '/cdocs/'`를 지워 기본값 `/`로 돌리고, dev 서버 말고 prod 정적 빌드를 서빙한다. dev 서버는 외부에 노출하면 안 되고 라우팅도 깨진다.

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

브라우저에서 `https://engwrite.mydomain.duckdns.org/`를 열어 자물쇠가 뜨고 화면이 정상이면 끝이다.

---

# [08] 트러블슈팅

| 증상 | 원인 / 해결 |
|------|-------------|
| `Timeout during connect (likely firewall problem)` | 해외 인바운드가 막힌 것(국가별 제한/ISP). HTTP-01 대신 DNS-01로 (이 글) |
| `No renewals were attempted` 찍고 멈춤 | certbot 서비스 entrypoint가 `certonly`를 삼킴. `--entrypoint certbot` 추가 |
| nginx 기동 실패: `options-ssl-nginx.conf 없음` | `certonly`는 이 파일을 안 만든다. nginx에 `ssl_protocols` 등을 인라인으로 |
| 호스트에서 `live/...` 접근 거부 | certbot이 root 0700으로 만든다. `[ -f ]` 검사는 컨테이너 안(`docker compose run --entrypoint test ...`)에서 하거나 sudo |
| DNS-01 발급은 됐는데 외부 접속이 안 됨 | 443도 막혔는지 확인. 국내만 쓰면 정상, 해외가 필요하면 국가 제한 해제나 터널 |
| rate limit (주 5회) | 실패 디버깅은 무조건 `--dry-run`(staging)으로 |

---

# [09] 정리

한국 홈서버에서 HTTPS가 안 붙을 때, 의외로 진짜 원인은 포트포워딩 실수가 아니라 해외 인바운드 차단인 경우가 많다. ISP가 막았든, iptime 국가별 접속 제한을 켜 뒀든 결과는 같다. 80포트로 들어오는 Let's Encrypt 검증이 닿질 못하는 것이다.

이럴 때 DNS-01 + DuckDNS 와일드카드를 쓰면, 포트를 더 열지 않고도, 국가별 접속 제한이라는 보안 설정을 그대로 둔 채 HTTPS를 붙일 수 있다. 덤으로 서브도메인 방식은 앱을 루트에 그대로 두니 base-path 때문에 골치 썩을 일도 없다.

:bulb: 반대로 해외 접근이 막히지 않은 평범한 환경이라면, 굳이 DNS-01까지 갈 것 없이 더 간단한 HTTP-01(80포트 webroot) 방식이 낫다. 그 경우는 [iptime 공유기에서 DuckDNS + HTTPS 설정하기](/Network/iptime-duckdns-https-guide/)를 먼저 보면 된다.
{: .notice--info}
