---
title: "Claude Code Superpowers Plugin — What, Why, Install/Uninstall, Usage, Examples"
description: "A guide to the Superpowers plugin for Claude Code: the structured skills workflow that enforces brainstorming, planning, TDD, and systematic debugging — covering why you need it, install/uninstall, slash commands, and real usage examples"
excerpt: "Stop coding first — Claude Code Superpowers enforces design, planning, and TDD. From install to brainstorm/write-plan/execute-plan examples"
date: 2026-07-23
categories: Etc
tags: [Claude Code, Superpowers, plugin, skills, TDD, brainstorm, write-plan, execute-plan, obra, AI-coding-agent, marketplace]
ref: claude-code-superpowers-plugin
---

:bulb: Claude Code writes code well out of the box, but it often **skips planning, tests, and verification and jumps straight into implementation**. [Superpowers](https://github.com/obra/superpowers) is a Claude Code plugin that pushes back against that habit and enforces a **systematic development workflow** — brainstorming → design → implementation plan → TDD → review — via composable skills.
{: .notice--info}

:memo: The official repo is [obra/superpowers](https://github.com/obra/superpowers). You can install it from Anthropic’s official marketplace or the author’s marketplace (`obra/superpowers-marketplace`). It also works with Cursor, Codex, OpenCode, and other agents; this post focuses on **Claude Code**.
{: .notice--warning}

**Environment**: Claude Code (build with `/plugin` marketplace support) / internet connection

---

# [01] What Plugin Is This

Superpowers is an **agentic software development methodology plus a library of composable skills**, built by Jesse Vincent / [Prime Radiant](https://primeradiant.com).

Once installed, Claude Code gets:

| Piece | What you get |
|-------|----------------|
| Skills | brainstorming, TDD, systematic-debugging, writing-plans, and more |
| Commands | `/superpowers:brainstorm`, `write-plan`, `execute-plan`, etc. |
| Agents | Preconfigured subagents such as code-reviewer |
| Hooks | Session-start bootstrap and context-aware skill activation |

The important part: these are closer to **mandatory workflows** than soft suggestions. Before a task, the agent checks for a matching skill and follows it when one applies.

## 1-1. The Basic Workflow

1. **brainstorming** — Before code: refine requirements with questions, present design in digestible sections
2. **using-git-worktrees** — After design approval: isolated branch/worktree and clean test baseline
3. **writing-plans** — Bite-sized tasks (2–5 minutes each) with file paths and verification steps
4. **subagent-driven-development** / **executing-plans** — Per-task subagents or batched execution with checkpoints
5. **test-driven-development** — Enforce RED → GREEN → REFACTOR
6. **requesting-code-review** — Review against the plan; Critical issues block progress
7. **finishing-a-development-branch** — Verify tests, then choose merge / PR / keep / discard

---

# [02] Why You Need It

Common Claude Code failure modes:

- Starts editing files **without agreeing on design or scope**
- Misses files during migrations / large refactors
- Claims “it should work” **without running verification**
- Debugs with **guess-and-patch** instead of root-cause investigation

Superpowers inserts skills at those moments so **skipping steps is hard**.

```text
Request only (stock Claude Code)
  "Add per-user API rate limiting"
  → Immediately edits middleware
  → Easy to miss tests, edge cases, auth interaction

With Superpowers
  → brainstorming: limits, storage, response shape, existing stack
  → writing-plans: per-file tasks + verification commands
  → TDD: failing test first
  → verification-before-completion: evidence before "done"
```

The philosophy in four lines:

- **Test-Driven Development** — tests first
- **Systematic over ad-hoc** — process over guessing
- **Complexity reduction** — YAGNI, simplicity first
- **Evidence over claims** — verify before declaring success

---

# [03] Installation

Install with slash commands **inside a Claude Code session**. It is not an npm package.

## 3-1. Official Marketplace (simplest)

```text
/plugin install superpowers@claude-plugins-official
```

Also listed on the [official Claude plugins page](https://claude.com/plugins/superpowers).

## 3-2. Superpowers Marketplace (author; includes related plugins)

```text
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

Pick one path. The core plugin is the same.

## 3-3. Install via UI

```text
/plugin
```

Open **Discover**, search for `superpowers`, and install.

## 3-4. Verify

After install, start a **new session** (skills load at session start).

```text
/plugin list
```

Or ask:

```text
Do you have superpowers?
```

If the agent confirms Superpowers and lists skills, you’re good. You may also see a session-start hook message such as `SessionStart:startup hook succeeded`.

## 3-5. Update

```text
/plugin update superpowers
```

---

# [04] Uninstall

Remove the plugin:

```text
/plugin uninstall superpowers
```

Also remove the author marketplace if you added it:

```text
/plugin marketplace remove obra/superpowers-marketplace
```

`claude-plugins-official` is Claude Code’s built-in marketplace — for Superpowers alone, `uninstall` is enough.

---

# [05] How to Use

## 5-1. Automatic Activation (default)

No extra config: matching skills **auto-trigger** from what you ask.

| You say something like… | Skill that often activates |
|-------------------------|----------------------------|
| "Design a new auth feature" | brainstorming |
| "This function crashes intermittently" | systematic-debugging |
| "Review my recent changes" | requesting-code-review |
| Implementation work | test-driven-development |
| "We're done" / success claims | verification-before-completion |

Force a skill explicitly:

```text
use brainstorming skill
use systematic-debugging skill
```

## 5-2. Slash Commands (explicit workflow)

For complex features and migrations, calling commands directly is more reliable.

| Command | Role |
|---------|------|
| `/superpowers:brainstorm` | Turn ideas into a design (before code) |
| `/superpowers:write-plan` | Write an implementation plan (short tasks) |
| `/superpowers:execute-plan` | Run the plan in batches with review checkpoints |

Recommended order:

```text
1. /superpowers:brainstorm
2. Approve the design
3. /superpowers:write-plan
4. Review the plan
5. /superpowers:execute-plan
```

## 5-3. Skills Library Snapshot

**Testing / Debugging**

- `test-driven-development` — RED-GREEN-REFACTOR
- `systematic-debugging` — 4-phase root-cause process
- `verification-before-completion` — no “done” without evidence

**Collaboration**

- `brainstorming`, `writing-plans`, `executing-plans`
- `subagent-driven-development`, `dispatching-parallel-agents`
- `requesting-code-review`, `receiving-code-review`
- `using-git-worktrees`, `finishing-a-development-branch`

**Meta**

- `using-superpowers` — intro to the skills system
- `writing-skills` — create custom skills

---

# [06] Usage Examples

## 6-1. New Feature — brainstorm → plan → execute

```text
/superpowers:brainstorm
I want per-user API rate limiting on the REST API.
Prefer Redis; return 429 when exceeded.
```

Typical flow:

1. Asks about limits, key design, auth interaction, exceptions
2. Presents design in short sections → you approve
3. `/superpowers:write-plan` produces file-level tasks + test/verify commands
4. `/superpowers:execute-plan` runs tasks; stops on Critical review findings

## 6-2. Bug — Systematic Debugging

```text
The payment webhook handler times out sometimes.
use systematic-debugging skill
```

Instead of blindly raising timeouts, the agent follows reproduce → logs/traces → hypotheses → minimal fix → verification.

## 6-3. Large Change — write-plan First

```text
/superpowers:write-plan
To enable cacheComponents in Next.js, list the files to change,
phase the work, and include verification commands per phase.
```

You get something closer to a real roadmap: **paths, before/after patterns, success criteria, rollback** — not a vague outline. Plans that live as files also survive session cuts.

## 6-4. Verify Before “Done”

```text
Rate limiting is implemented. Can we call it done?
```

With `verification-before-completion`, the agent should not declare success until it has **actually run** the relevant tests/build/manual checks and shown the output.

---

# [07] Troubleshooting

| Symptom | What to try |
|---------|-------------|
| `/plugin` not recognized | `npm update -g @anthropic-ai/claude-code`, restart |
| Marketplace add fails | Check network; verify `obra/superpowers-marketplace`; remove → re-add |
| Install fails | Confirm marketplace is registered; use full name `superpowers@...` |
| Skills missing | Start a **fresh session**, `/plugin list`, `/plugin update superpowers` |
| Auto-skills don’t fire | Call explicitly: `"use brainstorming skill"` |

Optional telemetry opt-out:

```bash
export SUPERPOWERS_DISABLE_TELEMETRY=1
# Also honors Claude Code DISABLE_TELEMETRY /
# CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC
```

---

# [08] Summary

| Item | Detail |
|------|--------|
| What | Structured skills/workflow plugin for Claude Code |
| Why | Steer “code first” habits toward design, TDD, and verification |
| Install | `/plugin install superpowers@claude-plugins-official` |
| Uninstall | `/plugin uninstall superpowers` |
| Core usage | brainstorm → write-plan → execute-plan, or auto skills |
| Refs | [GitHub](https://github.com/obra/superpowers) · [Install docs](https://obra-superpowers.mintlify.app/installation/claude-code) |

Overkill for one-line fixes. It shines on **new features, migrations, mysterious bugs, and multi-file refactors** — the work where coding first tends to cause accidents.
