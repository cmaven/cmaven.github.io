---
title: "Oh My Claude (omc): Claude Code Multi-Agent 오케스트레이션 도구"
description: "oh-my-claudecode 플러그인의 설치, 주요 명령어(team, autopilot, ralph, deep-interview), Skill 시스템, CLI 사용법 정리"
excerpt: "Claude Code에서 복잡한 작업을 자동으로 전문 에이전트에게 분배하는 omc 플러그인의 설치부터 실전 활용까지"
date: 2026-03-19
categories: Claude
tags: [Claude Code, omc, Oh-My-Claude, Multi-Agent, autopilot, team, ralph, deep-interview, 플러그인, 오케스트레이션]
---

:bulb: Claude Code에서 복잡한 작업을 여러 전문 에이전트에게 자동 분배하는 **oh-my-claudecode(omc)** 플러그인의 설치, 명령어, 활용법을 정리한다.
{: .notice--info}

---

# [01] omc란?

**oh-my-claudecode(omc)**는 Claude Code를 위한 **Multi-Agent 오케스트레이션 프레임워크**다. 복잡한 작업을 자동으로 전문화된 에이전트들에게 분배하고, 설정 없이 즉시 사용할 수 있다.

| 특징 | 설명 |
|------|------|
| **설정 불필요** | 기본값으로 즉시 작동 |
| **팀 우선** | 계획 → 설계 → 실행 → 검증 파이프라인 |
| **자연어 명령** | 명령어 암기 불필요, 자연어로 지시 |
| **자동 병렬화** | 복잡한 작업을 에이전트에게 자동 분배 |
| **19개 전문 에이전트** | 아키텍처, 연구, 테스트, 데이터과학 등 |
| **스마트 라우팅** | 간단한 작업은 Haiku, 복잡한 추론은 Opus 사용 |

---

# [02] 설치

## 2-1. 플러그인 마켓플레이스 (권장)

Claude Code 프롬프트에서 아래 명령어를 순서대로 입력한다.

```
/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
/plugin install oh-my-claudecode
```

## 2-2. npm CLI

```bash
npm i -g oh-my-claude-sisyphus@latest
```

:warning: 리포지토리는 `oh-my-claudecode`이지만, npm 패키지명은 **oh-my-claude-sisyphus**다.
{: .notice--warning}

## 2-3. 초기 설정

```
/setup
/omc-setup
```

또는 터미널에서:

```bash
omc setup
```

## 2-4. 빠른 시작

설치 후 바로 사용할 수 있다:

```
autopilot: build a REST API for managing tasks
```

---

# [03] 주요 명령어

## 3-1. 전체 명령어 맵

<pre class="mermaid">
graph TD
    OMC["omc"]

    OMC --> TEAM["/team\n팀 오케스트레이션"]
    OMC --> AUTO["/autopilot\n완전 자동 실행"]
    OMC --> RALPH["/ralph\n지속성 모드"]
    OMC --> ULW["/ultrawork\n최대 병렬화"]
    OMC --> DI["/deep-interview\n요구사항 분석"]
    OMC --> ASK["/ask\n전문가 자문"]
    OMC --> CCG["/ccg\n삼중 모델 종합"]
    OMC --> SKILL["/skill\nSkill 관리"]

    style OMC fill:#f3e5f5,stroke:#6a1b9a
    style TEAM fill:#e3f2fd,stroke:#1565c0
    style AUTO fill:#e8f5e9,stroke:#2e7d32
    style RALPH fill:#fff3e0,stroke:#e65100
    style ULW fill:#fce4ec,stroke:#c62828
    style DI fill:#f5f5f5,stroke:#616161
    style ASK fill:#ffffcc,stroke:#f9a825
    style CCG fill:#e0f7fa,stroke:#00838f
    style SKILL fill:#fce4ec,stroke:#ad1457
</pre>

## 3-2. 명령어 요약

| 명령어 | 설명 | 사용 시점 |
|--------|------|-----------|
| `/team` | 팀 기반 파이프라인 (계획→설계→실행→검증) | 구조적인 개발 작업 |
| `/autopilot` | 완전 자동 실행 | 명확한 요구사항의 빠른 구현 |
| `/ralph` | 완료될 때까지 지속 시도 | 끈기가 필요한 리팩토링 |
| `/ultrawork` (`/ulw`) | 최대 병렬화 | 대량 오류 수정 |
| `/deep-interview` | 소크라테스식 요구사항 분석 | 불명확한 요구사항 정리 |
| `/ask` | 특정 모델에 전문가 자문 요청 | 설계 검토, 리스크 분석 |
| `/ccg` | Codex + Gemini + Claude 통합 | 다각적 검토 |
| `/skill` | Skill 관리 (추가/삭제/검색) | 반복 패턴 등록 |

---

# [04] Team Mode — 팀 오케스트레이션

omc의 **핵심 기능**이다. 계획 → 설계 → 실행 → 검증 → 수정의 파이프라인 구조로 작업을 처리한다.

```
/team 3:executor "fix all TypeScript errors"
```

| 구문 | 의미 |
|------|------|
| `3:executor` | executor 에이전트 3명 배포 |
| `"fix all ..."` | 작업 지시 |

### tmux CLI에서 사용

```bash
omc team 2:codex "review auth module for security issues"
omc team 2:gemini "redesign UI components for accessibility"
omc team 1:claude "implement the payment flow"
```

### 상태 확인 및 종료

```bash
omc team status auth-review      # 상태 확인
omc team shutdown auth-review    # 종료
```

---

# [05] Autopilot — 완전 자동 실행

