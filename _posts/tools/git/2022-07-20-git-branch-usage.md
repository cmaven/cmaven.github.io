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