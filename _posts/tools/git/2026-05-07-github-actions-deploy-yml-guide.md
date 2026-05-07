---
title: "GitHub Actions deploy.yml 라인 단위로 이해하기 — VitePress + Pages 자동 배포 워크플로 해부"
description: "GitHub Actions 핵심 5개 용어와 VitePress + GitHub Pages 자동 배포 deploy.yml의 모든 라인(트리거·permissions·concurrency·build·deploy)을 한 줄씩 해부해 동작 원리를 학습한다"
excerpt: "main에 push하면 VitePress가 빌드되고 Pages에 배포되는 deploy.yml 워크플로를 라인 단위로 분석하면서 GitHub Actions의 workflow·event·job·step·action 개념을 함께 익힌다"
date: 2026-05-07
categories: Git
tags: [GitHub-Actions, deploy.yml, GitHub-Pages, CI-CD, workflow, YAML, VitePress, Node.js, ubuntu-latest, npm-ci, actions-checkout, actions-deploy-pages, automation, OIDC, GITHUB_TOKEN]
---

:bulb: GitHub Actions를 처음 마주하면 YAML이 뭐가 어떻게 굴러가는지 감이 안 잡힌다. 이 글은 **VitePress 사이트를 GitHub Pages에 자동 배포하는 `deploy.yml`** 한 줄 한 줄을 해부하면서 Actions의 동작 모델을 익히는 학습 노트다. 다른 프레임워크(Jekyll, Next.js, Hugo 등)도 구조는 동일하므로 그대로 응용할 수 있다.
{: .notice--info}

---

# [01] GitHub Actions 한 문장 정리

> **"저장소에 어떤 이벤트(push, PR, schedule 등)가 발생했을 때, GitHub이 빌려주는 가상 머신에서 YAML 파일에 적힌 명령을 자동으로 실행해주는 서비스"**

- 우리가 신경 쓸 것: YAML 파일 1개를 작성해 `.github/workflows/` 폴더에 push
- GitHub이 알아서: 저장소 감시 → 이벤트 매칭 → runner 할당 → 명령 실행 → 결과 표시(Actions 탭)

---

# [02] 핵심 용어 5개

| 용어 | 한 줄 정의 | 본문 예시 |
|------|------------|----------|
| **Workflow** | 자동화 시나리오 1개 (= YAML 파일 1개) | `Deploy VitePress site to Pages` |
| **Event** | 워크플로를 시작시키는 신호 | `push`, `workflow_dispatch` |
| **Job** | 같은 runner 위에서 실행되는 작업 묶음 | `build`, `deploy` |
| **Step** | Job 내부에서 순차 실행되는 한 명령 | `npm ci`, `npm run docs:build` |
| **Action** | 누군가 미리 만들어 둔 "재사용 가능한 step" 패키지 | `actions/checkout@v4` |

> **유닉스 비유**: workflow = 셸 스크립트, job = 함수, step = 명령 한 줄, action = 외부 라이브러리

:bulb: 이 5개 단어만 머릿속에 정리되면 어떤 워크플로 YAML을 봐도 70%는 읽힌다.
{: .notice--info}

---

# [03] 파일이 놓이는 위치

```
저장소 루트/
└── .github/
    └── workflows/
        └── deploy.yml      ← 이 파일
```

GitHub은 이 폴더를 **자동으로 감시**한다. YAML이 들어오면 즉시 "이런 워크플로가 등록되었구나" 라고 인식하고, 다음 이벤트부터 트리거가 동작한다.

:warning: 폴더 이름이 `.github/workflows/`(복수형) 임에 주의. `.github/workflow/`로 두면 무시된다.
{: .notice--warning}

---

# [04] `deploy.yml` 라인 단위 해설

이번 글에서 분석할 워크플로는 다음과 같다. main 브랜치에 push되면 VitePress 사이트를 빌드해서 GitHub Pages에 배포한다.

## 4-1. 헤더 주석

```yaml
# ============================================================
# deploy.yml: VitePress GitHub Pages 자동 배포
# main 브랜치 push 시 docs/.vitepress/dist 빌드 후 Pages 배포
# ============================================================
```

- `#` 으로 시작하는 줄은 YAML 주석. 실행에 영향 없음.
- 사람이 파일 용도를 3초 안에 파악할 수 있도록 작성한 메타 정보.

## 4-2. 워크플로 이름

```yaml
name: Deploy VitePress site to Pages
```

- Actions 탭의 **워크플로 목록**에 표시되는 이름.
- 생략하면 파일명이 그대로 표시됨. UI 가독성을 위해 한 줄짜리 설명문을 권장.

