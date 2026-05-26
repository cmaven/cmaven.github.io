---
title: "Viewing git commit Results Split by Time Range"
description: "How to use git shortlog to view per-contributor and total commit counts within a given period"
excerpt: "How to check period-based commit statistics with the git shortlog --since / --before options"
date: 2022-10-31
last_modified_at: 2026-05-26
categories: Git
tags: [Git, shortlog, commit, commit-statistics, Contributor, period-based-commits]
ref: git-commit-count
---

:bulb: This note explains how to inspect Git commit results within a specific time range.
{: .notice--info}

# [01] shortlog

> A command that provides a summarized view of `git log` output.

# [02] Check Commit Authors and Counts Within a Period

```shell
git shortlog -sne --since={$date} --before={$date}

# ex) commit count per contributor during 2022
root@master:~/tools# git shortlog -sne --since="01 Jan 2022" --before="30 Dec 2022"
   198  aaa <aaa@naver.com>
    65  bbb <bbb@naver.com>
    48  ccc <ccc@naver.com>
```

# [03] Check the Total Commit Count Within a Period

Combine with the `awk` command.

```shell
# current branch
git shortlog -sne --since={$date} --before={$date} | awk '{sum += $1} END {print sum}'

# all branch
git shortlog --all -sne --since="01 Jan 2022" --before="30 Dec 2022" | awk '{sum += $1} END {print sum}'

# without merge commit
git shortlog --all --no-merges -sne --since="01 Jan 2022" --before="30 Dec 2022" | awk '{sum += $1} END {print sum}'

# ex) total commit count during 2022
root@master:~/tools# git shortlog -sne --since="01 Jan 2022" --before="30 Dec 2022" | awk '{sum += $1} END {print sum}'
311
```

- `--all` pulls log information from all branches in the current repository.
- `--no-merges` excludes commits created by merging between branches.

:small_blue_diamond:Reference: [Git-shortlog](https://git-scm.com/docs/git-shortlog){:target="_blank"}
:small_blue_diamond:Reference: [Git number of commits per author on all branches](https://stackoverflow.com/questions/9839083/git-number-of-commits-per-author-on-all-branches){:target="_blank"}
