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

## 3-3. Local vs Remote Server — Where Your Data Lives

Sections [02] and [03-1] both assume a **local server**: run `agentmemory` on your own PC and memory is stored on that PC. But to share memory across a team, or across multiple machines, you connect to a **remote server** instead.

| Mode | Server location | Where data is stored | When to use |
|------|-----------------|----------------------|-------------|
| Local | Your PC (`agentmemory` directly) | Your PC | Solo, single machine |
| Remote | An always-on separate server (e.g. `10.0.0.10:3111`) | **That remote server** | Team-shared / multi-machine |

In remote mode, **no data is stored on your PC.** Local `~/.agentmemory/` holds *connection info only* (even `standalone.json` stays nearly empty).

```bash
# ~/.agentmemory/.env — connection info (not data)
AGENTMEMORY_URL=http://10.0.0.10:3111   # remote server address
AGENTMEMORY_SECRET=<your issued secret>       # auth token
AGENT_ID=alice-laptop                            # this client's/role's identifier
AGENTMEMORY_AGENT_SCOPE=isolated              # isolated=only yours / shared=everyone
```

All observations, sessions, and summaries accumulate in the remote server's store (KV). So you can switch machines and still reach the same memory as long as you have the same `.env`.

### Verifying Remote Storage Works

**① Check the server connection (health)** — pass the secret via `Authorization: Bearer`.

```bash
source ~/.agentmemory/.env
curl -s -H "Authorization: Bearer $AGENTMEMORY_SECRET" \
  "$AGENTMEMORY_URL/agentmemory/health" | jq .status
# "healthy" means the remote server is fine (no jq? just read the full response)
```

:warning: Hitting `/agentmemory/health` without the secret returns `{"error":"unauthorized"}`. The auth header must be `Authorization: Bearer <SECRET>` — headers like `x-agentmemory-secret` are rejected.
{: .notice--warning}

**② Check that data is actually accumulating** — in the Claude Code window, run `/session-history` or `/recall <keyword>` and stored sessions come back. To inspect via REST directly:

```bash
curl -s -H "Authorization: Bearer $AGENTMEMORY_SECRET" \
  "$AGENTMEMORY_URL/agentmemory/sessions?limit=5"
# {"sessions":[...]} — empty means nothing is stored under this scope (AGENT_ID/SCOPE) yet
```

:bulb: With `AGENTMEMORY_AGENT_SCOPE=isolated`, you only see what **your `AGENT_ID` saved**. If you clearly did work but `sessions` looks empty — ① the `AGENT_ID` differs between save and query, or ② the auto-capture hook (plugin) isn't wired so nothing was stored in the first place. Scope behavior is covered in [05].
{: .notice--info}

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

## 4-4. Slash Commands — Working With Memory Directly

Automatic capture runs in the background, but for the times you want to **query, save, or manage** memory yourself, the plugin registers a set of slash commands. You can type a command directly, or just say one of the natural-language triggers in the table (e.g., "recall", "where were we") and Claude Code invokes the matching command for you.

**① Query & save — the everyday set you'll reach for most**

| Command | Role | When / trigger phrases |
|---------|------|------------------------|
| `/recall` | Search past observations, sessions, and learnings about a topic | "recall", "remember", "what did we do" — when you need context from past sessions |
| `/remember` | **Explicitly** save an insight, decision, or learning to long-term storage | "remember this", "save this" — when you want to preserve knowledge for future sessions |
| `/recap` | Summarize the last N sessions, **grouped by date** | "recap", "this week", "today" — when you want a rollup of recent work |
| `/session-history` | Show an overview of what happened in recent sessions on this project | "what did we do last time", "past sessions" — when you want a sweep of previous work |
| `/handoff` | **Resume the most recent session** for the current working directory | "where were we", "resume", "pick up where I left off" — when starting with no fresh context |

**② Delete — for privacy and cleanup**

| Command | Role | When / trigger phrases |
|---------|------|------------------------|
| `/forget` | Delete specific observations or sessions from memory | "forget this", "delete memory" — when removing specific data for privacy |

**③ Commit ↔ session tracing — for recovering the "why" behind code**

| Command | Role | When / trigger phrases |
|---------|------|------------------------|
| `/commit-context` | Trace a file, function, or line back to the **agent session that produced its current commit** | "why is this code here", "what was the agent doing when this changed" — when you want context on a location |
| `/commit-history` | List recent **git commits linked to agent sessions** (filterable by branch/repo) | "show agent commits", "what has the agent shipped" — when you want commits with their session context |

:bulb: `/remember` (explicit save) and the automatic capture from [04-2] are complementary. Pin down must-keep items like key decisions with `/remember`, and let the hooks accumulate everything else from day-to-day work.
{: .notice--info}

## 4-5. A Day in the Claude Code Window — Real Workflow

The commands don't click in isolation, so here they are woven into **an actual day of work**. Most of the time you just code (auto-capture); you only type a command at the moments in bold.

```text
[Morning] Pick up yesterday
  > /handoff
  -> Restores "was working on auth middleware, introduced jose" context
     (or "what did we do last week?" -> /recap)

[While working] Code as usual
  Write code, run tests, fix bugs -> hooks capture it (nothing to do)

[At a decision] Pin down only what matters
  > /remember Using Upstash instead of Redis for the rate limiter — serverless compat
  -> Long-term save. The next session starts on top of this decision

[When stuck] Pull in past context
  > /recall where did we do JWT validation
  -> Returns src/middleware/auth.ts, test/auth.test.ts and the decisions made then

[Why is this code like this] Trace commit -> session
  > /commit-context src/middleware/auth.ts:42
  -> What the agent was doing in the session that produced this line

[Cleanup] Delete sensitive or unneeded memory
  > /forget   (remove specific observations/sessions)
```

:bulb: The point is "**automatic by default, manual only at decisive moments**." `/remember` pins plus the hooks' auto-capture combine to make the next session's `/handoff` and `/recall` richer.
{: .notice--info}

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
