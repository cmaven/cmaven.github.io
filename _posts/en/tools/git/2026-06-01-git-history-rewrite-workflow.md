---
title: "A Practical Git History Rewrite Workflow (rebase · filter-branch · safe push)"
description: "Untangle branches, drop only specific commits, and fix author/commit dates — the full investigate, backup, rebase, conflict, filter-branch, and force-push flow for rewriting Git history"
excerpt: "The standard workflow for rewriting Git history: investigate → back up → interactive rebase (drop/reword) → resolve conflicts → filter-branch (author/date) → force-with-lease push"
date: 2026-06-01
categories: Git
tags: [Git, rebase, filter-branch, git-history, force-with-lease, conflict, squash, history-rewrite, reflog]
ref: git-history-rewrite-workflow
---

:bulb: A **standard workflow for rewriting Git history** that you can reach for when branches get tangled, you need to drop only some of many commits, and you also have to clean up author/commit dates. Every step is destructive, so backups and verification are assumed throughout.
{: .notice--info}

:warning: Never rewrite history casually on a **shared branch.** The force-push in this post assumes a branch you alone use, or one you are certain nobody else has fetched yet.
{: .notice--warning}

# [01] Four mental models before you start

Rewriting is, in the end, about drawing an accurate picture of "which commit belongs where."

## 1-1. Range query — `A..B`

`A..B` means **"commits in B but not in A."**

```bash
git log A..B                              # commits in B but not in A
git log --oneline origin/main..HEAD       # how far local main is ahead of origin
```

A single-line result from `git log --oneline origin/main..HEAD` does **not** mean the whole history is one commit — it just means you are **one commit ahead** of origin/main. To see the full history, drop the range: `git log B`.

## 1-2. Base / Ancestry

Every commit has a parent, forming an ancestry chain. Saying "branch A's base is branch B" means **B's tip is in A's ancestry.**

```bash
# Divergence point (nearest common ancestor) of two branches
git merge-base main feature/x

# How many commits from base to branch
git rev-list --count base..branch
```

## 1-3. 3-way merge / conflict markers

```text
<<<<<<< HEAD            ← "ours" — current branch (during rebase: base + already-applied commits)
... current code ...
=======
... incoming code ...    ← "theirs" — incoming commit (during rebase: the commit being applied now)
>>>>>>> <hash> (<msg>)
```

The key point: **during a rebase, `--ours`/`--theirs` are the opposite of a merge.**

| Situation | ours | theirs |
|---|---|---|
| merge | current branch | branch being merged in |
| rebase | base + earlier picks | commit being applied now |

Locate conflict regions quickly:

```bash
grep -n -E "^<<<<<<<|^=======|^>>>>>>>" <file>
```

## 1-4. filter-branch's `$GIT_COMMIT`

When `git filter-branch` processes each commit, `$GIT_COMMIT` is the **original SHA before the rewrite**, so you can match on the original hash in a `case` statement. The new SHA is only known after filter-branch finishes.

# [02] Survey the situation (read-only)

**Always** run this first. You can only assess risk once the backup/branch/remote layout is clear in your head.

```bash
# 1) All branches + last commit
git branch -v

# 2) Remote tip vs local main gap
git remote -v
git log --oneline origin/main..HEAD       # how far local main is ahead of origin
git rev-list --count upstream/main..HEAD  # count only

# 3) Base of another branch
git merge-base main feature/x | xargs git log -1 --format="%h %s"

# 4) What a specific hash changed
git show --stat <hash>                    # files + line changes
git show <hash> -- <file>                 # patch for one file

# 5) Every commit that touched a file
git log --oneline base..HEAD -- <file>

# 6) author / committer info
git log --reverse base..HEAD --format="%h %ai %an <%ae> %s"

# 7) Check author date == committer date
git log --format="%H %at %ct" | awk '$2!=$3 {print "MISMATCH:", $1}'

# 8) Check chronological (monotonic) order
git log --reverse --format="%at %h %s" | awk \
  '{ if (prev != "" && $1 < prev) print "OUT OF ORDER:", $0; prev=$1 }'
```

## 2-1. Compare trees — is the code itself identical?

Two commits can have different messages but the same code (tree). Useful for spotting duplicated work.

```bash
git diff A B --stat                       # changed files
git diff A B | wc -l                      # changed lines (0 = identical tree)

# Tree hash of a specific commit
git rev-parse <hash>^{tree}

# Find commits with the same tree
T=$(git rev-parse <hash>^{tree})
git log --format="%h %T" | awk -v t="$T" '$2==t {print $1}'
```

