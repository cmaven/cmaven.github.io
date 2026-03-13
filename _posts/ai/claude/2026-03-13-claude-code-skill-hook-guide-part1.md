---
title: "Claude Code 완벽 가이드 (1부): CLAUDE.md, Skill, Hook 이해하기"
date: 2026-03-13
categories: Claude
tags: [Claude Code, Skill, Hook, CLAUDE.md, Agent]
---

:bulb: Claude Code로 개발할 때, 대화로 전달한 규칙이 컨텍스트에서 밀려나는 문제를 CLAUDE.md, Skill, Hook 세 가지 레이어로 해결하는 방법을 작성한다. 1부에서는 각 레이어의 개념과 사용법, 최적 조합까지 다룬다.
{: .notice--info}

:bulb: 프로젝트 적용, 확인 방법, 고급 구조, Agent Team 협업, FAQ는 [2부](/claude/claude-code-skill-hook-guide-part2/)에서 다룬다.
{: .notice}

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

<pre class="mermaid">
block-beta
    columns 1
    block:layer1:1
        A["CLAUDE.md → '이 프로젝트가 뭔지' (컨텍스트)\n세션 시작 시 자동 로드 | 프로젝트별로 다름"]
    end
    block:layer2:1
        B["Skill → '이렇게 해주세요' (상세 지침)\n트리거 키워드 매칭 시 로드 | 프로젝트 간 재사용 가능"]
    end
    block:layer3:1
        C["Hook → '이건 반드시 실행됩니다' (강제)\n이벤트 발생 시 100% 실행 | 셸 스크립트로 자동화"]
    end

    style layer1 fill:#e1f5fe
    style layer2 fill:#fff3e0
    style layer3 fill:#fce4ec
</pre>

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

:bulb: 프로젝트 적용 방법, 확인 방법, 고급 구조, Agent Team 협업, FAQ는 [2부](/claude/claude-code-skill-hook-guide-part2/)에서 이어진다.
{: .notice}
