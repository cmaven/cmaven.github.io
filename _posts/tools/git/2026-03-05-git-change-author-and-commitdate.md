---
title: "Git History에서 Author 변경 및 CommitDate를 AuthorDate로 맞추기"
date: 2026-03-05
categories: Git
tags: [git, author, rebase, filter-branch, filter-repo]
---

:bulb: 기존 git history(log)가 있을 때, 커밋 작성자(author)를 변경하고, CommitDate를 AuthorDate에 맞추는 방법을 작성한다.
{: .notice--info}

# [01] Git의 두 가지 날짜 개념

Git 커밋에는 날짜가 두 가지 존재한다.

| 항목 | 환경변수 | 설명 |
|---|---|---|
| **AuthorDate** | `GIT_AUTHOR_DATE` | 코드를 실제로 작성한 날짜 |
| **CommitDate** | `GIT_COMMITTER_DATE` | 커밋이 저장소에 기록된 날짜 |

- `git rebase`, `git cherry-pick`, `git commit --amend` 등을 수행하면 **CommitDate만 현재 시간으로 갱신**되어 두 날짜가 달라진다.
- `git log`의 기본 출력은 **AuthorDate** 기준이지만, GitHub 등 일부 서비스는 **CommitDate**를 기준으로 정렬하거나 표시한다.

현재 커밋의 두 날짜를 모두 확인하려면 아래 명령을 사용한다.

```shell
# 전체 로그 보기
git log --format='%h  author:%ad  commit:%cd  %s' --date=iso

# 최근 10개만 보기 (-n 10)
git log --format='%h  author:%ad  commit:%cd  %s' --date=iso -n 10
```

**출력 예:**

```
a1b2c3d  author:2025-01-02 10:00:00 +0900  commit:2025-03-07 22:14:33 +0900  feat: add login feature
e4f5g6h  author:2025-01-01 09:00:00 +0900  commit:2025-03-07 22:13:10 +0900  init: initial commit
```

위 예에서 **AuthorDate와 CommitDate가 다름**을 확인할 수 있다.

---

# [02] Author 변경하기

## 2-1. 앞으로 생성되는 커밋의 Author 변경 (가장 흔함)

새로운 커밋부터 적용하고 싶을 때는 `git config`로 author 정보를 설정한다.

### (A) 특정 repo에만 적용

```shell
git config user.name "New Tester"
git config user.email "newtest@example.com"
```

### (B) 내 계정의 모든 repo에 적용 (전역)

```shell
git config --global user.name "New Tester"
git config --global user.email "newtest@example.com"
```

설정 후 확인:

```shell
git config --list | grep user
```

**출력 예:**

```
user.name=New Tester
user.email=newtest@example.com
```

:bulb: `--global` 없이 설정하면 현재 repo의 `.git/config`에만 저장되며, `--global`로 설정하면 `~/.gitconfig`에 저장되어 모든 repo에 적용된다.
{: .notice--info}

---

## 2-2. 특정 커밋 1개만 수정 (--amend)

가장 최근 커밋의 author를 변경할 때는 `--amend`를 사용한다.

```shell
git commit --amend --author="New Tester <newtest@example.com>" --no-edit
```

**옵션 설명:**

| 옵션 | 설명 |
|---|---|
| `--amend` | 가장 최근 커밋을 수정 |
| `--author="..."` | 변경할 author 이름과 이메일 지정 |
| `--no-edit` | 커밋 메시지는 그대로 유지 |

**출력 예:**

```
[detached HEAD a9b8c7d] feat: add login feature
 Date: Thu Jan  2 10:00:00 2025 +0900
 1 file changed, 5 insertions(+)
```

---

## 2-3. 여러 커밋 수정 (rebase -i)

`git rebase -i`를 사용하면 최근 N개의 커밋을 인터랙티브하게 선택해 author를 수정할 수 있다.
`filter-branch`보다 범위를 제어하기 쉬우며, 소수의 커밋을 수정할 때 적합하다.

:warning: rebase는 history를 재작성하므로 **공유된 브랜치에서는 팀원과 협의** 후 진행한다.
{: .notice--warning}

**1) rebase todo 목록 열기** (최근 8개 커밋 대상)

```shell
git rebase -i HEAD~8
```

**2) 에디터에서 수정할 커밋의 `pick` → `edit` 으로 변경**

에디터가 열리면 아래와 같이 커밋 목록이 표시된다.
author를 변경할 커밋의 `pick`을 `edit`으로 바꾸고 저장한다.
**가장 아래 줄(최신 커밋)은 `pick` 유지를 권장한다.**

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

**3) rebase가 각 커밋에서 멈추면 터미널에서 순서대로 실행**

```shell
git commit --amend --author="New Tester <newtest@example.com>" --no-edit
git rebase --continue
```

