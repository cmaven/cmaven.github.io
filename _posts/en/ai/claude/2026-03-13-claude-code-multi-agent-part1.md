---
title: "Claude Code Multi-Agent (Part 1): Concepts and Practical Setup"
description: "An explanation of the Multi-Agent concept and practical setup for running multiple Claude Code CLI agents in parallel using tmux and git worktree."
excerpt: "How to run multiple agents simultaneously in Claude Code CLI using tmux and git worktree, with the Multi-Agent concept and practical configuration."
date: 2026-03-13
categories: Claude
tags: [Claude Code, Multi-Agent, tmux, git worktree, Orchestrator]
ref: claude-code-multi-agent-part1
---

:bulb: This post explains how to run multiple agents in parallel within a single project using the Claude Code CLI. Part 1 covers the Multi-Agent concept, the core tools, and the practical setup.
{: .notice--info}

:bulb: Automation scripts, inter-agent communication strategies, hands-on examples, and FAQ are covered in [Part 2](/claude/claude-code-multi-agent-part2/).
{: .notice}

---

# Chapter 1. What Is Multi-Agent?

## Summary

> A single Claude session can only handle one task at a time.
> Multi-Agent is a pattern that **runs multiple Claude sessions in parallel**, each performing a different task concurrently.

## 1.1 Concept

Multi-Agent means running **multiple Claude Code sessions (= agents)** simultaneously on a single project. Each agent runs in an independent terminal session and processes a different task in parallel.

<pre class="mermaid">
graph TB
    subgraph Project["One Project"]
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
    Orch["Orchestrator (human or agent)\nTask distribution, review, merge"]
    Orch --> A1
    Orch --> A2
    Orch --> A3

    style A1 fill:#e3f2fd,stroke:#1565c0
    style A2 fill:#e8f5e9,stroke:#2e7d32
    style A3 fill:#fff3e0,stroke:#e65100
    style Orch fill:#f3e5f5,stroke:#6a1b9a
</pre>

## 1.2 Why Is It Needed?

**Limits of a single agent:**

| Problem | Description |
|---|---|
| Sequential processing | Backend starts only after Frontend finishes — wasted time |
| Context pollution | Mixing tasks in one session leads to forgotten or confused instructions |
| Inefficient during long jobs | Cannot do other work while waiting for builds/tests |

**Benefits of Multi-Agent:**

| Benefit | Description |
|---|---|
| Parallel processing | Frontend, Backend, and Test run simultaneously |
| Isolated context | Each agent focuses solely on its own task |
| Independent branches | Each works in its own code area without conflicts |

### Section Summary

- Multi-Agent = a pattern of running multiple Claude Code sessions concurrently
- Parallel processing, context isolation, and branch separation are the key benefits
- Implemented with the tmux + git worktree combination
{: .notice--info}

---

# Chapter 2. Core Tools: tmux + git worktree

## Summary

> Two tools are needed to realize Multi-Agent.
> **tmux** manages multiple terminal sessions, and **git worktree** gives each agent an isolated working directory.

## 2.1 tmux — Running Multiple Agent Sessions Concurrently

### Concept

tmux is a tool that lets you run multiple sessions/panes in a single terminal. You can run an independent Claude Code session in each pane.

### Why tmux?

| Approach | Drawback |
|---|---|
| Multiple terminal tabs | All sessions die when SSH disconnects |
| Background (`&`) | Inconvenient output viewing, no interaction |
| **tmux** | Persists across SSH disconnects, real-time monitoring, free pane switching |

### Practical Usage

**1) Creating a session and splitting panes**

```shell
# Create a session for multi-agent
tmux new -s multi-agent

# Split horizontally (2 panes)
# Ctrl+b %

# Split horizontally again (3 panes)
# In the right pane, Ctrl+b %
```

**Resulting layout:**

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

**2) Moving between panes**

```
Ctrl+b  arrow keys   # Move to adjacent pane
Ctrl+b  q  number    # Jump to a pane by number
```

**3) Detaching from / reattaching to a session**

```shell
# Detach (session keeps running, agent continues)
# Ctrl+b d

# Reattach
tmux attach -t multi-agent
```