# [03] Backup strategy

Rewriting is destructive. **Always create a backup branch first.**

```bash
# Backup branch pointing at the current HEAD
git branch backup-pre-rebase-$(date +%F)

# Work on a temporary branch; force-update main only on success
git checkout -b main-rebuild <starting-point>
```

The **triple-backup rule** that has proven its worth in practice:

1. The work source itself (e.g. `feature/x` — kept for recovery)
2. main's starting point (e.g. `main-pre-rewrite-YYYY-MM-DD`)
3. A mid-failure fallback (e.g. `main-pre-rebuild-YYYY-MM-DD`)

```bash
git fetch --all
```

:warning: `git fetch origin upstream` is **not** "fetch both origin and upstream." It is parsed as `fetch <remote> <ref>` — "fetch a ref named upstream from origin." To fetch everything, use `git fetch --all`.
{: .notice--warning}

# [04] Interactive rebase — drop / reword / edit

Use this to drop only some commits or to edit messages.

## 4-1. Basic interactive mode

```bash
git rebase --interactive <base>
# A todo list opens in the editor:
#   pick aaa1111 commit msg
#   pick bbb2222 commit msg
# Change each line to pick / drop / reword / edit / squash / fixup
```

## 4-2. Non-interactive automation (scripts/CI)

`GIT_SEQUENCE_EDITOR` is the todo-list editor; `GIT_EDITOR` is the commit-message editor.

```bash
# Drop 2 commits + reword 1
export GIT_SEQUENCE_EDITOR='sed -i \
  -e "/^pick aaa1111 /s/^pick/drop/" \
  -e "/^pick bbb2222 /s/^pick/drop/" \
  -e "/^pick ccc3333 /s/^pick/reword/"'

# Auto-replace the commit message on reword
export GIT_EDITOR='sed -i -e "s|<old-keyword>|<new-keyword>|"'

git rebase --interactive <base>
```

:warning: `GIT_EDITOR` is invoked at **every step that needs a commit-message edit**, not only on reword. Write your sed pattern carefully so it affects only the intended commit.
{: .notice--warning}

## 4-3. Progress commands

```bash
git rebase --continue   # move to the next commit after resolving a conflict
git rebase --skip        # skip the current commit (alternative to drop)
git rebase --abort       # cancel everything, return to the base state
```

You can also inspect rebase state directly:

```bash
ls .git/rebase-merge                    # is a rebase in progress?
cat .git/rebase-merge/done              # commits already processed
cat .git/rebase-merge/git-rebase-todo   # remaining commits
```

# [05] Conflict resolution patterns

## 5-1. Diagnose

```bash
git status --short                        # UU = both modified
grep -n -E "^<<<<<<<|^=======|^>>>>>>>" <file>   # marker positions
git show <conflicting-hash> -- <file>     # the original commit's intent
```

## 5-2. Four resolution patterns

**Pattern A — keep HEAD (discard incoming)**

```bash
git checkout --ours <file>                # the whole file

# Or just a region with sed
sed -i -e '/^<<<<<<< HEAD$/d' \
       -e '/^=======$/,/^>>>>>>> /d' \
       <file>
# Effect: removes the <<<<<<< HEAD line and ======= through >>>>>>> = keeps only the HEAD section
```

**Pattern B — take incoming (discard HEAD)**

```bash
git checkout --theirs <file>

sed -i -e '/^<<<<<<< HEAD$/,/^=======$/d' \
       -e '/^>>>>>>> /d' \
       <file>
```

**Pattern C — take both (remove markers only)**

```bash
sed -i -e '/^<<<<<<< HEAD$/d' \
       -e '/^=======$/d' \
       -e '/^>>>>>>> /d' \
       <file>
```

This is safe even when HEAD is empty and only the incoming side exists (it effectively takes incoming).

**Pattern D — manual edit (safest)**

Open the file in an editor and write the conflict region exactly as intended. Essential for complex cases that take parts of both sides.

## 5-3. After resolving

```bash
<build-command>          # e.g. go build ./... / npm run build / cargo build — always sanity-check
git add <files>
git rebase --continue
```

# [06] Squash strategy and trade-offs

## 6-1. Heavy squash — everything into one

```bash
git reset --soft <base>          # keep changes staged, discard the commits
git commit -m "big integrated message"
```

## 6-2. The reset modes

| Mode | HEAD | index | working dir |
|---|:---:|:---:|:---:|
| `--soft` | moves | kept | kept |
| `--mixed` (default) | moves | moves | kept |
| `--hard` | moves | moves | **moves (destructive)** |