> `git commit --amend ...`는 에디터 안에 입력하는 것이 아니라,
> rebase가 멈춘 뒤 **터미널에서 실행**하는 명령이다.
> `git rebase --continue`를 실행하면 다음 커밋으로 진행하며, 이 과정을 `edit`으로 표시한 커밋 수만큼 반복한다.

**출력 예 (커밋 1개 처리 시):**

```
[detached HEAD a9b8c7d] feat: add search feature
 Date: Thu Jan  2 10:00:00 2025 +0900
 1 file changed, 3 insertions(+)
Successfully rebased and updated refs/heads/main.
```

**옵션 설명:**

| 명령/옵션 | 설명 |
|---|---|
| `git rebase -i HEAD~8` | 최근 8개 커밋을 인터랙티브하게 편집 |
| `edit` | 해당 커밋에서 rebase를 일시 정지하여 수정 가능하게 함 |
| `--amend --author="..."` | 현재 커밋의 author 정보를 변경 |
| `--no-edit` | 커밋 메시지는 수정하지 않음 |
| `git rebase --continue` | 수정 후 다음 커밋으로 rebase 진행 |

---

## 2-4. 전체 history 일괄 변경 (filter-branch)

:warning: `git filter-branch`는 history를 재작성하므로 **공유된 브랜치에 사용 시 팀원과 협의** 후 진행한다.
{: .notice--warning}

특정 이메일을 가진 author를 새 이름/이메일로 변경한다.

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

**옵션 설명:**

| 옵션 | 설명 |
|---|---|
| `--env-filter '...'` | 각 커밋마다 셸 스크립트를 실행하여 환경변수를 수정 |
| `GIT_COMMITTER_NAME/EMAIL` | CommitDate 기록자 정보 |
| `GIT_AUTHOR_NAME/EMAIL` | AuthorDate 기록자 정보 |
| `--tag-name-filter cat` | 태그도 함께 재작성 |
| `-- --branches --tags` | 모든 브랜치와 태그에 적용 |

**출력 예:**

```
Rewrite a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 (2/5) (0 seconds passed, remaining 0 predicted)
Rewrite e4f5g6h7i8j9k0l1m2n3o4p5q6r7s8t9u0v1w2x3 (5/5) (1 seconds passed, remaining 0 predicted)
Ref 'refs/heads/main' was rewritten
```

변경 결과를 확인한다.

```shell
# 전체 로그 확인
git log --format="%H | %an <%ae> | %s"

# 최근 10개만 확인
git log --format="%h | %an <%ae> | %s" -n 10
```

**출력 예:**

```
a9b8c7d | New Tester <newtest@example.com> | feat: add login feature
b8c7d6e | New Tester <newtest@example.com> | init: initial commit
```

---

## 2-5. 추천 방법: git filter-repo (더 빠르고 안전)

`git filter-repo`는 `filter-branch`의 공식 대체 도구로, 속도가 빠르고 사용하기 간편하다.

**설치:**

```shell
pip install git-filter-repo
```

**사용법:**

```shell
git filter-repo --mailmap mailmap.txt
```

`mailmap.txt` 파일 예시:

```
New Tester <newtest@example.com> Old Tester <oldtest@example.com>
```

**출력 예:**

```
Parsed 5 commits
New history written in 0.08 seconds; now repacking/cleaning...
Repacking your repo and cleaning out old unneeded objects
HEAD is now at a9b8c7d feat: add login feature
Enumerating objects: 10, done.
Writing objects: 100% (10/10), done.
```

---

# [03] CommitDate를 AuthorDate로 맞추기

rebase 등으로 인해 CommitDate가 현재 시간으로 변경된 경우, AuthorDate와 동일하게 맞출 수 있다.

## 3-1. 최근 N개 커밋의 CommitDate를 AuthorDate로 맞추기 (rebase -i)

범위를 지정해 선택적으로 수정할 때는 `git rebase -i`를 사용한다.

:warning: rebase는 history를 재작성하므로 **공유된 브랜치에서는 팀원과 협의** 후 진행한다.
{: .notice--warning}

**1) rebase todo 열기** (최근 8개 커밋 대상)

```shell
git rebase -i HEAD~8
```

**2) 수정할 커밋의 `pick` → `edit` 으로 변경 후 저장**

```
edit a1b2c3d feat: add search feature
edit e4f5g6h feat: add login feature
edit b7c8d9e fix: typo in README
pick h2i3j4k init: initial commit
```

**3) rebase가 각 커밋에서 멈추면 아래를 순서대로 실행**

```shell
export GIT_COMMITTER_DATE="$(git show -s --format=%aI HEAD)"
git commit --amend --no-edit --date "$(git show -s --format=%aI HEAD)"
git rebase --continue
```

