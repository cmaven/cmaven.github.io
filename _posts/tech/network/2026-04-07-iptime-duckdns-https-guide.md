---
title: "iptime 공유기에서 DuckDNS + HTTPS 설정하기"
description: "iptime 공유기 환경에서 DuckDNS 도메인과 Let's Encrypt 인증서를 활용해 외부 HTTPS 접속을 구성하는 방법"
excerpt: "DuckDNS 도메인 등록, iptime 포트포워딩, Nginx 리버스 프록시, Let's Encrypt 인증서 발급까지의 전체 과정"
date: 2026-04-07
categories: Network
tags: [iptime, DuckDNS, HTTPS, Let's Encrypt, Certbot, Nginx, Docker, 포트포워딩, 리버스프록시, SSL]
---

:bulb: iptime 공유기 아래 리눅스 서버를 DuckDNS 도메인으로 외부에서 HTTPS 접근 가능하게 만드는 방법을 작성한다.  
환경: iptime 공유기 + 리눅스 서버(Ubuntu) + Docker
{: .notice--info}

# [00] 전체 구성도

```
외부 PC
  │
  │  https://mydomain.duckdns.org:443
  ▼
DuckDNS DNS 서버
  │  (도메인 → 공유기 외부 IP 변환)
  ▼
iptime 공유기 (외부 IP)
  │  포트포워딩 (80, 443 → 내부 서버)
  ▼
리눅스 서버
  │
  ├── Nginx (리버스 프록시 + SSL 처리)
  │     │
  │     ├── service_a 컨테이너
  │     ├── service_b 컨테이너
  │     └── service_c 컨테이너
  │
  └── Certbot (Let's Encrypt 인증서 발급/갱신)
```

# [01] 왜 iptime DDNS가 아닌 DuckDNS인가?

`iptime.org` 도메인은 CAA(Certification Authority Authorization) 레코드가 아래와 같이 막혀있어 **Let's Encrypt 인증서 발급 자체가 불가능**하다.

```
0 issuewild ;
0 issue ;
```

DuckDNS는 CAA를 허용하고 있어 Let's Encrypt 인증서 발급이 가능하다.  
또한 DuckDNS는 무료이며 2013년부터 운영 중인 안정적인 서비스이다.

:memo: **참고**: iptime DDNS와 DuckDNS를 동시에 사용해도 된다.  
외부 HTTPS 접근 → `mydomain.duckdns.org` / 내부망 접근 → `mydomain.iptime.org`
{: .notice--warning}

# [02] DuckDNS 도메인 등록

**작업 위치: 외부 PC (브라우저)**

1. [https://www.duckdns.org](https://www.duckdns.org){:target="_blank"} 접속 후 구글/깃헙 계정으로 로그인
2. `add domain` 에서 원하는 도메인 입력 (예: `mydomain`)
3. 현재 공유기 외부 IP가 자동으로 등록됨
4. 페이지 상단의 **token** 값을 복사해서 메모해두기

# [03] iptime 공유기에 DuckDNS IP 자동 갱신 설정

**작업 위치: iptime 공유기 관리 페이지 (192.168.0.1)**

가정용 인터넷은 ISP가 유동 IP를 부여하므로 공유기 외부 IP가 바뀔 수 있다.  
서버가 꺼져 있어도 공유기가 켜져 있는 한 IP를 갱신하도록 공유기에서 직접 설정한다.

1. `192.168.0.1` 접속 → 관리자 로그인
2. `고급 설정` → `특수기능` → `DDNS 설정`
3. 아래와 같이 입력:

| 항목 | 입력값 |
|------|--------|
| DDNS 서비스 | 사용자 DDNS (또는 Custom) |
| URL | `https://www.duckdns.org/update?domains=mydomain&token=여기에토큰&ip=` |
| 갱신 주기 | 5분 |

:warning: iptime 펌웨어 버전에 따라 UI가 다를 수 있다.  
`사용자 DDNS` 항목이 없는 경우, 아래 대체 방법을 사용한다.
{: .notice--danger}

## 대체 방법 — 서버에서 crontab으로 갱신

**작업 위치: 리눅스 서버**

```bash
mkdir ~/duckdns

cat > ~/duckdns/duck.sh << 'EOF'
echo url="https://www.duckdns.org/update?domains=mydomain&token=여기에토큰&ip=" | curl -k -o ~/duckdns/duck.log -K -
EOF

chmod +x ~/duckdns/duck.sh

# 5분마다 자동 실행 등록
crontab -e
# 아래 줄 추가:
# */5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
```

# [04] iptime 공유기 포트포워딩 설정

**작업 위치: iptime 공유기 관리 페이지 (192.168.0.1)**

`고급 설정` → `NAT/라우터 관리` → `포트포워드 설정`

아래 규칙을 추가한다:

| 규칙 이름 | 외부 포트 | 내부 IP | 내부 포트 | 목적 |
|-----------|-----------|---------|-----------|------|
| certbot | 80 | 서버 내부 IP | 80 | 인증서 발급용 |
| https | 443 | 서버 내부 IP | 443 | HTTPS 서비스 |

:memo: **서버 내부 IP 확인**: 서버에서 `ip addr` 또는 `hostname -I` 명령으로 확인 (보통 `192.168.0.xxx` 형태)
{: .notice--info}

:memo: **포트 80**: 인증서 갱신(90일마다)할 때 필요하다. 상시 열어두고 Nginx에서 443으로 리다이렉트하면 실질적 보안 위협은 없다.
{: .notice--info}

# [05] 리눅스 서버 — Docker Compose 구성

**작업 위치: 리눅스 서버**

## 디렉토리 구조

```
~/myserver/
├── docker-compose.yml
├── nginx/
│   └── nginx.conf
└── data/
    └── certbot/
        ├── conf/    ← 인증서 저장 위치
        └── www/     ← certbot 인증용 webroot
```

## docker-compose.yml

```yaml
services:
  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./data/certbot/conf:/etc/letsencrypt:ro
      - ./data/certbot/www:/var/www/certbot:ro

  certbot:
    image: certbot/certbot
    container_name: certbot
    restart: unless-stopped
    volumes:
      - ./data/certbot/conf:/etc/letsencrypt
      - ./data/certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

  service_a:
    image: your-image-a
    container_name: service_a
    # ports 외부 노출 불필요 — nginx가 내부에서 연결

  service_b:
    image: your-image-b
    container_name: service_b

  service_c:
    image: your-image-c
    container_name: service_c
```

## nginx/nginx.conf

```nginx
events {}

http {
  # HTTPS 리다이렉트 + certbot 인증용
  server {
    listen 80;
    server_name mydomain.duckdns.org;

    location /.well-known/acme-challenge/ {
      root /var/www/certbot;
    }

    location / {
      return 301 https://$host$request_uri;
    }
  }

  # service_a
  server {
    listen 443 ssl;
    server_name mydomain.duckdns.org;

    ssl_certificate /etc/letsencrypt/live/mydomain.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mydomain.duckdns.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
      proxy_pass http://service_a:3000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }

  # service_b (서브도메인 사용 시)
  server {
    listen 443 ssl;
    server_name b.mydomain.duckdns.org;

    ssl_certificate /etc/letsencrypt/live/mydomain.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mydomain.duckdns.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
      proxy_pass http://service_b:4000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }
}
```

# [06] 인증서 최초 발급

**작업 위치: 리눅스 서버**

## 6-1. 임시 nginx.conf로 먼저 컨테이너 실행

인증서가 없으면 nginx가 SSL 설정을 읽다가 에러로 종료된다.  
우선 80 포트만 있는 임시 설정으로 nginx를 띄운다.

```nginx
# nginx/nginx.conf (임시)
events {}
http {
  server {
    listen 80;
    server_name mydomain.duckdns.org;

    location /.well-known/acme-challenge/ {
      root /var/www/certbot;
    }

    location / {
      return 200 'ok';
    }
  }
}
```

```bash
cd ~/myserver
docker compose up -d nginx
```

## 6-2. 인증서 발급

```bash
docker compose run --rm certbot certonly \
  --webroot \
  -w /var/www/certbot \
  -d mydomain.duckdns.org \
  --email your@email.com \
  --agree-tos \
  --no-eff-email
```

성공 시 `data/certbot/conf/live/mydomain.duckdns.org/` 에 인증서 파일이 생성된다.

## 6-3. 최종 nginx.conf로 교체 후 재시작

STEP 05의 최종 nginx.conf로 복원 후:

```bash
docker compose down
docker compose up -d
```

# [07] 인증서 자동 갱신 확인

**작업 위치: 리눅스 서버**

docker-compose.yml의 certbot 컨테이너가 12시간마다 자동으로 갱신을 시도한다.  
수동으로 갱신 테스트:

```bash
docker compose run --rm certbot renew --dry-run
```

# [08] 접속 테스트

```bash
# 외부 PC에서
curl -I https://mydomain.duckdns.org

# 또는 브라우저에서
# https://mydomain.duckdns.org 접속 → 자물쇠 아이콘 확인
```

# [09] 트러블슈팅

## nginx가 시작 안 될 때

```bash
docker logs nginx
# ssl 인증서 파일 경로 오류인지 확인
# 인증서 발급 전에는 임시 설정으로 먼저 실행
```

## certbot 발급 실패할 때

- 공유기 포트 80 포트포워딩이 설정되어 있는지 확인
- `http://mydomain.duckdns.org/.well-known/acme-challenge/test` 가 외부에서 접근 가능한지 확인
- DuckDNS 도메인이 현재 공유기 IP를 가리키는지 확인

## DuckDNS 도메인이 엉뚱한 IP를 가리킬 때

```bash
# 현재 공유기 외부 IP 확인
curl ifconfig.me

# DuckDNS에 수동으로 업데이트
curl "https://www.duckdns.org/update?domains=mydomain&token=여기에토큰&ip=$(curl -s ifconfig.me)"
```

# [10] 요약

| 단계 | 작업 위치 | 내용 |
|------|-----------|------|
| STEP 02 | 외부 PC 브라우저 | DuckDNS 도메인 등록 |
| STEP 03 | 공유기 관리 페이지 | DuckDNS IP 자동 갱신 설정 |
| STEP 04 | 공유기 관리 페이지 | 포트 80, 443 포트포워딩 추가 |
| STEP 05 | 리눅스 서버 | Docker Compose + Nginx 구성 |
| STEP 06 | 리눅스 서버 | Let's Encrypt 인증서 발급 |
| STEP 07 | 리눅스 서버 | 자동 갱신 동작 확인 |
