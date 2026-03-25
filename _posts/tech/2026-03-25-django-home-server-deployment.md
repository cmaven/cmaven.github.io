---
title: "Django 웹앱을 직접 서비스하기: 개발에서 배포까지"
description: "Django 프로젝트를 Gunicorn + systemd로 운영 환경 구성하고, DDNS + 포트포워딩으로 외부 접근 가능하게 배포하는 전체 과정"
excerpt: "runserver 대신 Gunicorn, systemd 자동 실행, DDNS/포트포워딩 설정까지 Django 홈서버 배포 가이드"
date: 2026-03-25
categories: Tech
tags: [Django, Gunicorn, Nginx, systemd, DDNS, 포트포워딩, 홈서버, 배포, ufw, 방화벽, WSGI]
---

:bulb: 개발 완료된 Django 프로젝트를 직접 사용하는 PC를 사용해서 실제로 외부 접근 가능하게 만드는 전체 과정을 정리한다.
{: .notice--info}

# [01] 전체 구조: 개발 vs 운영

개발 환경과 운영 환경은 근본적으로 다르다.

<pre class="mermaid">
graph LR
    subgraph 개발 환경
        DEV_USER[개발자 브라우저] --> DEV_SERVER[runserver :8000]
        DEV_SERVER --> DEV_DB[(SQLite)]
    end

    subgraph 운영 환경
        EXT_USER[외부 사용자] --> ROUTER[공유기<br/>포트포워딩]
        ROUTER --> GUNICORN[Gunicorn<br/>WSGI 서버]
        GUNICORN --> DJANGO[Django 앱]
        DJANGO --> PROD_DB[(SQLite)]
    end

    style DEV_SERVER fill:#ffcccc
    style GUNICORN fill:#ccffcc
</pre>

| 항목 | 개발 | 운영 |
|------|------|------|
| 서버 | `runserver` (단일 스레드) | Gunicorn (멀티 워커) |
| DEBUG | True (에러 상세 노출) | False (에러 숨김) |
| SECRET_KEY | 하드코딩 OK | 환경변수 필수 |
| 접근 범위 | localhost만 | 외부 인터넷 |
| 프로세스 관리 | 수동 실행 | systemd (자동 재시작) |

---

# [02] 핵심 도구 소개

이 포스트에서 사용하는 주요 도구를 먼저 정리한다.

## 2-1. Gunicorn (Green Unicorn)

Python용 **WSGI HTTP 서버**다. Django나 Flask 같은 Python 웹 프레임워크를 운영 환경에서 실행할 때 사용한다.

- **WSGI**(Web Server Gateway Interface): Python 웹 앱과 웹 서버 사이의 표준 인터페이스
- **멀티 워커** 방식으로 동시 요청을 처리한다 (runserver는 단일 스레드)
- 프로세스가 죽으면 자동으로 워커를 재생성한다

```shell
# 설치
pip install gunicorn

# 실행 (워커 3개, 포트 2929)
gunicorn myproject.wsgi:application --bind 0.0.0.0:2929 --workers 3
```

## 2-2. Nginx

**고성능 웹 서버이자 리버스 프록시**다. 정적 파일 서빙, SSL 처리, 로드 밸런싱 등을 담당한다.

- Gunicorn 앞에 배치하여 **리버스 프록시** 역할을 수행한다
- 정적 파일(CSS, JS, 이미지)을 Gunicorn을 거치지 않고 직접 서빙하여 성능을 높인다
- SSL(HTTPS) 인증서 처리, DDoS 기본 방어 등 보안 기능을 제공한다

```
외부 요청 → Nginx (정적 파일 직접 응답, 동적 요청은 Gunicorn으로 전달) → Gunicorn → Django
```

:bulb: 소규모 서비스에서는 Nginx 없이 Gunicorn만으로 충분하다. 이 포스트에서는 Gunicorn 단독 구성을 기본으로 설명하고, [10]에서 Nginx 확장을 다룬다.
{: .notice--info}

## 2-3. systemd

Linux의 **시스템 및 서비스 관리자**다. 서비스(데몬) 등록, 자동 시작, 프로세스 감시를 담당한다.

- PC 부팅 시 서비스를 자동으로 시작한다
- 프로세스가 비정상 종료되면 자동으로 재시작한다
- `journalctl` 명령으로 서비스 로그를 확인할 수 있다

