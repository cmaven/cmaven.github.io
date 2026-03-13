---
title: "Claude Code 완벽 가이드: Skill, Hook, CLAUDE.md로 코딩 워크플로우 자동화하기"
date: 2026-03-13
categories: Claude
tags: [Claude Code, Skill, Hook, CLAUDE.md, Agent]
---

:bulb: Claude Code로 개발할 때, 대화로 전달한 규칙이 컨텍스트에서 밀려나는 문제를 CLAUDE.md, Skill, Hook 세 가지 레이어로 해결하는 방법을 작성한다.
{: .notice--info}

# [01] 왜 필요한가?

Claude Code로 코딩할 때 이런 문제를 겪어본 적이 있을 것이다:

- Claude가 파일을 만들었는데, 나중에 뭐하는 파일인지 모르겠다
- 긴 대화 중 Claude가 초반에 했던 작업을 까먹는다
- 여러 agent가 같은 파일을 수정해서 충돌이 난다
- "주석 꼭 넣어줘"라고 말했는데, 3번째 파일부터 안 넣는다

이 문제들의 공통 원인은 하나다: **Claude에게 "규칙"을 대화로만 전달하기 때문이다.**

대화로 전달한 규칙은 컨텍스트 윈도우에서 밀려나면 사라진다.
이를 해결하는 것이 CLAUDE.md, Skill, Hook 세 가지 레이어다.

---

# [02] 3가지 레이어 이해하기

```
+-----------------------------------------------------+
|  CLAUDE.md  ->  "이 프로젝트가 뭔지" (컨텍스트)      |
|               세션 시작 시 자동 로드                   |
|               프로젝트별로 다름                        |
+-----------------------------------------------------+
|  Skill      ->  "이렇게 해주세요" (상세 지침)         |
|               트리거 키워드 매칭 시 로드                |
|               프로젝트 간 재사용 가능                   |
+-----------------------------------------------------+
|  Hook       ->  "이건 반드시 실행됩니다" (강제)        |
|               이벤트 발생 시 100% 실행                 |
|               셸 스크립트로 자동화                      |
+-----------------------------------------------------+
```

**핵심 차이:**

| 특성 | CLAUDE.md | Skill | Hook |
|---|---|---|---|
| 실행 보장 | 제안 수준 | 자동 트리거 불안정 | 100% 실행 |
| 유연성 | 자유 형식 | 복잡한 워크플로우 | 단일 명령 |
| 설정 난이도 | 매우 쉬움 | 쉬움 | 중간 |
| 적용 범위 | 해당 프로젝트 | 글로벌 or 프로젝트 | 글로벌 or 프로젝트 |

---

# [03] claude.ai 웹 vs Claude Code - 환경별 기능 차이

이 가이드에서 설명하는 CLAUDE.md, Skill, Hook은 **모든 환경에서 동일하게 작동하지 않는다.** 이 차이를 모르면 "왜 안 되지?" 하며 시간을 낭비하게 된다.

## 3-1. 환경별 기능 지원 현황

| 기능 | claude.ai (웹/앱) | Claude Code (CLI) |
|---|---|---|
| CLAUDE.md | X 사용 불가 | O 세션 시작 시 자동 로드 |
| Skill | O 업로드 가능 | O 폴더 복사로 설치 |
| Hook | X 사용 불가 | O 12가지 이벤트 |
| 슬래시 명령 (/skill) | X 없음 | O 지원 |
| 디버그 모드 | X 없음 | O `claude --debug` |
| 서브에이전트 | 제한적 | O `agents/` 활용 가능 |

## 3-2. claude.ai 웹에서 할 수 있는 것

Skill **하나만** 작동한다. 그것도 제약이 있다:

- `Customize > Skills` 에서 `.zip` 또는 `.skill` 파일을 업로드
- Claude가 대화 중 관련 작업을 감지하면 스킬을 자동 참조
- 하위 파일(`references/`, `scripts/`)은 Claude가 코드 실행 환경에서 접근 가능하지만, Hook처럼 "자동 실행"되지는 않음

