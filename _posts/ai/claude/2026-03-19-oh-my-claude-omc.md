---
title: "Oh My Claude (omc): Claude Code 워크플로우 자동화 도구"
description: "CLAUDE.md, Skill, Hook 설정과 Multi-Agent 환경 구성을 하나의 CLI로 자동화하는 omc(Oh My Claude) 도구 소개"
excerpt: "Claude Code의 Skill/Hook 설정, Multi-Agent 환경(tmux + git worktree) 구성을 omc 명령어 하나로 자동화"
date: 2026-03-19
categories: Claude
tags: [Claude Code, omc, Oh-My-Claude, Skill, Hook, Multi-Agent, CLAUDE.md, tmux, git-worktree, 자동화]
---

:bulb: Claude Code로 프로젝트를 구성할 때 필요한 CLAUDE.md, Skill, Hook, Multi-Agent 환경을 **하나의 CLI 도구**로 자동화하는 `omc`(Oh My Claude)를 소개한다.
{: .notice--info}

:bulb: 이 글은 아래 4개 포스트의 내용을 전제로 한다:
- [Skill/Hook 가이드 1부](/claude/claude-code-skill-hook-guide-part1/) — CLAUDE.md, Skill, Hook 개념
- [Skill/Hook 가이드 2부](/claude/claude-code-skill-hook-guide-part2/) — 프로젝트 적용, 고급 구조
- [Multi-Agent 1부](/claude/claude-code-multi-agent-part1/) — tmux + git worktree 구성
- [Multi-Agent 2부](/claude/claude-code-multi-agent-part2/) — 자동화 스크립트, 소통 전략
{: .notice}

---

# [01] omc가 필요한 이유

## 1-1. 현재의 문제

위 4개 포스트에서 다룬 Claude Code 워크플로우를 실제로 적용하려면, 매번 수동으로 해야 하는 작업이 많다:

| 단계 | 수동 작업 | 명령 수 |
|------|-----------|---------|
| 프로젝트 초기화 | CLAUDE.md 작성, Skill 복사, Hook 설정 | 5~10개 |
| Multi-Agent 시작 | worktree 생성, tmux 분할, claude 실행 | 8~12개 |
| Agent 통합 | 브랜치 머지, 충돌 해결 | 3~6개 |
| 환경 정리 | worktree 제거, 브랜치 삭제, tmux 종료 | 5~8개 |

프로젝트마다, 세션마다 이 과정을 반복하면 **설정에 시간을 쓰고, 실제 개발에 집중하지 못한다.**

## 1-2. omc의 목표

> **omc(Oh My Claude)** 는 Claude Code 워크플로우의 모든 설정과 환경 구성을 하나의 CLI로 자동화한다.

```
# Before (수동, 10개+ 명령)
mkdir -p .claude/skills && cp -r ... && vim CLAUDE.md && vim .claude/settings.json && ...

# After (omc, 1개 명령)
omc init
```

---

# [02] omc 명령어 체계

## 2-1. 전체 명령어 맵

<pre class="mermaid">
graph TD
    OMC["omc"]
    OMC --> INIT["omc init\n프로젝트 초기화"]
    OMC --> SKILL["omc skill\nSkill 관리"]
    OMC --> HOOK["omc hook\nHook 관리"]
    OMC --> AGENT["omc agent\nMulti-Agent 관리"]
    OMC --> STATUS["omc status\n상태 확인"]

    SKILL --> SI["omc skill install"]
    SKILL --> SL["omc skill list"]
    HOOK --> HS["omc hook setup"]
    HOOK --> HL["omc hook list"]
    AGENT --> AS["omc agent start"]
    AGENT --> AM["omc agent merge"]
    AGENT --> AC["omc agent clean"]

    style OMC fill:#f3e5f5,stroke:#6a1b9a
    style INIT fill:#e3f2fd,stroke:#1565c0
    style SKILL fill:#e8f5e9,stroke:#2e7d32
    style HOOK fill:#fff3e0,stroke:#e65100
    style AGENT fill:#fce4ec,stroke:#c62828
    style STATUS fill:#f5f5f5,stroke:#616161
