---
title: "Changing Git History Author and Syncing CommitDate"
description: "How to change commit Author with git rebase, filter-branch, and filter-repo, and how to sync CommitDate to AuthorDate"
excerpt: "Guide to changing the Author of existing Git commits and aligning CommitDate with AuthorDate using several approaches"
date: 2026-03-05
categories: Git
tags: [Git, author, rebase, filter-branch, filter-repo, CommitDate, AuthorDate, git-history]
ref: git-change-author-and-commitdate
---

:bulb: When existing Git history (log) is present, this post covers how to change the commit author and align CommitDate with AuthorDate.
{: .notice--info}

# [01] The Two Date Concepts in Git

Every Git commit has two dates.

| Item | Environment variable | Description |
|---|---|---|
| **AuthorDate** | `GIT_AUTHOR_DATE` | The date the code was actually written |
| **CommitDate** | `GIT_COMMITTER_DATE` | The date the commit was recorded in the repository |

- Operations like `git rebase`, `git cherry-pick`, and `git commit --amend` **update only CommitDate to the current time**, so the two dates can differ.
- `git log`'s default output is keyed on **AuthorDate**, but services like GitHub sort and display commits by **CommitDate**.

To check both dates of the current commits, use the command below.

```shell
# Show the full log
git log --format='%h  author:%ad  commit:%cd  %s' --date=iso

# Show only the most recent 10 (-n 10)
git log --format='%h  author:%ad  commit:%cd  %s' --date=iso -n 10
```

**Example output:**

```
a1b2c3d  author:2025-01-02 10:00:00 +0900  commit:2025-03-07 22:14:33 +0900  feat: add login feature
e4f5g6h  author:2025-01-01 09:00:00 +0900  commit:2025-03-07 22:13:10 +0900  init: initial commit
```

You can see in the example that **AuthorDate and CommitDate differ**.

---

# [02] Changing the Author

## 2-1. Change the Author for Future Commits (most common)

To apply the change starting from new commits, set the author info via `git config`.

### (A) Apply to a specific repo only

```shell
git config user.name "New Tester"
git config user.email "newtest@example.com"
```

### (B) Apply globally to every repo of your account

```shell
git config --global user.name "New Tester"
git config --global user.email "newtest@example.com"
```

Verify after setting:

```shell
git config --list | grep user
```

**Example output:**

```
user.name=New Tester
user.email=newtest@example.com
```

:bulb: Without `--global`, the setting is stored in the current repo's `.git/config`; with `--global`, it goes to `~/.gitconfig` and applies to all repos.
{: .notice--info}

---

## 2-2. Fix a Single Commit (--amend)

To change the author of the most recent commit, use `--amend`.

```shell
git commit --amend --author="New Tester <newtest@example.com>" --no-edit
```

**Options:**

| Option | Description |
|---|---|
| `--amend` | Modify the most recent commit |
| `--author="..."` | Specify the new author name and email |
| `--no-edit` | Keep the commit message unchanged |

**Example output:**

```
[detached HEAD a9b8c7d] feat: add login feature
 Date: Thu Jan  2 10:00:00 2025 +0900
 1 file changed, 5 insertions(+)
```

---

## 2-3. Fix Multiple Commits (rebase -i)

`git rebase -i` lets you interactively select the most recent N commits and change their author.
It gives finer range control than `filter-branch` and suits modifying a small number of commits.

:warning: Rebase rewrites history, so on **shared branches always coordinate with teammates** before proceeding.
{: .notice--warning}

**1) Open the rebase todo list** (targeting the most recent 8 commits)

```shell
git rebase -i HEAD~8
```

**2) In the editor, change `pick` → `edit` for the commits to modify**

The editor opens showing the commit list as below.
Change `pick` to `edit` for the commits whose author you want to change, then save.
**It is recommended to leave the bottom line (the most recent commit relative to the range, i.e. the oldest in the todo) as `pick`.**

```
edit a1b2c3d feat: add search feature
edit e4f5g6h feat: add login feature
edit b7c8d9e fix: typo in README
edit c0d1e2f refactor: clean up utils
edit d3e4f5g chore: update deps
edit f6g7h8i test: add unit tests
edit g9h0i1j docs: update API docs
pick h2i3j4k init: initial commit
```

**3) Each time rebase stops at a commit, run the following in the terminal**

```shell
git commit --amend --author="New Tester <newtest@example.com>" --no-edit
git rebase --continue
```