## 3-3. Claude Code에서 할 수 있는 것

**3가지 레이어 전부** 작동한다:

- CLAUDE.md -> 세션 시작 시 자동 로드
- Skill -> 자동 트리거 + `/skill-name` 슬래시 명령
- Hook -> 이벤트 발생 시 100% 실행 (셸 명령, 프롬프트, 에이전트)
- 서브에이전트 -> `agents/` 디렉토리의 지침에 따라 독립 실행
- 디버그 -> `claude --debug`로 스킬 로딩, Hook 실행 실시간 확인

## 3-4. 스킬 업로드용 zip 구조가 다르다

이것이 가장 자주 겪는 실수다. **claude.ai 웹과 Claude Code는 zip 구조가 다르다.**

**claude.ai 웹 업로드용** - SKILL.md가 최상위 폴더 바로 아래:

```
coding-workflow.zip
└── coding-workflow/       <- 최상위 폴더
    ├── SKILL.md           <- 여기!
    ├── agents/
    ├── references/
    └── scripts/
```

**Claude Code 프로젝트용** - 프로젝트 설정 파일 전체:

```
fullstack-claude-setup.zip
├── CLAUDE.md              <- 프로젝트 루트
└── .claude/               <- 설정 폴더
    ├── settings.json      <- Hook 설정
    └── skills/
        └── coding-workflow/
            ├── SKILL.md
            ├── agents/
            └── ...
```

:warning: 웹에서 프로젝트용 zip을 올리면 "SKILL.md must be in the top-level folder" 에러가 난다. 반드시 용도에 맞는 zip을 사용해야 한다.
{: .notice--warning}

## 3-5. 어떤 환경을 쓸지 결정하는 기준

| 상황 | 추천 환경 |
|---|---|
| 대화하면서 가벼운 코딩 | claude.ai 웹 + Skill만 |
| 본격적인 프로젝트 개발 | Claude Code + 3가지 전부 |
| 팀으로 agent 구성 | Claude Code + 프로젝트 레벨 설치 |

---

# [04] CLAUDE.md - 프로젝트 컨텍스트

## 4-1. 역할

Claude Code는 세션 시작 시 프로젝트 루트의 `CLAUDE.md`를 자동으로 읽는다. 여기에 프로젝트의 맥락을 적어두면 Claude가 "이 프로젝트가 뭔지"를 매 세션마다 이해한다.

## 4-2. 무엇을 적어야 하나

```markdown
# CLAUDE.md

## 프로젝트 개요
- 이름, 유형, 기술 스택

## 디렉토리 구조
- 주요 폴더와 역할 설명

## 핵심 규칙
- 파일 주석 작성 규칙
- Git 브랜치/커밋 규칙
- 코드 스타일 규칙

## 환경 변수
- .env.example 내용

## 자주 쓰는 명령어
- 개발 서버 실행, 테스트, 빌드 등

## Agent 팀 구성 (해당 시)
- 각 agent의 역할과 담당 브랜치
```

## 4-3. 핵심 포인트

- **프로젝트마다 다르다.** React 프로젝트와 FastAPI 프로젝트의 CLAUDE.md는 내용이 다르다.
- **간결하게 쓴다.** 상세한 워크플로우는 Skill에, CLAUDE.md에는 요약만 적는다.
- **Skill을 가리킨다.** "상세 규칙은 `.claude/skills/coding-workflow/SKILL.md`를 참조하라" 식으로.

---

# [05] Skill - 상세 워크플로우 정의

## 5-1. 역할

Skill은 Claude에게 "특정 작업을 이런 방식으로 해라"라는 상세 지침을 담는 패키지다. YAML frontmatter(`name` + `description`)가 있는 `SKILL.md` 파일이 핵심이다.

## 5-2. 기본 구조

가장 단순한 스킬:

```
coding-workflow/
└── SKILL.md
```

고급 스킬 (하위 파일 포함):

