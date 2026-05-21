---
title: "Claude Code Multi-Agent (Part 2): Automation, Communication, and Hands-On Example"
description: "Part 2 guide covering automation scripts, inter-agent communication strategies, a full-stack hands-on example, and FAQ for the Multi-Agent environment."
excerpt: "Part 2 guide covering automation scripts, inter-agent communication strategies, a full-stack hands-on example, and FAQ for the Multi-Agent environment."
date: 2026-03-13
categories: Claude
tags: [Claude Code, Multi-Agent, tmux, git worktree, Orchestrator]
ref: claude-code-multi-agent-part2
---

:bulb: This post covers automation scripts, inter-agent communication strategies, a full-stack hands-on example, and an FAQ for the Multi-Agent environment.
{: .notice--info}

:bulb: For the Multi-Agent concept, core tools (tmux, git worktree), and practical setup, see [Part 1](/en/claude/claude-code-multi-agent-part1/).
{: .notice}

---

# Chapter 4. Automation Scripts

## Summary

> Manually setting up worktrees and tmux every time is tedious.
> Preparation/cleanup can be automated with shell scripts.

## 4.1 Multi-Agent Start Script

```shell
#!/bin/bash
# multi-agent-start.sh
# Usage: ./multi-agent-start.sh /path/to/project

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR" || exit 1

echo "=== Preparing Multi-Agent environment ==="

# 1. Create worktrees
git worktree add ../wt-fe -b agent/frontend 2>/dev/null || echo "worktree-fe already exists"
git worktree add ../wt-be -b agent/backend 2>/dev/null || echo "worktree-be already exists"
git worktree add ../wt-test -b agent/test 2>/dev/null || echo "worktree-test already exists"

echo "worktrees created:"
git worktree list

# 2. Create tmux session and split panes
tmux new-session -d -s multi-agent -c ../wt-fe
tmux split-window -h -t multi-agent -c ../wt-be
tmux split-window -h -t multi-agent -c ../wt-test

# 3. Label each pane
tmux send-keys -t multi-agent:0.0 'echo "=== Frontend Agent ===" && claude' Enter
tmux send-keys -t multi-agent:0.1 'echo "=== Backend Agent ===" && claude' Enter
tmux send-keys -t multi-agent:0.2 'echo "=== Test Agent ===" && claude' Enter

# 4. Attach to session
tmux attach -t multi-agent

echo "=== Done ==="
```

**Run:**

```shell
chmod +x multi-agent-start.sh
./multi-agent-start.sh ~/my-project
```

## 4.2 Multi-Agent Cleanup Script

```shell
#!/bin/bash
# multi-agent-cleanup.sh
# Usage: ./multi-agent-cleanup.sh /path/to/project

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR" || exit 1

echo "=== Cleaning up Multi-Agent environment ==="

# 1. Kill tmux session
tmux kill-session -t multi-agent 2>/dev/null && echo "tmux session killed"

# 2. Remove worktrees
git worktree remove ../wt-fe 2>/dev/null && echo "wt-fe removed"
git worktree remove ../wt-be 2>/dev/null && echo "wt-be removed"
git worktree remove ../wt-test 2>/dev/null && echo "wt-test removed"

# 3. Prune worktree leftovers
git worktree prune

echo "=== Cleanup complete ==="
echo "Remaining branches (delete if needed):"
git branch --list "agent/*"
```

### Section Summary

- Automate repetitive work with start/cleanup scripts
- `multi-agent-start.sh`: worktree creation + tmux split + claude execution in one go
- `multi-agent-cleanup.sh`: tmux shutdown + worktree removal + leftover cleanup
{: .notice--info}

---

### Chapter 4 Summary

| Script | Role |
|---|---|
| `multi-agent-start.sh` | Create worktrees -> split tmux -> run claude |
| `multi-agent-cleanup.sh` | Kill tmux -> remove worktrees -> clean leftovers |

**Key terms:** `automation`, `shell script`, `tmux send-keys`
{: .notice}

---

# Chapter 5. Inter-Agent Communication Strategies

## Summary

> Agents working in parallel sometimes need to know each other's progress.
> Two methods: file-based communication (WORK_LOG.md) and branch-based communication (merge).

## 5.1 WORK_LOG.md — File-Based Communication

Each agent records its work into a shared file.

```markdown
# WORK_LOG.md

## [Frontend Agent] 2026-03-13 10:30
- src/pages/Login.tsx created
- LoginForm component will call POST /api/login
- **To Backend Agent**: Please make /api/login response shape { token: string, user: object }

## [Backend Agent] 2026-03-13 10:45
- POST /api/login implemented in backend/api/auth.py
- Response shape: { "token": "jwt...", "user": { "id": 1, "name": "..." } }
- **To Frontend Agent**: Integrate using the shape above
```

:warning: Editing the same file concurrently can cause conflicts. Operate WORK_LOG.md as **append only** (only add at the bottom).
{: .notice--warning}

## 5.2 Communication via a Shared Branch

When one agent's work output needs to be referenced by another:

```shell
# In the Backend Agent's worktree
cd ~/wt-be

# Pull the latest Frontend code
git fetch origin
git merge agent/frontend
```

## 5.3 Orchestrator Pattern

A pattern where a human or a separate Claude session manages the overall work.

