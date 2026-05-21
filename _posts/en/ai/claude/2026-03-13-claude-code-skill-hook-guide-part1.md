---
title: "The Complete Claude Code Guide (Part 1): Understanding CLAUDE.md, Skill, and Hook"
description: "How to solve the problem of rules conveyed via conversation being pushed out of context in Claude Code, using three layers: CLAUDE.md, Skill, and Hook."
excerpt: "Three layers for keeping rules in place when developing with Claude Code: CLAUDE.md, Skill, and Hook — concepts, usage, and the optimal combination."
date: 2026-03-13
categories: Claude
tags: [Claude Code, Skill, Hook, CLAUDE.md, Agent]
ref: claude-code-skill-hook-guide-part1
---

:bulb: When coding with Claude Code, rules conveyed only through chat tend to fall out of the context window. This post explains how to solve that with three layers — CLAUDE.md, Skill, and Hook. Part 1 covers the concept and usage of each layer, plus the optimal combination.
{: .notice--info}

:bulb: Project application, verification methods, advanced structures, Agent Team collaboration, and FAQ are covered in [Part 2](/en/claude/claude-code-skill-hook-guide-part2/).
{: .notice}

# [01] Why Is This Needed?

If you've coded with Claude Code, you've probably hit these issues:

- Claude created a file, and later you have no idea what it's for
- During a long chat, Claude forgets what it did early on
- Multiple agents modify the same file and conflict
- You said "always add comments", but from the 3rd file onward, it stops

These all share one root cause: **you're conveying "rules" to Claude only through conversation.**

Conversation-based rules disappear once they're pushed out of the context window.
Solving this is what the three layers — CLAUDE.md, Skill, Hook — are for.

---

# [02] Understanding the 3 Layers

<pre class="mermaid">
block-beta
    columns 1
    block:layer1:1
        A["CLAUDE.md → 'What this project is' (context)\nAuto-loaded at session start | differs per project"]
    end
    block:layer2:1
        B["Skill → 'Do it this way' (detailed instructions)\nLoaded on trigger keyword match | reusable across projects"]
    end
    block:layer3:1
        C["Hook → 'This MUST run' (enforced)\n100% execution on event | shell-script automation"]
    end

    style layer1 fill:#e1f5fe
    style layer2 fill:#fff3e0
    style layer3 fill:#fce4ec
</pre>

**Key differences:**

| Trait | CLAUDE.md | Skill | Hook |
|---|---|---|---|
| Execution guarantee | Suggestion | Unstable auto-trigger | 100% executed |
| Flexibility | Free form | Complex workflows | Single command |
| Setup difficulty | Very easy | Easy | Medium |
| Scope | That project | Global or project | Global or project |

---

# [03] claude.ai Web vs Claude Code — Feature Differences

The CLAUDE.md, Skill, and Hook explained in this guide **do not behave the same in every environment.** Not knowing this leads to wasted time wondering "why isn't this working?"

## 3-1. Feature Support by Environment

| Feature | claude.ai (web/app) | Claude Code (CLI) |
|---|---|---|
| CLAUDE.md | X Not available | O Auto-loaded at session start |
| Skill | O Uploadable | O Installed via folder copy |
| Hook | X Not available | O 12 event types |
| Slash commands (/skill) | X None | O Supported |
| Debug mode | X None | O `claude --debug` |
| Subagents | Limited | O Usable via `agents/` |

## 3-2. What You Can Do on claude.ai Web

Only Skill works — and even that has limits:

- Upload `.zip` or `.skill` files via `Customize > Skills`
- Claude auto-references the skill when it detects a related task in conversation
- Subfiles (`references/`, `scripts/`) are accessible inside Claude's code execution environment, but they aren't "auto-executed" like Hooks

## 3-3. What You Can Do in Claude Code

**All three layers** work:

- CLAUDE.md -> auto-loaded at session start
- Skill -> auto-trigger + `/skill-name` slash command
- Hook -> 100% execution on event (shell command, prompt, agent)
- Subagent -> runs independently following instructions in the `agents/` directory
- Debug -> `claude --debug` shows real-time skill loading and Hook execution

## 3-4. Different Skill Upload Zip Structures

This is the most common mistake. **claude.ai web and Claude Code use different zip structures.**

**For claude.ai web upload** — SKILL.md right under the top-level folder:

