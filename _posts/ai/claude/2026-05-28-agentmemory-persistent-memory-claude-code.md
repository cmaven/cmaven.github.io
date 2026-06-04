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

## 3-3. 로컬 서버 vs 원격 서버 — 데이터가 어디에 저장되나

[02]·[03-1]은 모두 **로컬 서버**를 가정한다. 내 PC에서 `agentmemory`를 띄우면 메모리도 내 PC에 저장된다. 하지만 팀이 공용으로 쓰거나 여러 머신에서 같은 메모리를 공유하려면 **원격 서버**에 연결한다.

| 모드 | 서버 위치 | 데이터 저장 위치 | 쓰는 상황 |
|------|-----------|------------------|-----------|
| 로컬 | 내 PC (`agentmemory` 직접 실행) | 내 PC | 혼자, 한 대에서 |
| 원격 | 항상 켜진 별도 서버 (예: `10.0.0.10:3111`) | **그 원격 서버** | 팀 공용 / 여러 머신 공유 |

원격 모드에서는 **내 PC에 데이터가 저장되지 않는다.** 로컬 `~/.agentmemory/`에는 *연결 정보만* 들어간다(`standalone.json`도 거의 빈 파일).

```bash
# ~/.agentmemory/.env — 연결 정보(데이터 아님)
AGENTMEMORY_URL=http://10.0.0.10:3111   # 원격 서버 주소
AGENTMEMORY_SECRET=<발급받은 시크릿>          # 인증 토큰
AGENT_ID=alice-laptop                            # 이 클라이언트/역할 식별자
AGENTMEMORY_AGENT_SCOPE=isolated              # isolated=내 것만 / shared=전체 공유
```

실제 관찰·세션·요약은 전부 원격 서버의 저장소(KV)에 쌓인다. 그래서 PC를 바꿔도 같은 `.env`만 있으면 동일한 메모리에 접근한다.

### 원격 저장이 잘 되는지 확인하기

**① 서버 연결(health) 확인** — `Authorization: Bearer`로 시크릿을 넘긴다.

```bash
source ~/.agentmemory/.env
curl -s -H "Authorization: Bearer $AGENTMEMORY_SECRET" \
  "$AGENTMEMORY_URL/agentmemory/health" | jq .status
# "healthy" 가 나오면 원격 서버 정상 (jq가 없으면 응답 전체를 봐도 된다)
```

:warning: 시크릿 없이 `/agentmemory/health`를 치면 `{"error":"unauthorized"}`가 나온다. 인증 헤더는 반드시 `Authorization: Bearer <SECRET>` 형식이어야 한다 — `x-agentmemory-secret` 같은 헤더는 거부된다.
{: .notice--warning}

**② 실제 데이터가 쌓였는지 확인** — Claude Code 창에서 `/session-history`나 `/recall <키워드>`를 실행하면 원격에 저장된 세션이 돌아온다. REST로 직접 보려면:

```bash
curl -s -H "Authorization: Bearer $AGENTMEMORY_SECRET" \
  "$AGENTMEMORY_URL/agentmemory/sessions?limit=5"
# {"sessions":[...]} — 비어 있으면 이 스코프(AGENT_ID/SCOPE)로 저장된 게 아직 없다는 뜻
```

:bulb: `AGENTMEMORY_AGENT_SCOPE=isolated`면 **내 `AGENT_ID`로 저장한 것만** 조회된다. 분명히 작업했는데 `sessions`가 비어 보인다면 — ① 저장 때와 조회 때 `AGENT_ID`가 다르거나, ② 자동 캡처 훅(플러그인)이 안 붙어 애초에 저장이 안 된 경우다. 스코프 동작은 [05]에서 자세히 다룬다.
{: .notice--info}

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

## 4-4. 슬래시 명령어 — 메모리를 직접 다루기

자동 캡처는 백그라운드에서 알아서 돌지만, 메모리를 **직접 조회·저장·관리**하고 싶을 때를 위해 플러그인이 슬래시 명령어를 등록한다. 명령어를 직접 입력해도 되고, 표의 "트리거 표현"에 적힌 자연어("recall", "where were we" 등)를 말하면 Claude Code가 알아서 해당 명령을 호출한다.

**① 조회·저장 — 일상적으로 가장 많이 쓰는 묶음**

