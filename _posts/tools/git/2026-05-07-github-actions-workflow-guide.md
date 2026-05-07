---
title: "GitHub Actions 워크플로 라인 단위 가이드 — deploy.yml(push로 빌드·배포)과 stale.yml(schedule로 이슈·PR 정리) 비교 학습"
description: "GitHub Actions 핵심 5개 용어(workflow/event/job/step/action) 정리 후, push 트리거로 사이트를 빌드·배포하는 deploy.yml과 schedule cron으로 비활성 이슈·PR을 자동 정리하는 stale.yml 두 워크플로를 한 줄씩 해부해 동작 원리를 비교하며 학습한다"
excerpt: "단순한 봇 워크플로(stale.yml)부터 다중 잡 빌드/배포 워크플로(deploy.yml)까지, 같은 5개 용어로 표현되는 GitHub Actions의 동작 모델을 두 가지 실제 YAML로 라인 단위 분석"
date: 2026-05-07
categories: Git
tags: [GitHub-Actions, deploy.yml, stale.yml, GitHub-Pages, schedule, cron, CI-CD, workflow, YAML, VitePress, Node.js, ubuntu-latest, npm-ci, actions-checkout, actions-deploy-pages, actions-stale, OIDC, GITHUB_TOKEN, automation, 이슈관리, exempt-labels]
---

:bulb: GitHub Actions를 처음 마주하면 YAML이 어떻게 굴러가는지 감이 안 잡힌다. 이 글은 한 저장소에 함께 들어 있는 **두 가지 실제 워크플로**를 라인 단위로 해부하면서 Actions의 동작 모델을 익히는 학습 노트다. (1) **`deploy.yml`** — `push` 이벤트로 트리거되어 VitePress 사이트를 빌드·배포하는 다중 잡 워크플로. (2) **`stale.yml`** — `schedule` cron으로 매일 자동 실행되어 비활성 이슈·PR을 정리하는 단일 액션 봇. 두 가지를 비교해 보면 트리거 방식과 잡 구조의 차이가 한눈에 들어온다.
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
| **Workflow** | 자동화 시나리오 1개 (= YAML 파일 1개) | `Deploy VitePress site to Pages` / `Close stale issues and PRs` |
| **Event** | 워크플로를 시작시키는 신호 | `push`, `workflow_dispatch`, `schedule` |
| **Job** | 같은 runner 위에서 실행되는 작업 묶음 | `build`, `deploy`, `stale` |
| **Step** | Job 내부에서 순차 실행되는 한 명령 | `npm ci`, `npm run docs:build` |
| **Action** | 누군가 미리 만들어 둔 "재사용 가능한 step" 패키지 | `actions/checkout@v4`, `actions/stale@v3` |

> **유닉스 비유**: workflow = 셸 스크립트, job = 함수, step = 명령 한 줄, action = 외부 라이브러리

:bulb: 이 5개 단어만 머릿속에 정리되면 어떤 워크플로 YAML을 봐도 70%는 읽힌다.
{: .notice--info}

---

# [03] 파일이 놓이는 위치

```
저장소 루트/
└── .github/
    └── workflows/
        ├── deploy.yml      ← 워크플로 ①
        └── stale.yml       ← 워크플로 ②
```

GitHub은 이 폴더를 **자동으로 감시**한다. YAML이 들어오면 즉시 "이런 워크플로가 등록되었구나" 라고 인식하고, 다음 이벤트부터 트리거가 동작한다.

:warning: 폴더 이름이 `.github/workflows/`(복수형) 임에 주의. `.github/workflow/`로 두면 무시된다.
{: .notice--warning}

---

# [04] 워크플로 ① — `deploy.yml` (push 트리거 빌드·배포)

main에 push되면 VitePress 사이트를 빌드해서 GitHub Pages에 게시하는 워크플로다.

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

## 4-3. 트리거 — `on:` (push + 수동 실행)

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
| `build:` | job ID — 다른 job이 `needs: build` 로 참조 |
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