```
coding-workflow/
├── SKILL.md              <- 핵심 규칙 + 하위 파일 참조 포인터
├── agents/               <- 서브에이전트 지침 (필요 시 로드)
│   └── code-reviewer.md
├── references/           <- 상세 문서 (필요 시 로드)
│   ├── annotation-formats.md
│   ├── git-cheatsheet.md
│   ├── work-log-template.md
│   └── diagram-templates.md
└── scripts/              <- 실행 가능 코드 (Hook이 호출)
    ├── check-annotation.sh
    └── auto-commit.sh
```

## 5-3. Progressive Disclosure (3단계 로딩)

이것이 Skill의 핵심 설계 원리다. Claude가 모든 파일을 한 번에 읽지 않는다:

| Level | 대상 | 로드 시점 | 토큰 |
|---|---|---|---|
| Level 1 | `name` + `description` (메타데이터) | 항상 로드 | ~100 |
| Level 2 | `SKILL.md` 본문 (핵심 지침) | 트리거 시 로드 | ~5K |
| Level 3 | `agents/`, `references/`, `scripts/` | 필요 시만 로드 | 무제한 |

## 5-4. SKILL.md frontmatter 작성법

```yaml
---
name: coding-workflow
description: >
  코딩 프로젝트에서 Claude agent가 따라야 할 핵심 워크플로우 컨벤션.
  파일 생성/수정 시 주석 명시, git 브랜치 관리 및 커밋 추적,
  작업 내역 메모리 덤프(.md)를 자동으로 수행한다.
  이 스킬은 코드를 작성하거나, 파일을 생성/수정/삭제하거나,
  프로젝트 구조를 변경하는 모든 코딩 작업에서 트리거되어야 한다.
---
```

:bulb: `description`을 구체적이고 "약간 공격적으로" 쓰는 것이 좋다. Claude는 스킬을 "언더트리거"하는 경향이 있기 때문이다.
{: .notice--info}

## 5-5. SKILL.md에서 하위 파일을 참조하는 방법

SKILL.md 안에 이렇게 적는다:

```markdown
## Reference Files

필요한 시점에 아래 파일을 읽어서 상세 지침을 따른다:

- `references/annotation-formats.md` - 언어별 파일 주석 포맷 상세
- `references/git-cheatsheet.md` - Git 명령어 및 컨벤션 요약
- `agents/code-reviewer.md` - 코드 리뷰 서브에이전트 지침
```

Claude는 이 지시를 읽고, 해당 작업을 할 때 필요한 파일만 선택적으로 로드한다. 컨텍스트 윈도우를 낭비하지 않으면서 풍부한 지침을 제공할 수 있다.

## 5-6. 스킬 설치 위치

| 위치 | 적용 범위 | 팀 공유 |
|---|---|---|
| `~/.claude/skills/` | 모든 프로젝트 (글로벌) | X (각자 설치) |
| `프로젝트/.claude/skills/` | 해당 프로젝트만 | O (git에 포함) |

**추천**: 글로벌 + 프로젝트 병행

```shell
# 스킬은 글로벌로 한 번만 설치
cp -r coding-workflow ~/.claude/skills/coding-workflow

# 팀 공유가 필요한 프로젝트에는 프로젝트 레벨에도 배치
cp -r coding-workflow my-project/.claude/skills/coding-workflow
```

---

# [06] Hook - 규칙의 강제 실행

## 6-1. Skill과 Hook의 본질적 차이

```
Skill의 지시  = "주석을 넣어주세요"       -> Claude가 판단해서 할 수도, 안 할 수도
Hook의 명령   = "파일 저장 후 주석 검사"   -> 무조건 실행, 100%
```

Git의 pre-commit hook을 떠올리면 된다. 특정 이벤트가 발생하면 지정된 명령이 자동으로 실행된다.

## 6-2. 주요 Hook 이벤트