> 위 세 줄을 `edit`으로 지정한 커밋 수만큼 반복하면 된다.
> `git commit --amend ...`는 에디터 안에 입력하는 것이 아니라,
> rebase가 멈춘 뒤 **터미널에서 실행**하는 명령이다.

**출력 예 (커밋 1개 처리 시):**

```
[detached HEAD a9b8c7d] feat: add search feature
 Date: Thu Jan  2 10:00:00 2025 +0900
 1 file changed, 3 insertions(+)
Successfully rebased and updated refs/heads/main.
```

**옵션 설명:**

| 명령/옵션 | 설명 |
|---|---|
| `git rebase -i HEAD~8` | 최근 8개 커밋을 인터랙티브하게 편집 |
| `edit` | 해당 커밋에서 rebase를 일시 정지하여 수정 가능하게 함 |
| `git show -s --format=%aI HEAD` | 현재 커밋의 AuthorDate를 ISO 8601 형식으로 출력 |
| `GIT_COMMITTER_DATE=...` | 셸 환경변수로 CommitDate를 지정 |
| `--amend --no-edit --date "..."` | CommitDate(및 AuthorDate)를 지정한 날짜로 수정, 메시지 유지 |
| `git rebase --continue` | 수정 후 다음 커밋으로 rebase 진행 |

---

## 3-2. 전체 history의 CommitDate를 AuthorDate로 일괄 수정

```shell
git filter-branch --env-filter 'GIT_COMMITTER_DATE=$GIT_AUTHOR_DATE' -- --all
```

**옵션 설명:**

| 옵션 | 설명 |
|---|---|
| `--env-filter '...'` | 각 커밋의 환경변수를 수정 |
| `GIT_COMMITTER_DATE=$GIT_AUTHOR_DATE` | CommitDate를 AuthorDate와 동일하게 설정 |
| `-- --all` | 저장소의 모든 ref(브랜치, 태그)에 적용 |

**출력 예:**

```
Rewrite a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0 (2/2) (0 seconds passed, remaining 0 predicted)
Ref 'refs/heads/main' was rewritten
```

수정 결과 확인:

```shell
# 전체 로그 확인
git log --format='%h  author:%ad  commit:%cd  %s' --date=iso

# 최근 10개만 확인
git log --format='%h  author:%ad  commit:%cd  %s' --date=iso -n 10
```

**출력 예 (수정 후):**

```
a9b8c7d  author:2025-01-02 10:00:00 +0900  commit:2025-01-02 10:00:00 +0900  feat: add login feature
b8c7d6e  author:2025-01-01 09:00:00 +0900  commit:2025-01-01 09:00:00 +0900  init: initial commit
```

AuthorDate와 CommitDate가 동일해진 것을 확인할 수 있다.

---

## 3-3. Author 변경과 CommitDate 동기화를 한 번에 처리

Author 변경과 날짜 동기화를 하나의 `--env-filter`로 동시에 처리할 수 있다.

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

# [04] 원격 저장소에 반영하기

history가 재작성되었으므로 `--force` 옵션으로 push해야 한다.

:warning: force push는 원격 저장소의 history를 덮어쓰므로, **팀원이 있는 브랜치에서는 반드시 사전 협의**한다.
{: .notice--warning}

## 특정 브랜치만 push (권장)

`--force-with-lease`는 내가 마지막으로 fetch한 이후 다른 사람이 push한 내역이 있으면 push를 거부하는 **더 안전한 force push** 방식이다.

```shell
git push --force-with-lease origin main
```

## 전체 브랜치 및 태그 push

```shell
git push origin --force --all
git push origin --force --tags
```

**출력 예:**

```
Enumerating objects: 10, done.
Counting objects: 100% (10/10), done.
Writing objects: 100% (10/10), 800 bytes | 800.00 KiB/s, done.
Total 10 (delta 2), reused 0 (delta 0), pack-reused 0
To https://github.com/testuser/test-repo.git
 + a1b2c3d...a9b8c7d main -> main (forced update)
```

| 옵션 | 설명 |
|---|---|
| `--force-with-lease` | 원격에 예상치 못한 변경이 있으면 push 거부 (안전) |
| `--force` | 원격 상태와 무관하게 강제 덮어쓰기 |
| `--all` | 모든 로컬 브랜치를 대상으로 push |
| `--tags` | 태그도 함께 push |

---  

# [05] filter-branch 사용 후 정리  

`filter-branch`는 기존 커밋 객체를 `refs/original/`에 백업해 두기 때문에, 작업 완료 후 아래 명령으로 정리한다.

```shell
# 백업 ref 제거
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d

# 불필요한 객체 정리
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**출력 예:**

```
Enumerating objects: 10, done.
Counting objects: 100% (10/10), done.
Delta compression using up to 8 threads
Compressing objects: 100% (8/8), done.
Writing objects: 100% (10/10), done.
Total 10 (delta 2), reused 10 (delta 2), pack-reused 0
```