## 4-8. deploy.yml 전체 실행 흐름

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

# [05] 워크플로 ② — `stale.yml` (schedule 트리거 봇)

같은 저장소에 함께 들어 있는 두 번째 워크플로다. 매일 자동 실행되어 비활성 이슈와 PR을 정리한다.

## 5-1. stale.yml이 하는 일 한 문장

> **"매일 새벽 1시 30분(UTC)에 자동 실행되어, 일정 기간 활동이 없는 이슈·PR에 `Status: Stale` 라벨을 붙이고, 그 이후로도 활동이 없으면 7일 뒤 자동으로 닫는 봇 워크플로"**

오픈소스 저장소에서 누적되는 "답이 안 오는 오래된 이슈/PR"을 사람 손 안 대고 정리해주는 자동화. 이 워크플로는 minimal-mistakes Jekyll 테마 같은 인기 저장소의 issue tracker가 폭발적으로 쌓이는 걸 막기 위해 도입된 것이다.

## 5-2. deploy.yml과 무엇이 다른가

| 비교 | `deploy.yml` | `stale.yml` |
|------|------------|-------------|
| 목적 | **사이트 배포** (산출물 게시) | **저장소 관리** (이슈/PR 정리) |
| 트리거 | `on: push` + `workflow_dispatch` | `on: schedule` (cron) |
| 실행 시점 | 사람이 push할 때 | **고정된 시각에 GitHub이 자동 실행** |
| 메인 액션 | `actions/checkout` + `actions/deploy-pages` | `actions/stale` 단 한 개 |
| 잡 개수 | 2개 (`build`, `deploy`) | 1개 (`stale`) |
| 산출물 | `_site` / `dist` (정적 파일) | 없음 — GitHub API 호출만 |

핵심 학습 포인트는 **"`schedule` 트리거가 어떻게 작동하는지"** 와 **"`actions/stale` 같은 단일 액션 워크플로의 구조"**.

## 5-3. 전체 코드

```yaml
name: "Close stale issues and PRs"
on:
  schedule:
    - cron: "30 1 * * *"

jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v3
        with:
          stale-issue-message: |
            This issue has been automatically marked as stale because it has not had recent activity.

            If this is a **bug** and you can still reproduce this error on the `master` branch, please reply with any additional information you have about it in order to keep the issue open.

            If this is a feature request, please [add as an Idea under discussions](https://github.com/mmistakes/minimal-mistakes/discussions/categories/ideas) and elaborate on why it is core to this project and why you feel more than 80% of users would find it beneficial.

            This issue will automatically be closed in 7 days if no further activity occurs. Thank you for all your contributions.
          stale-pr-message: |
            This pull request has been automatically marked as stale because it has not had recent activity.

            This pull request will automatically be closed in 7 days if no further activity occurs. Thank you for all your contributions.
          stale-issue-label: "Status: Stale"
          exempt-issue-labels: "Status: Accepted,Status: Under Consideration,Status: Review Needed,Status: In Progress"
          stale-pr-label: "Status: Stale"
          exempt-pr-labels: "Status: Accepted,Status: Under Consideration,Status: Review Needed,Status: In Progress"
```

전체 28줄. 이걸 5개 영역으로 끊어 보면 구조가 한눈에 들어온다.

## 5-4. 트리거 — `on: schedule` + cron

```yaml
on:
  schedule:
    - cron: "30 1 * * *"
```

| 줄 | 의미 |
|----|------|
| `on:` | 트리거 선언 (deploy.yml과 동일한 키) |
| `schedule:` | **시간 기반 트리거** — push/PR 같은 이벤트가 아니라 시계가 트리거 |
| `- cron: "30 1 * * *"` | cron 표현식. 매일 **01:30 UTC** 에 실행 |

### cron 표현식 5필드 읽기

