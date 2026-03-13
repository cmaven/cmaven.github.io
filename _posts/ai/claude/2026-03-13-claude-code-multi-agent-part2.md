---
title: "Claude Code Multi-Agent (2부): 자동화, 소통 전략, 실전 예제"
date: 2026-03-13
categories: Claude
tags: [Claude Code, Multi-Agent, tmux, git worktree, Orchestrator]
---

:bulb: Multi-Agent 환경의 자동화 스크립트, Agent 간 소통 전략, 풀스택 실전 예제, FAQ를 다룬다.
{: .notice--info}

:bulb: Multi-Agent 개념, 핵심 도구(tmux, git worktree), 실전 구성은 [1부](/claude/claude-code-multi-agent-part1/)를 참고한다.
{: .notice}

---

# 4장. 자동화 스크립트

## 요약

> 매번 수동으로 worktree와 tmux를 세팅하는 것은 번거롭다.
> 셸 스크립트로 준비/정리를 자동화할 수 있다.

## 4.1 Multi-Agent 시작 스크립트

```shell
#!/bin/bash
# multi-agent-start.sh
# 사용법: ./multi-agent-start.sh /path/to/project

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR" || exit 1

echo "=== Multi-Agent 환경 준비 ==="

# 1. worktree 생성
git worktree add ../wt-fe -b agent/frontend 2>/dev/null || echo "worktree-fe already exists"
git worktree add ../wt-be -b agent/backend 2>/dev/null || echo "worktree-be already exists"
git worktree add ../wt-test -b agent/test 2>/dev/null || echo "worktree-test already exists"

echo "worktree 생성 완료:"
git worktree list

# 2. tmux 세션 생성 및 패널 분할
tmux new-session -d -s multi-agent -c ../wt-fe
tmux split-window -h -t multi-agent -c ../wt-be
tmux split-window -h -t multi-agent -c ../wt-test

# 3. 각 패널에 이름 표시
tmux send-keys -t multi-agent:0.0 'echo "=== Frontend Agent ===" && claude' Enter
tmux send-keys -t multi-agent:0.1 'echo "=== Backend Agent ===" && claude' Enter
tmux send-keys -t multi-agent:0.2 'echo "=== Test Agent ===" && claude' Enter

# 4. 세션 접속
tmux attach -t multi-agent

echo "=== 완료 ==="
```

**실행:**

```shell
chmod +x multi-agent-start.sh
./multi-agent-start.sh ~/my-project
```

## 4.2 Multi-Agent 정리 스크립트

```shell
#!/bin/bash
# multi-agent-cleanup.sh
# 사용법: ./multi-agent-cleanup.sh /path/to/project

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR" || exit 1

echo "=== Multi-Agent 환경 정리 ==="

# 1. tmux 세션 종료
tmux kill-session -t multi-agent 2>/dev/null && echo "tmux 세션 종료"

# 2. worktree 제거
git worktree remove ../wt-fe 2>/dev/null && echo "wt-fe 제거"
git worktree remove ../wt-be 2>/dev/null && echo "wt-be 제거"
git worktree remove ../wt-test 2>/dev/null && echo "wt-test 제거"

# 3. worktree 잔여물 정리
git worktree prune

echo "=== 정리 완료 ==="
echo "남은 브랜치 (필요 시 삭제):"
git branch --list "agent/*"
```

### 절 요약

- 시작/정리 스크립트로 반복 작업을 자동화
- `multi-agent-start.sh`: worktree 생성 + tmux 분할 + claude 실행까지 한 번에
- `multi-agent-cleanup.sh`: tmux 종료 + worktree 제거 + 잔여물 정리
{: .notice--info}

---

### 4장 요약

| 스크립트 | 역할 |
|---|---|
| `multi-agent-start.sh` | worktree 생성 -> tmux 분할 -> claude 실행 |
| `multi-agent-cleanup.sh` | tmux 종료 -> worktree 제거 -> 잔여물 정리 |

**핵심 키워드:** `자동화`, `셸 스크립트`, `tmux send-keys`
{: .notice}

---

# 5장. Agent 간 소통 전략

## 요약