```shell
# 서비스 시작 / 중지 / 재시작
sudo systemctl start myservice
sudo systemctl stop myservice
sudo systemctl restart myservice

# 부팅 시 자동 시작 등록
sudo systemctl enable myservice

# 로그 확인
sudo journalctl -u myservice -f
```

## 2-4. ufw (Uncomplicated Firewall)

Ubuntu의 **방화벽 관리 도구**다. iptables를 간단한 명령으로 제어한다.

```shell
# 방화벽 활성화
sudo ufw enable

# 특정 포트 허용
sudo ufw allow 2929/tcp

# 현재 규칙 확인
sudo ufw status
```

---

# [03] runserver로 서비스하면 안 되는 이유

Django의 `runserver`는 개발 전용이다.

<pre class="mermaid">
graph TD
    A[runserver의 한계] --> B[단일 스레드<br/>동시 접속 불가]
    A --> C[보안 검증 없음<br/>DEBUG 모드 전제]
    A --> D[정적 파일<br/>비효율 서빙]
    A --> E[장애 시<br/>자동 복구 없음]

    F[Gunicorn의 장점] --> G[멀티 워커<br/>동시 접속 처리]
    F --> H[WSGI 표준<br/>운영 최적화]
    F --> I[프로세스 관리<br/>워커 자동 재시작]
    F --> J[systemd 연동<br/>서버 부팅 시 자동 실행]
</pre>

**핵심**: `runserver`는 "맛보기", Gunicorn은 "실전"이다.

---

# [04] 외부 접근을 위한 네트워크 구조

집 PC를 외부에서 접근하려면 **DDNS + 포트포워딩**이 필요하다.

<pre class="mermaid">
sequenceDiagram
    participant User as 외부 사용자
    participant DNS as DDNS 서버<br/>(iptime 등)
    participant Router as 공유기
    participant PC as 집 PC

    User->>DNS: xxx.xxx.com 접속 요청
    DNS-->>User: 공유기 공인 IP 반환
    User->>Router: 공인IP:2929 접속
    Router->>PC: 내부IP:2929으로 전달<br/>(포트포워딩)
    PC-->>Router: Django 응답
    Router-->>User: 응답 전달
</pre>

## 4-1. DDNS란?

가정용 인터넷은 IP가 수시로 바뀐다(유동 IP). DDNS(Dynamic DNS)는 바뀌는 IP를 고정 도메인에 자동 연결해준다.

```
공유기 IP: 221.148.xxx.xxx (수시 변경)
    ↕ DDNS 자동 갱신
도메인: xxx.xxx.com (고정)
```

대부분의 iptime 공유기는 DDNS 기능을 내장하고 있어 무료로 사용할 수 있다.

## 4-2. 포트포워딩이란?

공유기 뒤에는 여러 기기가 있다. 외부에서 특정 포트로 접속하면, 공유기가 어떤 내부 기기로 보낼지 정하는 규칙이 포트포워딩이다.

<pre class="mermaid">
graph LR
    EXT[외부 인터넷] -->|:2929| ROUTER[공유기]
    EXT -->|:3131| ROUTER

    ROUTER -->|:2929| PC1[PC - engwrite]
    ROUTER -->|:3131| PC2[PC - 다른 서비스]

    style ROUTER fill:#ffffcc
</pre>

**하나의 PC에서 여러 서비스**를 운영할 때는 포트 번호로 구분한다:
- `xxx.xxx.com:2929` → engwrite (Django)
- `xxx.xxx.com:3131` → 다른 서비스

---

# [05] 운영 환경 구성 요소

<pre class="mermaid">
graph TB
    subgraph "운영 환경 스택"
        direction TB
        A[systemd] -->|프로세스 관리| B[Gunicorn]
        B -->|WSGI 프로토콜| C[Django]
        C -->|ORM| D[(SQLite DB)]
        E[환경변수 .env] -.->|SECRET_KEY<br/>DEBUG<br/>ALLOWED_HOSTS| C
        F[방화벽 ufw] -.->|포트 2929 허용| B
    end
</pre>

| 구성 요소 | 역할 | 없으면? |
|-----------|------|---------|
| **Gunicorn** | Python WSGI 서버, 요청을 Django로 전달 | 동시 접속 불가, 성능 저하 |
| **systemd** | 프로세스 감시, 서버 부팅 시 자동 실행 | PC 재부팅마다 수동 실행 필요 |
| **환경변수** | 비밀키, 설정값을 코드 밖에서 관리 | 비밀키 유출, 설정 하드코딩 |
| **방화벽** | 허용된 포트만 외부 접근 허용 | 보안 취약 |