```
cron: "30 1 * * *"
       │  │ │ │ │
       │  │ │ │ └─ 요일 (0=일~6=토, * = 매일)
       │  │ │ └─── 월 (1~12, * = 매월)
       │  │ └───── 일 (1~31, * = 매일)
       │  └─────── 시 (0~23 UTC)
       └────────── 분 (0~59)
```

| 필드 | 값 | 의미 |
|------|----|----|
| 분 | `30` | 30분 |
| 시 | `1` | 1시 (UTC) |
| 일 | `*` | 매일 |
| 월 | `*` | 매월 |
| 요일 | `*` | 모든 요일 |

**최종 해석**: 매일 01:30 UTC = **한국시간 매일 오전 10:30** (UTC+9) 에 실행.

:warning: GitHub Actions의 `schedule:` 시각은 **항상 UTC** 다. KST로 "매일 09:00에 돌리고 싶다" 면 UTC 기준 `0 0 * * *` (00:00 UTC = 09:00 KST) 로 적어야 한다.
{: .notice--warning}

:bulb: cron 시각에 ±10분 정도 지연이 생길 수 있다 — GitHub runner 가용량에 따라 큐잉되기 때문. 분 단위 정확성이 필요한 작업에는 부적합.
{: .notice--info}

### 자주 쓰는 cron 패턴

| cron | 의미 |
|------|------|
| `0 * * * *` | 매시 정각 |
| `*/15 * * * *` | 15분마다 |
| `0 0 * * *` | 매일 자정 UTC (= 09:00 KST) |
| `0 0 * * 0` | 매주 일요일 자정 UTC |
| `0 0 1 * *` | 매월 1일 자정 UTC |

## 5-5. Jobs — `stale` 잡

```yaml
jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v3
```

| 줄 | 의미 |
|----|------|
| `jobs:` | 워크플로의 모든 job 정의 시작 |
| `stale:` | job ID — 한 단어로도 충분 (다른 job이 참조할 일이 없으면) |
| `runs-on: ubuntu-latest` | Ubuntu 최신 LTS runner. 이 워크플로는 GitHub API만 호출하므로 OS는 사실상 무엇이든 무방 |
| `- uses: actions/stale@v3` | **`actions/stale` v3 액션을 호출**. 이 한 줄이 워크플로의 거의 전부 |

:bulb: deploy.yml의 build 잡과 비교하면 `name:` 필드가 step에 없다 (Actions UI에는 액션 이름이 그대로 표시됨). step이 1개일 때 흔히 생략한다.
{: .notice--info}

### `actions/stale@v3` 가 하는 일

내부에서 다음 단계를 수행한다.

1. **이슈/PR 목록 가져오기** — REST API로 모든 open issue/PR 조회
2. **활동 시점 확인** — `updated_at` 기준 최근 60일(기본값) 이상 변동 없으면 후보
3. **면제 라벨 검사** — `exempt-issue-labels` 에 지정한 라벨이 붙어 있으면 건너뜀
4. **stale 표시** — 후보에 `stale-issue-label` 라벨 붙이고 `stale-issue-message` 코멘트 게시
5. **닫기** — 이미 stale 라벨이 붙어 있고 7일(기본값) 추가로 활동 없으면 자동 close

여기서 단계 3·4·5의 동작을 결정하는 게 아래 `with:` 블록의 옵션들이다.

## 5-6. Stale 메시지 — `with:` 블록의 멀티라인 문자열

```yaml
with:
  stale-issue-message: |
    This issue has been automatically marked as stale because it has not had recent activity.

    If this is a **bug** and you can still reproduce this error on the `master` branch, please reply ...
```

### YAML 멀티라인 문자열 — `|` 의 의미

`|` (block scalar / literal style) 는 **줄바꿈을 그대로 보존**한다. 들여쓰기는 첫 줄 기준으로 제거되고, 그 안의 빈 줄·마크다운 강조까지 모두 살아간다.

```yaml
key: |
  Line 1
  Line 2

  Line 4 (after blank)
```

→ 결과 문자열:
```
Line 1
Line 2

Line 4 (after blank)
```

