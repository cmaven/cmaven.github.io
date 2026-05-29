---
title: "agentmemory — Claude Code가 작업 내용을 기억하게 만드는 영구 메모리"
description: "세션이 끝나면 모든 맥락을 잊어버리는 Claude Code에 영구 메모리를 더하는 agentmemory 소개. 설치, Claude Code 연결, 자동 캡처·검색 사용법과 작동 원리(메모리 파이프라인, 4단계 통합) 정리"
excerpt: "Claude Code는 세션이 끝나면 다 잊는다. agentmemory는 훅으로 작업을 자동 기록하고 다음 세션에 다시 주입해 '재설명'을 없앤다"
date: 2026-05-28
categories: Claude
tags: [Claude Code, agentmemory, 영구메모리, persistent-memory, MCP, hooks, 메모리, AI-coding-agent, CLAUDE.md, MEMORY.md, 시맨틱검색, iii]
ref: agentmemory-persistent-memory-claude-code
---

:bulb: Claude Code를 비롯한 모든 코딩 에이전트는 **세션이 끝나면 작업 맥락을 전부 잊는다.** 매 세션 첫 5분을 "우리 스택은 이렇고, 인증은 JWT를 쓰고…" 다시 설명하는 데 쓰게 된다. [agentmemory](https://github.com/rohitg00/agentmemory)는 백그라운드에서 작업을 자동 기록하고 다음 세션에 다시 주입해 이 반복을 없애는 **영구 메모리** 도구다.
{: .notice--info}

:memo: agentmemory는 [iii 엔진](https://github.com/iii-hq/iii) 위에 구현되었으며 Claude Code뿐 아니라 Cursor, Gemini CLI, Codex CLI 등 훅·MCP·REST를 지원하는 모든 에이전트와 함께 동작한다.
{: .notice--warning}

---

# [01] 왜 필요한가 — Claude Code는 매번 잊는다

Claude Code에도 `CLAUDE.md` / `MEMORY.md` 같은 기본 메모리가 있다. Cursor의 notepad, Cline의 memory bank도 마찬가지다. 하지만 이것들은 **포스트잇**에 가깝다. agentmemory는 그 포스트잇 뒤에서 동작하는 **검색 가능한 데이터베이스**다.

```text
세션 1: "API에 인증 기능 추가해줘"
  에이전트가 코드 작성, 테스트 실행, 버그 수정
  agentmemory가 모든 도구 사용을 조용히 캡처
  세션 종료 → 관찰 내용을 구조화된 메모리로 압축

세션 2: "이제 rate limiting 추가해줘"
  에이전트가 이미 알고 있음:
    - 인증은 src/middleware/auth.ts의 JWT 미들웨어 사용
    - test/auth.test.ts가 토큰 검증을 커버
    - Edge 호환성 때문에 jsonwebtoken 대신 jose 선택
  재설명 0. 곧바로 작업 시작.
```

## 1-1. 기본 메모리와의 차이

| 구분 | 기본 메모리 (CLAUDE.md) | agentmemory |
|------|-------------------------|-------------|
| 규모 | 200줄 제한 | 무제한 |
| 검색 | 전체를 컨텍스트에 로드 | BM25 + 벡터 + 그래프 (상위 K개만) |
| 토큰 비용 | 관찰 240개에서 22K+ | 약 1,900 토큰 (92% 절감) |
| 교차 에이전트 | 에이전트별 파일 | MCP + REST (모든 에이전트) |
| 관찰성 | 파일을 직접 열어봐야 함 | :3113 실시간 뷰어 |

---

# [02] 설치

Node 환경에서 npm 전역 설치가 권장된다. 설치하면 `agentmemory` 명령을 어디서나 쓸 수 있다.

```bash
npm install -g @agentmemory/agentmemory
# macOS/Linux 시스템 Node에서 EACCES가 나면:
# sudo npm install -g @agentmemory/agentmemory

agentmemory          # 메모리 서버 시작 (:3111)
agentmemory demo     # 샘플 세션을 넣고 검색(recall) 동작 시연
agentmemory stop     # 서버 종료
agentmemory remove   # 생성한 것 전부 제거(언인스톨)
```

설치 없이 바로 써보려면 `npx`도 가능하다.

```bash
npx @agentmemory/agentmemory
```

:warning: `npx`는 버전별로 캐시한다. 예전 버전이 뜨면 `npx -y @agentmemory/agentmemory@latest`로 최신을 강제하거나 캐시(`~/.npm/_npx`)를 지운다. 안정적으로 쓰려면 전역 설치가 낫다.
{: .notice--warning}

서버가 뜨면 메모리가 쌓이는 과정을 **실시간 뷰어** `http://localhost:3113`에서 볼 수 있다.

---

# [03] Claude Code 연결

## 3-1. 플러그인 설치 (권장)

별도 터미널에서 메모리 서버(`agentmemory`)를 띄운 뒤, Claude Code 안에서 다음을 실행한다.

```text
/plugin marketplace add rohitg00/agentmemory
/plugin install agentmemory
```

이 한 번의 설치로 **12개 자동 훅**, Skill, 그리고 `@agentmemory/mcp` stdio 서버(`.mcp.json` 자동 연결)까지 등록된다. 추가 설정 없이 **53개 MCP 도구**(`memory_smart_search`, `memory_save`, `memory_sessions` 등)를 바로 쓸 수 있다.

연결 확인:

```bash
curl http://localhost:3111/agentmemory/health
```

## 3-2. 플러그인 없이 연결 (--with-hooks)

플러그인 설치 대신 훅을 직접 병합하려면 아래 명령을 쓴다. `~/.claude/settings.json`에 절대 경로로 훅이 추가되며, agentmemory 업그레이드 후 다시 실행해 경로를 갱신하면 된다.

```bash
agentmemory connect claude-code --with-hooks
```

:memo: 가능하면 `/plugin install` 경로가 권장된다. MCP만 직접 연결하면 업그레이드 시 훅 경로가 깨질 수 있다.
{: .notice--warning}

---

# [04] 사용법

## 4-1. 30초 데모로 체험하기

```bash
# 터미널 1: 서버 시작
npx @agentmemory/agentmemory

# 터미널 2: 샘플 세션 주입 + 검색 시연
npx @agentmemory/agentmemory demo
```

`demo`는 현실적인 세션 3개(JWT 인증, N+1 쿼리 수정, rate limiting)를 넣고 시맨틱 검색을 돌린다. "database performance optimization"으로 검색하면 "N+1 query fix"를 찾아낸다 — 단순 키워드 매칭으로는 불가능한 동작이다.

## 4-2. 자동 캡처 — 손댈 필요 없음

연결만 해두면 별도 조작이 필요 없다. Claude Code의 훅이 발동할 때마다 작업이 자동으로 기록되고, 다음 세션 시작 시 관련 메모리가 컨텍스트에 주입된다.

| 훅 | 캡처 내용 |
|----|-----------|
| `SessionStart` | 프로젝트 경로, 세션 ID, (관련 메모리 주입) |
| `UserPromptSubmit` | 사용자 프롬프트 (개인정보 필터링) |
| `PreToolUse` | 파일 접근 패턴 + 보강된 컨텍스트 |
| `PostToolUse` | 도구 이름, 입력, 출력 |
| `PreCompact` | 압축(compaction) 전 메모리 재주입 |
| `Stop` / `SessionEnd` | 세션 요약 및 종료 마커 |

:bulb: 개인정보 보호가 기본이다. API 키·시크릿·`<private>` 태그는 저장 전에 제거된다.
{: .notice--info}

## 4-3. 기존 Claude Code 기록 가져오기

이미 쌓인 Claude Code JSONL 트랜스크립트를 메모리로 불러올 수 있다.

```bash
# ~/.claude/projects 아래 전체 가져오기
npx @agentmemory/agentmemory import-jsonl

# 특정 파일만 가져오기
npx @agentmemory/agentmemory import-jsonl ~/.claude/projects/-my-project/abc123.jsonl
```

가져온 세션은 뷰어의 **Replay** 탭에서 프롬프트·도구 호출·응답을 타임라인으로 재생(0.5×~4× 속도)할 수 있다.

---

# [05] 메모리 구분(스코프)과 자동 참조 — 흔한 오해

"클라이언트 서버(A/B/C)별로 메모리가 자동 구분되고, 후속 작업 때 이전 작업 맥락을 자동으로 참조한다"고 생각하기 쉽다. **부분적으로만 맞다.** 실제 동작을 짚어본다.

## 5-1. 구분 기준은 "서버(host)"가 아니라 project + AGENT_ID

agentmemory는 물리적 클라이언트 서버로 **자동 구분하지 않는다.** 구분 축은 다음 세 가지다.

| 스코프 축 | 설명 | 기본값 |
|-----------|------|--------|
| `project` (주 스코프) | 메모리를 묶는 1차 네임스페이스 (예: 작업/프로젝트 이름) | 호출 시 지정 |
| `AGENT_ID` (env) | 쓰기마다 역할(architect/dev 등) 태그 부착 | 미설정 시 태그 없음 |
| `AGENTMEMORY_AGENT_SCOPE` | `shared`(태그만 달고 recall은 전체) / `isolated`(자기 것만) | `shared` |

:warning: MCP 등록 env에 URL·SECRET만 있고 `AGENT_ID`가 없으면, 여러 클라이언트가 **같은 `project`로 쓸 때 한 저장소에 전부 뒤섞인다** (unscoped legacy — 태그도 필터도 없음). 서버 A의 작업과 서버 B의 작업이 구분 없이 공유된다.
{: .notice--warning}

A/B/C를 구분하려면 각 클라이언트/작업마다 **다른 값을 명시**해야 한다.

- **작업 단위 구분**: `memory_save` 호출 시 `project`를 다르게 지정
- **서버/역할 단위 구분**: MCP env에 `AGENT_ID=serverA` 추가 (필요시 `AGENTMEMORY_AGENT_SCOPE=isolated`)

## 5-2. 후속 작업이 이전 맥락을 자동 참조? — 조건부 YES

두 가지 전제가 모두 충족돼야 한다.

**전제 ① 자동 주입은 플러그인(SessionStart hook)이 있어야 한다.** [04]에서 본 자동 주입은 플러그인이 등록하는 `SessionStart` 훅이 담당한다. **MCP만 등록한 상태라면 자동 주입이 일어나지 않는다.** 이 경우 작업 중 Claude가 직접 `memory_recall` / `memory_smart_search`를 호출해야 이전 기록을 가져온다.

**전제 ② 같은 스코프에서 조회해야 한다.** 후속 작업이 이전 작업과 **같은 `project`(또는 같은 agent 스코프)**로 조회해야 검색에 걸린다. 저장은 A `project`, 조회는 B `project`로 하면 안 잡힐 수 있고, `isolated` 모드면 더 엄격하다.

| 기대 | 실제 |
|------|------|
| "A 서버 작업이 A로 자동 구분 저장" | ❌ 자동 아님. `project`/`AGENT_ID`를 명시해야 구분. 미설정 시 섞임 |
| "후속 작업 때 이전 맥락 자동 참조" | ⚠️ 조건부. 플러그인 있으면 자동 / 없으면 명시 recall 필요. 게다가 같은 스코프여야 함 |

:bulb: 원하는 그림("서버·작업별 분리 + 후속 자동 참조")을 구현하려면 — ① 각 클라이언트 MCP env에 `AGENT_ID`를 설정하고 작업별 `project`를 일관되게 부여, ② 자동 맥락 주입을 원하면 **플러그인(SessionStart hook)을 설치**한다. 플러그인 없이 MCP만 쓰면 작업 시작 시 수동으로 recall해야 한다.
{: .notice--info}

---

# [06] 작동 원리

## 6-1. 메모리 파이프라인

```text
PostToolUse 훅 발동
  → SHA-256 중복 제거 (5분 윈도우)
  → 개인정보 필터 (시크릿·API 키 제거)
  → 원본 관찰 저장
  → LLM 압축 → 구조화된 사실 + 개념 + 내러티브
  → 벡터 임베딩
  → BM25 + 벡터 인덱싱

Stop / SessionEnd 훅 발동
  → 세션 요약
  → 지식 그래프 추출

SessionStart 훅 발동
  → 프로젝트 프로필 로드 (핵심 개념·파일·패턴)
  → 하이브리드 검색 (BM25 + 벡터 + 그래프)
  → 토큰 예산 적용 (기본 2,000 토큰)
  → 대화에 주입
```

## 6-2. 4단계 메모리 통합

사람 뇌가 수면 중 기억을 정리하는 방식에서 영감을 받았다.

| 단계 | 내용 | 비유 |
|------|------|------|
| **Working** | 도구 사용에서 나온 원본 관찰 | 단기 기억 |
| **Episodic** | 압축된 세션 요약 | "무슨 일이 있었나" |
| **Semantic** | 추출된 사실과 패턴 | "내가 아는 것" |
| **Procedural** | 워크플로·의사결정 패턴 | "하는 방법" |

자주 쓰는 메모리는 강화되고, 오래된 메모리는 자동 소멸(Ebbinghaus 망각 곡선)하며, 모순은 감지·해소된다.

---

# [07] 정리

| 항목 | 내용 |
|------|------|
| 핵심 가치 | 세션 간 작업 맥락을 유지해 "재설명" 제거 |
| 설치 | `npm install -g @agentmemory/agentmemory` |
| Claude Code 연결 | `/plugin marketplace add` → `/plugin install agentmemory` |
| 서버 / 뷰어 | `:3111` (REST) / `:3113` (실시간 뷰어) |
| 외부 DB | 불필요 (0개) |

:bulb: Claude Code가 "어제 우리가 뭘 했는지"를 매번 다시 듣지 않게 하고 싶다면, agentmemory를 한 번 연결해두자. 이후로는 훅이 알아서 기록하고, 다음 세션이 그 위에서 시작된다.
{: .notice--info}

> 출처 및 최신 정보: [github.com/rohitg00/agentmemory](https://github.com/rohitg00/agentmemory)
