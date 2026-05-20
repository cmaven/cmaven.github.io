---
title: "The Complete Claude Code Guide (Part 2): Project Application, Advanced Structures, FAQ"
description: "How to apply CLAUDE.md, Skill, and Hook to real projects, plus advanced skill structures, Agent Team collaboration, and FAQ."
excerpt: "How to apply CLAUDE.md, Skill, and Hook to real projects, plus advanced skill structures, Agent Team collaboration, and FAQ."
date: 2026-03-13
categories: Claude
tags: [Claude Code, Skill, Hook, CLAUDE.md, Agent]
ref: claude-code-skill-hook-guide-part2
---

:bulb: This post covers how to apply CLAUDE.md, Skill, and Hook to real projects, advanced skill structures, Agent Team collaboration, and FAQ.
{: .notice--info}

:bulb: For the concepts and usage of the 3 layers, see [Part 1](/claude/claude-code-skill-hook-guide-part1/).
{: .notice}

# [08] Applying to a Project (Step by Step)

## 8-1. Per-Project Install (Team-Shareable)

```shell
# 1. Go to the project
cd ~/my-web-app

# 2. Unzip fullstack-claude-setup.zip at the project root
unzip fullstack-claude-setup.zip

# 3. Make scripts executable
chmod +x .claude/skills/coding-workflow/scripts/*.sh

# 4. Edit CLAUDE.md for your actual project
nano CLAUDE.md

# 5. Add to git (share with the team)
git add CLAUDE.md .claude/
git commit -m "chore: add Claude Code workflow setup"
```

Resulting directory:

```
my-web-app/
├── CLAUDE.md                           <- edited project context
├── .claude/
│   ├── settings.json                   <- 4 Hooks
│   └── skills/coding-workflow/
│       ├── SKILL.md                    <- 4 rules
│       ├── agents/code-reviewer.md
│       ├── references/ (4 files)
│       └── scripts/ (2 shell scripts)
├── frontend/
├── backend/
└── ...
```

## 8-2. Global Install (Auto-Applied to All Projects)

```shell
# 1. Install the skill globally (once)
mkdir -p ~/.claude/skills
cp -r coding-workflow ~/.claude/skills/coding-workflow
chmod +x ~/.claude/skills/coding-workflow/scripts/*.sh

# 2. Add Hooks to the global settings.json (once)
# Write Hook JSON into ~/.claude/settings.json

# 3. After that, just write CLAUDE.md in each project
cd ~/project-a && nano CLAUDE.md
cd ~/project-b && nano CLAUDE.md
```

## 8-3. Recommended Strategy

| Install Location | Target | Notes |
|---|---|---|
| Global (`~/.claude/`) | Skill + Hook | Install once, shared across all projects |
| Per-project (`my-app/`) | CLAUDE.md | Different content per project |

If you work solo, global is easiest; for team work, include it at the project level in git.

---

# [09] Verifying It Works

## 9-1. claude.ai (web/app)

```
Settings > Capabilities > confirm Code execution is enabled
Customize > Skills > confirm the toggle is ON in the list
```

## 9-2. Claude Code (CLI)

```shell
# Debug mode — see skill loading and Hook execution in real time
claude --debug

# Inside a session, list hooks
/hooks

# Invoke a skill directly via slash command
/coding-workflow

# Verify file presence
ls ~/.claude/skills/coding-workflow/SKILL.md
```

## 9-3. Functional Testing

In a Claude Code session, ask for "create a simple function". If everything is applied correctly:

1. It checks out or creates the `claude-bot` branch
2. It adds a role-explaining comment at the top of the file
3. It commits using Conventional Commits format
4. After the response ends, Hooks automatically run comment checks/commits

## 9-4. When the Skill Doesn't Trigger

| Symptom | Fix |
|---|---|
| Skill isn't visible at all | Check the file path and that `SKILL.md` exists |
| Visible but doesn't auto-trigger | Make the `description` keywords more specific |
| Triggers only sometimes | Force a reminder via `UserPromptSubmit` Hook |
| Even slash command fails | Check the `name` field in frontmatter |

---

# [10] Skill's Advanced Structure: Progressive Disclosure

## 10-1. Simple Skill vs Advanced Skill

**Simple (SKILL.md only)**:
Rule-conveyance focused. Write "do it this way" and Claude reads and follows it.

**Advanced (with subdirectories)**:
SKILL.md becomes the commander, referencing subfiles at the right moment.

```
coding-workflow/
├── SKILL.md          <- Level 2: core rules + pointers to "what to read when"
├── agents/           <- Level 3: subagent instructions (code review, etc.)
├── references/       <- Level 3: detailed docs (comment formats, git commands, etc.)
├── scripts/          <- Level 3: executable code (called by Hook)
└── assets/           <- Level 3: templates, icons, static resources
```

## 10-2. Role of Each Directory

| Directory | Role | Load Timing |
|---|---|---|
| `agents/` | Instructions for tasks delegated to subagents | For specific tasks like review/analysis |
| `references/` | Reference docs loaded into context | When SKILL.md directs |
| `scripts/` | Shell/Python scripts to execute directly | When called by Hook or run by Claude |
| `assets/` | HTML templates, static files | During output generation |