### `>` 와의 차이

| 표기 | 동작 | 사용 시나리오 |
|------|------|--------------|
| `key: \|` | 줄바꿈 보존 | **여기처럼** 마크다운 메시지·여러 줄 코드 |
| `key: >` | 줄바꿈 → 공백 (folded) | 한 문장이지만 길어서 줄바꿈만 한 경우 |
| `key: "..."` | 한 줄 문자열 | 짧은 값 |

`actions/stale` 메시지에는 빈 줄과 마크다운(`**bug**`, `[링크](URL)`)이 들어가야 하므로 반드시 `|` 를 써야 한다.

:bulb: `stale-issue-message` 는 **봇이 자동으로 코멘트로 게시**하는 텍스트다. 즉 사용자에게 "왜 갑자기 stale이 됐는지·뭘 하면 되는지"를 알려주는 인터페이스. 비슷한 워크플로를 자기 저장소에 도입할 때 톤·언어·연락 채널만 맞춰 수정하면 된다.
{: .notice--info}

## 5-7. 라벨 정책

```yaml
stale-issue-label: "Status: Stale"
exempt-issue-labels: "Status: Accepted,Status: Under Consideration,Status: Review Needed,Status: In Progress"
stale-pr-label: "Status: Stale"
exempt-pr-labels: "Status: Accepted,Status: Under Consideration,Status: Review Needed,Status: In Progress"
```

| 옵션 | 역할 |
|------|------|
| `stale-issue-label` | stale로 판단된 이슈에 **붙일** 라벨 이름 |
| `exempt-issue-labels` | 이 라벨이 **이미 붙어 있으면 stale 처리에서 제외** (콤마 구분) |
| `stale-pr-label` | PR용 stale 라벨 |
| `exempt-pr-labels` | PR용 면제 라벨 |

### 면제 라벨이 필요한 이유

다음 4개 라벨이 붙은 이슈/PR은 **활동이 없어도 자동 close되지 않는다.**

| 라벨 | 의미 |
|------|------|
| `Status: Accepted` | 메인테이너가 이미 작업하기로 받아들임 → 묵혀도 OK |
| `Status: Under Consideration` | 검토 중인 제안 → 빠른 결정이 어려운 사안 |
| `Status: Review Needed` | 코드 리뷰 대기 → 메인테이너 쪽 책임 |
| `Status: In Progress` | 작업 진행 중 → 시간이 걸려도 살려둬야 함 |

:warning: 이런 안전장치 없이 stale 봇만 돌리면 **장기 추적 중인 의미 있는 이슈도 잘려나간다.** 내 저장소에 stale을 도입할 때 면제 라벨 정의는 필수.
{: .notice--warning}

## 5-8. stale.yml 전체 실행 흐름

<pre class="mermaid">
flowchart TD
    A["GitHub 스케줄러<br/>매일 01:30 UTC"] --> B["runner 할당<br/>ubuntu-latest"]
    B --> C["actions/stale@v3 실행"]
    C --> D["GitHub API:<br/>open issue/PR 목록 조회"]
    D --> E{"updated_at이<br/>60일 이상 전?"}
    E -->|No| F["다음 항목"]
    E -->|Yes| G{"면제 라벨<br/>붙어 있나?"}
    G -->|Yes| F
    G -->|No| H{"이미 stale<br/>라벨 있나?"}
    H -->|No| I["stale 라벨 추가<br/>+ 안내 코멘트 게시"]
    H -->|Yes, 7일 경과| J["이슈/PR 자동 close"]
    H -->|Yes, 7일 미만| F

    style A fill:#e3f2fd,stroke:#1565c0
    style I fill:#fff3e0,stroke:#e65100
    style J fill:#ffcccc,stroke:#c62828
    style F fill:#f5f5f5,stroke:#616161
</pre>

---

# [06] 두 워크플로 비교 정리