| 이벤트 | 발생 시점 | 주요 용도 |
|---|---|---|
| `SessionStart` | 세션 시작 | 환경 세팅, 컨텍스트 로드 |
| `UserPromptSubmit` | 프롬프트 제출 직전 | 스킬 규칙 주입, 프롬프트 검증 |
| `PreToolUse` | 도구 실행 직전 | 위험 작업 차단 (차단 가능!) |
| `PostToolUse` | 도구 실행 완료 후 | 린트, 포맷팅, 주석 검사 |
| `Stop` | Claude 응답 완료 | 자동 커밋, 작업 로그 |
| `SubagentStop` | 서브에이전트 완료 | 서브에이전트 결과 검증 |
| `Notification` | 알림 발생 | Slack/메일 알림 연동 |
| `PreCompact` | 컨텍스트 압축 직전 | 대화 백업 |

## 6-3. 3가지 핸들러 타입

| 타입 | 방식 | 용도 |
|---|---|---|
| `command` | 셸 명령 실행 | 린팅, 파일 체크, git 명령 |
| `prompt` | Claude에 프롬프트 전송 | 의미 기반 판단 ("이 코드에 보안 문제 있어?") |
| `agent` | 서브에이전트 생성 | 심층 검증 (도구 접근 가능) |

## 6-4. Hook 설정 파일 위치

| 위치 | 적용 범위 |
|---|---|
| `~/.claude/settings.json` | 모든 프로젝트 (글로벌) |
| `프로젝트/.claude/settings.json` | 해당 프로젝트 + 팀 공유 (git) |
| `프로젝트/.claude/settings.local.json` | 해당 프로젝트 + 개인만 |

## 6-5. 실전 Hook 예시

### (A) UserPromptSubmit - 매 요청마다 스킬 규칙 상기

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo 'INSTRUCTION: coding-workflow 스킬 규칙을 따르세요. (1) 파일 상단 주석 (2) claude-bot 브랜치 (3) conventional commits (4) WORK_LOG.md 덤프'"
          }
        ]
      }
    ]
  }
}
```

### (B) PostToolUse - 파일 편집 후 주석 존재 검사

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/skills/coding-workflow/scripts/check-annotation.sh"
          }
        ]
      }
    ]
  }
}
```

`matcher`는 정규표현식이다. `Edit|Write|MultiEdit`는 "파일 편집 또는 쓰기 도구가 실행됐을 때"를 의미한다.

### (C) PreToolUse - 민감 파일 수정 차단

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'INPUT=$(cat); FILE=$(echo \"$INPUT\" | jq -r \".tool_input.file_path // empty\"); if [[ \"$FILE\" =~ \\.(env|secret|pem|key)$ ]]; then echo \"{\\\"hookSpecificOutput\\\":{\\\"hookEventName\\\":\\\"PreToolUse\\\",\\\"permissionDecision\\\":\\\"deny\\\",\\\"permissionDecisionReason\\\":\\\"민감 파일 수정 차단\\\"}}\"; fi'"
          }
        ]
      }
    ]
  }
}
```

:bulb: `PreToolUse`는 JSON으로 `permissionDecision: "deny"`를 반환하면 해당 작업을 **차단**할 수 있다.
{: .notice--info}

### (D) Stop - 작업 완료 시 자동 커밋

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/skills/coding-workflow/scripts/auto-commit.sh"
          }
        ]
      }
    ]
  }
}
```

## 6-6. Hook 생성 방법

### (A) /hooks 명령 (GUI, 가장 쉬움)

```
Claude Code 세션 내에서 /hooks 입력
-> 인터랙티브 UI에서 이벤트 선택 -> matcher 입력 -> 명령어 등록
```

### (B) settings.json 직접 편집

위의 JSON 예시를 `.claude/settings.json` 파일에 작성한다.

---

# [07] 3가지 레이어 최적 조합

```
CLAUDE.md     -> 프로젝트 컨텍스트 + 핵심 규칙 요약
                "이 프로젝트는 React + Express야, 이런 규칙을 따라"

Skill         -> 상세 워크플로우 + 예시 + 템플릿 + 서브에이전트
                "주석은 이런 포맷으로, 커밋은 이런 형식으로"

Hook          -> 규칙의 강제 실행 + 자동 검증
                "파일 저장하면 주석 검사 실행, 작업 끝나면 자동 커밋"
```

왜 3가지 다 필요한가?

