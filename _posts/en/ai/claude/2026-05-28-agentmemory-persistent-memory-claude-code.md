---
title: "agentmemory — Persistent Memory So Claude Code Remembers Your Work"
description: "An intro to agentmemory, which adds persistent memory to Claude Code so it stops forgetting context when a session ends. Covers installation, wiring into Claude Code, automatic capture/search usage, and how it works (memory pipeline, 4-tier consolidation)"
excerpt: "Claude Code forgets everything when a session ends. agentmemory auto-records your work via hooks and re-injects it next session, eliminating re-explaining"
date: 2026-05-28
categories: Claude
tags: [Claude Code, agentmemory, persistent-memory, MCP, hooks, memory, AI-coding-agent, CLAUDE.md, MEMORY.md, semantic-search, iii]
ref: agentmemory-persistent-memory-claude-code
---

:bulb: Every coding agent, Claude Code included, **forgets all context the moment a session ends.** You waste the first 5 minutes of every session re-explaining "our stack is X, auth uses JWT…". [agentmemory](https://github.com/rohitg00/agentmemory) is a **persistent memory** tool that records your work in the background and re-injects it into the next session, eliminating that repetition.
{: .notice--info}

:memo: agentmemory is built on the [iii engine](https://github.com/iii-hq/iii) and works not only with Claude Code but with any agent that supports hooks, MCP, or REST — Cursor, Gemini CLI, Codex CLI, and more.
{: .notice--warning}

---

# [01] Why You Need It — Claude Code Forgets Every Time

Claude Code ships with built-in memory like `CLAUDE.md` / `MEMORY.md`. So do Cursor (notepads) and Cline (memory bank). But those are like **sticky notes**. agentmemory is the **searchable database** that runs behind those sticky notes.

```text
Session 1: "Add auth to the API"
  Agent writes code, runs tests, fixes bugs
  agentmemory silently captures every tool use
  Session ends -> observations compressed into structured memory

Session 2: "Now add rate limiting"
  Agent already knows:
    - Auth uses JWT middleware in src/middleware/auth.ts
    - Tests in test/auth.test.ts cover token validation
    - You chose jose over jsonwebtoken for Edge compatibility
  Zero re-explaining. Starts working immediately.
```

## 1-1. vs Built-in Memory

| | Built-in (CLAUDE.md) | agentmemory |
|---|----------------------|-------------|
| Scale | 200-line cap | Unlimited |
| Search | Loads everything into context | BM25 + vector + graph (top-K only) |
| Token cost | 22K+ at 240 observations | ~1,900 tokens (92% less) |
| Cross-agent | Per-agent files | MCP + REST (any agent) |
| Observability | Read files manually | Real-time viewer on :3113 |

---

# [02] Installation

A global npm install is recommended, after which the `agentmemory` command works everywhere.

```bash
npm install -g @agentmemory/agentmemory
# If you hit EACCES on macOS/Linux system Node installs:
# sudo npm install -g @agentmemory/agentmemory

agentmemory          # start the memory server (:3111)
agentmemory demo     # seed sample sessions and prove recall
agentmemory stop     # tear it down
agentmemory remove   # uninstall everything it created
```

To try it without installing, `npx` also works.

```bash
npx @agentmemory/agentmemory
```

:warning: `npx` caches per-version. If a stale version is served, force the latest with `npx -y @agentmemory/agentmemory@latest` or clear the cache (`~/.npm/_npx`). A global install is more reliable.
{: .notice--warning}

Once the server is up, watch memory build live in the **real-time viewer** at `http://localhost:3113`.

---

# [03] Wiring Into Claude Code

## 3-1. Plugin Install (Recommended)

Start the memory server (`agentmemory`) in a separate terminal, then run the following inside Claude Code.

```text
/plugin marketplace add rohitg00/agentmemory
/plugin install agentmemory
```

This single install registers **12 auto hooks**, skills, and the `@agentmemory/mcp` stdio server (auto-wired via `.mcp.json`). With no extra config you immediately get **53 MCP tools** (`memory_smart_search`, `memory_save`, `memory_sessions`, etc.).

Verify the connection:

```bash
curl http://localhost:3111/agentmemory/health
```

## 3-2. Without the Plugin (--with-hooks)

To merge hooks directly instead of installing the plugin, use the command below. It adds hooks with absolute paths to `~/.claude/settings.json`; re-run it after upgrading agentmemory to refresh the paths.

```bash
agentmemory connect claude-code --with-hooks
```

:memo: The `/plugin install` path is recommended when possible. Wiring only MCP directly can break hook paths on upgrade.
{: .notice--warning}

---

# [04] Usage

## 4-1. Try It in 30 Seconds

```bash
# Terminal 1: start the server
npx @agentmemory/agentmemory

# Terminal 2: seed sample data and see recall in action
npx @agentmemory/agentmemory demo
```

`demo` seeds 3 realistic sessions (JWT auth, N+1 query fix, rate limiting) and runs semantic searches against them. Search "database performance optimization" and it finds the "N+1 query fix" — something plain keyword matching can't do.

## 4-2. Automatic Capture — Nothing to Do

Once wired up, no manual effort is needed. Every time a Claude Code hook fires, your work is recorded automatically, and relevant memory is injected into context at the start of the next session.

| Hook | Captures |
|------|----------|
| `SessionStart` | Project path, session ID (and injects relevant memory) |
| `UserPromptSubmit` | User prompts (privacy-filtered) |
| `PreToolUse` | File access patterns + enriched context |
| `PostToolUse` | Tool name, input, output |
| `PreCompact` | Re-injects memory before compaction |
| `Stop` / `SessionEnd` | Session summary and completion marker |

:bulb: Privacy comes first. API keys, secrets, and `<private>` tags are stripped before storage.
{: .notice--info}

## 4-3. Import Existing Claude Code History

You can bring existing Claude Code JSONL transcripts into memory.

```bash
# Import everything under ~/.claude/projects
npx @agentmemory/agentmemory import-jsonl

# Or import a single file
npx @agentmemory/agentmemory import-jsonl ~/.claude/projects/-my-project/abc123.jsonl
```

Imported sessions can be replayed from the viewer's **Replay** tab — prompts, tool calls, and responses on a scrubbable timeline (0.5×–4× speed).

---

# [05] Memory Scoping and Auto-Reference — A Common Misconception

It's easy to assume that "memory is automatically separated per client server (A/B/C), and follow-up work automatically references the earlier task's context." **That's only partly true.** Here is how it actually works.

## 5-1. The Boundary Is project + AGENT_ID, Not the Host

agentmemory does **not** automatically separate by physical client server. There are three scoping axes.

| Scope axis | Description | Default |
|------------|-------------|---------|
| `project` (primary scope) | The primary namespace that groups memories (e.g., a task/project name) | Specified per call |
| `AGENT_ID` (env) | Tags every write with a role (architect/dev, etc.) | No tag if unset |
| `AGENTMEMORY_AGENT_SCOPE` | `shared` (tags only; recall sees everything) / `isolated` (only your own) | `shared` |

:warning: If the MCP registration env only has URL and SECRET but no `AGENT_ID`, then when multiple clients write to the **same `project`, everything mixes into one store** (unscoped legacy — no tags, no filters). Server A's work and Server B's work are shared without separation.
{: .notice--warning}

To separate A/B/C, you must **explicitly specify a distinct value** per client/task.

- **Per-task separation**: pass a different `project` when calling `memory_save`
- **Per-server/role separation**: add `AGENT_ID=serverA` to the MCP env (and `AGENTMEMORY_AGENT_SCOPE=isolated` if needed)

## 5-2. Does Follow-up Work Auto-Reference the Earlier Context? — Conditional YES

Two conditions must both be met.

**Condition ①: Auto-injection requires the plugin (SessionStart hook).** The auto-injection seen in [04] is handled by the `SessionStart` hook that the plugin registers. **If only the MCP is registered, no auto-injection happens.** In that case Claude must explicitly call `memory_recall` / `memory_smart_search` during the work to pull the earlier records.

**Condition ②: You must query within the same scope.** The follow-up work must query with the **same `project` (or the same agent scope)** as the earlier work to hit the search. If you store under `project` A but query under `project` B, it may not match — and `isolated` mode is even stricter.

| Expectation | Reality |
|-------------|---------|
| "Server A's work is auto-separated under A" | ❌ Not automatic. You must specify `project`/`AGENT_ID`; otherwise it mixes |
| "Follow-up work auto-references the earlier context" | ⚠️ Conditional. Automatic with the plugin / explicit recall without it — and it must be the same scope |

:bulb: To actually implement the picture you want ("separation per server/task + automatic follow-up reference") — ① set `AGENT_ID` in each client's MCP env and assign a consistent `project` per task, and ② install the **plugin (SessionStart hook)** if you want automatic context injection. With MCP only, you must recall manually at the start of each task.
{: .notice--info}

---

# [06] How It Works

## 6-1. Memory Pipeline

```text
PostToolUse hook fires
  -> SHA-256 dedup (5min window)
  -> Privacy filter (strip secrets, API keys)
  -> Store raw observation
  -> LLM compress -> structured facts + concepts + narrative
  -> Vector embedding
  -> Index in BM25 + vector

Stop / SessionEnd hook fires
  -> Summarize session
  -> Knowledge graph extraction

SessionStart hook fires
  -> Load project profile (top concepts, files, patterns)
  -> Hybrid search (BM25 + vector + graph)
  -> Token budget (default: 2000 tokens)
  -> Inject into conversation
```

## 6-2. 4-Tier Memory Consolidation

Inspired by how the human brain consolidates memory during sleep.

| Tier | What | Analogy |
|------|------|---------|
| **Working** | Raw observations from tool use | Short-term memory |
| **Episodic** | Compressed session summaries | "What happened" |
| **Semantic** | Extracted facts and patterns | "What I know" |
| **Procedural** | Workflows and decision patterns | "How to do it" |

Frequently accessed memories strengthen, stale ones auto-evict (Ebbinghaus forgetting curve), and contradictions are detected and resolved.

---

# [07] Summary

| Item | Detail |
|------|--------|
| Core value | Keeps context across sessions, killing "re-explaining" |
| Install | `npm install -g @agentmemory/agentmemory` |
| Wire into Claude Code | `/plugin marketplace add` -> `/plugin install agentmemory` |
| Server / Viewer | `:3111` (REST) / `:3113` (real-time viewer) |
| External DBs | None (zero) |

:bulb: If you're tired of telling Claude Code "what we did yesterday" every single time, wire up agentmemory once. From then on the hooks record everything, and the next session starts on top of it.
{: .notice--info}

> Source and latest info: [github.com/rohitg00/agentmemory](https://github.com/rohitg00/agentmemory)
