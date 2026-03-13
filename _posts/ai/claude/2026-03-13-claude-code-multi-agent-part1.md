---
title: "Claude Code Multi-Agent (1부): 개념과 실전 구성"
date: 2026-03-13
categories: Claude
tags: [Claude Code, Multi-Agent, tmux, git worktree, Orchestrator]
---

:bulb: Claude Code CLI 환경에서 여러 agent를 동시에 실행하여, 하나의 프로젝트를 병렬로 개발하는 방법을 작성한다. 1부에서는 Multi-Agent의 개념, 핵심 도구, 실전 구성까지 다룬다.
{: .notice--info}

:bulb: 자동화 스크립트, Agent 간 소통 전략, 실전 예제, FAQ는 [2부](/claude/claude-code-multi-agent-part2/)에서 다룬다.
{: .notice}

---

# 1장. Multi-Agent란 무엇인가

## 요약

> 하나의 Claude 세션으로는 한 번에 하나의 작업만 가능하다.
> Multi-Agent는 **여러 Claude 세션을 동시에 띄워** 각자 다른 작업을 병렬로 수행하게 하는 패턴이다.

## 1.1 개념

Multi-Agent는 하나의 프로젝트에서 **여러 개의 Claude Code 세션(= agent)**을 동시에 실행하는 것을 말한다. 각 agent는 독립적인 터미널 세션에서 실행되며, 서로 다른 작업을 병렬로 처리한다.

<pre class="mermaid">
graph TB
    subgraph Project["하나의 프로젝트"]
        subgraph A1["Agent 1 (Frontend)"]
            A1a["tmux pane 1\nworktree-fe/\nbranch: fe"]
        end
        subgraph A2["Agent 2 (Backend)"]
            A2a["tmux pane 2\nworktree-be/\nbranch: be"]
        end
        subgraph A3["Agent 3 (Test/Docs)"]
            A3a["tmux pane 3\nworktree-test/\nbranch: test"]
        end
    end
    Orch["Orchestrator (사람 또는 Agent)\n작업 분배, 리뷰, 머지"]
    Orch --> A1
    Orch --> A2
    Orch --> A3

    style A1 fill:#e3f2fd,stroke:#1565c0
    style A2 fill:#e8f5e9,stroke:#2e7d32
    style A3 fill:#fff3e0,stroke:#e65100
    style Orch fill:#f3e5f5,stroke:#6a1b9a
</pre>

## 1.2 왜 필요한가

**단일 agent의 한계:**

| 문제 | 설명 |
|---|---|
| 순차 처리 | Frontend 완료 후 Backend 시작 - 시간 낭비 |
| 컨텍스트 오염 | 하나의 세션에 여러 작업을 넣으면 지시를 잊거나 혼동 |
| 긴 작업 시 비효율 | 빌드/테스트 대기 시간에 다른 작업 불가 |

**Multi-Agent의 장점:**

| 장점 | 설명 |
|---|---|
| 병렬 처리 | Frontend, Backend, Test를 동시에 진행 |
| 격리된 컨텍스트 | 각 agent가 자기 작업에만 집중 |
| 독립된 브랜치 | 충돌 없이 각자의 코드 영역에서 작업 |

### 절 요약

- Multi-Agent = 여러 Claude Code 세션을 동시 실행하는 패턴
- 병렬 처리, 컨텍스트 격리, 브랜치 분리가 핵심 이점
- tmux + git worktree 조합으로 구현
{: .notice--info}

---

# 2장. 핵심 도구: tmux + git worktree

## 요약

> Multi-Agent를 실현하려면 두 가지 도구가 필요하다.
> **tmux**로 여러 터미널 세션을 관리하고, **git worktree**로 각 agent에게 격리된 작업 디렉토리를 제공한다.

## 2.1 tmux - 여러 agent 세션을 동시에 운영

### 개념

tmux는 하나의 터미널에서 여러 세션/패널을 동시에 운영하는 도구다. 각 패널에서 독립적인 Claude Code 세션을 실행할 수 있다.

### 왜 tmux인가

| 방법 | 단점 |
|---|---|
| 터미널 탭 여러 개 | SSH 끊기면 전부 종료 |
| 백그라운드 (`&`) | 출력 확인 불편, 상호작용 불가 |
| **tmux** | SSH 끊겨도 유지, 실시간 모니터링, 패널 전환 자유 |

### 실전 사용법

**1) 세션 생성 및 패널 분할**

```shell
# multi-agent용 세션 생성
tmux new -s multi-agent

# 좌우 분할 (2개 패널)
# Ctrl+b %

# 한 번 더 좌우 분할 (3개 패널)
# 오른쪽 패널에서 Ctrl+b %
```

**결과 화면:**

```
+-------------------+-------------------+-------------------+
|                   |                   |                   |
|   Agent 1         |   Agent 2         |   Agent 3         |
|   (Frontend)      |   (Backend)       |   (Test)          |
|                   |                   |                   |
|   $ claude        |   $ claude        |   $ claude        |
|                   |                   |                   |
+-------------------+-------------------+-------------------+
```

