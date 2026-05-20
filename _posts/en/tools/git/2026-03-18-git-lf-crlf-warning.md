---
title: "Git LF/CRLF Line-Ending Warning — Causes and Fixes"
description: "Cause of the 'LF will be replaced by CRLF' warning in Git, and how to resolve it via .gitattributes and core.autocrlf"
excerpt: "Analyzing the Git warning caused by line-ending differences (LF/CRLF) between Windows and Linux, and resolving it via .gitattributes and core.autocrlf settings"
date: 2026-03-18
categories: Git
tags: [Git, CRLF, LF, gitattributes, autocrlf, line-break, line-ending, Windows, Linux]
ref: git-lf-crlf-warning
---

:bulb: This post covers the cause of the `LF will be replaced by CRLF` warning that appears when `git add`-ing a file, and how to fix it.
{: .notice--info}

# [01] The Warning Message

```bash
git add filename
```

```
warning: in the working copy of 'filename', LF will be replaced by CRLF the next time Git touches it
```

# [02] Cause: OS Differences in Line-Ending Characters

Different operating systems use different newline (line break) characters in text files.

| OS | Line ending | Notation |
|---|---|---|
| Windows | CR + LF | `\r\n` |
| Linux / macOS | LF | `\n` |

- **CR** (Carriage Return): move the cursor to the start of the line
- **LF** (Line Feed): move the cursor to the next line

Internally Git uses **LF** as the standard. On Windows with `core.autocrlf` set to `true`, Git converts LF to CRLF on checkout — and the warning above is its way of saying so.

# [03] core.autocrlf Values

```bash
# Check the current setting
git config --global core.autocrlf
```

| Value | checkout (repo → working dir) | commit (working dir → repo) | Recommended environment |
|---|---|---|---|
| `true` | LF → CRLF conversion | CRLF → LF conversion | Windows-only projects |
| `input` | No conversion | CRLF → LF conversion | Linux/macOS, or cross-platform |
| `false` | No conversion | No conversion | When managing line endings manually |

# [04] How to Fix

## Option A: Configure via `.gitattributes` (recommended)

Create or edit a `.gitattributes` file at the repository root with the following content.

```
* text=auto eol=lf
```

| Attribute | Description |
|---|---|
| `text=auto` | Let Git auto-detect text files and normalize line endings |
| `eol=lf` | Unify line endings to LF for all text files |

> `.gitattributes` is included in the repository, so it **applies uniformly to all collaborators**, takes precedence over personal settings (`core.autocrlf`), and guarantees consistency.
{: .notice--info}

## Option B: Change Git's Global Setting

```bash
git config --global core.autocrlf input
```

Performs CRLF → LF conversion only on commit, with no conversion on checkout. The warning disappears.

> This setting **applies only to your personal environment**, so for team projects `.gitattributes` is recommended.
{: .notice--warning}

# [05] Bulk-Normalize Line Endings on Existing Files

After applying `.gitattributes`, run the following to apply it to existing files as well.

```bash
# Reset the Git index, then re-add
git rm --cached -r .
git reset --hard
```

If any files changed afterward, commit them.

# [06] Summary

| Method | Scope | Strength |
|---|---|---|
| `.gitattributes` | Whole repo (all collaborators) | Consistency guaranteed, version-controlled with Git |
| `core.autocrlf` | Personal environment | Quick to set |

**For cross-platform projects, setting `* text=auto eol=lf` in `.gitattributes` is the most reliable approach.**