> 병렬로 작업하는 agent들이 서로의 진행 상황을 알아야 할 때가 있다.
> 파일 기반 소통(WORK_LOG.md)과 브랜치 기반 소통(머지) 두 가지 방법이 있다.

## 5.1 WORK_LOG.md - 파일 기반 소통

각 agent가 작업 내역을 공유 파일에 기록하는 방법이다.

```markdown
# WORK_LOG.md

## [Frontend Agent] 2026-03-13 10:30
- src/pages/Login.tsx 생성 완료
- LoginForm 컴포넌트에서 POST /api/login 호출 예정
- **Backend Agent에게**: /api/login 응답 형식을 { token: string, user: object } 로 맞춰주세요

## [Backend Agent] 2026-03-13 10:45
- backend/api/auth.py 에 POST /api/login 구현 완료
- 응답 형식: { "token": "jwt...", "user": { "id": 1, "name": "..." } }
- **Frontend Agent에게**: 위 형식으로 연동하시면 됩니다
```

:warning: 같은 파일을 동시에 수정하면 충돌이 발생할 수 있다. WORK_LOG.md는 **append only** (아래에 추가만)로 운영한다.
{: .notice--warning}

## 5.2 공유 브랜치를 통한 소통

한 agent의 작업 결과를 다른 agent가 참조해야 할 때:

```shell
# Backend Agent의 worktree에서
cd ~/wt-be

# Frontend의 최신 코드를 가져오기
git fetch origin
git merge agent/frontend
```

## 5.3 Orchestrator 패턴

사람이 직접 또는 별도의 Claude 세션이 전체 작업을 관리하는 패턴이다.

<pre class="mermaid">
graph TD
    O["Orchestrator\n(tmux 별도 패널 또는 사람이 직접)"]
    O -- "작업 분배" --> FE["FE Agent\n(실행자)"]
    O -- "작업 분배" --> BE["BE Agent\n(실행자)"]
    O -- "작업 분배" --> TE["Test Agent\n(실행자)"]
    FE -- "결과 보고" --> O
    BE -- "결과 보고" --> O
    TE -- "결과 보고" --> O

    O -.- R["역할:\n- 작업 분배\n- 진행 확인 (WORK_LOG.md, git log)\n- 충돌 해결\n- 품질 관리 (리뷰)"]

    style O fill:#f3e5f5,stroke:#6a1b9a
    style FE fill:#e3f2fd,stroke:#1565c0
    style BE fill:#e8f5e9,stroke:#2e7d32
    style TE fill:#fff3e0,stroke:#e65100
    style R fill:#fafafa,stroke:#bdbdbd
</pre>

### 절 요약

- WORK_LOG.md로 agent 간 비동기 메시지 교환 (append only)
- `git merge`로 다른 agent의 코드를 가져올 수 있음
- Orchestrator가 전체 작업을 분배하고 통합하는 것이 가장 안정적
{: .notice--info}

---

### 5장 요약

| 소통 방법 | 적합한 상황 | 주의사항 |
|---|---|---|
| WORK_LOG.md | API 인터페이스 공유, 진행 상황 알림 | append only로 운영 |
| git merge | 다른 agent의 코드가 필요할 때 | 충돌 가능성 있음 |
| Orchestrator | 전체 작업 관리 | 사람 또는 별도 agent |

**핵심 키워드:** `WORK_LOG.md`, `append only`, `Orchestrator`, `브랜치 머지`
{: .notice}

---

# 6장. 실전 예제: 풀스택 로그인 기능 개발

## 요약

> 3개 agent로 로그인 기능을 병렬 개발하는 전체 시나리오를 단계별로 보여준다.

## 6.1 시나리오

```
목표: 로그인 기능 구현 (Frontend + Backend + Test)
예상 소요: 단일 agent 30분 -> Multi-Agent 10~15분
```

## 6.2 전체 명령 흐름

