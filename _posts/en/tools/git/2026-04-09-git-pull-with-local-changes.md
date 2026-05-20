---
title: "Preserving Local Changes During git pull — Using git stash"
description: "How to use git stash to run git pull without conflicts when there are local modifications on a production server"
excerpt: "Temporarily save local changes with git stash, pull, then restore — receive remote updates without merge conflicts"
date: 2026-04-09
categories: Git
tags: [Git, git-stash, git-pull, merge-conflict, production-server, preserve-local-changes]
ref: git-pull-with-local-changes
---

:bulb: This post covers how to receive remote changes without conflicts when you have local modifications (e.g., config files) on a production server.
{: .notice--info}

---

# [01] The Problem

On a production server, you've directly modified things like Docker configuration. Running `git pull` in this state may cause merge conflicts.

```bash
user@server:~/project$ git status
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   docker-compose.dev.yml
        modified:   package-lock.json

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        docs/2025/project-alpha/
        docs/2025/project-beta/
        docs/2026/project-gamma/
```

Meanwhile on the remote, a different file like `config.ts` has been changed. You want to keep your local edits to `docker-compose.dev.yml` and `package-lock.json` as-is, and pull only the remote changes.

```
Remote: config.ts changed
Local:  docker-compose.dev.yml, package-lock.json changed
        → different files, so this should work without conflicts
```

But running `git pull` directly:

```bash
user@server:~/project$ git pull
error: Your local changes to the following files would be overwritten by merge:
        package-lock.json
Please commit your changes or stash them before you can merge.
```

Git **refuses to pull when there are uncommitted changes**.

---

# [02] Solution: git stash

## 2-1. One-Line Command

```bash
git stash && git pull && git stash pop
```

That single line does it. What each step does:

| Step | Command | Action |
|------|------|------|
| 1 | `git stash` | Save local changes to a temporary stash |
| 2 | `git pull` | Download and apply remote changes |
| 3 | `git stash pop` | Restore the previously-stashed local changes |

## 2-2. Execution Result

```bash
# 1. Stash local changes
user@server:~/project$ git stash
Saved working directory and index state WIP on main: abc1234 latest commit message

# 2. Pull remote changes (works normally now that local is clean)
user@server:~/project$ git pull
Updating abc1234..def5678
Fast-forward
 config.ts | 5 +++--
 1 file changed, 3 insertions(+), 2 deletions(-)

# 3. Restore local changes
user@server:~/project$ git stash pop
On branch main
Changes not staged for commit:
        modified:   docker-compose.dev.yml
        modified:   package-lock.json

Dropped refs/stash@{0} (a1b2c3d4...)
```

Remote changes to `config.ts` are applied, and the local edits to `docker-compose.dev.yml` and `package-lock.json` are preserved.

---

# [03] git stash in Detail

## 3-1. How It Works

```
Working directory (modified files)
    ↓ git stash
Temporary stash (stash stack)    ← changes stored here
Working directory (clean state)  ← git pull is now possible
    ↓ git pull
Remote changes applied
    ↓ git stash pop
Restored from the temporary stash  ← local + remote changes coexist
```

## 3-2. Main Commands

| Command | Description |
|--------|------|
| `git stash` | Stash changes temporarily (tracked files only) |
| `git stash -u` | Stash including untracked files |
| `git stash list` | List saved stashes |
| `git stash show` | Show a summary of the most recent stash |
| `git stash show -p` | Show the diff of the most recent stash |
| `git stash pop` | Restore the most recent stash and delete it |
| `git stash apply` | Restore the most recent stash (without deleting) |
| `git stash drop` | Delete the most recent stash |
| `git stash clear` | Delete all stashes |

## 3-3. pop vs apply

| Command | Restore | Delete stash | Use case |
|------|------|-----------|------|
| `git stash pop` | Yes | Yes | Normal use (one-shot) |
| `git stash apply` | Yes | No | Applying the same change to multiple branches |

---

# [04] If stash pop Causes a Conflict

If local and remote modified **the same part of the same file**, `stash pop` causes a conflict.

```bash
user@server:~/project$ git stash pop
Auto-merging docker-compose.dev.yml
CONFLICT (content): Merge conflict in docker-compose.dev.yml
```

In that case:

```bash
# 1. Check conflicted files
git status

# 2. Resolve conflicts manually (open in an editor and clean up the <<<< ==== >>>> markers)
vi docker-compose.dev.yml

# 3. After resolving, clean up the stash
git stash drop
```

:warning: When `stash pop` results in a conflict, the stash is **not auto-deleted**. After resolving the conflict, delete it yourself with `git stash drop`.
{: .notice--warning}

---

# [05] Other Approaches

## 5-1. Stash Only Specific Files

When you want to stash only specific files instead of all changes:

```bash
# Stash only specific files
git stash push docker-compose.dev.yml package-lock.json

# After pull, restore
git pull
git stash pop
```

## 5-2. git pull --rebase --autostash

Git 2.9+ offers an option that handles stash automatically.

```bash
git pull --rebase --autostash
```

This one command performs `stash → pull → rebase → stash pop` automatically.

Make it permanent:

```bash
git config --global rebase.autoStash true
```

After this, plain `git pull --rebase` will apply stash/pop automatically.

---

# [06] Summary

| Situation | Command |
|------|--------|
| Preserve local changes + pull | `git stash && git pull && git stash pop` |
| Auto stash + rebase | `git pull --rebase --autostash` |
| Stash specific files only | `git stash push <file1> <file2>` |
| Stash pop conflict | Resolve manually, then `git stash drop` |

:bulb: In environments like a production server where local config files are modified, making `git stash && git pull && git stash pop` a habit lets you pull remote changes without worrying about conflicts.
{: .notice--info}
