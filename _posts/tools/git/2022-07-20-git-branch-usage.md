---
title: "git clone으로 로컬 환경에 받은 저장소에서 브랜치(branch) 변경"
date: 2022-07-20
categories: Git
tags: [Clone, Branch]
---

로컬 환경에서 git clone으로 받은 원격 저장소(Repository)의 브랜치(branch) 생성, 변경 하기
------

> 원격 저장소를 받은 경우, 전체 branch가 표시되지 않는다.

### 전체 브랜치 확인

- 내려 받은 저장소 브랜치 확인 `git branch`  

```shell
git branch

''' 실행 예 '''
D:\githubblog\flask-app> git branch
* main
```  

- 전체 브랜치 확인 `git branch -a`  

```shell
git branch -a 

''' 실행 예 '''
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


### 브랜치 생성 후, 작업환경을 생성 브런치로 변경

- 기본 방법(2개 명령어 사용)  

```shell
git branch ${branch_name}
git checkout ${branch_name}

''' 실행 예 '''
D:\githubblog\flask-app> git branch
* main
D:\githubblog\flask-app> git branch test-branch-01
D:\githubblog\flask-app> git checkout test-branch-01
Switched to branch 'test-branch-01'
PS D:\githubblog\flask-app> git branch
  main
* test-branch-01
```  

- 한 번의 명령어로 생성 및 이동하기  

```shell
git checkout -b ${branchname}

''' 실행 예 '''
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

### 브랜치에서 작업 완료 후, main 에 병합

```shell
# 작업 내용 commit
git add *
git commit -m "comment"

git push
git checkout main
git merge ${branchname}
```  