## 6-3. Which squash to choose

| Approach | Pros | Cons |
|---|---|---|
| Heavy (N→1) | clean log | loses per-step intent/blame |
| Medium (rebase + drop) | preserves original units | conflicts possible |
| Light (+1 commit) | safe, fast | exposes "X used to be here" history |

**Rule of thumb**: if the "why it became this way" of the history matters, go Medium; if only appearance matters, go Heavy.

# [07] Fixing Author / CommitDate (filter-branch)

To bulk-fix a specific commit's author date or author info, use `filter-branch --env-filter`.

```bash
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --env-filter '
case "$GIT_COMMIT" in
  aaa1111*) export GIT_AUTHOR_DATE="2099-12-31T09:00:00+09:00" ;;
  bbb2222*) export GIT_AUTHOR_DATE="2099-12-31T10:00:00+09:00" ;;
esac

# Sync committer date to author date (all commits)
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"

# Unify a specific author only
if [ "$GIT_AUTHOR_EMAIL" = "old@example.com" ]; then
  export GIT_AUTHOR_NAME="NewName"
  export GIT_AUTHOR_EMAIL="new@example.com"
fi
' <base>..HEAD
```

| Variable | Meaning |
|---|---|
| `GIT_AUTHOR_DATE` | when the code was written |
| `GIT_AUTHOR_NAME` / `GIT_AUTHOR_EMAIL` | the author |
| `GIT_COMMITTER_DATE` | when the commit object was created (reassigned automatically during rebase) |
| `$GIT_COMMIT` | the original commit SHA being processed (for case matching) |

Use ISO 8601 dates (`YYYY-MM-DDTHH:MM:SS+TZ`). **Always clean up** afterward.

```bash
rm -rf .git/refs/original                 # backup refs left by filter-branch
git reflog expire --expire=now --all
git gc --prune=now
```

:bulb: For a deeper treatment of changing the author and syncing CommitDate (including `--amend`, `rebase -i`, and a `git filter-repo` comparison), see the dedicated post [Changing Git History Author and Syncing CommitDate](/en/git/git-change-author-and-commitdate/). Note that `filter-branch` is officially deprecated; for complex cases, `git filter-repo` is faster and safer.
{: .notice--info}

# [08] Branch cleanup

```bash
git branch -d <branch>    # safe — allowed only if reachable from another ref
git branch -D <branch>    # force — deletes even if unreachable (orphan risk)
```

- A verified temporary branch (e.g. after resetting main to `main-rebuild`) → `-d`
- An old, unreachable backup → `-D`
- The **current active branch cannot be deleted** — check out another branch first

```bash
# Replace main with the work branch
git checkout main
git reset --hard main-rebuild

# Clean up backups in bulk
for b in main-pre-* backup-*; do git branch -D "$b"; done
```

# [09] Safe push

```bash
git push origin main                      # rejected after a rewrite (non-fast-forward)
git push --force origin main              # dangerous: overwrites others' new commits too
git push --force-with-lease origin main   # recommended
```

`--force-with-lease` refuses the push if the remote tip differs from what you last fetched, **protecting others' work.**

- **Safe**: personal repos only you use; a stale remote nobody else has fetched
- **Dangerous**: active shared branches (main/dev); someone already working on top of that branch

# [10] Chronological reordering

Because the default author date of rebase/cherry-pick is "now," commits authored in the past can show recent dates, breaking chronological order. Build a mapping table and reassign only the wrong dates.

```bash
git filter-branch -f --env-filter '
case "$GIT_COMMIT" in
  hash1*) export GIT_AUTHOR_DATE="2026-05-01T09:00:00+09:00" ;;
  hash2*) export GIT_AUTHOR_DATE="2026-05-01T10:00:00+09:00" ;;
esac
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
' <base>..HEAD

# Verify
git log --reverse <base>..HEAD --format="%h | %ai | %ci | %s"
git log --reverse --format="%at" | awk \
  '{ if (prev != "" && $1 < prev) print "OUT OF ORDER"; prev=$1 }'
```

**Time-distribution guide**: 30-minute to 1-hour gaps within a day, related commits close together, and don't push the last commit's timestamp too late.

# [11] Gotchas

**1) `git fetch origin upstream` ≠ "fetch origin + upstream"** — use `git fetch --all` or `git fetch origin && git fetch upstream`.

**2) grep no-match → exit 1 → `&&` short-circuit**

```bash
# Intent: create a backup if none exists — but a grep no-match fails the whole && chain
git branch | grep "backup" && echo "exists" && git branch backup   # never created

# Fix
git branch | grep -q "backup" || git branch backup
```