## 4-3. 트리거 — `on:` 블록

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:
```

| 줄 | 의미 |
|----|------|
| `on:` | "이 워크플로를 어떤 이벤트에 반응시킬지" 선언하는 루트 키 |
| `push:` | git push 이벤트 |
| `branches: [main]` | **`main` 브랜치에 push될 때만** 동작 (다른 브랜치 push는 무시) |
| `workflow_dispatch:` | Actions UI에 **수동 실행 버튼** 노출 (디버깅/재배포용) |

:warning: `git push origin feature/foo` 처럼 다른 브랜치로 push하면 트리거되지 않는다 — main에 머지되어야 비로소 발동.
{: .notice--warning}

## 4-4. 권한 — `permissions:`

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

GitHub Actions는 `GITHUB_TOKEN` 이라는 자동 발급 토큰으로 GitHub API에 접근한다. 이 토큰의 권한을 **최소한으로** 명시하는 블록.

| 권한 | 왜 필요한가 |
|------|------------|
| `contents: read` | 저장소 코드를 checkout 하려면 읽기 권한 필요 |
| `pages: write` | GitHub Pages에 산출물을 게시하려면 쓰기 권한 필요 |
| `id-token: write` | OIDC 토큰 발급 (Pages 공식 액션이 인증용으로 요구) |

:warning: `id-token: write` 가 없으면 `actions/deploy-pages@v4` 가 인증 실패한다. Pages 배포의 필수 조건.
{: .notice--warning}

## 4-5. 동시 실행 제어 — `concurrency:`

```yaml
concurrency:
  group: pages
  cancel-in-progress: false
```

| 줄 | 의미 |
|----|------|
| `group: pages` | 같은 그룹명을 공유하는 워크플로는 **동시에 1개만 실행** |
| `cancel-in-progress: false` | 이미 진행 중인 배포가 있으면 **취소하지 않고 끝날 때까지 대기** |

:bulb: 빠른 push 2번이 들어와도 첫 번째 배포가 끝난 뒤 두 번째가 시작됨 → Pages 산출물이 꼬이는 것을 방지.
{: .notice--info}

## 4-6. Jobs — `build` 잡

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      ...
```

| 줄 | 의미 |
|----|------|
| `jobs:` | 이 워크플로의 모든 job 정의 시작 |
| `build:` | job ID (영문/숫자/하이픈) — 다른 job이 `needs: build` 로 참조 |
| `runs-on: ubuntu-latest` | 이 job이 돌아갈 가상 머신 OS — Ubuntu 최신 LTS |

### Step ① Checkout

```yaml
- name: Checkout
  uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

| 줄 | 의미 |
|----|------|
| `- name: Checkout` | step 표시 이름 (Actions UI에 노출) |
| `uses: actions/checkout@v4` | 공식 checkout 액션 v4 사용 — runner에 저장소 코드를 복제 |
| `fetch-depth: 0` | 전체 히스토리 fetch (sitemap·last-modified 등 git 메타데이터를 쓰는 빌드에 필요) |

:bulb: 기본값은 `fetch-depth: 1` (마지막 커밋만). VitePress sitemap, Jekyll의 `git-authors-plugin` 같은 기능을 쓸 때는 `0` (= 전체) 이 안전하다.
{: .notice--info}

### Step ② Node 설치

```yaml
- name: Setup Node
  uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: npm
```

| 줄 | 의미 |
|----|------|
| `actions/setup-node@v4` | 공식 액션으로 runner에 Node.js 설치 |
| `node-version: 20` | LTS 버전 명시 (`package.json` 권장 버전과 일치) |
| `cache: npm` | `~/.npm` 폴더를 GitHub 캐시에 저장 → 다음 실행에서 `npm ci` 가속 |

### Step ③ 의존성 설치

```yaml
- name: Install dependencies
  run: npm ci
```

| 항목 | 의미 |
|------|------|
| `run:` | runner의 셸에서 직접 실행할 명령 (`uses:` 와 대비됨) |
| `npm ci` | `package-lock.json` 기준의 **clean install** — 빌드 재현성 보장. `npm install` 보다 엄격·빠름 |

### Step ④ VitePress 빌드

```yaml
- name: Build with VitePress
  run: npm run docs:build
```

- `package.json` 의 `"docs:build": "vitepress build docs"` 가 호출됨
- 산출물 경로: `docs/.vitepress/dist/` — 정적 HTML/CSS/JS

### Step ⑤ Pages 환경 준비

```yaml
- name: Setup Pages
  uses: actions/configure-pages@v4
