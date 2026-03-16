---
title: "git commit 결과를 기간에 따라 나누어 보기"
description: "git shortlog로 특정 기간 동안의 Contributor별 커밋 수와 전체 커밋 수를 확인하는 방법"
excerpt: "git shortlog --since --before 옵션으로 기간별 커밋 통계를 확인하는 방법"
date: 2022-10-31
categories: Git
tags: [Git, shortlog, commit, 커밋통계, Contributor, 기간별커밋]
---

:bulb: Git Commit 결과를 일정 시간 범위로 확인하는 방법을 작성한다.
{: .notice--info}

# [01] shortlog

> `git log` 결과에 대한 요약된 출력을 제공하는 명령어

# [02] 특정 기간 동안 커밋(Commit) Author 및 수 확인

```shell
git shortlog -sne --since={$날짜} --before={$날짜}

# ex) 2022년 동안 Contributor 별 Commit 수
root@master:~/tools# git shortlog -sne --since="01 Jan 2022" --before="30 Dec 2022"
   198  aaa <aaa@naver.com>
    65  bbb <bbb@naver.com>
    48  ccc <ccc@naver.com>
```

# [03] 특정 기간 동안 전체 커밋(Commit) 수 확인

`awk` 명령어와 조합하여 사용한다.

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
- `--no-merges`의 경우, branch 간 merge commit으로 발생한 commit은 제외한다.

:small_blue_diamond:참조: [Git-shortlog](https://git-scm.com/docs/git-shortlog){:target="_blank"}
:small_blue_diamond:참조: [Git number of commits per author on all branches](https://stackoverflow.com/questions/9839083/git-number-of-commits-per-author-on-all-branches){:target="_blank"}
