---
title: "Oh My Claude (omc): A Multi-Agent Orchestration Tool for Claude Code"
description: "Installation, main commands (team, autopilot, ralph, deep-interview), Skill system, and CLI usage for the oh-my-claudecode plugin."
excerpt: "From installation to real-world use of the omc plugin, which automatically dispatches complex Claude Code tasks to specialist agents."
date: 2026-03-19
categories: Claude
tags: [Claude Code, omc, Oh-My-Claude, Multi-Agent, autopilot, team, ralph, deep-interview, plugin, orchestration]
ref: oh-my-claude-omc
---

:bulb: Installation, commands, and practical usage of the **oh-my-claudecode (omc)** plugin, which automatically dispatches complex Claude Code tasks to multiple specialist agents.
{: .notice--info}

---

# [01] What Is omc?

**oh-my-claudecode (omc)** is a **Multi-Agent orchestration framework** for Claude Code. It automatically dispatches complex tasks to specialized agents and works out of the box with zero configuration.

| Feature | Description |
|------|------|
| **No setup needed** | Works immediately with defaults |
| **Team-first** | Plan → Design → Execute → Verify pipeline |
| **Natural-language commands** | No need to memorize commands; instruct in natural language |
| **Auto-parallelization** | Automatically distributes complex work across agents |
| **19 specialized agents** | Architecture, research, testing, data science, etc. |
| **Smart routing** | Haiku for simple tasks, Opus for complex reasoning |

---

# [02] Installation

## 2-1. Plugin Marketplace (Recommended)

Enter the following commands in the Claude Code prompt in order.

```
/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
/plugin install oh-my-claudecode
```

## 2-2. npm CLI

```bash
npm i -g oh-my-claude-sisyphus@latest
```

:warning: The repository is `oh-my-claudecode`, but the npm package name is **oh-my-claude-sisyphus**.
{: .notice--warning}

## 2-3. Initial Setup

```
/setup
/omc-setup
```

Or in the terminal:

```bash
omc setup
```

## 2-4. Quick Start

You can use it immediately after installation:

```
autopilot: build a REST API for managing tasks
```

---

# [03] Main Commands

## 3-1. Full Command Map

<pre class="mermaid">
graph TD
    OMC["omc"]

    OMC --> TEAM["/team\nTeam orchestration"]
    OMC --> AUTO["/autopilot\nFully autonomous execution"]
    OMC --> RALPH["/ralph\nPersistence mode"]
    OMC --> ULW["/ultrawork\nMax parallelization"]
    OMC --> DI["/deep-interview\nRequirements analysis"]
    OMC --> ASK["/ask\nExpert consultation"]
    OMC --> CCG["/ccg\nTriple-model synthesis"]
    OMC --> SKILL["/skill\nSkill management"]

    style OMC fill:#f3e5f5,stroke:#6a1b9a
    style TEAM fill:#e3f2fd,stroke:#1565c0
    style AUTO fill:#e8f5e9,stroke:#2e7d32
    style RALPH fill:#fff3e0,stroke:#e65100
    style ULW fill:#fce4ec,stroke:#c62828
    style DI fill:#f5f5f5,stroke:#616161
    style ASK fill:#ffffcc,stroke:#f9a825
    style CCG fill:#e0f7fa,stroke:#00838f
    style SKILL fill:#fce4ec,stroke:#ad1457
</pre>

## 3-2. Command Summary

| Command | Description | When to use |
|--------|------|-----------|
| `/team` | Team-based pipeline (plan→design→execute→verify) | Structured development work |
| `/autopilot` | Fully autonomous execution | Fast implementation of clear requirements |
| `/ralph` | Retry until completion | Stubborn refactoring jobs |
| `/ultrawork` (`/ulw`) | Max parallelization | Bulk error fixes |
| `/deep-interview` | Socratic requirements analysis | Clarifying ambiguous requirements |
| `/ask` | Expert consultation with a specific model | Design review, risk analysis |
| `/ccg` | Codex + Gemini + Claude synthesis | Multi-perspective review |
| `/skill` | Skill management (add/remove/search) | Registering recurring patterns |

---

# [04] Team Mode — Team Orchestration

This is omc's **core feature**. It handles work in a plan → design → execute → verify → revise pipeline.

```
/team 3:executor "fix all TypeScript errors"
```

| Syntax | Meaning |
|------|------|
| `3:executor` | Deploy 3 executor agents |
| `"fix all ..."` | Task instruction |

### Usage from tmux CLI

```bash
omc team 2:codex "review auth module for security issues"
omc team 2:gemini "redesign UI components for accessibility"
omc team 1:claude "implement the payment flow"
```

### Status check and shutdown

```bash
omc team status auth-review      # Check status
omc team shutdown auth-review    # Shut down
```

---

# [05] Autopilot — Fully Autonomous Execution

When requirements are clear, run the whole thing autonomously from start to finish.