- **CLAUDE.md만** 쓰면: 긴 대화에서 규칙이 밀려남
- **Skill만** 쓰면: 자동 트리거가 불안정 (50% 정도)
- **Hook만** 쓰면: 셸 명령만으로는 복잡한 워크플로우 표현 불가
- **3가지를 조합하면**: CLAUDE.md가 맥락을 잡고, Skill이 상세 지침을 제공하고, Hook이 강제로 실행

---

# [08] 프로젝트에 적용하는 방법 (step by step)

## 8-1. 프로젝트별 설치 (팀 공유 가능)

```shell
# 1. 프로젝트로 이동
cd ~/my-web-app

# 2. fullstack-claude-setup.zip을 프로젝트 루트에서 풀기
unzip fullstack-claude-setup.zip

# 3. 스크립트 실행 권한 부여
chmod +x .claude/skills/coding-workflow/scripts/*.sh

# 4. CLAUDE.md를 실제 프로젝트에 맞게 수정
nano CLAUDE.md

# 5. git에 추가 (팀원과 공유)
git add CLAUDE.md .claude/
git commit -m "chore: Claude Code 워크플로우 설정 추가"
```

결과 디렉토리:

```
my-web-app/
├── CLAUDE.md                           <- 수정한 프로젝트 컨텍스트
├── .claude/
│   ├── settings.json                   <- Hook 4개
│   └── skills/coding-workflow/
│       ├── SKILL.md                    <- 4가지 규칙
│       ├── agents/code-reviewer.md
│       ├── references/ (4개 파일)
│       └── scripts/ (2개 셸스크립트)
├── frontend/
├── backend/
└── ...
```

## 8-2. 글로벌 설치 (모든 프로젝트에 자동 적용)

```shell
# 1. 스킬을 글로벌로 설치 (한 번만)
mkdir -p ~/.claude/skills
cp -r coding-workflow ~/.claude/skills/coding-workflow
chmod +x ~/.claude/skills/coding-workflow/scripts/*.sh

# 2. Hook을 글로벌 settings.json에 추가 (한 번만)
# ~/.claude/settings.json에 Hook JSON 작성

# 3. 이후 각 프로젝트에는 CLAUDE.md만 작성
cd ~/project-a && nano CLAUDE.md
cd ~/project-b && nano CLAUDE.md
```

## 8-3. 추천 전략

| 설치 위치 | 대상 | 비고 |
|---|---|---|
| 글로벌 (`~/.claude/`) | Skill + Hook | 한 번 설치, 모든 프로젝트 공유 |
| 프로젝트별 (`my-app/`) | CLAUDE.md | 프로젝트마다 다른 내용 |

혼자 작업하면 글로벌이 편하고, 팀 작업이면 프로젝트 레벨로 git에 포함시키는 게 좋다.

---

# [09] 적용 확인 방법

## 9-1. claude.ai (웹/앱)

```
Settings > Capabilities > Code execution 활성화 확인
Customize > Skills > 목록에서 토글 ON 확인
```

## 9-2. Claude Code (CLI)

```shell
# 디버그 모드 - 스킬 로딩, Hook 실행 실시간 확인
claude --debug

# 세션 내에서 Hook 목록 확인
/hooks

# 슬래시 명령으로 스킬 직접 호출
/coding-workflow

# 파일 존재 확인
ls ~/.claude/skills/coding-workflow/SKILL.md
```

## 9-3. 실제 동작 테스트

Claude Code 세션에서 "간단한 함수 하나 만들어줘"라고 요청해본다. 제대로 적용되었다면:

1. `claude-bot` 브랜치를 체크아웃하거나 생성한다
2. 파일 상단에 역할 설명 주석을 넣는다
3. conventional commit 형식으로 커밋한다
4. 응답이 끝나면 Hook이 자동으로 주석 검사/커밋을 실행한다

## 9-4. 스킬이 트리거되지 않을 때

