---
title: "Claude Code 완벽 가이드 (2부): 프로젝트 적용, 고급 구조, FAQ"
date: 2026-03-13
categories: Claude
tags: [Claude Code, Skill, Hook, CLAUDE.md, Agent]
---

:bulb: CLAUDE.md, Skill, Hook을 실제 프로젝트에 적용하는 방법, 고급 스킬 구조, Agent Team 협업, FAQ를 다룬다.
{: .notice--info}

:bulb: 3가지 레이어의 개념과 사용법은 [1부](/claude/claude-code-skill-hook-guide-part1/)를 참고한다.
{: .notice}

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

Ubuntu 24.04 + Claude Code 환경에서 여러 agent를 팀으로 구성할 때의 가이드다.

## 11-1. 추천 팀 구조

<pre class="mermaid">
graph TD
    O["Orchestrator\n(작업 분배, 리뷰, 통합)"]
    O --> FE["Frontend Agent\nclaude-bot/frontend"]
    O --> BE["Backend Agent\nclaude-bot/backend"]
    O --> DO["DevOps Agent\nclaude-bot/devops"]

    style O fill:#fff3e0,stroke:#e65100
    style FE fill:#e3f2fd,stroke:#1565c0
    style BE fill:#e8f5e9,stroke:#2e7d32
    style DO fill:#f3e5f5,stroke:#6a1b9a
</pre>

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

**아니다. 큰 차이가 있다.** claude.ai 웹에서는 Skill만 사용 가능하고, Hook과 CLAUDE.md는 Claude Code(CLI) 전용이다. 상세 비교는 1부 [03] 섹션을 참조.

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
