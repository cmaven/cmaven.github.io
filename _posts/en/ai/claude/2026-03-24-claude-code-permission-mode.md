---
title: "Claude Code's 5 Permission Modes: From Default to YOLO"
description: "Execution methods for Claude Code's 5 permission-delegation modes (default, Accept Edits, Plan, Bypass, YOLO) and a Docker-isolation safety guide."
excerpt: "A comparison of Claude Code's 5 permission modes, how to run them, real-world incident cases, and a Docker-isolation safety guide."
date: 2026-03-24
categories: Claude
tags: [Claude Code, permission, YOLO, bypassPermissions, Docker, permission-mode, auto-approve, safe-usage]
ref: claude-code-permission-mode
---

:bulb: Claude Code offers 5 permission modes. Choosing the right mode for the task at hand gives you both productivity and safety.
{: .notice--info}

# [01] The 5 Permission Modes

By default, Claude Code requests user approval for every tool execution (file edits, shell commands, etc.).
The **permission mode** controls how much approval is required.

| Mode | Command / How to switch | Description |
|------|---------------------|------|
| **Default** | `claude` | Asks for approval every time |
| **Accept Edits** | `Shift+Tab` (in-session) | Auto-approves file edits; still asks for shell commands |
| **Plan** | `claude --permission-mode plan` | Shows the full plan first, then executes |
| **Bypass** | `claude --permission-mode bypassPermissions` | Auto-approves all permissions |
| **YOLO** | `claude --dangerously-skip-permissions` | Same as Bypass, with a more intuitive name |

:bulb: `Shift+Tab` cycles through Default → Accept Edits → Plan during a session.
{: .notice--info}

---

# [02] Running Each Mode

## 2-1. Default Mode

```shell
claude
```

Asks for approval before every tool execution. Safest, but repetitive work creates approval fatigue.

## 2-2. Accept Edits Mode

Press `Shift+Tab` in-session to switch.

- **Auto-approved**: file read, edit, create
- **Approval required**: shell commands (`Bash` tool)

Suited for when you trust file edits but want to vet shell commands.

## 2-3. Plan Mode

```shell
claude --permission-mode plan
```

Claude **presents the entire plan first** before executing.
Once you review and approve the plan, execution begins.

Useful for complex refactors or cross-file work.

## 2-4. Bypass / YOLO Mode

```shell
# Interactive
claude --dangerously-skip-permissions

# One-shot (with -p)
claude --dangerously-skip-permissions -p "Fix all lint errors"
```

Auto-approves all tool executions. Since file edits and shell commands run without approval, **use only in isolated environments**.

### Blocking specific tools (partial restriction)

```shell
# Block rm-family commands while auto-approving the rest
claude --dangerously-skip-permissions \
  --disallowedTools "Bash(rm:*)" \
  "Refactor the Todo app"
```

---

# [03] Persistent Settings

## 3-1. Change Default Mode via settings.json

Skip flags every time by changing the default mode:

```json
// ~/.claude/settings.json
{
  "defaultMode": "bypassPermissions"
}
```

| Value | Mode |
|---|---|
| `"default"` | Default (approve each time) |
| `"acceptEdits"` | Accept Edits |
| `"plan"` | Plan |
| `"bypassPermissions"` | Bypass / YOLO |

## 3-2. Allow Specific Tools Only

You can also add specific tools to the auto-approve list in settings.json:

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Edit",
      "Write",
      "Glob",
      "Grep"
    ]
  }
}
```

This skips approval for frequently used tools without going full-YOLO.

---

# [04] Real-World Incidents

:warning: **Running YOLO mode without isolation can destroy your system.** Real reported cases follow.
{: .notice--danger}

## 4-1. Case 1 — System Directory Deletion (Oct 2025)

Developer Mike Wolak, while working with nested directories on Ubuntu/WSL2, saw Claude Code **run `rm -rf` at the root (`/`)**, attempting to delete entire system paths including `/bin`, `/boot`, `/etc`.

## 4-2. Case 2 — Home Directory Deletion (Dec 2025)

When another user asked for package cleanup, Claude Code ran:

```shell
rm -rf tests/ patches/ plan/ ~/
```

Since `~/` (home directory) was included, **all personal files were deleted**.

## 4-3. Lessons

Both incidents share one cause: **YOLO mode used without isolation**.
Claude Code is powerful, but a misread context can lead to unintended destructive commands.

---

# [05] Using It Safely — Docker Isolation

The official docs recommend using `bypassPermissions` mode **only inside isolated environments like containers or VMs**.

## 5-1. Docker-Isolated Execution

```shell
# 1. Always create a git checkpoint before running
git add -A && git commit -m "checkpoint before claude YOLO"

# 2. Run only inside a Docker container
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  --network none \
  ubuntu:22.04 \
  claude --dangerously-skip-permissions "Implement the feature"

# 3. Roll back if something goes wrong
git reset --hard HEAD
```

| Option | Role |
|------|------|
| `-v $(pwd):/workspace` | Mount only the current directory into the container |
| `--network none` | Block network (prevent external access) |
| `--rm` | Auto-remove the container when it exits |

## 5-2. Git Checkpoint Pattern

Even without Docker, follow at least this pattern when using YOLO mode:

```shell
# Commit -> YOLO mode -> review result -> commit or roll back
git add -A && git commit -m "before"
claude --dangerously-skip-permissions -p "Build the todo app"
git diff   # Inspect changes
git add -A && git commit -m "after"   # or git reset --hard HEAD
```

---

# [06] Recommended Mode by Situation

| Situation | Recommended Mode | Reason |
|------|-----------|------|
| Normal development (no approval fatigue) | Default | Safest |
| Tired of approving every time | `Shift+Tab` (Accept Edits) | Auto file edits, manual shell |
| Complex work, want to see the plan first | `--permission-mode plan` | Review the full plan before execution |
| Automated pipeline, CI/CD | `--dangerously-skip-permissions` | Required when no human is present |
| Solo development, long autonomous runs | Docker isolation + YOLO | Full approval only inside isolation |

:warning: **Running YOLO/Bypass directly on the host OS is dangerous.** Always combine with Docker/VM isolation, or at minimum a git checkpoint.
{: .notice--danger}