> `git commit --amend ...` is **not** typed in the editor —
> it is a command you **run in the terminal** after rebase pauses.
> Running `git rebase --continue` advances to the next commit; repeat the process for each commit marked `edit`.

**Example output (single commit processed):**

```
[detached HEAD a9b8c7d] feat: add search feature
 Date: Thu Jan  2 10:00:00 2025 +0900
 1 file changed, 3 insertions(+)
Successfully rebased and updated refs/heads/main.
```

**Options:**

| Command/Option | Description |
|---|---|
| `git rebase -i HEAD~8` | Interactively edit the most recent 8 commits |
| `edit` | Pause rebase at that commit to allow modifications |
| `--amend --author="..."` | Change the author info of the current commit |
| `--no-edit` | Don't modify the commit message |
| `git rebase --continue` | Continue rebase to the next commit after edits |

---

## 2-4. Rewrite All History at Once (filter-branch)

:warning: `git filter-branch` rewrites history, so on **shared branches always coordinate with teammates** before using it.
{: .notice--warning}

Change an author identified by a specific email to a new name/email.

```shell
git filter-branch --env-filter '
OLD_EMAIL="oldtest@example.com"
NEW_NAME="New Tester"
NEW_EMAIL="newtest@example.com"

if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]; then
    export GIT_COMMITTER_NAME="$NEW_NAME"
    export GIT_COMMITTER_EMAIL="$NEW_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]; then
    export GIT_AUTHOR_NAME="$NEW_NAME"
    export GIT_AUTHOR_EMAIL="$NEW_EMAIL"
fi
' --tag-name-filter cat -- --branches --tags
```

**Options:**

| Option | Description |
|---|---|
| `--env-filter '...'` | Run a shell script per commit to modify environment variables |
| `GIT_COMMITTER_NAME/EMAIL` | The committer info for CommitDate |
| `GIT_AUTHOR_NAME/EMAIL` | The author info for AuthorDate |
| `--tag-name-filter cat` | Rewrite tags as well |
| `-- --branches --tags` | Apply to all branches and tags |

**Example output:**

```
Rewrite a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 (2/5) (0 seconds passed, remaining 0 predicted)
Rewrite e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3 (5/5) (1 seconds passed, remaining 0 predicted)
Ref 'refs/heads/main' was rewritten
```

Verify the result.

```shell
# Show the full log
git log --format="%H | %an <%ae> | %s"

# Show only the most recent 10
git log --format="%h | %an <%ae> | %s" -n 10
```

**Example output:**

```
a9b8c7d | New Tester <newtest@example.com> | feat: add login feature
b8c7d6e | New Tester <newtest@example.com> | init: initial commit
```

---

## 2-5. Recommended: git filter-repo (faster and safer)

`git filter-repo` is the official replacement for `filter-branch` — it's faster and easier to use.

**Install:**

```shell
pip install git-filter-repo
```

**Usage:**

```shell
git filter-repo --mailmap mailmap.txt
```

Example `mailmap.txt`:

```
New Tester <newtest@example.com> Old Tester <oldtest@example.com>
```

**Example output:**

```
Parsed 5 commits
New history written in 0.08 seconds; now repacking/cleaning...
Repacking your repo and cleaning out old unneeded objects
HEAD is now at a9b8c7d feat: add login feature
Enumerating objects: 10, done.
Writing objects: 100% (10/10), done.
```

---

# [03] Align CommitDate with AuthorDate

When CommitDate has drifted to the current time due to a rebase or similar operation, you can align it with AuthorDate.

## 3-1. Align CommitDate to AuthorDate for the Most Recent N Commits (rebase -i)

When you want to selectively modify a specified range, use `git rebase -i`.

:warning: Rebase rewrites history, so on **shared branches always coordinate with teammates** before proceeding.
{: .notice--warning}

**1) Open the rebase todo** (targeting the most recent 8 commits)

```shell
git rebase -i HEAD~8
```

**2) Change `pick` → `edit` for the commits to modify, then save**

```
edit a1b2c3d feat: add search feature
edit e4f5g6h feat: add login feature
edit b7c8d9e fix: typo in README
pick h2i3j4k init: initial commit
```

**3) Each time rebase stops at a commit, run the following in order**

```shell
export GIT_COMMITTER_DATE="$(git show -s --format=%aI HEAD)"
git commit --amend --no-edit --date "$(git show -s --format=%aI HEAD)"
git rebase --continue
```

> Repeat the three lines above for as many commits as you marked `edit`.
> `git commit --amend ...` is **not** typed inside the editor —
> it is a command you **run in the terminal** after rebase pauses.