```
/autopilot "build a todo app"
```

Or natural-language shortcut:

```
autopilot: build a REST API for managing tasks
```

---

# [06] Ralph — Persistence Mode

**Doesn't give up** and keeps trying until completion. Good for complex refactors or migrations.

```
/ralph "refactor authentication module"
```

---

# [07] Deep Interview — Requirements Analysis

Use when requirements are unclear, or you want to scrutinize the design first.

```
/deep-interview "I want to build a task management app"
```

Through Socratic questioning, it:
- Surfaces hidden assumptions
- Measures clarity across multiple aspects
- Aims to **know exactly what to build before writing any code**

---

# [08] Ultrawork — Max Parallelization

Process bulk work with maximum parallelism.

```
/ultrawork "fix all errors"
```

Short form:

```
/ulw "fix all errors"
```

---

# [09] Ask & CCG — Expert Consultation

## 9-1. Ask — Single-Model Consultation

Request expert advice from a specific model.

```
/ask claude "review this migration plan"
/ask codex "identify architecture risks"
/ask gemini "propose UI design ideas"
```

Terminal CLI:

```bash
omc ask claude "review this migration plan"
omc ask codex --prompt "identify architecture risks"
omc ask gemini --prompt "propose UI ideas"
```

## 9-2. CCG — Triple-Model Synthesis

Combine the perspectives of Codex + Gemini + Claude.

```
/ccg "review this PR - architecture (Codex) and UI (Gemini)"
```

---

# [10] Skill System

omc lets you save recurring patterns as **Skills** for reuse.

## 10-1. Skill Storage Locations

| Scope | Path | Sharing | Priority |
|------|------|----------|---------|
| Project | `.omc/skills/` | Whole team (versioned) | High |
| User | `~/.omc/skills/` | All projects | Low |

## 10-2. Skill File Example

```yaml
# .omc/skills/fix-proxy-crash.md
---
name: Fix Proxy Crash
description: aiohttp proxy crashes on ClientDisconnectedError
triggers: ["proxy", "aiohttp", "disconnected"]
source: extracted
---
Wrap handler at server.py:42 in try/except ClientDisconnectedError...
```

## 10-3. Skill Management Commands

```
/skill list              # List skills
/skill add               # Add a new skill
/skill remove            # Remove a skill
/skill edit              # Edit a skill
/skill search            # Search skills
/learner                 # Auto-extract patterns
```

---

# [11] CLI Utilities

## 11-1. Terminal Commands

| Command | Description |
|--------|------|
| `omc setup` | Initial setup |
| `omc hud` | Real-time HUD status display |
| `omc doctor` | Diagnose and clear cache |
| `omc wait` | Check rate-limit status |
| `omc wait --start` | Enable auto-resume |
| `omc wait --stop` | Disable auto-resume |

## 11-2. Autoresearch — Automated Research

```bash
omc autoresearch
omc autoresearch --mission "improve startup performance" \
  --eval "npm test -- --run src/tests/perf.test.ts"
omc autoresearch init --topic "benchmark onboarding flow"
```

## 11-3. Notifications (Telegram/Discord/Slack)

Get notified when work completes.

```bash
# Telegram
omc config-stop-callback telegram --enable \
  --token <bot_token> --chat <chat_id>

# Discord
omc config-stop-callback discord --enable \
  --webhook <url>

# Slack
omc config-stop-callback slack --enable \
  --webhook <url>
```

---

# [12] In-Session Natural-Language Shortcuts

You can use natural language inside a Claude Code session instead of slash commands.

| Natural language | Action |
|--------|------|
| `autopilot: build me a todo app` | Run Autopilot |
| `ralph: refactor the auth module` | Run Ralph |
| `deepsearch for auth middleware` | Search the codebase |
| `ultrathink about this design` | Deep reasoning |
| `cancelomc` / `stopomc` | Abort execution |

---

# [13] Updating

```bash
# npm
npm i -g oh-my-claude-sisyphus@latest

# Plugin
/plugin marketplace update omc
/setup

# When something is wrong
/omc-doctor
```

---

# [14] Summary

| Use Case | Command | Description |
|------|--------|------|
| Structured development | `/team 3:executor "task"` | Team pipeline |
| Fast implementation | `/autopilot "task"` | Fully autonomous |
| Persistent work | `/ralph "task"` | Repeat until done |
| Bulk processing | `/ulw "task"` | Max parallelization |
| Requirements clarification | `/deep-interview "idea"` | Socratic analysis |
| Expert review | `/ask codex "review request"` | Single-model consultation |
| Multi-angle review | `/ccg "review request"` | Triple-model synthesis |

> Refs: [oh-my-claudecode GitHub](https://github.com/Yeachan-Heo/oh-my-claudecode) · [Official Docs](https://yeachan-heo.github.io/oh-my-claudecode-website)