같은 5개 용어(workflow / event / job / step / action) 위에서 두 워크플로가 어떻게 다르게 표현되는지를 한 표로 정리한다.

| 항목 | `deploy.yml` | `stale.yml` |
|------|------------|-------------|
| **Event** | `push` + `workflow_dispatch` | `schedule` (cron) |
| **트리거 발동 주체** | 사람 (push) | GitHub 스케줄러 (시계) |
| **Permissions** | 명시 (`contents`, `pages`, `id-token`) | 기본 `GITHUB_TOKEN` (별도 명시 X) |
| **Concurrency** | `group: pages`, `cancel-in-progress: false` | 명시 X (배포 동시성 이슈 없음) |
| **Job 개수** | 2개 (`build` → `deploy`, `needs:` 의존) | 1개 (`stale`) |
| **Step 개수** | 약 7개 (checkout/setup-node/npm ci/build/configure-pages/upload/deploy) | 1개 (`uses: actions/stale@v3`) |
| **주요 Action** | `actions/checkout`, `actions/setup-node`, `actions/configure-pages`, `actions/upload-pages-artifact`, `actions/deploy-pages` | `actions/stale` 하나 |
| **동작 방식** | runner에서 **빌드 명령 직접 실행** (`run: npm ci`) | **GitHub API 호출만** (외부 명령 실행 없음) |
| **산출물** | 정적 사이트 (`docs/.vitepress/dist`) | 없음 (이슈/PR 상태만 변경) |
| **실패 시 영향** | 사이트가 갱신되지 않음 | 그날 정리가 1회 누락될 뿐 |

## 두 워크플로가 같은 메커니즘 위에 있다는 증거

```
공통 구조:
.github/workflows/<file>.yml
│
├─ name:                    # ← 둘 다 있음
├─ on:                      # ← 둘 다 있음 (값만 다름)
│
└─ jobs:                    # ← 둘 다 있음
   └─ <job-id>:
       runs-on: ubuntu-latest
       steps:
         - ...              # ← 둘 다 있음 (개수·내용만 다름)
```

**같은 5개 용어로 모든 워크플로가 표현된다**는 게 핵심이다. 사이트 배포·이슈 정리·테스트 자동화·릴리스·시크릿 회전 — 무엇이든 이 구조 위에 얹힌다.

---

# [07] 자주 만나는 에러·함정

## 7-1. `deploy.yml` 쪽에서 자주 만나는 에러 3가지

### `HttpError: Not Found` (configure-pages 단계)

- **원인**: 저장소 Pages 미활성, 또는 Source가 `Deploy from a branch`
- **해결**: `Settings → Pages → Source = GitHub Actions`

### `Resource not accessible by integration`

- **원인**: `permissions:` 블록에서 `pages: write` 또는 `id-token: write` 누락
- **해결**: 4-4의 3개 권한을 모두 명시

### CSS·이미지가 깨짐 (404)

- **원인**: Project Pages (`username.github.io/repo-name/`) 인데 `base` 경로 미설정
- **해결**: `docs/.vitepress/config.ts` 에 `base: '/repo-name/'` 추가
  - Jekyll의 경우 `_config.yml` 에 `baseurl: "/repo-name"` 추가

## 7-2. `stale.yml` 쪽에서 자주 만나는 함정 3가지

### cron 시각이 KST가 아닌 UTC다

```yaml
# 잘못 — "매일 오전 9시 KST에 돌리고 싶음"
- cron: "0 9 * * *"   # 실제로는 UTC 09:00 = KST 18:00 에 실행

# 올바름
- cron: "0 0 * * *"   # UTC 00:00 = KST 09:00
```

GitHub Actions는 시간대 설정 옵션이 없다. UTC 기준으로 변환해서 적어야 한다.

### fork된 저장소에서는 schedule이 안 돈다

`schedule:` 트리거는 **fork된 저장소에서는 자동으로 비활성화**된다. fork에서도 cron이 돌면 GitHub 전체에 의도치 않은 부하가 생기기 때문. 비공개 fork에서 자동화를 돌리고 싶다면 `workflow_dispatch:` 를 추가하거나 외부 스케줄러를 써야 한다.