**2) 패널 간 이동**

```
Ctrl+b  방향키      # 인접 패널로 이동
Ctrl+b  q  번호     # 번호로 패널 이동
```

**3) 세션에서 빠져나오기 / 재접속**

```shell
# 빠져나오기 (세션 유지, agent 계속 실행)
# Ctrl+b d

# 재접속
tmux attach -t multi-agent
```

:bulb: tmux 상세 사용법은 별도 포스트를 참고: [tmux 기본 사용법](/linux/2026-03-06-tmux-basic/)
{: .notice--info}

### 절 요약

- tmux로 하나의 터미널에서 여러 Claude 세션을 동시 실행
- SSH가 끊겨도 agent 세션이 유지됨
- `Ctrl+b %`로 패널 분할, `Ctrl+b 방향키`로 이동
{: .notice--info}

---

## 2.2 git worktree - agent별 격리된 작업 디렉토리

### 개념

git worktree는 **하나의 git 저장소에서 여러 개의 작업 디렉토리를 생성**하는 기능이다. 각 worktree는 서로 다른 브랜치를 체크아웃하고 있으며, 파일 시스템 수준에서 완전히 격리된다.

```
my-project/                    <- 원본 (main 브랜치)
  |
  +-- ../worktree-fe/          <- worktree 1 (fe 브랜치)
  +-- ../worktree-be/          <- worktree 2 (be 브랜치)
  +-- ../worktree-test/        <- worktree 3 (test 브랜치)
```

### 왜 git worktree인가

| 방법 | 문제 |
|---|---|
| 같은 디렉토리에서 작업 | agent끼리 파일 충돌 발생 |
| git clone 여러 개 | 디스크 낭비, .git 중복 |
| **git worktree** | 하나의 .git 공유, 브랜치만 분리, 가볍고 빠름 |

### 실전 사용법

**1) worktree 생성**

```shell
cd ~/my-project

# Frontend agent용 worktree
git worktree add ../worktree-fe -b agent/frontend

# Backend agent용 worktree
git worktree add ../worktree-be -b agent/backend

# Test agent용 worktree
git worktree add ../worktree-test -b agent/test
```

**출력 예:**

```
Preparing worktree (new branch 'agent/frontend')
HEAD is now at a1b2c3d feat: initial commit
```

**옵션 설명:**

| 옵션 | 설명 |
|---|---|
| `../worktree-fe` | worktree가 생성될 디렉토리 경로 |
| `-b agent/frontend` | 새 브랜치를 생성하면서 체크아웃 |

**2) worktree 목록 확인**

```shell
git worktree list
```

**출력 예:**

```
/home/user/my-project          a1b2c3d [main]
/home/user/worktree-fe         a1b2c3d [agent/frontend]
/home/user/worktree-be         a1b2c3d [agent/backend]
/home/user/worktree-test       a1b2c3d [agent/test]
```

**3) 작업 완료 후 worktree 제거**

```shell
git worktree remove ../worktree-fe
git worktree remove ../worktree-be
git worktree remove ../worktree-test

# 브랜치도 정리 (머지 완료 후)
git branch -d agent/frontend agent/backend agent/test
```

### 절 요약

- git worktree = 하나의 repo에서 여러 작업 디렉토리를 브랜치별로 격리
- `git worktree add ../경로 -b 브랜치명`으로 생성
- 각 agent가 서로의 파일을 건드리지 않아 충돌 방지
{: .notice--info}

---

### 2장 요약

| 도구 | 역할 | 핵심 명령 |
|---|---|---|
| tmux | 여러 터미널 세션을 동시 운영 | `tmux new -s`, `Ctrl+b %` |
| git worktree | agent별 격리된 작업 디렉토리 | `git worktree add` |

**핵심 키워드:** `tmux`, `git worktree`, `세션 분할`, `브랜치 격리`
{: .notice}

---

# 3장. Multi-Agent 실전 구성

## 요약

> tmux + git worktree를 조합하여 실제로 여러 agent를 동시에 실행하는 전체 워크플로우를 설명한다.

## 3.1 전체 흐름

<pre class="mermaid">
graph LR
    S1["[1] 준비\nworktree 생성\ntmux 세션 생성\nCLAUDE.md 배치"]
    S2["[2] 실행\n각 agent에게 작업 지시\n(각 패널에서 claude)"]
    S3["[3] 통합\nOrchestrator가\n브랜치 머지\n충돌 해결"]
    S4["[4] 정리\nworktree 제거\n브랜치 정리\ntmux 종료"]

    S1 --> S2 --> S3 --> S4

    style S1 fill:#e3f2fd,stroke:#1565c0
    style S2 fill:#e8f5e9,stroke:#2e7d32
    style S3 fill:#fff3e0,stroke:#e65100
    style S4 fill:#fce4ec,stroke:#c62828
</pre>

## 3.2 Step 1: 준비

### (A) worktree 생성

```shell
cd ~/my-project

git worktree add ../wt-fe -b agent/frontend
git worktree add ../wt-be -b agent/backend
git worktree add ../wt-test -b agent/test
```

