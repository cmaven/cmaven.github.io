---
title: "Git Branch vs Tag — Differences and Usage Strategy"
description: "Understanding the difference between Git branches and tags, and which to use in which situation"
excerpt: "Branch is a moving pointer, tag is a fixed pointer — how to use each for development flow and release management"
date: 2026-03-26
categories: Git
tags: [Git, branch, tag, release, version-control, lightweight-tag, annotated-tag, branching-strategy]
ref: git-branch-vs-tag
---

:bulb: Both branches and tags in Git are pointers to commits, but their purposes and behaviors differ. This post organizes the differences and practical usage of each.
{: .notice--info}

# [01] The Core Difference: Moving Pointer vs Fixed Pointer

```
          branch (moves)
              ↓
  A ← B ← C ← D ← E     ← when a new commit is added, branch follows
              ↑
          tag v1.0 (fixed)   ← tag always points to C
```

| Aspect | Branch | Tag |
|------|--------|-----|
| **Essence** | Moving pointer | Fixed pointer |
| **When a commit is added** | Automatically follows the latest commit | Stays pinned to the commit at creation time |
| **Purpose** | Development flow (branching work) | Recording a specific moment (release, milestone) |
| **Lifetime** | Typically deleted after merge | Kept permanently |
| **Analogy** | Sticky note (can be moved) | Stamp (fixed once applied) |

---

# [02] Branch — Separating Development Flows

## 2-1. Concept

A branch is a tool for **separating work**. You can develop features, fix bugs, and experiment without affecting the main code.

```bash
# Create and switch to a branch
git checkout -b feature/login

# Work and commit
git add .
git commit -m "implement login feature"

# Merge into main
git checkout main
git merge feature/login

# Delete after the merge completes
git branch -d feature/login
```

## 2-2. When to Use Branches

| Situation | Example branch name |
|------|-----------------|
| New feature development | `feature/login`, `feature/search` |
| Bug fix | `fix/login-error`, `hotfix/payment` |
| Experiment / prototype | `experiment/new-ui`, `spike/redis` |
| Release preparation | `release/1.2.0` |
| Environment separation | `develop`, `staging` |

## 2-3. Listing Branches

```bash
# Local branches
git branch

# All branches including remote
git branch -a

# Only merged branches (candidates for deletion)
git branch --merged
```

---

# [03] Tag — Recording a Specific Moment

## 3-1. Concept

A tag is a tool that **pins a specific commit with a name**. Use it for release versions, deployment points, milestones — anytime you want to say "remember this point".

```bash
# Create a tag (on the current commit)
git tag v1.0.0

# Push the tag to the remote
git push origin v1.0.0
```

## 3-2. Lightweight Tag vs Annotated Tag

Git has two kinds of tags.

### (A) Lightweight Tag — a simple pointer

```bash
git tag v1.0.0
```

Creates only a pointer to a commit. It has no metadata such as author, date, or message.

### (B) Annotated Tag — includes metadata (recommended)

```bash
git tag -a v1.0.0 -m "first official release"
```

| Included info | Example |
|-----------|------|
| Tag name | `v1.0.0` |
| Author | `user <user@email.com>` |
| Creation date | `2026-03-26` |
| Message | `first official release` |

:bulb: **Annotated tags are recommended.** They record who tagged this moment, when, and why. GitHub Releases also operates on annotated tags.
{: .notice--info}

## 3-3. When to Use Tags

| Situation | Example tag name |
|------|---------------|
| Official release | `v1.0.0`, `v2.1.3` |
| Beta / RC release | `v1.0.0-beta.1`, `v1.0.0-rc.1` |
| Deployment record | `deploy-2026-03-26` |
| Milestone | `milestone-mvp`, `sprint-5-done` |

## 3-4. Tag-Related Commands

```bash
# List tags
git tag

# Filter by pattern
git tag -l "v1.*"

# Show tag details
git show v1.0.0

# Tag a past commit
git tag -a v0.9.0 -m "beta release" abc1234

# Push all tags to the remote
git push origin --tags

# Delete a tag (local)
git tag -d v1.0.0

# Delete a tag (remote)
git push origin --delete v1.0.0

# Check out the state of a specific tag
git checkout v1.0.0
```

:warning: Checking out a tag puts you in **detached HEAD** state. Commits made in this state belong to no branch, so create a branch if you need to do work.
{: .notice--warning}

```bash
# Create a hotfix branch from a tag point
git checkout v1.0.0
git checkout -b hotfix/v1.0.1
```

---

# [04] Practical Comparison: Which to Use in the Same Situation?

| Situation | Branch | Tag | Recommended |
|------|--------|-----|------|
| Starting login feature development | `feature/login` | - | **Branch** |
| v1.0.0 release shipped | - | `v1.0.0` | **Tag** |
| Critical bug found after release | `hotfix/payment` | - | **Branch** |
| Hotfix released after critical fix | - | `v1.0.1` | **Tag** |
| Starting development for the next version | `release/1.1.0` | - | **Branch** |
| "Let me come back to this commit" | - | `backup-before-refactor` | **Tag** |
| Forking code for an A/B test | `experiment/new-checkout` | - | **Branch** |

:bulb: **The rule of thumb is simple:**
- **Going to add commits going forward** → Branch
- **Want to pin this moment for memory** → Tag
{: .notice--info}

---

# [05] Practical Workflow Example

A typical development-release flow where branches and tags work together.

```bash
# 1. Feature development (branch)
git checkout -b feature/search
# ... work ...
git commit -m "implement search feature"

# 2. Merge into main
git checkout main
git merge feature/search
git branch -d feature/search

# 3. Release tag (tag)
git tag -a v1.2.0 -m "add search feature"
git push origin main --tags

# 4. Bug found after deploy → hotfix (branch)
git checkout -b hotfix/search-crash
# ... fix ...
git commit -m "fix search crash"

# 5. Merge + patch tag (tag)
git checkout main
git merge hotfix/search-crash
git branch -d hotfix/search-crash
git tag -a v1.2.1 -m "fix search crash"
git push origin main --tags
```

```
main:  A ─ B ─ C ─ D(merge) ─ E ─ F(merge)
              │         ↑              ↑
              │      v1.2.0         v1.2.1
              │
feature/search: C1 ─ C2
                         hotfix: E1
```

---

# [06] Semantic Versioning (Tag Naming)

It is standard to follow **Semantic Versioning (SemVer)** rules when naming tags.

```
v MAJOR . MINOR . PATCH
  │       │       │
  │       │       └─ bug fix (backward compatible)
  │       └───────── feature addition (backward compatible)
  └───────────────── breaking change
```

| Change | Version change | Example |
|-----------|-----------|------|
| Typo fix, bug fix | PATCH +1 | `v1.0.0` → `v1.0.1` |
| New feature (compatible) | MINOR +1 | `v1.0.1` → `v1.1.0` |
| API change (breaking) | MAJOR +1 | `v1.1.0` → `v2.0.0` |

---

# [07] Summary

| Item | Branch | Tag |
|------|--------|-----|
| **One-line summary** | Ongoing work flow | Snapshot of a completed point |
| **Pointer** | Moves automatically when commits are added | Fixed |
| **Created when** | Before work starts | After release/deployment completes |
| **Deletion** | Typically deleted after merge | Don't delete (kept permanently) |
| **Main use** | Branching for feature, fix, release | Version releases, milestones |
| **Push to remote** | `git push origin branch` | `git push origin tag` |

```
Branch = "in progress" marker
Tag    = "completed" stamp
```