<pre class="mermaid">
graph TD
    O["Orchestrator\n(separate tmux pane or human)"]
    O -- "Distribute work" --> FE["FE Agent\n(executor)"]
    O -- "Distribute work" --> BE["BE Agent\n(executor)"]
    O -- "Distribute work" --> TE["Test Agent\n(executor)"]
    FE -- "Report result" --> O
    BE -- "Report result" --> O
    TE -- "Report result" --> O

    O -.- R["Role:\n- Task distribution\n- Progress check (WORK_LOG.md, git log)\n- Conflict resolution\n- Quality control (review)"]

    style O fill:#f3e5f5,stroke:#6a1b9a
    style FE fill:#e3f2fd,stroke:#1565c0
    style BE fill:#e8f5e9,stroke:#2e7d32
    style TE fill:#fff3e0,stroke:#e65100
    style R fill:#fafafa,stroke:#bdbdbd
</pre>

### Section Summary

- WORK_LOG.md for async message exchange between agents (append only)
- Use `git merge` to pull code from another agent
- An Orchestrator distributing and integrating work is the most stable approach
{: .notice--info}

---

### Chapter 5 Summary

| Communication | Suitable When | Caveats |
|---|---|---|
| WORK_LOG.md | Sharing API interfaces, progress updates | Operate as append only |
| git merge | When another agent's code is required | Conflicts possible |
| Orchestrator | Managing overall work | Human or separate agent |

**Key terms:** `WORK_LOG.md`, `append only`, `Orchestrator`, `branch merge`
{: .notice}

---

# Chapter 6. Hands-On Example: Building a Full-Stack Login Feature

## Summary

> A step-by-step scenario for developing a login feature in parallel with 3 agents.

## 6.1 Scenario

```
Goal: Implement login (Frontend + Backend + Test)
Estimated time: single agent 30 min -> Multi-Agent 10-15 min
```

## 6.2 Full Command Flow

```shell
# === 1. Prepare ===
cd ~/login-project
git worktree add ../wt-fe -b agent/frontend
git worktree add ../wt-be -b agent/backend
git worktree add ../wt-test -b agent/test

tmux new -s login-dev

# === 2. Split panes and run each agent ===
# (Pane 1) cd ~/wt-fe && claude
# (Pane 2) cd ~/wt-be && claude
# (Pane 3) cd ~/wt-test && claude

# === 3. Give each agent a task ===
# Pane 1: "Build the login page UI with React + TailwindCSS."
# Pane 2: "Build a POST /api/login JWT auth API with FastAPI."
# Pane 3: "Write unit tests for existing utils/ functions."

# === 4. After all agents complete, integrate ===
cd ~/login-project
git merge agent/frontend --no-edit
git merge agent/backend --no-edit
git merge agent/test --no-edit

# === 5. Clean up ===
git worktree remove ../wt-fe
git worktree remove ../wt-be
git worktree remove ../wt-test
git branch -d agent/frontend agent/backend agent/test
tmux kill-session -t login-dev
```

---

### Chapter 6 Summary

| Step | Estimated Time | Task |
|---|---|---|
| Prepare | 1 min | Set up worktrees + tmux |
| Parallel run | 10 min | 3 agents work simultaneously |
| Integrate | 2 min | Branch merges |
| Clean up | 1 min | Remove worktrees/branches |

**Key terms:** `parallel development`, `branch integration`, `full stack`
{: .notice}

---

# Chapter 7. Frequently Asked Questions (FAQ)

## Q: What happens if agents modify each other's files?

Since they are isolated via worktrees, **no real-time conflicts occur.** However, if the same file was modified at merge time, a git conflict may arise. Specify assigned directories in CLAUDE.md to prevent this.

## Q: How many agents can run concurrently?

There is no technical limit, but practically **2–4** is reasonable. Reasons:

| # of agents | Characteristics |
|---|---|
| 2 | Easy to manage, the most common config (FE + BE) |
| 3 | FE + BE + Test, balanced setup |
| 4+ | Increased orchestrator load, more complex merges |

## Q: Will I hit API rate limits?

Claude Code makes independent API calls per session. With many concurrent sessions you may hit rate limits, so check the concurrent-request limit for your plan.

## Q: Does this work on Windows?

- **WSL2**: both tmux + git worktree work (recommended)
- **PowerShell**: use Windows Terminal tabs instead of tmux; git worktree still works
- **Git Bash**: tmux is not supported; open multiple terminals instead

## Q: Can I create a worktree from an existing branch?

```shell
# Check out an existing branch without -b
git worktree add ../wt-fe agent/frontend
```

Omitting `-b` uses an existing branch instead of creating a new one.

---

# [Appendix A] Command Summary

| Command | Description |
|---|---|
| `git worktree add ../path -b branch` | Create new worktree + branch |
| `git worktree add ../path branch` | Create worktree from existing branch |
| `git worktree list` | List worktrees |
| `git worktree remove ../path` | Remove worktree |
| `git worktree prune` | Clean up worktree references |
| `tmux new -s name` | Create tmux session |
| `tmux attach -t name` | Reattach to session |
| `Ctrl+b %` | Horizontal pane split |
| `Ctrl+b "` | Vertical pane split |
| `Ctrl+b d` | Detach (keep session) |

---

# [Appendix B] Comparison of Composition Patterns

| Pattern | # of agents | Suitable for |
|---|---|---|
| Solo | 1 | Small work, single feature |
| Pair | 2 | FE + BE, code + tests |
| Trio | 3 | FE + BE + Test/Docs |
| Squad | 4+ | Large features, microservices |