---

# [06] Django 설정: 개발 → 운영 전환

운영 환경에서는 Django 설정이 달라져야 한다.

<pre class="mermaid">
graph LR
    subgraph "개발 모드"
        D1[DEBUG = True]
        D2[SECRET_KEY = 하드코딩]
        D3["ALLOWED_HOSTS = ['*']"]
    end

    subgraph "운영 모드"
        P1[DEBUG = False]
        P2[SECRET_KEY = 환경변수]
        P3["ALLOWED_HOSTS = ['xxx.xxx.com']"]
    end

    D1 -->|변경| P1
    D2 -->|변경| P2
    D3 -->|변경| P3

    style D1 fill:#ffcccc
    style D2 fill:#ffcccc
    style D3 fill:#ffcccc
    style P1 fill:#ccffcc
    style P2 fill:#ccffcc
    style P3 fill:#ccffcc
</pre>

## 6-1. DEBUG = False

```
개발: 에러 발생 시 코드, 변수, SQL 쿼리 모두 노출
운영: "Server Error (500)" 한 줄만 표시
```

## 6-2. SECRET_KEY

```
개발: 아무 값이나 OK
운영: 50자 이상 랜덤 문자열, 절대 외부 노출 금지
      → 세션 위조, CSRF 우회 등 치명적 취약점 발생 가능
```

## 6-3. ALLOWED_HOSTS

```
개발: ['*'] (모든 호스트 허용)
운영: ['xxx.xxx.com', 'localhost'] (명시적 도메인만)
      → Host Header 공격 방지
```

---

# [07] 배포 프로세스 흐름

<pre class="mermaid">
flowchart TD
    START([배포 시작]) --> VENV[1. 가상환경 생성<br/>python3 -m venv venv]
    VENV --> DEPS[2. 의존성 설치<br/>pip install -r requirements.txt<br/>pip install gunicorn]
    DEPS --> ENV[3. 환경변수 설정<br/>.env 파일 작성<br/>SECRET_KEY 생성]
    ENV --> MIGRATE[4. DB 마이그레이션<br/>python manage.py migrate]
    MIGRATE --> SYSTEMD[5. systemd 서비스 등록<br/>자동 시작 설정]
    SYSTEMD --> FIREWALL[6. 방화벽 포트 오픈<br/>ufw allow 2929/tcp]
    FIREWALL --> ROUTER[7. 공유기 설정<br/>포트포워딩 + DDNS]
    ROUTER --> TEST[8. 외부 접속 테스트<br/>xxx.xxx.com:2929]
    TEST --> DONE([배포 완료])

    style START fill:#e6f3ff
    style DONE fill:#e6ffe6
</pre>

---

# [08] systemd: 서비스를 "항상 켜진 상태"로

systemd는 Linux의 프로세스 관리자다. 서비스 파일을 등록하면:

- **PC 부팅 시** 자동으로 Django 서버 시작
- **프로세스 죽으면** 5초 후 자동 재시작
- **로그**를 체계적으로 관리

<pre class="mermaid">
stateDiagram-v2
    [*] --> 시작: PC 부팅 / systemctl start
    시작 --> 실행중: Gunicorn 프로세스 생성
    실행중 --> 실행중: 요청 처리
    실행중 --> 비정상종료: 프로세스 크래시
    비정상종료 --> 시작: 5초 후 자동 재시작
    실행중 --> 정상종료: systemctl stop
    정상종료 --> [*]
</pre>

## 8-1. 서비스 파일 구조

```ini
[Unit]
Description=서비스 설명
After=network.target          # 네트워크가 준비된 후 시작

[Service]
User=kcloud                   # 실행 사용자
WorkingDirectory=/path/to/app # 프로젝트 경로
EnvironmentFile=/path/.env    # 환경변수 파일
ExecStart=/path/gunicorn ...  # 실행 명령
Restart=always                # 항상 재시작
RestartSec=5                  # 5초 후 재시작

[Install]
WantedBy=multi-user.target    # 부팅 시 자동 시작
```

---

# [09] 여러 서비스를 한 PC에서 운영하기