**Example output (single commit processed):**

```
[detached HEAD a9b8c7d] feat: add search feature
 Date: Thu Jan  2 10:00:00 2025 +0900
 1 file changed, 3 insertions(+)
Successfully rebased and updated refs/heads/main.
```

**Options:**

| Command/Option | Description |
|---|---|
| `git rebase -i HEAD~8` | Interactively edit the most recent 8 commits |
| `edit` | Pause rebase at that commit to allow modifications |
| `git show -s --format=%aI HEAD` | Print the current commit's AuthorDate in ISO 8601 format |
| `GIT_COMMITTER_DATE=...` | Set CommitDate via a shell environment variable |
| `--amend --no-edit --date "..."` | Set CommitDate (and AuthorDate) to the specified date, keeping the message |
| `git rebase --continue` | Continue rebase to the next commit after edits |

---

## 3-2. Bulk-Sync CommitDate to AuthorDate Across Full History

```shell
git filter-branch --env-filter 'GIT_COMMITTER_DATE=$GIT_AUTHOR_DATE' -- --all
```

**Options:**

| Option | Description |
|---|---|
| `--env-filter '...'` | Modify environment variables per commit |
| `GIT_COMMITTER_DATE=$GIT_AUTHOR_DATE` | Set CommitDate equal to AuthorDate |
| `-- --all` | Apply to every ref in the repo (branches, tags) |

**Example output:**

```
Rewrite a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 (2/2) (0 seconds passed, remaining 0 predicted)
Ref 'refs/heads/main' was rewritten
```

Verify the result:

```shell
# Show the full log
git log --format='%h  author:%ad  commit:%cd  %s' --date=iso

# Show only the most recent 10
git log --format='%h  author:%ad  commit:%cd  %s' --date=iso -n 10
```

**Example output (after fix):**

```
a9b8c7d  author:2025-01-02 10:00:00 +0900  commit:2025-01-02 10:00:00 +0900  feat: add login feature
b8c7d6e  author:2025-01-01 09:00:00 +0900  commit:2025-01-01 09:00:00 +0900  init: initial commit
```

AuthorDate and CommitDate are now identical.

---

## 3-3. Change Author and Sync CommitDate in One Pass

Author change and date sync can be handled together inside a single `--env-filter`.

```shell
git filter-branch --env-filter '
OLD_EMAIL="oldtest@example.com"
NEW_NAME="New Tester"
NEW_EMAIL="newtest@example.com"

if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]; then
    export GIT_AUTHOR_NAME="$NEW_NAME"
    export GIT_AUTHOR_EMAIL="$NEW_EMAIL"
fi
if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]; then
    export GIT_COMMITTER_NAME="$NEW_NAME"
    export GIT_COMMITTER_EMAIL="$NEW_EMAIL"
fi

export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
' --tag-name-filter cat -- --branches --tags
```

---

# [04] Pushing to the Remote

Because history has been rewritten, you must push with `--force`.

:warning: Force push overwrites the remote history, so on **branches shared with teammates always coordinate beforehand**.
{: .notice--warning}

## Push Only a Specific Branch (recommended)

`--force-with-lease` is a **safer force push** that rejects the push if someone else has pushed since your last fetch.

```shell
git push --force-with-lease origin main
```

## Push All Branches and Tags

```shell
git push origin --force --all
git push origin --force --tags
```

**Example output:**

```
Enumerating objects: 10, done.
Counting objects: 100% (10/10), done.
Writing objects: 100% (10/10), 800 bytes | 800.00 KiB/s, done.
Total 10 (delta 2), reused 0 (delta 0), pack-reused 0
To https://github.com/testuser/test-repo.git
 + a1b2c3d...a9b8c7d main -> main (forced update)
```

| Option | Description |
|---|---|
| `--force-with-lease` | Reject the push if the remote has unexpected changes (safer) |
| `--force` | Overwrite forcibly regardless of remote state |
| `--all` | Push every local branch |
| `--tags` | Push tags as well |

---

# [05] Cleanup After filter-branch

`filter-branch` backs up the original commit objects under `refs/original/`, so once the work is done, clean up with the commands below.

```shell
# Remove backup refs
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d

# Clean up unreachable objects
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**Example output:**

```
Enumerating objects: 10, done.
Counting objects: 100% (10/10), done.
Delta compression using up to 8 threads
Compressing objects: 100% (8/8), done.
Writing objects: 100% (10/10), done.
Total 10 (delta 2), reused 10 (delta 2), pack-reused 0
```