</pre>

## 2-2. 명령어 요약

| 명령어 | 설명 | 자동화 대상 (기존 포스트) |
|--------|------|---------------------------|
| `omc init` | 프로젝트에 CLAUDE.md + Skill + Hook 일괄 설정 | Skill/Hook 가이드 2부 [08] |
| `omc skill install` | Skill 패키지 설치 (글로벌/프로젝트) | Skill/Hook 가이드 1부 [05] |
| `omc skill list` | 설치된 Skill 목록 확인 | Skill/Hook 가이드 2부 [09] |
| `omc hook setup` | Hook 이벤트 등록 | Skill/Hook 가이드 1부 [06] |
| `omc hook list` | 등록된 Hook 목록 확인 | Skill/Hook 가이드 2부 [09] |
| `omc agent start` | Multi-Agent 환경 시작 (worktree + tmux + claude) | Multi-Agent 1부 3장, 2부 4장 |
| `omc agent merge` | Agent 브랜치 통합 | Multi-Agent 1부 3.4 |
| `omc agent clean` | 환경 정리 (worktree + 브랜치 + tmux) | Multi-Agent 2부 4.2 |
| `omc status` | 전체 상태 확인 (Skill, Hook, Agent, worktree) | Skill/Hook 가이드 2부 [09] |

---

# [03] omc init — 프로젝트 초기화

## 3-1. 기능

프로젝트 루트에서 `omc init`을 실행하면, Claude Code에 필요한 모든 설정 파일을 자동으로 생성한다.

```shell
cd ~/my-project
omc init
```

**실행 결과:**

```
[omc] 프로젝트 초기화 시작: ~/my-project
[omc] ✓ CLAUDE.md 생성 (기술 스택 감지: React + FastAPI)
[omc] ✓ .claude/skills/coding-workflow/ 설치
[omc] ✓ .claude/settings.json Hook 4개 등록
[omc] ✓ scripts 실행 권한 설정
[omc] 초기화 완료. `claude` 명령으로 시작하세요.
```

## 3-2. 자동 생성되는 파일

```
my-project/
├── CLAUDE.md                              <- 프로젝트 컨텍스트 (자동 감지)
├── .claude/
│   ├── settings.json                      <- Hook 4개 등록
│   └── skills/coding-workflow/
│       ├── SKILL.md                       <- 4가지 규칙
│       ├── agents/code-reviewer.md
│       ├── references/ (4개 파일)
│       └── scripts/ (2개 셸스크립트)
```