하나의 PC에서 여러 웹 서비스를 운영할 수 있다.

<pre class="mermaid">
graph TB
    EXT[외부 인터넷]

    EXT -->|:2929| S1
    EXT -->|:3131| S2
    EXT -->|:4040| S3

    subgraph "집 PC (하나의 머신)"
        S1[engwrite<br/>Gunicorn :2929<br/>engwrite.service]
        S2[서비스 B<br/>Node.js :3131<br/>service-b.service]
        S3[서비스 C<br/>Flask :4040<br/>service-c.service]
    end

    style S1 fill:#ddeeff
    style S2 fill:#ddfedd
    style S3 fill:#ffddee
</pre>

**규칙:**
- 각 서비스는 **다른 포트 번호** 사용
- 각 서비스마다 **별도 systemd 서비스 파일** 등록
- 공유기에서 **각 포트별 포트포워딩 규칙** 추가

---

# [10] 보안 체크리스트

:warning: 홈서버를 외부에 노출할 때 반드시 확인해야 할 사항이다.
{: .notice--warning}

<pre class="mermaid">
graph TD
    SEC[보안 체크리스트] --> A[DEBUG = False<br/>에러 정보 숨김]
    SEC --> B[SECRET_KEY<br/>환경변수로 분리]
    SEC --> C[ALLOWED_HOSTS<br/>도메인 명시]
    SEC --> D[방화벽<br/>필요한 포트만 오픈]
    SEC --> E[비밀번호 정책<br/>최소 길이 + 흔한 비밀번호 차단]
    SEC --> F[CSRF 보호<br/>폼 전송 시 토큰 검증]

    A --> PASS{통과?}
    B --> PASS
    C --> PASS
    D --> PASS
    E --> PASS
    F --> PASS

    PASS -->|모두 Yes| SAFE[배포 가능]
    PASS -->|하나라도 No| DANGER[위험 - 수정 필요]

    style SAFE fill:#ccffcc
    style DANGER fill:#ffcccc
</pre>

---

# [11] 선택적 확장: Nginx 리버스 프록시

더 안정적인 구성을 원한다면 Gunicorn 앞에 Nginx를 추가할 수 있다.

<pre class="mermaid">
graph LR
    USER[외부 사용자] --> NGINX[Nginx<br/>:2929]
    NGINX -->|프록시| GUNICORN[Gunicorn<br/>:8000 내부]
    GUNICORN --> DJANGO[Django]

    style NGINX fill:#ccffcc
    style GUNICORN fill:#ffffcc
</pre>

| Gunicorn만 | Nginx + Gunicorn |
|------------|-----------------|
| 구성 간단 | 정적 파일 효율적 서빙 |
| 소규모에 적합 | SSL(HTTPS) 설정 가능 |
| 바로 외부 노출 | DDoS 기본 방어 |

:bulb: 이 프로젝트 규모에서는 Gunicorn만으로 충분하다. 사용자가 늘거나 HTTPS가 필요하면 그때 Nginx를 추가한다.
{: .notice--info}

---

# [12] 전체 아키텍처 요약

<pre class="mermaid">
graph TB
    subgraph "인터넷"
        USER[외부 사용자<br/>브라우저]
    end

    subgraph "공유기"
        DDNS[DDNS: xxx.xxx.com]
        FWD[포트포워딩<br/>:2929 → 내부IP:2929]
    end

    subgraph "집 PC (Ubuntu)"
        FW[방화벽 ufw<br/>2929/tcp 허용]
        SD[systemd<br/>프로세스 관리]
        GU[Gunicorn<br/>WSGI 서버<br/>워커 x3]
        DJ[Django<br/>engwrite 앱]
        DB[(SQLite<br/>db.sqlite3)]
        ENV[.env<br/>SECRET_KEY<br/>설정값]
    end

    USER -->|xxx.xxx.com:2929| DDNS
    DDNS --> FWD
    FWD --> FW
    FW --> SD
    SD -->|관리| GU
    GU -->|WSGI| DJ
    DJ --> DB
    ENV -.-> DJ

    style USER fill:#e6f3ff
    style GU fill:#ccffcc
    style DJ fill:#ddeeff
    style DB fill:#ffffcc
</pre>

이 구조를 이해하면 어떤 웹 프레임워크(Flask, FastAPI, Express 등)든 동일한 패턴으로 홈서버에 배포할 수 있다.