---

# [11] Agent Team Collaboration Guide

A guide for organizing multiple agents into a team on Ubuntu 24.04 + Claude Code.

## 11-1. Recommended Team Structure

<pre class="mermaid">
graph TD
    O["Orchestrator\n(work distribution, review, integration)"]
    O --> FE["Frontend Agent\nclaude-bot/frontend"]
    O --> BE["Backend Agent\nclaude-bot/backend"]
    O --> DO["DevOps Agent\nclaude-bot/devops"]

    style O fill:#fff3e0,stroke:#e65100
    style FE fill:#e3f2fd,stroke:#1565c0
    style BE fill:#e8f5e9,stroke:#2e7d32
    style DO fill:#f3e5f5,stroke:#6a1b9a
</pre>

## 11-2. Collaboration Rules

1. **Each agent works on its own branch** (`claude-bot/<role>`)
2. **Use WORK_LOG.md as a shared medium** — read before work, write after
3. **State agent identifiers** — e.g., `[frontend-agent]`
4. **Mark files under modification** — in WORK_LOG.md
5. **Orchestrator merges** — periodically integrate branches

## 11-3. Benefits of Project-Level Install

Including the `.claude/` folder in git:

```shell
git add .claude/ CLAUDE.md
git commit -m "chore: add Claude workflow setup"
```

Whichever agent opens this project gets the **same Skills + Hooks** applied automatically.

---

# [12] Frequently Asked Questions (FAQ)

## Q: Do I need to copy CLAUDE.md into every project?

Yes. CLAUDE.md holds per-project context (tech stack, directory structure, etc.) and thus varies. Skills and Hooks, however, can be installed globally once and shared by all projects.

## Q: What if my Skill doesn't auto-trigger?

Realistically, Skill auto-triggering is not 100% reliable. That's why we pair it with Hooks. Use a `UserPromptSubmit` Hook to remind the skill rules every request.

## Q: How do I auto-generate diagrams after coding is done?

Three approaches:

| Level | Method | Characteristics |
|---|---|---|
| Level 1 | Ask "draw an architecture diagram" | No setup needed |
| Level 2 | Specify diagram rules in Skill | Consistent output |
| Level 3 | Add a prompt-type Stop Hook | Fully automated |

## Q: Does claude.ai (web) work the same way?

**No, there's a big difference.** On claude.ai web, only Skill is available; Hook and CLAUDE.md are Claude Code (CLI) only. For a detailed comparison, see section [03] of Part 1.

```
claude.ai web:  Skill only O (Hook X, CLAUDE.md X)
Claude Code:    Skill O + Hook O + CLAUDE.md O (all available)
```

## Q: Getting a zip error when uploading to claude.ai web?

The error "SKILL.md must be in the top-level folder" means the zip structure is wrong. claude.ai web requires SKILL.md to be right under the top-level folder:

```
## Correct structure (coding-workflow-for-web.zip):
coding-workflow/
├── SKILL.md          <- here (right under top-level folder)
├── agents/
└── references/

## Wrong structure (fullstack-claude-setup.zip):
.claude/skills/coding-workflow/
└── SKILL.md          <- too deep
```

`fullstack-claude-setup.zip` is for installing into a Claude Code project, not for web upload. Use a separate `coding-workflow-for-web.zip` for the web.

## Q: Are Skills different for claude.ai vs Claude Code?

The SKILL.md file format is identical. However, **packaging and feature scope differ**:

| Item | claude.ai web | Claude Code |
|---|---|---|
| Install | Zip upload (Customize > Skills) | Folder copy (`~/.claude/skills/`) |
| Zip structure | SKILL.md at top | Under `.claude/skills/` |
| Auto-trigger | O (description-based) | O + slash commands |
| Hook integration | X | O Hook calls `scripts/` |
| `agents/` | Limited (subagent restrictions) | O Fully supported |
| Debug | X | O `claude --debug` |

## Q: Do I have to keep both zip files?

If you plan to use Claude Code, install globally and then both zips can be deleted:

```shell
# Global install (once)
cp -r coding-workflow ~/.claude/skills/coding-workflow
# Add Hooks to ~/.claude/settings.json
# -> After this, you can delete the zip and just write CLAUDE.md for new projects
```

For claude.ai web only, upload `coding-workflow-for-web.zip`; after uploading you can delete the zip.

---

# [Appendix A] The 4 Rules of the coding-workflow Skill

| Rule | Content |
|---|---|
| Rule 1: File comments | Write role-explaining comments at the top of every file in the language-appropriate format |
| Rule 2: Git management | Work on the claude-bot branch, commit using Conventional Commits |
| Rule 3: Memory dump | Record changes (append only) to `.claude/WORK_LOG.md` during long work |
| Rule 4: Diagram generation | Update Mermaid diagrams in `.claude/diagrams/` when architecture/API changes |

---

# [Appendix B] Provided File List

| File | Purpose | Environment |
|---|---|---|
| `coding-workflow-for-web.zip` | Skill upload | claude.ai web |
| `fullstack-claude-setup.zip` | Full project setup | Claude Code |
| `claude-skill-hook-guide.md` | This blog post | Reference |
