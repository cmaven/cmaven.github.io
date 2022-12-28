---
title: "git commit 결과를 기간에 따라 나누어 보기"
date: 2022-10-31
categories: Git
tags: [Git_Shortlog]
---

Git Commit 결과를 일정 시간 범위로 확인하고 싶을 때
------

> ex) 2022년의 Contributor 별 Commit 수는?

### shortlog  
- `git log` 결과에 대한 요약된 출력을 제공


#### 특정 기간 동안 커밋(Commit) Author 및 수 확인
```shell
git shortlog -sne --since={$날짜} --before={$날짜}

# ex) 2022년 동안 Contributor 별 Commit 수
root@master:~/tools# git shortlog -sne --since="01 Jan 2022" --before="30 Dec 2022"
   198  aaa <aaa@naver.com>
    65  bbb <bbb@naver.com>
    48  ccc <ccc@naver.com>
```

#### 특정 기간 동안 전체 커밋(Commit) 수 확인
- `awk` 명령어와 조합

```shell
# current branch
git shortlog -sne --since={$날짜} --before={$날짜} | awk '{sum += $1} END {print sum}'

# all branch
git shortlog --all -sne --since="01 Jan 2022" --before="30 Dec 2022" | awk '{sum += $1} END {print sum}'

# without merge commit
git shortlog --all --no-merges -sne --since="01 Jan 2022" --before="30 Dec 2022" | awk '{sum += $1} END {print sum}'

# ex) 2022년 동안 Contributor 별 Commit 수
root@master:~/tools# git shortlog -sne --since="01 Jan 2022" --before="30 Dec 2022" | awk '{sum += $1} END {print sum}'
311
```  

- `--all`은 현재 Repository의 모든 branch에 대한 log 정보를 가져온다.
- `--nomerges`의 경우, branch 간 merger commit으로 발생한 commit은 제외한다.


[참조][Git-shortlog](https://git-scm.com/docs/git-shortlog){: target="_blank"}   
[참조][Git number of commits per author on all branches](https://stackoverflow.com/questions/9839083/git-number-of-commits-per-author-on-all-branches){: target="_blank"}   