```
coding-workflow.zip
└── coding-workflow/       <- top-level folder
    ├── SKILL.md           <- here!
    ├── agents/
    ├── references/
    └── scripts/
```

**For Claude Code projects** — the full project settings:

```
fullstack-claude-setup.zip
├── CLAUDE.md              <- project root
└── .claude/               <- settings folder
    ├── settings.json      <- Hook configuration
    └── skills/
        └── coding-workflow/
            ├── SKILL.md
            ├── agents/
            └── ...
```

:warning: If you upload the project-style zip to the web, you'll get "SKILL.md must be in the top-level folder". Always use the zip that matches its intended purpose.
{: .notice--warning}

## 3-5. How to Choose an Environment

| Situation | Recommended environment |
|---|---|
| Light coding while chatting | claude.ai web + Skill only |
| Serious project development | Claude Code + all 3 layers |
| Agent team setup | Claude Code + project-level install |

---

# [04] CLAUDE.md — Project Context

## 4-1. Role

Claude Code automatically reads `CLAUDE.md` from the project root at session start. Writing the project's context there lets Claude understand "what this project is" every session.

## 4-2. What to Write

```markdown
# CLAUDE.md

## Project Overview
- Name, type, tech stack

## Directory Structure
- Description of major folders and their purpose

## Core Rules
- File-comment rules
- Git branch/commit rules
- Code style rules

## Environment Variables
- Contents of .env.example

## Common Commands
- Dev server, tests, build, etc.

## Agent Team Composition (if applicable)
- Each agent's role and assigned branch
```

## 4-3. Key Points

- **It differs per project.** A React project and a FastAPI project will have different CLAUDE.md files.
- **Keep it concise.** Put detailed workflows in Skills; CLAUDE.md should hold only summaries.
- **Point to your Skills.** Like: "See `.claude/skills/coding-workflow/SKILL.md` for detailed rules."

---

# [05] Skill — Defining Detailed Workflows

## 5-1. Role

A Skill is a package that holds detailed instructions telling Claude "do this specific task this way". A `SKILL.md` file with YAML frontmatter (`name` + `description`) is its core.

## 5-2. Basic Structure

The simplest skill:

```
coding-workflow/
└── SKILL.md
```

Advanced skill (with subfiles):

```
coding-workflow/
├── SKILL.md              <- core rules + pointers to subfiles
├── agents/               <- subagent instructions (loaded as needed)
│   └── code-reviewer.md
├── references/           <- detailed docs (loaded as needed)
│   ├── annotation-formats.md
│   ├── git-cheatsheet.md
│   ├── work-log-template.md
│   └── diagram-templates.md
└── scripts/              <- executable code (called by Hook)
    ├── check-annotation.sh
    └── auto-commit.sh
```

## 5-3. Progressive Disclosure (3-Level Loading)

This is Skill's core design principle. Claude doesn't read all files at once:

| Level | Target | Load Timing | Tokens |
|---|---|---|---|
| Level 1 | `name` + `description` (metadata) | Always loaded | ~100 |
| Level 2 | `SKILL.md` body (core instructions) | Loaded on trigger | ~5K |
| Level 3 | `agents/`, `references/`, `scripts/` | Loaded only when needed | unlimited |

## 5-4. Writing SKILL.md Frontmatter

```yaml
---
name: coding-workflow
description: >
  Core workflow conventions a Claude agent must follow in coding projects.
  Automatically performs file comments on creation/edit, git branch management
  and commit tracking, and memory dumps of work logs (.md).
  This skill must be triggered for any coding work that writes code,
  creates/modifies/deletes files, or changes project structure.
---
```

:bulb: Write `description` concretely and "a bit aggressively". Claude tends to under-trigger skills.
{: .notice--info}

## 5-5. Referencing Subfiles from SKILL.md

Write this inside SKILL.md:

```markdown
## Reference Files

Read these files at the appropriate time and follow the detailed instructions:

- `references/annotation-formats.md` - per-language file comment formats
- `references/git-cheatsheet.md` - Git commands and conventions
- `agents/code-reviewer.md` - code review subagent instructions
```

Claude reads this directive and selectively loads only the files needed for the task. This provides rich instructions without wasting the context window.

## 5-6. Skill Install Locations

| Location | Scope | Team Sharing |
|---|---|---|
| `~/.claude/skills/` | All projects (global) | X (each user installs) |
| `project/.claude/skills/` | That project only | O (committed to git) |

**Recommendation**: Global + project together