```shell
# === 1. 준비 ===
cd ~/login-project
git worktree add ../wt-fe -b agent/frontend
git worktree add ../wt-be -b agent/backend
git worktree add ../wt-test -b agent/test

tmux new -s login-dev

# === 2. 패널 분할 후 각 agent 실행 ===
# (패널 1) cd ~/wt-fe && claude
# (패널 2) cd ~/wt-be && claude
# (패널 3) cd ~/wt-test && claude

# === 3. 각 agent에게 지시 ===
# 패널 1: "로그인 페이지 UI를 만들어줘. React + TailwindCSS로."
# 패널 2: "POST /api/login JWT 인증 API를 만들어줘. FastAPI로."
# 패널 3: "기존 utils/ 함수들의 단위 테스트를 작성해줘."

# === 4. 모든 agent 작업 완료 후 통합 ===
cd ~/login-project
git merge agent/frontend --no-edit
git merge agent/backend --no-edit
git merge agent/test --no-edit

# === 5. 정리 ===
git worktree remove ../wt-fe
git worktree remove ../wt-be
git worktree remove ../wt-test
git branch -d agent/frontend agent/backend agent/test
tmux kill-session -t login-dev
```

---

### 6장 요약

| 단계 | 소요 시간 (예상) | 작업 |
|---|---|---|
| 준비 | 1분 | worktree + tmux 세팅 |
| 병렬 실행 | 10분 | 3개 agent 동시 작업 |
| 통합 | 2분 | 브랜치 머지 |
| 정리 | 1분 | worktree/브랜치 제거 |

**핵심 키워드:** `병렬 개발`, `브랜치 통합`, `풀스택`
{: .notice}

---

# 7장. 자주 묻는 질문 (FAQ)

## Q: agent가 서로의 파일을 수정하면 어떻게 되나?

worktree로 격리되어 있으므로 **실시간 충돌은 발생하지 않는다.** 단, 머지 시점에 같은 파일을 수정했다면 git 충돌이 발생할 수 있다. CLAUDE.md에 담당 디렉토리를 명시하여 예방한다.

## Q: agent를 몇 개까지 동시에 돌릴 수 있나?

기술적 제한은 없지만, 실용적으로는 **2~4개**가 적당하다. 이유:

| agent 수 | 특성 |
|---|---|
| 2개 | 관리 쉬움, 가장 흔한 구성 (FE + BE) |
| 3개 | FE + BE + Test, 균형 잡힌 구성 |
| 4개+ | Orchestrator 부담 증가, 머지 복잡도 상승 |

## Q: API rate limit에 걸리지 않나?

Claude Code는 세션별로 독립적인 API 호출을 한다. 동시 세션 수가 많으면 rate limit에 도달할 수 있으므로, 플랜에 따른 동시 요청 제한을 확인해야 한다.

## Q: Windows에서도 가능한가?

- **WSL2**: tmux + git worktree 모두 사용 가능 (권장)
- **PowerShell**: tmux 대신 Windows Terminal 탭을 사용, git worktree는 동일하게 사용 가능
- **Git Bash**: tmux 미지원, 터미널 여러 개 열어서 대체

## Q: 이미 존재하는 브랜치로 worktree를 만들 수 있나?

```shell
# -b 없이 기존 브랜치를 체크아웃
git worktree add ../wt-fe agent/frontend
```

`-b`를 빼면 새 브랜치를 생성하지 않고 기존 브랜치를 사용한다.

---

# [부록 A] 명령어 요약

| 명령어 | 설명 |
|---|---|
| `git worktree add ../경로 -b 브랜치` | 새 worktree + 브랜치 생성 |
| `git worktree add ../경로 브랜치` | 기존 브랜치로 worktree 생성 |
| `git worktree list` | worktree 목록 확인 |
| `git worktree remove ../경로` | worktree 제거 |
| `git worktree prune` | 잔여 worktree 참조 정리 |
| `tmux new -s 세션명` | tmux 세션 생성 |
| `tmux attach -t 세션명` | 세션 재접속 |
| `Ctrl+b %` | 좌우 패널 분할 |
| `Ctrl+b "` | 상하 패널 분할 |
| `Ctrl+b d` | 세션에서 빠져나오기 (유지) |

---

# [부록 B] 구성 패턴별 비교

| 패턴 | agent 수 | 적합한 상황 |
|---|---|---|
| Solo | 1 | 소규모 작업, 단일 기능 |
| Pair | 2 | FE + BE, 코드 + 테스트 |
| Trio | 3 | FE + BE + Test/Docs |
| Squad | 4+ | 대규모 기능, 마이크로서비스 |