요구사항이 명확할 때, 처음부터 끝까지 자동으로 실행한다.

```
/autopilot "build a todo app"
```

또는 자연어 단축키:

```
autopilot: build a REST API for managing tasks
```

---

# [06] Ralph — 지속성 모드

완료될 때까지 **포기하지 않고 계속 시도**한다. 복잡한 리팩토링이나 마이그레이션에 적합하다.

```
/ralph "refactor authentication module"
```

---

# [07] Deep Interview — 요구사항 분석

요구사항이 불명확하거나, 설계부터 꼼꼼히 검토하고 싶을 때 사용한다.

```
/deep-interview "I want to build a task management app"
```

소크라테스식 질문을 통해:
- 숨겨진 전제를 파악한다
- 여러 항목에 대한 명확도를 측정한다
- **코드를 작성하기 전에 무엇을 만들지 정확히 아는 것**이 목표다

---

# [08] Ultrawork — 최대 병렬화

대량의 작업을 최대한 병렬로 처리한다.

```
/ultrawork "fix all errors"
```

축약형:

```
/ulw "fix all errors"
```

---

# [09] Ask & CCG — 전문가 자문

## 9-1. Ask — 단일 모델 자문

특정 모델에 전문가 조언을 요청한다.

```
/ask claude "review this migration plan"
/ask codex "identify architecture risks"
/ask gemini "propose UI design ideas"
```

터미널 CLI:

```bash
omc ask claude "review this migration plan"
omc ask codex --prompt "identify architecture risks"
omc ask gemini --prompt "propose UI ideas"
```

## 9-2. CCG — 삼중 모델 종합

Codex + Gemini + Claude 세 모델의 관점을 종합한다.

```
/ccg "review this PR - architecture (Codex) and UI (Gemini)"
```

---

# [10] Skill 시스템

omc는 반복되는 패턴을 **Skill**로 저장하고 재사용할 수 있다.

## 10-1. Skill 저장 위치

| 범위 | 경로 | 공유 범위 | 우선순위 |
|------|------|----------|---------|
| 프로젝트 | `.omc/skills/` | 팀 전체 (버전관리) | 높음 |
| 사용자 | `~/.omc/skills/` | 모든 프로젝트 | 낮음 |

## 10-2. Skill 파일 예시

```yaml
# .omc/skills/fix-proxy-crash.md
---
name: Fix Proxy Crash
description: aiohttp proxy crashes on ClientDisconnectedError
triggers: ["proxy", "aiohttp", "disconnected"]
source: extracted
---
Wrap handler at server.py:42 in try/except ClientDisconnectedError...
```

## 10-3. Skill 관리 명령어

```
/skill list              # Skill 목록
/skill add               # 새 Skill 추가
/skill remove            # Skill 제거
/skill edit              # Skill 편집
/skill search            # Skill 검색
/learner                 # 자동 패턴 추출
```

---

# [11] CLI 유틸리티

## 11-1. 터미널 명령어

| 명령어 | 설명 |
|--------|------|
| `omc setup` | 초기 설정 |
| `omc hud` | 실시간 HUD 상태 표시 |
| `omc doctor` | 진단 및 캐시 정리 |
| `omc wait` | Rate Limit 상태 확인 |
| `omc wait --start` | 자동 재개 활성화 |
| `omc wait --stop` | 자동 재개 비활성화 |

## 11-2. Autoresearch — 자동 연구

```bash
omc autoresearch
omc autoresearch --mission "improve startup performance" \
  --eval "npm test -- --run src/tests/perf.test.ts"
omc autoresearch init --topic "benchmark onboarding flow"
```

## 11-3. 알림 설정 (Telegram/Discord/Slack)

작업 완료 시 알림을 받을 수 있다.

```bash
# Telegram
omc config-stop-callback telegram --enable \
  --token <bot_token> --chat <chat_id>

# Discord
omc config-stop-callback discord --enable \
  --webhook <url>

# Slack
omc config-stop-callback slack --enable \
  --webhook <url>
```

---

# [12] In-Session 자연어 단축키

Claude Code 세션 안에서 슬래시 명령어 없이 자연어로도 사용할 수 있다.

| 자연어 | 동작 |
|--------|------|
| `autopilot: 할 일 앱 만들어줘` | Autopilot 실행 |
| `ralph: 인증 모듈 리팩토링` | Ralph 실행 |
| `deepsearch for auth middleware` | 코드베이스 검색 |
| `ultrathink about this design` | 깊은 추론 |
| `cancelomc` / `stopomc` | 실행 중단 |

---

# [13] 업데이트

```bash
# npm
npm i -g oh-my-claude-sisyphus@latest

# 플러그인
/plugin marketplace update omc
/setup

# 문제 발생 시
/omc-doctor
```

---

# [14] 정리

| 용도 | 명령어 | 설명 |
|------|--------|------|
| 구조적 개발 | `/team 3:executor "작업"` | 팀 파이프라인 |
| 빠른 구현 | `/autopilot "작업"` | 완전 자동 |
| 끈기 있는 작업 | `/ralph "작업"` | 완료까지 반복 |
| 대량 처리 | `/ulw "작업"` | 최대 병렬화 |
| 요구사항 정리 | `/deep-interview "아이디어"` | 소크라테스식 분석 |
| 전문가 검토 | `/ask codex "검토 요청"` | 단일 모델 자문 |
| 다각적 검토 | `/ccg "검토 요청"` | 삼중 모델 종합 |

> 참고: [oh-my-claudecode GitHub](https://github.com/Yeachan-Heo/oh-my-claudecode) · [공식 문서](https://yeachan-heo.github.io/oh-my-claudecode-website)