### 60일 / 7일 기본값을 명시하지 않으면 그대로 사용된다

```yaml
# stale.yml에는 적혀 있지 않은 항목들의 기본값
days-before-stale: 60         # 마지막 활동 후 stale 표시까지 대기 일수
days-before-close: 7          # stale 표시 후 close까지 대기 일수
operations-per-run: 30        # 한 번 실행에서 처리할 최대 항목 수
```

활동이 적은 저장소에서 60일은 너무 짧을 수 있다. 옵션을 명시적으로 적는 편이 안전하다.

```yaml
with:
  days-before-stale: 180       # 6개월 무활동 후 stale
  days-before-close: 14        # 추가 2주 후 close
```

---

# [08] 디버깅 팁 (공통)

| 상황 | 방법 |
|------|------|
| 워크플로가 트리거되지 않음 | 파일 위치(`.github/workflows/`)·확장자(`.yml`)·`on:` 블록 확인 |
| 특정 step에서만 실패 | Actions UI에서 step 클릭 → 콘솔 로그 펼치기 |
| schedule이 발동하지 않음 | 저장소가 fork인지 확인 / 마지막 commit이 60일 이상 전이면 일부 schedule이 자동 비활성화됨 |
| 로컬에서 재현하고 싶다 | [`act`](https://github.com/nektos/act) 도구로 워크플로를 로컬 Docker에서 실행 |
| 비밀값(API 키 등) 필요 | 저장소 `Settings → Secrets and variables → Actions` 에 등록 후 `${{ secrets.MY_KEY }}` 로 참조 |
| 수동으로 한번 돌려보고 싶다 | `workflow_dispatch:` 가 있으면 Actions UI에 **Run workflow** 버튼이 생김 |

---

# [09] 한 장 요약 — 두 워크플로 트리

```
.github/workflows/
│
├── deploy.yml                                   ← push 트리거 빌드·배포
│   │
│   ├─ on: push(main) | workflow_dispatch        # ① 언제?
│   ├─ permissions: contents:r pages:w id-token:w
│   ├─ concurrency: group=pages
│   │
│   └─ jobs:
│      ├─ build:                                 # ② 무엇을?
│      │   1. checkout (전체 히스토리)
│      │   2. setup-node 20 + npm 캐시
│      │   3. npm ci
│      │   4. npm run docs:build  → docs/.vitepress/dist
│      │   5. configure-pages
│      │   6. upload-pages-artifact (dist)
│      │
│      └─ deploy: needs=build
│          1. deploy-pages → https://*.github.io 갱신
│
└── stale.yml                                    ← schedule 트리거 봇
    │
    ├─ on: schedule (cron: 30 1 * * * = 매일 01:30 UTC)
    │
    └─ jobs:
       └─ stale: ubuntu-latest
           └─ uses: actions/stale@v3
               with:
                 stale-*-message:    "..."        # 안내 메시지
                 stale-*-label:      "Status: Stale"
                 exempt-*-labels:    "Accepted, ..."
```

push 한 번이든, 시계가 한 번 째깍이든 — GitHub Actions는 **이벤트 → runner 할당 → step 순차 실행** 이라는 동일한 모델로 두 워크플로를 굴린다.

:star: Jekyll·Hugo·Next.js·Astro 등 다른 정적 사이트 생성기도 빌드 명령과 artifact 경로만 바꾸면 `deploy.yml` 패턴 그대로 쓸 수 있고, 이슈/PR 정리뿐 아니라 시크릿 회전·릴리스 노트 자동 작성·DB 백업도 `stale.yml` 같은 schedule 패턴으로 동일하게 표현된다. **5개 용어 + 2개 패턴(이벤트형/스케줄형)으로 거의 모든 자동화 시나리오가 커버된다.**
{: .notice--info}