**3) awk built-in `match` name clash** — `match` is a built-in function, so don't use it as a variable name; use `status` or similar.

**4) filter-branch's leftover `.git/refs/original/`** — if not cleaned, the next run needs `--force`. Always follow up with reflog expire + gc.

**5) rebase todo hashes are original hashes** — new SHAs appear during the work, but the todo list matches on the original hash.

**6) sed delimiter clash (`/`)** — when a path contains `/`, change the delimiter, e.g. `sed 's|a/b|c|'`.

**7) Parent vs child git repo confusion** — use `git rev-parse --show-toplevel` to confirm which repo you're running commands in. This bites often when a parent directory `.gitignore`s the child.

# [12] Standard end-to-end flow

The standard order for, in one pass: dropping K keyword-related commits out of N, integrating upstream's extra commits, and fixing the author/date of some commits.

```bash
# Step 1 — analyze
git fetch --all
git branch -v
git log --oneline upstream/main..<source-branch>
git log --oneline --all | grep -i "<keyword>"

# Step 2 — backup + work branch
git branch main-pre-rewrite-$(date +%F) main
git branch main-pre-rebuild-$(date +%F) main
git checkout -b main-rebuild <source-branch>

# Step 3 — interactive rebase (drop + reword)
export GIT_SEQUENCE_EDITOR='sed -i \
  -e "/^pick aaa1111 /s/^pick/drop/" \
  -e "/^pick ccc3333 /s/^pick/reword/"'
export GIT_EDITOR='sed -i -e "s|<old-keyword>|<new-keyword>|"'
git rebase --interactive upstream/main

# Step 4 — conflict resolution loop (per commit)
git status --short
grep -n -E "^<<<<<<<|^=======|^>>>>>>>" <file>
<build-command>
git add <file>; git rebase --continue

# Step 5 — verify
grep -rln -i "<removed-keyword>" --include="*.<ext>" .        # 0 code leftovers
git log <base>..HEAD --format=%B | grep -ic "<removed-keyword>"  # 0 message leftovers

# Step 6 — swap main
git checkout main
git reset --hard main-rebuild

# Step 7 — fix author/date
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --env-filter '
case "$GIT_COMMIT" in
  hash1*) export GIT_AUTHOR_DATE="2026-05-01T09:00:00+09:00" ;;
esac
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
' upstream/main..HEAD
rm -rf .git/refs/original
git reflog expire --expire=now --all
git gc --prune=now

# Step 8 — final verification
git log <base>..HEAD --format="%H %at %ct %ae %ce" | awk '
  $2!=$3 {print "DATE MISMATCH:", $1}
  $4!=$5 {print "EMAIL MISMATCH:", $1}
  prev!="" && $2<prev {print "OUT OF ORDER:", $1}
  {prev=$2}'

# Step 9 — branch cleanup
git branch -d main-rebuild
for b in main-pre-* backup-*; do git branch -D "$b"; done

# Step 10 — push (manual)
git push --force-with-lease origin main
```

# [13] Quick reference card

```text
=== Survey ===
git branch -v
git log --oneline <range>
git rev-list --count <range>
git merge-base A B
git diff A B --stat

=== Backup ===
git branch backup-$(date +%F)
git checkout -b main-rebuild <source>

=== Rebase ===
git rebase -i <base>
git rebase --continue / --skip / --abort
GIT_SEQUENCE_EDITOR='sed ...' GIT_EDITOR='sed ...' git rebase -i <base>

=== Conflict ===
git status --short
grep -n "<<<<<<<\|=======\|>>>>>>>" <file>
git checkout --ours/--theirs <file>
git add <file>; git rebase --continue

=== Squash ===
git reset --soft <base>; git commit -m "..."

=== Date/Author ===
git filter-branch -f --env-filter '
  case "$GIT_COMMIT" in hash*) export GIT_AUTHOR_DATE="..." ;; esac
  export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
' <base>..HEAD
rm -rf .git/refs/original
git reflog expire --expire=now --all && git gc --prune=now

=== Push ===
git push --force-with-lease <remote> <branch>
```

:bulb: Further reading: `git help rebase`, `git help filter-branch`, and the replacement for the deprecated filter-branch, [git-filter-repo](https://github.com/newren/git-filter-repo). Related posts: [Changing Git History Author and Syncing CommitDate](/en/git/git-change-author-and-commitdate/), [git commit --amend and force push](/en/git/git-amend-force-push/).
{: .notice--info}
