---
title: "Viewing git commit Results Split by Time Range"
description: "How to use git shortlog to view per-contributor and total commit counts within a given time period"
excerpt: "Check period-based commit statistics per contributor or total using git shortlog with --since and --before options"
date: 2022-10-31
last_modified_at: 2026-05-26
categories: Git
tags: [Git, shortlog, commit, commit-statistics, Contributor, period-based-commits]
ref: git-commit-count
---

:bulb: Use `git shortlog` with `--since` and `--before` to quickly audit commit activity by contributor or total count within any date range.
{: .notice--info}

# [01] What is git shortlog?

> `git shortlog` summarizes `git log` output, grouping commits by author — ideal for generating statistics reports.

Key flags used in this post:

| Flag | Meaning |
|------|---------|
| `-s` | Show only the commit count (suppress commit messages) |
| `-n` | Sort by number of commits, descending |
| `-e` | Show author email addresses |
| `--since` | Include commits after this date |
| `--before` | Include commits before this date |
| `--all` | Include commits from all branches |
| `--no-merges` | Exclude merge commits |

# [02] Check Commit Authors and Counts Within a Period

```shell
git shortlog -sne --since={$date} --before={$date}
```

Example — commit count per contributor during 2022:

```shell
root@master:~/tools# git shortlog -sne --since="01 Jan 2022" --before="30 Dec 2022"
   198  aaa <aaa@naver.com>
    65  bbb <bbb@naver.com>
    48  ccc <ccc@naver.com>
```

The output is sorted by commit count (highest first) and includes each author's email.

# [03] Check the Total Commit Count Within a Period

Pipe the output through `awk` to sum all counts:

```shell
# Current branch only
git shortlog -sne --since={$date} --before={$date} | awk '{sum += $1} END {print sum}'

# All branches
git shortlog --all -sne --since="01 Jan 2022" --before="30 Dec 2022" | awk '{sum += $1} END {print sum}'

# All branches, excluding merge commits
git shortlog --all --no-merges -sne --since="01 Jan 2022" --before="30 Dec 2022" | awk '{sum += $1} END {print sum}'
```

Example output:

```shell
root@master:~/tools# git shortlog -sne --since="01 Jan 2022" --before="30 Dec 2022" | awk '{sum += $1} END {print sum}'
311
```

- `--all` pulls log information from all branches in the current repository.
- `--no-merges` excludes commits created by merging between branches — useful when you want to count only meaningful work commits.

# [04] Date Format Tips

`git shortlog` accepts flexible date strings for `--since` and `--before`:

| Format | Example |
|--------|---------|
| Human-readable | `"01 Jan 2022"` |
| ISO 8601 | `"2022-01-01"` |
| Relative | `"6 months ago"` |
| Last N days | `"30 days ago"` |

> Use ISO 8601 format (`YYYY-MM-DD`) for scripting to avoid locale-dependent parsing issues.

:small_blue_diamond: Reference: [Git-shortlog](https://git-scm.com/docs/git-shortlog){:target="_blank"}  
:small_blue_diamond: Reference: [Git number of commits per author on all branches](https://stackoverflow.com/questions/9839083/git-number-of-commits-per-author-on-all-branches){:target="_blank"}

# [05] Notes

When sharing commit-count metrics, double-check the date range and author filter so the number reflects what you intend (per-author vs project-wide, since-when vs all-time). Combine `--shortstat` with `wc -l` for line-change totals, or pipe `git log` into a CSV for spreadsheet analysis. For long-running repos, prefer ISO date ranges over relative ones to keep counts reproducible.
