---
title: "git clone으로 로컬 환경에 받은 저장소에서 브랜치(branch) 변경"
description: "git clone으로 받은 원격 저장소에서 브랜치 확인, 생성, 변경 및 main에 병합하는 방법"
excerpt: "git branch, git checkout으로 브랜치 생성/변경 후 main에 merge하는 방법"
date: 2022-07-20
categories: Git
tags: [Git, branch, checkout, merge, clone, 브랜치변경, 브랜치생성]
---

:bulb: 로컬 환경에서 git clone으로 받은 원격 저장소(Repository)의 브랜치(branch)를 생성, 변경하는 방법을 작성한다.
{: .notice--info}

# [01] 전체 브랜치 확인

## 1-1. 내려 받은 저장소 브랜치 확인

```shell
git branch

# 실행 예
D:\githubblog\flask-app> git branch
* main
```

## 1-2. 전체 브랜치 확인

```shell
git branch -a

# 실행 예
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

:bulb: 원격 저장소를 받은 경우, `git branch`만으로는 전체 branch가 표시되지 않는다. `git branch -a`를 사용한다.
{: .notice--info}

# [02] 브랜치 생성 및 변경

## 2-1. 기본 방법 (2개 명령어 사용)

```shell
git branch ${branch_name}
git checkout ${branch_name}

# 실행 예
D:\githubblog\flask-app> git branch
* main
D:\githubblog\flask-app> git branch test-branch-01
D:\githubblog\flask-app> git checkout test-branch-01
Switched to branch 'test-branch-01'
PS D:\githubblog\flask-app> git branch
  main
* test-branch-01
```

## 2-2. 한 번의 명령어로 생성 및 이동

```shell
git checkout -b ${branchname}

# 실행 예
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

# [03] 브랜치에서 작업 완료 후 main에 병합

```shell
# 작업 내용 commit
git add *
git commit -m "comment"

git push
git checkout main
git merge ${branchname}
```
