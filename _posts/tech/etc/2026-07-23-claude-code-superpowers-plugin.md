---
title: "Claude Code Superpowers 플러그인 — 무엇·왜·설치/삭제·사용법·예제"
description: "Claude Code용 Superpowers 플러그인 소개. 브레인스토밍·계획·TDD·체계적 디버깅 스킬을 강제하는 워크플로우 프레임워크의 필요성, 설치/삭제, slash 명령, 실제 사용 예까지 정리"
excerpt: "코드부터 쓰기 전에 설계·계획·TDD를 강제하는 Claude Code Superpowers — 설치부터 brainstorm/write-plan/execute-plan 사용 예까지"
date: 2026-07-23
categories: Etc
tags: [Claude Code, Superpowers, plugin, 플러그인, skills, TDD, brainstorm, write-plan, execute-plan, obra, AI-coding-agent, marketplace]
ref: claude-code-superpowers-plugin
---

:bulb: Claude Code는 기본 상태에서도 코드를 잘 쓰지만, **계획·테스트·검증을 건너뛰고 바로 구현**하는 경우가 많다. [Superpowers](https://github.com/obra/superpowers)는 그 습관을 막고, 브레인스토밍 → 설계 → 구현 계획 → TDD 실행 → 리뷰까지 **체계적 개발 워크플로우**를 스킬로 강제하는 Claude Code 플러그인이다.
{: .notice--info}

:memo: 공식 저장소는 [obra/superpowers](https://github.com/obra/superpowers)이며, Anthropic 공식 마켓플레이스와 제작자 마켓플레이스(`obra/superpowers-marketplace`) 양쪽에서 설치할 수 있다. Claude Code뿐 아니라 Cursor, Codex, OpenCode 등 여러 에이전트에서도 지원한다. 이 글은 **Claude Code** 기준이다.
{: .notice--warning}

**환경**: Claude Code (플러그인 마켓플레이스 `/plugin` 지원 버전) / 인터넷 연결

---

# [01] 어떤 플러그인인가

Superpowers는 Jesse Vincent / [Prime Radiant](https://primeradiant.com)가 만든 **에이전트용 소프트웨어 개발 방법론 + 조합 가능한 스킬 라이브러리**다.

설치하면 Claude Code에 다음이 들어온다.

| 구성 | 내용 |
|------|------|
| Skills | brainstorming, TDD, systematic-debugging, writing-plans 등 |
| Commands | `/superpowers:brainstorm`, `write-plan`, `execute-plan` 등 |
| Agents | code-reviewer 등 사전 구성된 서브에이전트 |
| Hooks | 세션 시작 시 워크플로우 부트스트랩, 컨텍스트에 맞는 스킬 자동 활성화 |

핵심은 "제안"이 아니라 **필수 워크플로우**에 가깝다는 점이다. 에이전트는 작업 전에 관련 스킬이 있는지 확인하고, 해당되면 그 절차를 따른다.

## 1-1. 기본 워크플로우

1. **brainstorming** — 코드 작성 전, 질문으로 요구를 구체화하고 설계를 섹션 단위로 검증
2. **using-git-worktrees** — 설계 승인 후 격리된 브랜치/워크트리 준비
3. **writing-plans** — 2~5분 단위 태스크로 쪼갠 구현 계획(파일 경로·검증 단계 포함)
4. **subagent-driven-development** / **executing-plans** — 태스크별 서브에이전트 또는 배치 실행 + 체크포인트
5. **test-driven-development** — RED → GREEN → REFACTOR 강제
6. **requesting-code-review** — 계획 대비 리뷰, Critical이면 진행 차단
7. **finishing-a-development-branch** — 테스트 확인 후 merge / PR / keep / discard 선택

---

# [02] 왜 필요한가

Claude Code의 흔한 실패 모드는 다음과 같다.

- 기능 요청 직후 **설계·범위 합의 없이** 파일을 고치기 시작
- 마이그레이션·대규모 리팩터에서 **누락 파일** 발생
- "고친 것 같다"고 말하고 **검증 명령을 안 돌림**
- 디버깅 시 원인 조사 없이 **추측성 패치**를 반복

Superpowers는 이 지점에서 스킬을 끼워 넣어 **건너뛰기를 어렵게** 만든다.

```text
요청만 했을 때 (기본 Claude Code)
  "로그인에 rate limit 추가해줘"
  → 곧바로 middleware 수정 시도
  → 테스트/엣지케이스/기존 인증 흐름 누락 가능

Superpowers가 있을 때
  → brainstorming: 한도·저장소·응답 형식·기존 스택 질문
  → writing-plans: 파일별 태스크 + 검증 커맨드
  → TDD: 실패 테스트 먼저
  → verification-before-completion: 통과 증거 후 "완료" 선언
```

철학은 네 가지로 요약된다.

- **Test-Driven Development** — 테스트 먼저
- **Systematic over ad-hoc** — 추측보다 절차
- **Complexity reduction** — YAGNI, 단순함 우선
- **Evidence over claims** — 성공 주장 전 검증

---

# [03] 설치

Claude Code **세션 안**에서 slash 명령으로 설치한다. npm 패키지가 아니다.

## 3-1. 공식 마켓플레이스 (간단)

```text
/plugin install superpowers@claude-plugins-official
```

[Anthropic 공식 플러그인 페이지](https://claude.com/plugins/superpowers)에도 등록되어 있다.

## 3-2. Superpowers 마켓플레이스 (제작자 쪽, 관련 플러그인 포함)

```text
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

둘 중 하나만 쓰면 된다. 코어 플러그인은 같다.

## 3-3. UI로 설치

```text
/plugin
```

메뉴에서 **Discover** → `superpowers` 검색 → 설치해도 된다.

## 3-4. 설치 확인

설치 후 **새 세션**을 열고 확인한다. 스킬은 세션 시작 시 로드된다.

```text
/plugin list
```

또는 자연어로:

```text
Do you have superpowers?
```

에이전트가 Superpowers 설치 여부와 사용 가능한 스킬을 답하면 정상이다. 세션 시작 훅이 성공하면 `SessionStart:startup hook succeeded` 같은 메시지를 볼 수 있다.

## 3-5. 업데이트

```text
/plugin update superpowers
```

---

# [04] 삭제

플러그인만 제거:

```text
/plugin uninstall superpowers
```

제작자 마켓플레이스까지 제거:

```text
/plugin marketplace remove obra/superpowers-marketplace
```

공식 마켓(`claude-plugins-official`)은 Claude Code 기본 마켓이므로, Superpowers만 지울 때는 `uninstall`만으로 충분하다.

---

# [05] 사용 방법

## 5-1. 자동 활성화 (기본)

별도 설정 없이, 요청 내용에 맞는 스킬이 **자동으로** 걸린다.

| 말했을 때 | 대략 활성화되는 스킬 |
|-----------|----------------------|
| "새 인증 기능 설계해줘" | brainstorming |
| "이 함수가 간헐적으로 크래시나" | systematic-debugging |
| "최근 변경 리뷰해줘" | requesting-code-review |
| 구현 단계 | test-driven-development |
| "다 됐어" / 완료 주장 | verification-before-completion |

명시적으로 스킬을 부르려면:

```text
use brainstorming skill
use systematic-debugging skill
```

## 5-2. Slash 명령 (명시적 워크플로우)

복잡한 기능·마이그레이션에서는 명령을 직접 치는 편이 안정적이다.

| 명령 | 역할 |
|------|------|
| `/superpowers:brainstorm` | 아이디어를 설계로 정제 (코드 전) |
| `/superpowers:write-plan` | 구현 계획 문서 작성 (짧은 태스크 단위) |
| `/superpowers:execute-plan` | 계획 배치 실행 + 리뷰 체크포인트 |

권장 순서:

```text
1. /superpowers:brainstorm
2. 설계 승인
3. /superpowers:write-plan
4. 계획 확인
5. /superpowers:execute-plan
```

## 5-3. 스킬 라이브러리 요약

**Testing / Debugging**

- `test-driven-development` — RED-GREEN-REFACTOR
- `systematic-debugging` — 4단계 원인 분석
- `verification-before-completion` — 증거 없는 완료 금지

**Collaboration**

- `brainstorming`, `writing-plans`, `executing-plans`
- `subagent-driven-development`, `dispatching-parallel-agents`
- `requesting-code-review`, `receiving-code-review`
- `using-git-worktrees`, `finishing-a-development-branch`

**Meta**

- `using-superpowers` — 스킬 시스템 소개
- `writing-skills` — 커스텀 스킬 작성

---

# [06] 사용 예

## 6-1. 새 기능 — brainstorm → plan → execute

```text
/superpowers:brainstorm
REST API에 사용자별 API rate limit을 넣고 싶어.
Redis 기반이면 좋겠고, 초과 시 429를 줘.
```

예상 동작:

1. 한도(분당/시간당), 키 설계, 기존 인증과의 관계, 예외 경로 등을 **질문**
2. 설계를 짧은 섹션으로 제시 → 사용자 승인
3. `/superpowers:write-plan`으로 파일 단위 태스크 + 테스트/검증 커맨드 작성
4. `/superpowers:execute-plan`으로 태스크별 실행, Critical 이슈 시 중단

## 6-2. 버그 — systematic debugging

```text
결제 웹훅 핸들러가 가끔 타임아웃 나.
use systematic-debugging skill
```

에이전트는 바로 `setTimeout`을 늘리기보다, 재현 조건 → 로그/트레이스 → 가설 → 최소 수정 → 검증 순서를 따른다.

## 6-3. 대규모 변경 — write-plan만 먼저

```text
/superpowers:write-plan
Next.js에서 cacheComponents를 켜려면 어떤 파일을 고쳐야 하는지
단계별 계획과 각 단계 검증 커맨드를 만들어줘.
```

결과물은 "대충 이런 식으로"가 아니라 **파일 경로·Before/After 패턴·성공 기준·롤백**이 들어간 계획에 가깝다. 계획이 파일로 남으면 세션이 잘려도 이어서 실행하기 쉽다.

## 6-4. 완료 전 검증

```text
rate limit 구현 끝났어. 완료해도 돼?
```

`verification-before-completion`이 걸리면, 관련 테스트/빌드/수동 검증 명령을 **실제로 돌린 결과**를 보여 주기 전에는 "완료"라고 단정하지 않는다.

---

# [07] 문제 해결

| 증상 | 대응 |
|------|------|
| `/plugin` 인식 안 됨 | `npm update -g @anthropic-ai/claude-code` 후 재시작 |
| 마켓 등록 실패 | 네트워크 확인, `obra/superpowers-marketplace` 철자 확인 후 remove → 재등록 |
| 설치 실패 | 마켓 등록 여부 확인, `superpowers@...` 전체 이름 지정 |
| 스킬이 안 뜸 | **새 세션** 시작, `/plugin list`로 활성 확인, `/plugin update superpowers` |
| 자동 스킬이 안 걸림 | `"use brainstorming skill"`처럼 명시 호출 |

텔레메트리(선택)를 끄려면:

```bash
export SUPERPOWERS_DISABLE_TELEMETRY=1
# 또는 Claude Code의 DISABLE_TELEMETRY /
# CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC 도 존중됨
```

---

# [08] 정리

| 항목 | 내용 |
|------|------|
| 무엇인가 | Claude Code용 체계적 개발 스킬/워크플로우 플러그인 |
| 왜 | 바로 코딩하는 습관 → 설계·TDD·검증으로 유도 |
| 설치 | `/plugin install superpowers@claude-plugins-official` |
| 삭제 | `/plugin uninstall superpowers` |
| 핵심 사용 | brainstorm → write-plan → execute-plan, 또는 자동 스킬 |
| 참고 | [GitHub](https://github.com/obra/superpowers) · [설치 문서](https://obra-superpowers.mintlify.app/installation/claude-code) |

작은 원라이너 수정에는 과할 수 있다. **새 기능, 마이그레이션, 원인 불명 버그, 멀티 파일 리팩터**처럼 "바로 짜면 사고 나는" 작업에서 진가를 발휘한다.