```

- 저장소의 Pages 설정을 읽어 환경 변수(`base path` 등)를 주입
- 저장소에 Pages 사이트가 enabled 되어 있지 않으면 여기서 `HttpError: Not Found` 로 실패
- 해결: `Settings → Pages → Source = "GitHub Actions"`

### Step ⑥ artifact 업로드

```yaml
- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: docs/.vitepress/dist
```

| 줄 | 의미 |
|----|------|
| `actions/upload-pages-artifact@v3` | 빌드 산출물을 **Pages 전용 artifact** 형식으로 패키징·업로드 |
| `path: docs/.vitepress/dist` | 업로드할 폴더 (= VitePress 빌드 결과) |

:warning: 일반 `actions/upload-artifact` 와는 다른 액션이다. Pages 배포는 전용 artifact만 받는다.
{: .notice--warning}

## 4-7. Jobs — `deploy` 잡

```yaml
deploy:
  needs: build
  runs-on: ubuntu-latest
  environment:
    name: github-pages
    url: ${{ steps.deployment.outputs.page_url }}
  steps:
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v4
```

| 줄 | 의미 |
|----|------|
| `needs: build` | `build` job이 **성공해야** 실행 (실패 시 자동 스킵) |
| `environment:` | 배포 대상 환경 등록 → 저장소 Settings → Environments에서 **승인 정책·시크릿** 관리 가능 |
| `name: github-pages` | Pages가 자동 인식하는 **예약된 환경 이름** (변경 금지) |
| `url: ${{ steps.deployment.outputs.page_url }}` | 배포 후 Actions UI에 표시될 사이트 URL — 아래 step의 output을 참조 |
| `id: deployment` | step 식별자 — `steps.deployment.outputs.page_url` 형태로 다른 곳에서 참조 |
| `actions/deploy-pages@v4` | 직전 잡이 업로드한 Pages artifact를 가져와 **실제로 게시** |

---

# [05] 전체 실행 흐름

<pre class="mermaid">
flowchart TD
    A["git push origin main"] --> B{"on.push.branches<br/>= main?"}
    B -->|No| Z["무시"]
    B -->|Yes| C["runner 할당<br/>ubuntu-latest"]

    C --> D1["build: checkout"]
    D1 --> D2["build: setup-node 20"]
    D2 --> D3["build: npm ci"]
    D3 --> D4["build: vitepress build"]
    D4 --> D5["build: configure-pages"]
    D5 --> D6["build: upload-pages-artifact<br/>(dist 폴더 업로드)"]

    D6 --> E{"build 성공?"}
    E -->|No| F["deploy 스킵"]
    E -->|Yes| G["deploy: deploy-pages<br/>artifact를 Pages에 게시"]
    G --> H["https://username.github.io 갱신"]

    style B fill:#fff3e0,stroke:#e65100
    style E fill:#fff3e0,stroke:#e65100
    style Z fill:#f5f5f5,stroke:#616161
    style F fill:#ffcccc,stroke:#c62828
    style H fill:#e8f5e9,stroke:#2e7d32
</pre>

---

# [06] 자주 만나는 에러 3가지

## 6-1. `HttpError: Not Found` (configure-pages 단계)

- **원인**: 저장소 Pages 미활성, 또는 Source가 `Deploy from a branch`
- **해결**: `Settings → Pages → Source = GitHub Actions`

## 6-2. `Resource not accessible by integration`

- **원인**: `permissions:` 블록에서 `pages: write` 또는 `id-token: write` 누락
- **해결**: 4-4의 3개 권한을 모두 명시

## 6-3. CSS·이미지가 깨짐 (404)

- **원인**: Project Pages (`username.github.io/repo-name/`) 인데 `base` 경로 미설정
- **해결**: `docs/.vitepress/config.ts` 에 `base: '/repo-name/'` 추가
  - Jekyll의 경우 `_config.yml` 에 `baseurl: "/repo-name"` 추가

---

# [07] 디버깅 팁

| 상황 | 방법 |
|------|------|
| 워크플로가 트리거되지 않음 | 파일 위치(`.github/workflows/`)·확장자(`.yml`)·`on:` 블록 확인 |
| 특정 step에서만 실패 | Actions UI에서 step 클릭 → 콘솔 로그 펼치기 |
| 로컬에서 재현하고 싶다 | [`act`](https://github.com/nektos/act) 도구로 워크플로를 로컬 Docker에서 실행 |
| 비밀값(API 키 등) 필요 | 저장소 `Settings → Secrets and variables → Actions` 에 등록 후 `${{ secrets.MY_KEY }}` 로 참조 |
| 수동으로 한번 돌려보고 싶다 | `workflow_dispatch:` 가 있으면 Actions UI에 **Run workflow** 버튼이 생김 |

---

# [08] 한 장 요약

```
.github/workflows/deploy.yml
│
├─ on: push(main) | workflow_dispatch              # ① 언제 트리거?
│
├─ permissions: contents:r pages:w id-token:w      # ② 어떤 권한으로?
│
├─ concurrency: group=pages                        # ③ 동시 실행 정책
│
└─ jobs:
   ├─ build:                                       # ④ 빌드
   │   1. checkout (전체 히스토리)
   │   2. setup-node 20 + npm 캐시
   │   3. npm ci
   │   4. npm run docs:build  → docs/.vitepress/dist
   │   5. configure-pages
   │   6. upload-pages-artifact (dist)
   │
   └─ deploy: needs=build                          # ⑤ 배포 (build 성공 후만)
       1. deploy-pages → https://*.github.io 갱신
```

push 한 번 = 위 단계 자동 실행. 이게 GitHub Actions가 정적 사이트를 **서버 없이도** 인터넷에 공개해주는 메커니즘이다.

:star: Jekyll·Hugo·Next.js·Astro 등 다른 정적 사이트 생성기도 **빌드 명령**(`npm run docs:build` 부분)과 **artifact 경로**(`docs/.vitepress/dist`)만 바꾸면 동일한 구조의 워크플로로 배포할 수 있다.
{: .notice--info}