| 증상 | 해결책 |
|---|---|
| 스킬 자체가 안 보임 | 파일 경로와 `SKILL.md` 존재 확인 |
| 보이지만 자동 트리거 안 됨 | `description`의 키워드를 더 구체적으로 수정 |
| 간헐적으로만 작동 | Hook의 `UserPromptSubmit`으로 강제 상기 |
| 슬래시 명령도 안 됨 | frontmatter의 `name` 필드 확인 |

---

# [10] Skill의 고급 구조: Progressive Disclosure

## 10-1. 단순 스킬 vs 고급 스킬

**단순 (SKILL.md만)**:
규칙 전달 중심. "이렇게 해주세요"를 적어두면 Claude가 읽고 따른다.

**고급 (하위 디렉토리 포함)**:
SKILL.md가 지휘관이 되고, 하위 파일을 필요 시점에 참조한다.

```
coding-workflow/
├── SKILL.md          <- Level 2: 핵심 규칙 + "언제 무엇을 읽을지" 포인터
├── agents/           <- Level 3: 서브에이전트 지침 (코드 리뷰 등)
├── references/       <- Level 3: 상세 문서 (주석 포맷, Git 명령어 등)
├── scripts/          <- Level 3: 실행 가능 코드 (Hook이 호출)
└── assets/           <- Level 3: 템플릿, 아이콘 등 정적 리소스
```

## 10-2. 각 디렉토리의 역할

| 디렉토리 | 역할 | 로드 시점 |
|---|---|---|
| `agents/` | 서브에이전트에게 위임할 작업의 지침서 | 리뷰/분석 등 특정 작업 시 |
| `references/` | 컨텍스트에 로드되는 참조 문서 | SKILL.md가 지시할 때 |
| `scripts/` | 직접 실행하는 셸/파이썬 스크립트 | Hook이 호출하거나 Claude가 실행 |
| `assets/` | HTML 템플릿, 정적 파일 | 출력물 생성 시 |

---

# [11] Agent Team 협업 가이드

Ubuntu 22.04 + Claude Code 환경에서 여러 agent를 팀으로 구성할 때의 가이드다.

## 11-1. 추천 팀 구조

```
Orchestrator (작업 분배, 리뷰, 통합)
├── Frontend Agent  -> claude-bot/frontend
├── Backend Agent   -> claude-bot/backend
└── DevOps Agent    -> claude-bot/devops
```

## 11-2. 협업 규칙

1. **각 agent는 자기 브랜치에서 작업한다** (`claude-bot/<역할>`)
2. **WORK_LOG.md를 공유 매체로 사용한다** - 작업 전에 읽고, 작업 후에 쓴다
3. **agent 식별자를 명시한다** - `[frontend-agent]` 등
4. **충돌 가능 파일은 "수정 중" 표시** - WORK_LOG.md에 기재
5. **Orchestrator가 머지** - 주기적으로 브랜치 통합

## 11-3. 프로젝트 레벨 설치의 장점

`.claude/` 폴더를 git에 포함하면:

```shell
git add .claude/ CLAUDE.md
git commit -m "chore: Claude 워크플로우 설정 추가"
```

어떤 agent가 이 프로젝트를 열든 **동일한 Skill + Hook**이 자동 적용된다.

---

# [12] 자주 묻는 질문 (FAQ)

## Q: CLAUDE.md는 프로젝트마다 복사해야 하나?

네. CLAUDE.md는 프로젝트별 컨텍스트(기술 스택, 디렉토리 구조 등)를 담기 때문에 프로젝트마다 내용이 다르다. 하지만 Skill과 Hook은 글로벌로 한 번 설치하면 모든 프로젝트에서 공유 가능하다.

## Q: Skill이 자동으로 트리거되지 않는다면?

현실적으로 Skill의 자동 트리거는 100% 신뢰할 수 없다. 이것이 Hook과 함께 쓰는 이유다. `UserPromptSubmit` Hook으로 매 요청마다 스킬 규칙을 상기시킨다.

## Q: 코드 완료 후 구조도를 자동으로 만들려면?

세 가지 방법이 있다:

