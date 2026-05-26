---
title: "Switching Branches in a Repository Cloned Locally with git clone"
description: "How to view, create, switch, and merge branches into main in a remote repository fetched via git clone"
excerpt: "How to create/switch branches with git branch and git checkout, then merge them into main"
date: 2022-07-20
last_modified_at: 2026-05-26
categories: Git
tags: [Git, branch, checkout, merge, clone, branch-switch, branch-create]
ref: git-branch-usage
---

:bulb: This note describes how to create and switch branches in a remote repository cloned to a local environment with git clone.
{: .notice--info}

# [01] List All Branches

## 1-1. List branches in the cloned repository

```shell
git branch

# example
D:\githubblog\flask-app> git branch
* main
```

## 1-2. List all branches (including remote)

```shell
git branch -a

# example
D:\githubblog\flask-app> git branch -a
PS D:\githubblog\flask-pybo> git branch -a
* main
  remotes/origin/2-04
  remotes/origin/2-05
  remotes/origin/2-06
  remotes/origin/2-07
  remotes/origin/2-08
  remotes/origin/2-09
  remotes/origin/2-10
  remotes/origin/3-01
  remotes/origin/3-02
  remotes/origin/3-03
  remotes/origin/3-04
  remotes/origin/3-05
  remotes/origin/3-06
  remotes/origin/3-07
  remotes/origin/HEAD -> origin/main
  remotes/origin/main
```

:bulb: After cloning a remote repository, `git branch` alone does not show all branches. Use `git branch -a` instead.
{: .notice--info}

# [02] Create and Switch Branches

## 2-1. Basic method (two commands)

```shell
git branch ${branch_name}
git checkout ${branch_name}

# example
D:\githubblog\flask-app> git branch
* main
D:\githubblog\flask-app> git branch test-branch-01
D:\githubblog\flask-app> git checkout test-branch-01
Switched to branch 'test-branch-01'
PS D:\githubblog\flask-app> git branch
  main
* test-branch-01
```

## 2-2. Create and switch in a single command

```shell
git checkout -b ${branchname}

# example
D:\githubblog\flask-pybo> git branch
  main
* test-branch-01
D:\githubblog\flask-pybo> git checkout -b test-branch-02
Switched to a new branch 'test-branch-02'
D:\githubblog\flask-pybo> git branch
  main
  test-branch-01
* test-branch-02
```

# [03] Merge Branch Work Back into main

```shell
# commit the work
git add *
git commit -m "comment"

git push
git checkout main
git merge ${branchname}
```
