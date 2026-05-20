---
title: "Squashing Changes into the Previous Commit in Git (amend + force push)"
description: "How to edit the previous commit with git commit --amend and publish it to the remote via force push"
excerpt: "Modify commit content/message with git --amend, then safely force push with --force-with-lease"
date: 2026-03-12
categories: Git
tags: [Git, amend, force-push, force-with-lease, commit-edit, commit-message-change]
ref: git-amend-force-push
---

:bulb: When you want to modify the content or message of the most recent commit that has already been pushed to the remote, this post covers how to fold the change into the previous commit with `--amend` and force push.
{: .notice--info}

# [01] When to Use This

- Right after pushing to the remote, you find a **typo, missing file, or small fix**
- You want to **fix the commit message**
- You don't want to bloat history with a new commit

---

# [02] How to Do It

## 2-1. Edit Files and Stage Them

Edit the files you want to modify, then add them to the staging area.

```shell
git add path/to/modified_file
```

**Example output:**

```shell
$ git add _posts/2026-03-05-my-post.md
```

Completes silently on success.

---

## 2-2. Squash into the Previous Commit

### (A) Keep the existing commit message

```shell
git commit --amend --no-edit
```

**Example output:**

```
[main a9b8c7d] docs: add git author change post
 Date: Wed Mar 12 10:00:00 2026 +0900
 1 file changed, 5 insertions(+), 2 deletions(-)
```

### (B) Change the commit message as well

```shell
git commit --amend -m "docs: fix heading level in git post"
```

**Example output:**

```
[main b8c7d6e] docs: fix heading level in git post
 Date: Wed Mar 12 10:00:00 2026 +0900
 1 file changed, 5 insertions(+), 2 deletions(-)
```

### (C) Edit the message interactively in the editor

```shell
git commit --amend
```

An editor (vi, etc.) opens, letting you edit the existing commit message directly. Save and exit to apply.

:bulb: If you want to **change only the commit message** with no file changes, just run `git commit --amend -m "new message"` without `git add`.
{: .notice--info}

**Options:**

| Option | Description |
|---|---|
| `--amend` | **Fold changes into the previous commit** instead of creating a new one |
| `--no-edit` | Keep the existing commit message unchanged |
| `-m "message"` | Replace the commit message with the given content |
| (no option) | Open the editor to edit the existing message |

---

## 2-3. Force Push to the Remote

Since the commit that was already pushed has been modified, a normal push is rejected. A force push is required.

```shell
git push --force-with-lease origin main
```

**Options:**

| Option | Description |
|---|---|
| `--force-with-lease` | Allow force push only if no one else has pushed since your last fetch. Safer than `--force` |

**Example output:**

```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Writing objects: 100% (3/3), 320 bytes | 320.00 KiB/s, done.
Total 3 (delta 1), reused 0 (delta 0), pack-reused 0
To https://github.com/testuser/test-repo.git
 + a1b2c3d...a9b8c7d main -> main (forced update)
```

---

# [03] Full Flow Summary

```shell
# --- Keep file + message, just add more content ---
git add path/to/modified_file
git commit --amend --no-edit
git push --force-with-lease origin main

# --- Modify files + change the message ---
git add path/to/modified_file
git commit --amend -m "new commit message"
git push --force-with-lease origin main

# --- Change only the message, no file edits ---
git commit --amend -m "new commit message"
git push --force-with-lease origin main
```

---

# [04] Cautions

:warning: **Use freely only in solo repos.** On branches shared with teammates, always coordinate beforehand.
{: .notice--warning}

| Situation | Recommended approach |
|---|---|
| Solo repo / branch | Use `--amend` + `--force-with-lease` freely |
| Branch shared with teammates | Push a new commit instead (avoid amend) |

- `--amend` **changes the commit hash**, so if someone has already pulled, force pushing causes conflicts on their side.
- `--force-with-lease` is safer than `--force`, but it still overwrites the remote history.
- To modify a commit **older than the most recent one**, use `git rebase -i` instead.