```shell
# Install the skill globally once
cp -r coding-workflow ~/.claude/skills/coding-workflow

# Also place it at project level for team-shared projects
cp -r coding-workflow my-project/.claude/skills/coding-workflow
```

---

# [06] Hook — Enforcing Rules

## 6-1. Essential Difference Between Skill and Hook

```
Skill's instruction = "Please add comments"        -> Claude may or may not do it
Hook's command      = "Check comments after save"  -> Always runs, 100%
```

Think of Git's pre-commit hook. When a specific event occurs, the configured command runs automatically.

## 6-2. Main Hook Events

| Event | When | Typical Use |
|---|---|---|
| `SessionStart` | Session start | Environment setup, context load |
| `UserPromptSubmit` | Just before prompt submit | Inject skill rules, validate prompts |
| `PreToolUse` | Just before tool execution | Block risky operations (can deny!) |
| `PostToolUse` | After tool execution | Lint, format, comment check |
| `Stop` | Claude response done | Auto-commit, work log |
| `SubagentStop` | Subagent done | Validate subagent results |
| `Notification` | On notification | Slack/email notification integration |
| `PreCompact` | Just before context compaction | Conversation backup |

## 6-3. Three Handler Types

| Type | How | Use Case |
|---|---|---|
| `command` | Shell command | Linting, file checks, git commands |
| `prompt` | Send a prompt to Claude | Semantic judgment ("is there a security issue?") |
| `agent` | Spawn a subagent | Deep verification (with tool access) |

## 6-4. Hook Config File Locations

| Location | Scope |
|---|---|
| `~/.claude/settings.json` | All projects (global) |
| `project/.claude/settings.json` | That project + team-shared (git) |
| `project/.claude/settings.local.json` | That project + personal only |

## 6-5. Practical Hook Examples

### (A) UserPromptSubmit — Remind skill rules every request

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo 'INSTRUCTION: Follow the coding-workflow skill rules. (1) top-of-file comment (2) claude-bot branch (3) conventional commits (4) WORK_LOG.md dump'"
          }
        ]
      }
    ]
  }
}
```

### (B) PostToolUse — Check comments after file edit

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/skills/coding-workflow/scripts/check-annotation.sh"
          }
        ]
      }
    ]
  }
}
```

`matcher` is a regex. `Edit|Write|MultiEdit` means "when a file edit or write tool runs".

### (C) PreToolUse — Block sensitive-file edits

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'INPUT=$(cat); FILE=$(echo \"$INPUT\" | jq -r \".tool_input.file_path // empty\"); if [[ \"$FILE\" =~ \\.(env|secret|pem|key)$ ]]; then echo \"{\\\"hookSpecificOutput\\\":{\\\"hookEventName\\\":\\\"PreToolUse\\\",\\\"permissionDecision\\\":\\\"deny\\\",\\\"permissionDecisionReason\\\":\\\"Blocked sensitive file edit\\\"}}\"; fi'"
          }
        ]
      }
    ]
  }
}
```

:bulb: `PreToolUse` can **block** an action by returning JSON with `permissionDecision: "deny"`.
{: .notice--info}

### (D) Stop — Auto-commit when work is done

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/skills/coding-workflow/scripts/auto-commit.sh"
          }
        ]
      }
    ]
  }
}
```

## 6-6. Creating Hooks

### (A) /hooks command (GUI, easiest)

```
Inside a Claude Code session, type /hooks
-> Pick the event in the interactive UI -> enter matcher -> register the command
```

### (B) Edit settings.json directly

Write the JSON examples above into `.claude/settings.json`.

---

# [07] Optimal Combination of the 3 Layers

```
CLAUDE.md     -> Project context + summary of core rules
                "This project is React + Express, follow these rules"

Skill         -> Detailed workflows + examples + templates + subagents
                "Use this comment format, use this commit format"

Hook          -> Enforce rules + automatic verification
                "After save, check comments; when done, auto-commit"
```

Why all three?

- **CLAUDE.md alone**: rules get pushed out in long chats
- **Skill alone**: auto-triggering is unstable (~50%)
- **Hook alone**: shell commands can't express complex workflows
- **All three combined**: CLAUDE.md sets the context, Skill provides detailed instructions, Hook enforces execution

---

:bulb: Project application, verification, advanced structures, Agent Team collaboration, and FAQ continue in [Part 2](/en/claude/claude-code-skill-hook-guide-part2/).
{: .notice}