:bulb: For detailed tmux usage, see this separate post: [tmux basic usage](/linux/2026-03-06-tmux-basic/)
{: .notice--info}

### Section Summary

- Run multiple Claude sessions concurrently in one terminal with tmux
- Agent sessions persist even when SSH disconnects
- Split panes with `Ctrl+b %`, navigate with `Ctrl+b arrow keys`
{: .notice--info}

---

## 2.2 git worktree — Isolated Working Directory Per Agent

### Concept

git worktree is a feature that **creates multiple working directories from a single git repository**. Each worktree checks out a different branch and is fully isolated at the filesystem level.

```
my-project/                    <- original (main branch)
  |
  +-- ../worktree-fe/          <- worktree 1 (fe branch)
  +-- ../worktree-be/          <- worktree 2 (be branch)
  +-- ../worktree-test/        <- worktree 3 (test branch)
```

### Why git worktree?

| Approach | Problem |
|---|---|
| Working in the same directory | File conflicts between agents |
| Multiple git clones | Wasted disk space, duplicated .git |
| **git worktree** | Shares one .git, branches separated, lightweight and fast |

### Practical Usage

**1) Creating a worktree**

```shell
cd ~/my-project

# worktree for Frontend agent
git worktree add ../worktree-fe -b agent/frontend

# worktree for Backend agent
git worktree add ../worktree-be -b agent/backend

# worktree for Test agent
git worktree add ../worktree-test -b agent/test
```

**Example output:**

```
Preparing worktree (new branch 'agent/frontend')
HEAD is now at a1b2c3d feat: initial commit
```

**Option explanation:**

| Option | Description |
|---|---|
| `../worktree-fe` | Path where the worktree will be created |
| `-b agent/frontend` | Creates and checks out a new branch |

**2) Listing worktrees**

```shell
git worktree list
```

**Example output:**

```
/home/user/my-project          a1b2c3d [main]
/home/user/worktree-fe         a1b2c3d [agent/frontend]
/home/user/worktree-be         a1b2c3d [agent/backend]
/home/user/worktree-test       a1b2c3d [agent/test]
```

**3) Removing a worktree after the work is done**

```shell
git worktree remove ../worktree-fe
git worktree remove ../worktree-be
git worktree remove ../worktree-test

# Clean up branches too (after merging)
git branch -d agent/frontend agent/backend agent/test
```

### Section Summary

- git worktree = isolate multiple working directories per branch from a single repo
- Create with `git worktree add ../path -b branch-name`
- Each agent doesn't touch others' files, preventing conflicts
{: .notice--info}

---

### Chapter 2 Summary

| Tool | Role | Core Commands |
|---|---|---|
| tmux | Run multiple terminal sessions concurrently | `tmux new -s`, `Ctrl+b %` |
| git worktree | Isolated working directory per agent | `git worktree add` |

**Key terms:** `tmux`, `git worktree`, `pane split`, `branch isolation`
{: .notice}

---

# Chapter 3. Practical Multi-Agent Setup

## Summary

> Walk through the full workflow of running multiple agents in parallel by combining tmux + git worktree.

## 3.1 Overall Flow

<pre class="mermaid">
graph LR
    S1["[1] Prepare\nCreate worktree\nCreate tmux session\nPlace CLAUDE.md"]
    S2["[2] Run\nGive tasks to each agent\n(claude in each pane)"]
    S3["[3] Integrate\nOrchestrator\nmerges branches\nresolves conflicts"]
    S4["[4] Clean up\nRemove worktrees\nClean branches\nKill tmux"]

    S1 --> S2 --> S3 --> S4

    style S1 fill:#e3f2fd,stroke:#1565c0
    style S2 fill:#e8f5e9,stroke:#2e7d32
    style S3 fill:#fff3e0,stroke:#e65100
    style S4 fill:#fce4ec,stroke:#c62828
</pre>

## 3.2 Step 1: Preparation

### (A) Create worktrees

```shell
cd ~/my-project

git worktree add ../wt-fe -b agent/frontend
git worktree add ../wt-be -b agent/backend
git worktree add ../wt-test -b agent/test
```

