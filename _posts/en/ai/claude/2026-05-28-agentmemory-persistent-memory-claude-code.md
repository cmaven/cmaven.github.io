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

# [05] How It Works

## 5-1. Memory Pipeline

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

## 5-2. 4-Tier Memory Consolidation

Inspired by how the human brain consolidates memory during sleep.

| Tier | What | Analogy |
|------|------|---------|
| **Working** | Raw observations from tool use | Short-term memory |
| **Episodic** | Compressed session summaries | "What happened" |
| **Semantic** | Extracted facts and patterns | "What I know" |
| **Procedural** | Workflows and decision patterns | "How to do it" |

Frequently accessed memories strengthen, stale ones auto-evict (Ebbinghaus forgetting curve), and contradictions are detected and resolved.

---

# [06] Summary

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