이것은 [Skill/Hook 가이드 2부 [08]](/claude/claude-code-skill-hook-guide-part2/#08-프로젝트에-적용하는-방법-step-by-step)에서 수동으로 수행하던 전체 과정을 한 번에 처리한다.

## 3-3. 기술 스택 자동 감지

`omc init`은 프로젝트의 파일 구조를 분석하여 CLAUDE.md에 적절한 내용을 채운다:

| 감지 대상 | 판단 기준 | CLAUDE.md 반영 내용 |
|-----------|-----------|---------------------|
| Frontend | `package.json`의 react/vue/angular | 프레임워크명, 컴포넌트 디렉토리 |
| Backend | `requirements.txt`, `go.mod`, `pom.xml` | 언어, 프레임워크, API 디렉토리 |
| Docker | `Dockerfile`, `docker-compose.yml` | 컨테이너 구조 |
| CI/CD | `.github/workflows/`, `Jenkinsfile` | 파이프라인 구조 |

## 3-4. 옵션

```shell
# 기본 초기화
omc init

# Skill 없이 CLAUDE.md만 생성
omc init --minimal

# 기존 설정 덮어쓰기
omc init --force

# 특정 스킬 템플릿 사용
omc init --template fullstack
omc init --template data-pipeline
```

---

# [04] omc skill — Skill 관리

## 4-1. omc skill install

[Skill/Hook 가이드 1부 [05]](/claude/claude-code-skill-hook-guide-part1/#05-skill---상세-워크플로우-정의)에서 설명한 Skill 설치를 자동화한다.

```shell
# 프로젝트 레벨에 설치 (팀 공유)
omc skill install coding-workflow

# 글로벌 설치 (모든 프로젝트 적용)
omc skill install coding-workflow --global

# zip 파일에서 설치
omc skill install ./my-skill.zip
```

**실행 결과:**

```
[omc] Skill 설치: coding-workflow
[omc] ✓ .claude/skills/coding-workflow/SKILL.md
[omc] ✓ .claude/skills/coding-workflow/agents/code-reviewer.md
[omc] ✓ .claude/skills/coding-workflow/references/ (4개 파일)
[omc] ✓ .claude/skills/coding-workflow/scripts/ (2개 파일, 실행 권한 설정)
[omc] 설치 완료. /coding-workflow 로 호출 가능.
```

## 4-2. omc skill list

설치된 Skill 목록과 상태를 확인한다.

```shell
omc skill list
```

**출력:**

```
[omc] 설치된 Skills:

  위치          이름                상태
  ─────────────────────────────────────────
  글로벌        coding-workflow     ✓ 활성
  프로젝트      data-pipeline       ✓ 활성
  프로젝트      api-docs            ✗ SKILL.md 누락

  글로벌 경로: ~/.claude/skills/
  프로젝트 경로: ./.claude/skills/
```

---

# [05] omc hook — Hook 관리

## 5-1. omc hook setup

[Skill/Hook 가이드 1부 [06]](/claude/claude-code-skill-hook-guide-part1/#06-hook---규칙의-강제-실행)에서 설명한 4가지 Hook을 자동 등록한다.

```shell
# 프로젝트 레벨 Hook 등록
omc hook setup

# 글로벌 Hook 등록
omc hook setup --global
```

**등록되는 Hook 4개:**

| Hook 이벤트 | 동작 | 타입 |
|-------------|------|------|
| `UserPromptSubmit` | Skill 규칙 상기 | command |
| `PostToolUse` (Edit/Write) | 파일 주석 검사 | command |
| `PreToolUse` (Edit/Write) | 민감 파일 차단 (.env, .key) | command |
| `Stop` | 자동 커밋 | command |

## 5-2. omc hook list

```shell
omc hook list
```

**출력:**

```
[omc] 등록된 Hooks:

  위치          이벤트               매처                   타입
  ────────────────────────────────────────────────────────────────
  글로벌        UserPromptSubmit     *                      command
  프로젝트      PostToolUse          Edit|Write|MultiEdit   command
  프로젝트      PreToolUse           Edit|Write|MultiEdit   command
  프로젝트      Stop                 *                      command

  글로벌 설정: ~/.claude/settings.json
  프로젝트 설정: ./.claude/settings.json
```

---

# [06] omc agent — Multi-Agent 관리

이것이 omc의 핵심 기능이다. [Multi-Agent 1부](/claude/claude-code-multi-agent-part1/)와 [2부](/claude/claude-code-multi-agent-part2/)에서 다룬 전체 워크플로우를 하나의 명령으로 실행한다.

## 6-1. omc agent start

### 기본 사용법

```shell
# 기본 3-agent 구성 (frontend, backend, test)
omc agent start

# 2-agent 구성
omc agent start --agents fe,be

# 커스텀 agent 구성
omc agent start --agents fe,be,docs,devops
```

### 실행 과정

`omc agent start`는 다음을 순서대로 실행한다:

```
[omc] Multi-Agent 환경 시작
[omc] [1/5] worktree 생성...
[omc]   ✓ ../wt-fe (브랜치: agent/frontend)
[omc]   ✓ ../wt-be (브랜치: agent/backend)
[omc]   ✓ ../wt-test (브랜치: agent/test)
[omc] [2/5] CLAUDE.md 배치...
[omc]   ✓ ../wt-fe/CLAUDE.md (Frontend Agent 역할 명시)
[omc]   ✓ ../wt-be/CLAUDE.md (Backend Agent 역할 명시)
[omc]   ✓ ../wt-test/CLAUDE.md (Test Agent 역할 명시)
[omc] [3/5] Skill + Hook 복사...
[omc]   ✓ 3개 worktree에 .claude/ 동기화
[omc] [4/5] tmux 세션 생성 및 패널 분할...
[omc]   ✓ 세션: multi-agent (패널 3개)
[omc] [5/5] 각 패널에서 claude 실행...
[omc]   ✓ 패널 0: Frontend Agent (~/wt-fe)
[omc]   ✓ 패널 1: Backend Agent (~/wt-be)
[omc]   ✓ 패널 2: Test Agent (~/wt-test)
[omc] 완료. tmux 세션에 접속합니다.
```

### 자동화되는 기존 수동 작업과의 비교

<pre class="mermaid">
graph LR
    subgraph Before["기존 (수동, 12개 명령)"]
        B1["git worktree add (x3)"]
        B2["cat > CLAUDE.md (x3)"]
        B3["cp -r .claude/ (x3)"]
        B4["tmux new + split (x3)"]
        B5["cd + claude (x3)"]
        B1 --> B2 --> B3 --> B4 --> B5
    end

    subgraph After["omc (자동, 1개 명령)"]
        A1["omc agent start"]
    end

    style Before fill:#fce4ec,stroke:#c62828
    style After fill:#e8f5e9,stroke:#2e7d32
</pre>

### Agent별 자동 CLAUDE.md

`omc agent start` 시, 각 worktree에 역할별 CLAUDE.md가 자동 배치된다:

```markdown
# wt-fe/CLAUDE.md (자동 생성)
# Agent: Frontend
- 역할: React 컴포넌트 개발
- 담당 디렉토리: src/components/, src/pages/
- 브랜치: agent/frontend
- 다른 agent의 영역(backend/, tests/)은 수정하지 않는다
- 작업 내역을 WORK_LOG.md에 기록한다
```

## 6-2. omc agent merge

모든 agent의 작업이 완료된 후, 브랜치를 통합한다.

```shell
omc agent merge
```

**실행 결과:**

```
[omc] Agent 브랜치 통합 시작
[omc] 현재 브랜치: main
[omc]
[omc] ✓ agent/frontend 머지 완료 (커밋 3개)
[omc] ✓ agent/backend 머지 완료 (커밋 5개)
[omc] ⚠ agent/test 머지 시 충돌 발생:
[omc]   - tests/conftest.py (양쪽에서 수정)
[omc]
[omc] 충돌을 해결한 후 `omc agent merge --continue`를 실행하세요.
[omc] 또는 `claude`를 실행하여 Claude에게 충돌 해결을 맡기세요.
```

### 옵션

```shell
# 기본 머지 (충돌 시 중단)
omc agent merge

# 충돌 해결 후 계속
omc agent merge --continue

# 특정 agent만 머지
omc agent merge --only fe,be

# 머지 전 각 브랜치 변경 내역 미리보기
omc agent merge --dry-run
```

## 6-3. omc agent clean

[Multi-Agent 2부 4.2](/claude/claude-code-multi-agent-part2/#42-multi-agent-정리-스크립트)의 정리 스크립트를 대체한다.

```shell
omc agent clean
```

**실행 결과:**

```
[omc] Multi-Agent 환경 정리
[omc] ✓ tmux 세션 종료: multi-agent
[omc] ✓ worktree 제거: ../wt-fe
[omc] ✓ worktree 제거: ../wt-be
[omc] ✓ worktree 제거: ../wt-test
[omc] ✓ worktree 잔여물 정리 (prune)
[omc]
[omc] 남은 agent 브랜치:
[omc]   agent/frontend  (머지 완료)
[omc]   agent/backend   (머지 완료)
[omc]   agent/test      (머지 완료)
[omc]
[omc] 브랜치도 삭제하시겠습니까? (y/N)
```

### 옵션

```shell
# worktree만 정리 (브랜치 유지)
omc agent clean

# worktree + 브랜치 전부 삭제
omc agent clean --all

# 확인 없이 전부 삭제
omc agent clean --all --yes
```

---

# [07] omc status — 상태 확인

[Skill/Hook 가이드 2부 [09]](/claude/claude-code-skill-hook-guide-part2/#09-적용-확인-방법)에서 수동으로 확인하던 내용을 한 번에 보여준다.

```shell
omc status
```

**출력:**

```
[omc] Oh My Claude 상태

  ── 프로젝트 ──────────────────────────────
  경로: ~/my-project
  CLAUDE.md: ✓ 존재 (1.2KB)

  ── Skills ────────────────────────────────
  글로벌: coding-workflow ✓
  프로젝트: (없음)

  ── Hooks ─────────────────────────────────
  글로벌: UserPromptSubmit (1개)
  프로젝트: PostToolUse, PreToolUse, Stop (3개)

  ── Agent ─────────────────────────────────
  tmux 세션: multi-agent (활성, 패널 3개)
  worktree:
    ../wt-fe     agent/frontend   커밋 3개 ahead
    ../wt-be     agent/backend    커밋 5개 ahead
    ../wt-test   agent/test       커밋 2개 ahead
```

---

# [08] omc 설치 및 설정

## 8-1. 설치

```shell
# 1. 스크립트 다운로드
curl -fsSL https://raw.githubusercontent.com/cmaven/omc/main/install.sh | bash

# 2. 또는 수동 설치
git clone https://github.com/cmaven/omc.git ~/.omc
echo 'export PATH="$HOME/.omc/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 3. 설치 확인
omc --version
```

## 8-2. 설정 파일

`~/.omc/config.yml`에서 기본 동작을 설정할 수 있다:

```yaml
# ~/.omc/config.yml

# omc init 기본 설정
init:
  skill: coding-workflow          # 기본 설치 Skill
  hooks: true                     # Hook 자동 등록
  detect_stack: true              # 기술 스택 자동 감지

# omc agent 기본 설정
agent:
  default_agents: [fe, be, test]  # 기본 agent 구성
  worktree_prefix: wt             # worktree 디렉토리 접두사 (../wt-fe)
  branch_prefix: agent            # 브랜치 접두사 (agent/frontend)
  auto_claude_md: true            # agent별 CLAUDE.md 자동 생성
  tmux_session: multi-agent       # tmux 세션 이름

# agent 역할 정의
agent_roles:
  fe:
    name: Frontend Agent
    branch: frontend
    directories: [src/components/, src/pages/, src/styles/]
  be:
    name: Backend Agent
    branch: backend
    directories: [backend/, api/, db/]
  test:
    name: Test Agent
    branch: test
    directories: [tests/, __tests__/]
  docs:
    name: Docs Agent
    branch: docs
    directories: [docs/, README.md]
  devops:
    name: DevOps Agent
    branch: devops
    directories: [.github/, docker/, infra/]
```

## 8-3. 커스텀 agent 역할 추가

```yaml
# ~/.omc/config.yml에 추가
agent_roles:
  ml:
    name: ML Agent
    branch: ml-pipeline
    directories: [models/, training/, data/]
```

```shell
# 사용
omc agent start --agents fe,be,ml
```

---

# [09] 4개 포스트 기능 ↔ omc 명령어 매핑

## 9-1. Skill/Hook 가이드 (1부, 2부) → omc

| 포스트 섹션 | 수동 작업 | omc 명령 |
|-------------|-----------|----------|
| 1부 [04] CLAUDE.md 작성 | `vim CLAUDE.md` | `omc init` (자동 감지 + 생성) |
| 1부 [05] Skill 설치 | `cp -r`, `chmod +x` | `omc skill install` |
| 1부 [06] Hook 설정 | `vim settings.json` | `omc hook setup` |
| 2부 [08] 프로젝트 적용 | `unzip`, `chmod`, `git add` | `omc init` |
| 2부 [09] 적용 확인 | `claude --debug`, `ls` | `omc status` |

## 9-2. Multi-Agent (1부, 2부) → omc

| 포스트 섹션 | 수동 작업 | omc 명령 |
|-------------|-----------|----------|
| 1부 2장 worktree 생성 | `git worktree add` x3 | `omc agent start` |
| 1부 3.2 CLAUDE.md 배치 | `cat > CLAUDE.md` x3 | `omc agent start` (자동) |
| 1부 3.3 tmux + claude | `tmux new`, `Ctrl+b %`, `cd && claude` | `omc agent start` |
| 1부 3.4 브랜치 머지 | `git merge` x3 | `omc agent merge` |
| 1부 3.5 정리 | `git worktree remove`, `git branch -d`, `tmux kill` | `omc agent clean` |
| 2부 4장 자동화 스크립트 | `multi-agent-start.sh` | `omc agent start` |
| 2부 5장 WORK_LOG.md | 수동 운영 | `omc agent start` (Skill/Hook으로 자동화) |

---

# [10] 실전 예제: omc로 풀스택 프로젝트 개발

## 10-1. 시나리오

React + FastAPI 기반 로그인 기능을 3개 agent로 병렬 개발한다.

## 10-2. 전체 흐름

```shell
# 1. 프로젝트 초기화 (최초 1회)
cd ~/login-project
omc init

# 2. Multi-Agent 시작
omc agent start

# 3. (각 tmux 패널에서 작업 지시)
#   패널 0: "로그인 페이지 UI를 만들어줘"
#   패널 1: "POST /api/login JWT 인증 API를 만들어줘"
#   패널 2: "기존 함수의 단위 테스트를 작성해줘"

# 4. 작업 완료 후 통합
omc agent merge

# 5. 정리
omc agent clean --all
```

**기존 대비 명령 수:**

| 방법 | 명령 수 | 예상 소요 |
|------|---------|-----------|
| 수동 (포스트 따라하기) | 20개+ | 5~10분 (설정만) |
| `omc` | 4개 | 30초 |

---

# [11] omc 동작 구조

## 11-1. 아키텍처

<pre class="mermaid">
graph TB
    CLI["omc CLI"]
    CLI --> INIT["init 모듈"]
    CLI --> SKILL["skill 모듈"]
    CLI --> HOOK["hook 모듈"]
    CLI --> AGENT["agent 모듈"]
    CLI --> STATUS["status 모듈"]

    INIT --> DET["기술 스택 감지"]
    INIT --> GEN["CLAUDE.md 생성"]
    INIT --> SKILL
    INIT --> HOOK

    AGENT --> WT["git worktree"]
    AGENT --> TM["tmux"]
    AGENT --> CMD["claude 실행"]

    subgraph 외부도구["외부 도구"]
        WT
        TM
        CMD
    end

    style CLI fill:#f3e5f5,stroke:#6a1b9a
    style 외부도구 fill:#f5f5f5,stroke:#bdbdbd
</pre>

## 11-2. 의존성

| 도구 | 용도 | 필수 여부 |
|------|------|-----------|
| `git` | worktree, 브랜치 관리 | 필수 |
| `tmux` | Multi-Agent 세션 관리 | `omc agent` 사용 시 필수 |
| `claude` | Claude Code CLI | 필수 |
| `jq` | JSON 설정 파일 처리 | 권장 |

---

# [12] 정리

## omc가 자동화하는 것

| 영역 | 기존 (수동) | omc |
|------|-------------|-----|
| 프로젝트 초기화 | CLAUDE.md 작성, Skill 복사, Hook JSON 편집 | `omc init` |
| Skill 관리 | `cp -r`, `chmod +x`, 경로 확인 | `omc skill install/list` |
| Hook 관리 | `settings.json` 직접 편집 | `omc hook setup/list` |
| Multi-Agent 시작 | worktree + tmux + CLAUDE.md + claude 실행 | `omc agent start` |
| 브랜치 통합 | `git merge` 반복, 충돌 수동 확인 | `omc agent merge` |
| 환경 정리 | worktree 삭제, 브랜치 삭제, tmux 종료 | `omc agent clean` |
| 상태 확인 | `ls`, `cat`, `claude --debug` 조합 | `omc status` |

## 핵심 가치

```
설정이 아닌 개발에 집중한다.
```

omc는 Claude Code를 "잘 쓰기 위한 도구"다. CLAUDE.md, Skill, Hook, Multi-Agent라는 4가지 레이어를 이해했다면, 그 다음 단계는 **매번 수동으로 하지 않는 것**이다.