### (B) Place CLAUDE.md in each worktree (optional)

Writing role-specific instructions in CLAUDE.md per agent is more effective.

```shell
cat > ../wt-fe/CLAUDE.md << 'EOF'
# Agent: Frontend
- Role: React component development
- Assigned directories: src/components/, src/pages/
- Branch: agent/frontend
- Do not modify other agents' areas (backend/, tests/)
EOF

cat > ../wt-be/CLAUDE.md << 'EOF'
# Agent: Backend
- Role: FastAPI endpoint development
- Assigned directories: backend/, api/
- Branch: agent/backend
- Do not modify other agents' areas (src/, tests/)
EOF
```

### (C) Create tmux session and split panes

```shell
# Create session
tmux new -s multi-agent

# Split panes (left | center | right)
# Ctrl+b %   (split horizontally)
# In the right pane, Ctrl+b %  (split once more)
```

### Section Summary

- Prepare in order: create worktrees -> place CLAUDE.md -> split tmux panes
- Specifying each agent's role and area in CLAUDE.md controls the work scope
{: .notice--info}

---

## 3.3 Step 2: Give Each Agent a Task

In each tmux pane, move to the corresponding worktree and run Claude Code.

**Pane 1 (Frontend Agent):**

```shell
cd ~/wt-fe
claude
```

Example prompt:

```
Create a user login page.
Generate src/pages/Login.tsx and src/components/LoginForm.tsx,
and implement validation with React Hook Form.
```

**Pane 2 (Backend Agent):**

```shell
cd ~/wt-be
claude
```

Example prompt:

```
Create a login API.
Implement a POST /api/login endpoint in backend/api/auth.py,
including JWT token issuance logic.
```

**Pane 3 (Test Agent):**

```shell
cd ~/wt-test
claude
```

Example prompt:

```
Write tests for the existing code.
Add pytest-based unit tests to the tests/ directory.
```

**While running:**

```
+---------------------+---------------------+---------------------+
|  ~/wt-fe            |  ~/wt-be            |  ~/wt-test          |
|                     |                     |                     |
|  claude> creating   |  claude> implement- |  claude> writing    |
|  the Login page...  |  ing POST /api/     |  tests...           |
|                     |  login endpoint...  |                     |
|                     |                     |                     |
+---------------------+---------------------+---------------------+
```

### Section Summary

- In each tmux pane, navigate to the worktree directory and run `claude`
- Specify a clear scope per agent in each prompt
- 3 agents work in parallel simultaneously
{: .notice--info}

---

## 3.4 Step 3: Branch Integration (Merge)

When all agents are done, merge the branches from the original project.

```shell
cd ~/my-project

# Merge Frontend branch
git merge agent/frontend

# Merge Backend branch
git merge agent/backend

# Merge Test branch
git merge agent/test
```

**If conflicts occur:**

```shell
# Check conflicting files
git status

# Resolve manually or delegate to Claude
claude
# Prompt: "A merge conflict has occurred. Check git status and resolve it."
```

### Section Summary

- From the original directory, merge each agent branch in order
- You can delegate conflict resolution to Claude when needed
{: .notice--info}

---

## 3.5 Step 4: Clean Up

```shell
# Remove worktrees
git worktree remove ../wt-fe
git worktree remove ../wt-be
git worktree remove ../wt-test

# Delete merged branches
git branch -d agent/frontend agent/backend agent/test

# Kill tmux session
tmux kill-session -t multi-agent
```

---

### Chapter 3 Summary

| Step | Task | Core Commands |
|---|---|---|
| Prepare | Create worktrees, split tmux | `git worktree add`, `Ctrl+b %` |
| Run | Run claude in each pane | `cd ~/wt-xx && claude` |
| Integrate | Merge branches | `git merge agent/xxx` |
| Clean up | Remove worktrees/branches/sessions | `git worktree remove`, `git branch -d` |

**Key terms:** `worktree add`, `tmux pane`, `parallel execution`, `branch merge`
{: .notice}

---

:bulb: Automation scripts, inter-agent communication strategies, hands-on examples, and FAQ continue in [Part 2](/claude/claude-code-multi-agent-part2/).
{: .notice}
