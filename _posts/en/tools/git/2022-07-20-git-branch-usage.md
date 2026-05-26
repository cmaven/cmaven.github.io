---
title: "Switching Branches in a Repository Cloned Locally with git clone"
description: "How to view, create, switch, and merge branches in a remote repository fetched via git clone — covering git branch, checkout, and merge"
excerpt: "Create and switch Git branches with git branch and git checkout, then merge changes back into main"
date: 2022-07-20
last_modified_at: 2026-05-26
categories: Git
tags: [Git, branch, checkout, merge, clone, branch-switch, branch-create]
ref: git-branch-usage
---

:bulb: After cloning a remote repository, use `git branch -a` to see all remote branches, then `git checkout` to create and switch between them locally.
{: .notice--info}

# [01] List All Branches

## 1-1. List local branches only

```shell
git branch
```

Example output:

```shell
D:\githubblog\flask-app> git branch
* main
```

The `*` marks the currently active branch.

## 1-2. List all branches (including remote)

```shell
git branch -a
```

Example output:

```shell
D:\githubblog\flask-app> git branch -a
* main
  remotes/origin/2-04
  remotes/origin/2-05
  remotes/origin/2-06
  remotes/origin/HEAD -> origin/main
  remotes/origin/main
```

:bulb: After cloning a remote repository, `git branch` alone shows only locally checked-out branches. Use `git branch -a` to see all remote branches as well.
{: .notice--info}

| Command | Shows |
|---------|-------|
| `git branch` | Local branches only |
| `git branch -a` | Local + remote tracking branches |
| `git branch -r` | Remote tracking branches only |

# [02] Create and Switch Branches

## 2-1. Basic method (two commands)

```shell
git branch ${branch_name}
git checkout ${branch_name}
```

Example:

```shell
D:\githubblog\flask-app> git branch test-branch-01
D:\githubblog\flask-app> git checkout test-branch-01
Switched to branch 'test-branch-01'
D:\githubblog\flask-app> git branch
  main
* test-branch-01
```

## 2-2. Create and switch in a single command

```shell
git checkout -b ${branch_name}
```

Example:

```shell
D:\githubblog\flask-pybo> git checkout -b test-branch-02
Switched to a new branch 'test-branch-02'
D:\githubblog\flask-pybo> git branch
  main
  test-branch-01
* test-branch-02
```

> Modern Git (v2.23+) introduced `git switch` as a cleaner alternative: `git switch -c ${branch_name}` creates and switches in one step. Both `checkout -b` and `switch -c` work the same way.

# [03] Merge Branch Work Back into main

After completing work on a feature branch, merge it back into `main`:

```shell
# Stage and commit your changes on the feature branch
git add <file>
git commit -m "feat: describe your change"

# Push the branch to remote (optional)
git push

# Switch back to main and merge
git checkout main
git merge ${branch_name}
```

| Step | Command | Purpose |
|------|---------|---------|
| Stage changes | `git add <file>` | Mark files for commit |
| Commit | `git commit -m "..."` | Save snapshot to branch history |
| Switch | `git checkout main` | Return to main branch |
| Merge | `git merge ${branch_name}` | Integrate branch changes into main |

> If there are conflicts during merge, Git will mark the conflicting files. Open them, resolve the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`), then run `git add` and `git commit` to complete the merge.