| 명령어 | 역할 | 언제 / 트리거 표현 |
|--------|------|--------------------|
| `/recall` | 특정 토픽에 대한 과거 관찰·세션·학습을 검색 | "recall", "remember", "what did we do" — 과거 세션 맥락이 필요할 때 |
| `/remember` | 인사이트·결정·학습을 장기 저장소에 **명시적으로** 보관 | "remember this", "save this" — 다음 세션을 위해 지식을 남기고 싶을 때 |
| `/recap` | 최근 N개 세션을 **날짜별로 묶어** 요약 | "recap", "this week", "today" — 최근 작업을 롤업하고 싶을 때 |
| `/session-history` | 이 프로젝트의 최근 세션에서 무슨 일이 있었는지 개요 표시 | "what did we do last time", "past sessions" — 지난 작업 전반을 훑고 싶을 때 |
| `/handoff` | 현재 작업 디렉토리의 **가장 최근 세션을 이어받아 재개** | "where were we", "resume", "pick up where I left off" — 새 컨텍스트 없이 시작할 때 |

**② 삭제 — 프라이버시·정리용**

| 명령어 | 역할 | 언제 / 트리거 표현 |
|--------|------|--------------------|
| `/forget` | 특정 관찰이나 세션을 메모리에서 삭제 | "forget this", "delete memory" — 프라이버시 등으로 특정 데이터를 지울 때 |

**③ 커밋 ↔ 세션 추적 — 코드의 "왜"를 되짚는 묶음**

| 명령어 | 역할 | 언제 / 트리거 표현 |
|--------|------|--------------------|
| `/commit-context` | 파일·함수·라인을 그 **현재 커밋을 만든 에이전트 세션**으로 역추적 | "이 코드가 왜 여기 있지", "바뀔 때 에이전트가 뭘 하고 있었지" — 특정 위치의 맥락이 궁금할 때 |
| `/commit-history` | 에이전트 세션에 **연결된 최근 git 커밋** 목록 (브랜치·레포로 필터 가능) | "show agent commits", "에이전트가 뭘 배포했지" — 세션 맥락이 붙은 커밋 목록이 필요할 때 |

:bulb: `/remember`(이 글의 명시 저장)와 [04-2]의 자동 캡처는 보완 관계다. 중요한 결정처럼 "반드시 남기고 싶은 것"은 `/remember`로 못 박고, 나머지 일상 작업은 훅이 알아서 쌓게 두면 된다.
{: .notice--info}

## 4-5. 실전 워크플로 — Claude Code 창에서 하루

명령어를 따로따로 보면 와닿지 않으니, **실제 하루 작업 흐름**으로 엮어 본다. 대부분은 그냥 코딩하면 되고(자동 캡처), 굵게 표시한 순간에만 명령어를 친다.

```text
[아침] 어제 작업 이어가기
  > /handoff
  → "어제 auth 미들웨어 작업 중이었고, jose 도입까지 함" 맥락 복원
     (또는 "지난주 우리 뭐 했지?" → /recap)

[작업 중] 평소처럼 코딩
  코드 작성·테스트·버그 수정 → 훅이 알아서 캡처 (할 일 없음)

[결정한 순간] 꼭 남길 것만 못 박기
  > /remember rate limiter는 Redis 대신 Upstash 사용 — 서버리스 호환 때문
  → 장기 저장. 다음 세션이 이 결정 위에서 시작

[막혔을 때] 과거 맥락 끌어오기
  > /recall 우리 JWT 검증 어디서 했지
  → src/middleware/auth.ts, test/auth.test.ts 위치와 당시 결정 반환

[이 코드가 왜 이런지] 커밋 → 세션 역추적
  > /commit-context src/middleware/auth.ts:42
  → 이 줄을 만든 그 세션에서 에이전트가 뭘 하고 있었는지

[정리] 민감하거나 불필요한 메모리 삭제
  > /forget   (특정 관찰·세션 제거)
```

:bulb: 핵심은 "**평소엔 자동, 결정적 순간에만 수동**"이다. `/remember`로 못 박은 것과 훅의 자동 캡처가 합쳐져, 다음 세션의 `/handoff`·`/recall`이 더 풍부해진다.
{: .notice--info}

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