### (B) 각 worktree에 CLAUDE.md 배치 (선택)

agent별로 역할에 맞는 지시를 CLAUDE.md에 작성하면 더 효과적이다.

```shell
cat > ../wt-fe/CLAUDE.md << 'EOF'
# Agent: Frontend
- 역할: React 컴포넌트 개발
- 담당 디렉토리: src/components/, src/pages/
- 브랜치: agent/frontend
- 다른 agent의 영역(backend/, tests/)은 수정하지 않는다
EOF

cat > ../wt-be/CLAUDE.md << 'EOF'
# Agent: Backend
- 역할: FastAPI 엔드포인트 개발
- 담당 디렉토리: backend/, api/
- 브랜치: agent/backend
- 다른 agent의 영역(src/, tests/)은 수정하지 않는다
EOF
```

### (C) tmux 세션 생성 및 패널 분할

```shell
# 세션 생성
tmux new -s multi-agent

# 패널 분할 (좌 | 중 | 우)
# Ctrl+b %   (좌우 분할)
# 오른쪽 패널에서 Ctrl+b %  (한 번 더 분할)
```

### 절 요약

- worktree 생성 -> CLAUDE.md 배치 -> tmux 패널 분할 순서로 준비
- CLAUDE.md에 agent 역할과 담당 영역을 명시하면 작업 범위 제어 가능
{: .notice--info}

---

## 3.3 Step 2: 각 agent에게 작업 지시

각 tmux 패널에서 해당 worktree로 이동 후 Claude Code를 실행한다.

**패널 1 (Frontend Agent):**

```shell
cd ~/wt-fe
claude
```

프롬프트 예:

```
사용자 로그인 페이지를 만들어줘.
src/pages/Login.tsx와 src/components/LoginForm.tsx를 생성하고,
React Hook Form으로 유효성 검사를 구현해줘.
```

**패널 2 (Backend Agent):**

```shell
cd ~/wt-be
claude
```

프롬프트 예:

```
로그인 API를 만들어줘.
backend/api/auth.py에 POST /api/login 엔드포인트를 구현하고,
JWT 토큰 발급 로직을 포함해줘.
```

**패널 3 (Test Agent):**

```shell
cd ~/wt-test
claude
```

프롬프트 예:

```
기존 코드의 테스트를 작성해줘.
tests/ 디렉토리에 pytest 기반 단위 테스트를 추가해줘.
```

**실행 중 화면:**

```
+---------------------+---------------------+---------------------+
|  ~/wt-fe            |  ~/wt-be            |  ~/wt-test          |
|                     |                     |                     |
|  claude> Login      |  claude> POST /api  |  claude> pytest     |
|  페이지를 생성      |  /login 엔드포인트  |  테스트 작성 중...  |
|  하고 있습니다...   |  구현 중...         |                     |
|                     |                     |                     |
+---------------------+---------------------+---------------------+
```

### 절 요약

- 각 tmux 패널에서 worktree 디렉토리로 이동 후 `claude` 실행
- agent별로 명확한 작업 범위를 프롬프트에 지정
- 동시에 3개 agent가 병렬로 작업 진행
{: .notice--info}

---

## 3.4 Step 3: 브랜치 통합 (머지)

모든 agent의 작업이 완료되면 원본 프로젝트에서 브랜치를 머지한다.

```shell
cd ~/my-project

# Frontend 브랜치 머지
git merge agent/frontend

# Backend 브랜치 머지
git merge agent/backend

# Test 브랜치 머지
git merge agent/test
```

**충돌 발생 시:**

```shell
# 충돌 파일 확인
git status

# 수동 해결 또는 Claude에게 맡기기
claude
# 프롬프트: "머지 충돌이 발생했어. git status 확인하고 해결해줘."
```

### 절 요약

- 원본 디렉토리에서 각 agent 브랜치를 순서대로 머지
- 충돌 발생 시 Claude에게 해결을 맡길 수 있음
{: .notice--info}

---

## 3.5 Step 4: 정리

```shell
# worktree 제거
git worktree remove ../wt-fe
git worktree remove ../wt-be
git worktree remove ../wt-test

# 머지 완료된 브랜치 삭제
git branch -d agent/frontend agent/backend agent/test

# tmux 세션 종료
tmux kill-session -t multi-agent
```

---

### 3장 요약

| 단계 | 작업 | 핵심 명령 |
|---|---|---|
| 준비 | worktree 생성, tmux 분할 | `git worktree add`, `Ctrl+b %` |
| 실행 | 각 패널에서 claude 실행 | `cd ~/wt-xx && claude` |
| 통합 | 브랜치 머지 | `git merge agent/xxx` |
| 정리 | worktree/브랜치/세션 제거 | `git worktree remove`, `git branch -d` |

**핵심 키워드:** `worktree add`, `tmux 패널`, `병렬 실행`, `브랜치 머지`
{: .notice}

---

:bulb: 자동화 스크립트, Agent 간 소통 전략, 실전 예제, FAQ는 [2부](/claude/claude-code-multi-agent-part2/)에서 이어진다.
{: .notice}