| Level | 방법 | 특징 |
|---|---|---|
| Level 1 | "아키텍처 다이어그램 그려줘" 요청 | 별도 설정 불필요 |
| Level 2 | Skill에 다이어그램 규칙 명시 | 일관된 출력 |
| Level 3 | Stop Hook에 prompt 타입으로 추가 | 완전 자동화 |

## Q: claude.ai (웹)에서도 같은 방식으로 적용되나?

**아니다. 큰 차이가 있다.** claude.ai 웹에서는 Skill만 사용 가능하고, Hook과 CLAUDE.md는 Claude Code(CLI) 전용이다. 상세 비교는 [03] 섹션을 참조.

```
claude.ai 웹:  Skill만 O (Hook X, CLAUDE.md X)
Claude Code:   Skill O + Hook O + CLAUDE.md O (전부 가능)
```

## Q: claude.ai 웹에 업로드할 때 zip 에러가 나는데?

"SKILL.md must be in the top-level folder" 에러는 zip 구조가 맞지 않기 때문이다. claude.ai 웹에서 요구하는 구조는 SKILL.md가 최상위 폴더 바로 아래에 있어야 한다:

```
## 올바른 구조 (coding-workflow-for-web.zip):
coding-workflow/
├── SKILL.md          <- 여기 (최상위 폴더 바로 아래)
├── agents/
└── references/

## 틀린 구조 (fullstack-claude-setup.zip):
.claude/skills/coding-workflow/
└── SKILL.md          <- 너무 깊음
```

`fullstack-claude-setup.zip`은 Claude Code 프로젝트 설치용이지, 웹 업로드용이 아니다. 웹에는 별도의 `coding-workflow-for-web.zip`을 사용해야 한다.

## Q: Skill은 claude.ai용과 Claude Code용이 다른가?

SKILL.md 파일 형식은 동일하다. 하지만 **패키징 방식과 기능 범위가 다르다**:

| 항목 | claude.ai 웹 | Claude Code |
|---|---|---|
| 설치 | zip 업로드 (Customize > Skills) | 폴더 복사 (`~/.claude/skills/`) |
| zip 구조 | SKILL.md가 최상위 | `.claude/skills/` 하위 |
| 자동 트리거 | O (description 기반) | O + 슬래시 명령 |
| Hook 연동 | X 불가 | O `scripts/`를 Hook이 호출 |
| `agents/` | 제한적 (서브에이전트 제약) | O 완전 지원 |
| 디버그 | X | O `claude --debug` |

## Q: zip 파일 두 개를 다 보관해야 하나?

Claude Code를 쓸 예정이면 글로벌 설치 후 둘 다 삭제 가능:

```shell
# 글로벌 설치 (한 번만)
cp -r coding-workflow ~/.claude/skills/coding-workflow
# ~/.claude/settings.json에 Hook 추가
# -> 이후 zip 삭제 가능, 새 프로젝트에는 CLAUDE.md만 작성
```

claude.ai 웹만 쓰면 `coding-workflow-for-web.zip`을 업로드하면 되고, 업로드 후 zip은 삭제해도 된다.

---

# [부록 A] coding-workflow 스킬의 4가지 규칙

| 규칙 | 내용 |
|---|---|
| Rule 1: 파일 주석 | 모든 파일 상단에 언어별 포맷으로 역할 설명 주석 작성 |
| Rule 2: Git 관리 | claude-bot 브랜치에서 작업, Conventional Commits 형식 커밋 |
| Rule 3: 메모리 덤프 | 긴 작업 시 `.claude/WORK_LOG.md`에 변경 내역 기록 (append only) |
| Rule 4: 구조도 생성 | 아키텍처/API 변경 시 `.claude/diagrams/`에 Mermaid 다이어그램 업데이트 |

---

# [부록 B] 제공 파일 목록

| 파일 | 용도 | 적용 환경 |
|---|---|---|
| `coding-workflow-for-web.zip` | Skill 업로드 | claude.ai 웹 |
| `fullstack-claude-setup.zip` | 프로젝트 전체 설정 | Claude Code |
| `claude-skill-hook-guide.md` | 이 블로그 포스트 | 참조용 |
