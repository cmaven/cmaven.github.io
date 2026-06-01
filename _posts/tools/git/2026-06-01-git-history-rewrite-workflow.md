---
title: "Git 히스토리 재작성 실전 워크플로우 (rebase · filter-branch · 안전 push)"
description: "꼬인 브랜치 정리, 특정 커밋만 제거, author/commit date 보정까지 — Git 히스토리 재작성의 조사·백업·rebase·conflict·filter-branch·force-push 전체 흐름을 실전 순서로 정리"
excerpt: "조사 → 백업 → interactive rebase(drop/reword) → conflict 해결 → filter-branch(author/date) → force-with-lease push까지, Git 히스토리 재작성의 표준 워크플로우"
date: 2026-06-01
categories: Git
tags: [Git, rebase, filter-branch, git-history, force-with-lease, conflict, squash, 히스토리재작성, reflog]
ref: git-history-rewrite-workflow
---

:bulb: 브랜치가 꼬이고, 여러 커밋 중 일부만 제거하고, author/commit date까지 정리해야 하는 상황에서 즉시 참조할 수 있는 **Git 히스토리 재작성 표준 워크플로우**를 정리한다. 모든 단계는 destructive하므로 백업과 검증을 전제로 한다.
{: .notice--info}

:warning: 히스토리 재작성은 **공유 브랜치에서 절대 가볍게 하지 않는다.** 본 글의 force-push는 본인만 쓰는 브랜치이거나, 다른 사람이 아직 fetch하지 않은 것이 확실한 경우를 전제로 한다.
{: .notice--warning}

# [01] 시작 전 정신 모델 4가지

재작성 작업의 사고는 결국 "어떤 커밋이 어디에 속하는가"를 정확히 그리는 데서 출발한다.

## 1-1. Range query — `A..B`

`A..B`는 **"A에는 없고 B에는 있는 커밋"**을 의미한다.

```bash
git log A..B                              # A에 없고 B에 있는 커밋
git log --oneline origin/main..HEAD       # 로컬 main이 origin보다 얼마나 앞서 있나
```

`git log --oneline origin/main..HEAD` 결과가 1줄이라고 해서 전체 히스토리가 1줄인 게 아니다. origin/main보다 **1커밋 앞**이라는 뜻일 뿐이다. 전체 히스토리는 range 없이 `git log B`로 본다.

## 1-2. Base / Ancestry

모든 커밋은 부모 커밋을 가지며 ancestry(조상 사슬)를 형성한다. "브랜치 A의 base가 브랜치 B"라는 말은 **A의 ancestry 안에 B의 tip이 있다**는 뜻이다.

```bash
# 두 브랜치의 분기점(가장 가까운 공통 조상)
git merge-base main feature/x

# base부터 branch까지 몇 커밋인지
git rev-list --count base..branch
```

## 1-3. 3-way merge / conflict marker

```text
<<<<<<< HEAD            ← "ours" — 현재 브랜치 (rebase 중에는 base + 이미 적용된 커밋들)
... 현재 코드 ...
=======
... 가져오려는 코드 ...   ← "theirs" — incoming 커밋 (rebase 중에는 지금 적용하는 커밋)
>>>>>>> <hash> (<msg>)
```

여기서 핵심은 **rebase 중에는 `--ours`/`--theirs`의 의미가 merge와 반대**라는 점이다.

| 상황 | ours | theirs |
|---|---|---|
| merge | 현재 브랜치 | merge하려는 브랜치 |
| rebase | base + 이전 pick들 | 지금 적용하려는 커밋 |

conflict 영역은 다음으로 빠르게 찾는다.

```bash
grep -n -E "^<<<<<<<|^=======|^>>>>>>>" <file>
```

## 1-4. filter-branch의 `$GIT_COMMIT`

`git filter-branch`가 각 커밋을 처리할 때 `$GIT_COMMIT`은 **rewrite 이전의 원본 SHA**다. 따라서 `case` 문에서 원본 hash로 매칭할 수 있다. 새 SHA는 filter-branch가 끝난 뒤에야 확정된다.

# [02] 현황 파악 (read-only 조사)

작업 시작 전 **항상** 먼저 실행한다. 백업·브랜치·remote 분포를 머릿속에 그려야 위험을 평가할 수 있다.

```bash
# 1) 모든 브랜치 + 마지막 커밋
git branch -v

# 2) remote tip vs 로컬 main 격차
git remote -v
git log --oneline origin/main..HEAD       # 로컬 main이 origin보다 얼마나 앞
git rev-list --count upstream/main..HEAD  # 커밋 개수만

# 3) 다른 브랜치의 base
git merge-base main feature/x | xargs git log -1 --format="%h %s"

# 4) 특정 hash가 만진 변경
git show --stat <hash>                    # 파일 + line 변동
git show <hash> -- <file>                 # 특정 파일의 patch

# 5) 특정 파일을 만진 모든 커밋
git log --oneline base..HEAD -- <file>

# 6) author / committer 정보
git log --reverse base..HEAD --format="%h %ai %an <%ae> %s"

# 7) author date == committer date 일치 확인
git log --format="%H %at %ct" | awk '$2!=$3 {print "MISMATCH:", $1}'

# 8) 시간순(monotonic) 확인
git log --reverse --format="%at %h %s" | awk \
  '{ if (prev != "" && $1 < prev) print "OUT OF ORDER:", $0; prev=$1 }'
```

## 2-1. Tree 비교 — 코드 자체가 같은지

커밋 메시지가 달라도 코드(tree)는 동일할 수 있다. 중복 작업을 식별할 때 유용하다.

```bash
git diff A B --stat                       # 변경 파일 목록
git diff A B | wc -l                      # 변경 line 수 (0이면 tree 동일)

# 특정 커밋의 tree 해시
git rev-parse <hash>^{tree}

# 같은 tree를 가진 커밋 찾기
T=$(git rev-parse <hash>^{tree})
git log --format="%h %T" | awk -v t="$T" '$2==t {print $1}'
```

# [03] 백업 전략

rewrite는 destructive하다. **작업 전 반드시 backup 브랜치를 만든다.**

```bash
# 현재 HEAD를 가리키는 백업 브랜치
git branch backup-pre-rebase-$(date +%F)

# 작업은 임시 브랜치에서 하고, 성공 시 main으로 force-update
git checkout -b main-rebuild <starting-point>
```

실전에서 효과를 확인한 **3중 백업 원칙**:

1. 작업 source 자체 (예: `feature/x` — 복원용으로 유지)
2. main 시작 시점 백업 (예: `main-pre-rewrite-YYYY-MM-DD`)
3. 중간 실패 시 복귀용 (예: `main-pre-rebuild-YYYY-MM-DD`)

```bash
git fetch --all
```

:warning: `git fetch origin upstream`은 "origin과 upstream을 둘 다 fetch"가 **아니다.** `fetch <remote> <ref>` 문법으로 해석되어 "origin에서 upstream이라는 ref를 가져오기"가 된다. 모두 받으려면 `git fetch --all`을 쓴다.
{: .notice--warning}

# [04] Interactive rebase — drop / reword / edit

여러 커밋 중 일부만 제거하거나 메시지를 수정할 때 쓴다.

## 4-1. 기본 대화형

```bash
git rebase --interactive <base>
# editor에 todo list가 열린다:
#   pick aaa1111 commit msg
#   pick bbb2222 commit msg
# 각 줄을 pick / drop / reword / edit / squash / fixup 로 변경
```

## 4-2. 비대화형 자동화 (스크립트/CI용)

`GIT_SEQUENCE_EDITOR`는 todo list 편집기, `GIT_EDITOR`는 커밋 메시지 편집기다.

```bash
# 커밋 2개 drop + 1개 reword
export GIT_SEQUENCE_EDITOR='sed -i \
  -e "/^pick aaa1111 /s/^pick/drop/" \
  -e "/^pick bbb2222 /s/^pick/drop/" \
  -e "/^pick ccc3333 /s/^pick/reword/"'

# reword 시 커밋 메시지 자동 치환
export GIT_EDITOR='sed -i -e "s|<old-keyword>|<new-keyword>|"'

git rebase --interactive <base>
```

:warning: `GIT_EDITOR`는 reword뿐 아니라 **커밋 메시지 편집이 필요한 모든 단계**에서 호출된다. sed 패턴이 의도한 커밋에만 영향을 주도록 신중히 작성한다.
{: .notice--warning}

## 4-3. 진행 명령

```bash
git rebase --continue   # conflict 해결 후 다음 커밋으로
git rebase --skip        # 현재 커밋 건너뛰기 (drop 대체)
git rebase --abort       # 전체 취소, base 상태로 복귀
```

rebase 도중 상태를 직접 확인할 수도 있다.

```bash
ls .git/rebase-merge                    # rebase 진행 중인지
cat .git/rebase-merge/done              # 처리 완료된 커밋
cat .git/rebase-merge/git-rebase-todo   # 남은 커밋
```

# [05] Conflict 해결 패턴

## 5-1. 진단

```bash
git status --short                        # UU = both modified
grep -n -E "^<<<<<<<|^=======|^>>>>>>>" <file>   # marker 위치
git show <conflicting-hash> -- <file>     # 원본 커밋의 의도 확인
```

## 5-2. 해결 패턴 4가지

**패턴 A — HEAD 쪽 유지 (incoming 버림)**

```bash
git checkout --ours <file>                # 파일 전체

# 또는 특정 영역만 sed로
sed -i -e '/^<<<<<<< HEAD$/d' \
       -e '/^=======$/,/^>>>>>>> /d' \
       <file>
# 효과: <<<<<<< HEAD 줄 + ======= 부터 >>>>>>> 줄까지 제거 = HEAD section만 유지
```

**패턴 B — incoming 쪽 채택 (HEAD 버림)**

```bash
git checkout --theirs <file>

sed -i -e '/^<<<<<<< HEAD$/,/^=======$/d' \
       -e '/^>>>>>>> /d' \
       <file>
```

**패턴 C — 양쪽 다 채택 (marker만 제거)**

```bash
sed -i -e '/^<<<<<<< HEAD$/d' \
       -e '/^=======$/d' \
       -e '/^>>>>>>> /d' \
       <file>
```

HEAD가 비어 있고 incoming만 있는 경우에도 안전하다(incoming 자동 채택 효과).

**패턴 D — 수동 편집 (가장 안전)**

editor로 열어 conflict 영역만 의도대로 작성한다. 양쪽을 일부씩 채택하는 복잡한 케이스에는 필수다.

## 5-3. 해결 후 진행

```bash
<build-command>          # 예: go build ./... / npm run build / cargo build — 반드시 sanity
git add <files>
git rebase --continue
```

# [06] Squash 전략과 trade-off

## 6-1. Heavy squash — 전부 1개로

```bash
git reset --soft <base>          # 변경분은 stage에 남기고 커밋만 폐기
git commit -m "큰 통합 메시지"
```

## 6-2. reset 모드의 차이

| 모드 | HEAD | index | working dir |
|---|:---:|:---:|:---:|
| `--soft` | 이동 | 유지 | 유지 |
| `--mixed` (default) | 이동 | 이동 | 유지 |
| `--hard` | 이동 | 이동 | **이동 (destructive)** |

## 6-3. 어떤 squash를 고를까

| 방식 | 장점 | 단점 |
|---|---|---|
| Heavy (N→1) | 깨끗한 log | 단계별 작업 의도/blame 손실 |
| Medium (rebase + drop) | 원본 단위 보존 | conflict 가능 |
| Light (+1 commit) | 안전, 빠름 | "원래 X 있었구나" 히스토리 노출 |

**선택 기준**: 히스토리의 "왜 그렇게 되었나"가 중요하면 Medium, 외관만 중요하면 Heavy.

# [07] Author / CommitDate 정리 (filter-branch)

특정 커밋의 author date나 author 정보를 일괄 보정할 때 `filter-branch --env-filter`를 쓴다.

```bash
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --env-filter '
case "$GIT_COMMIT" in
  aaa1111*) export GIT_AUTHOR_DATE="2099-12-31T09:00:00+09:00" ;;
  bbb2222*) export GIT_AUTHOR_DATE="2099-12-31T10:00:00+09:00" ;;
esac

# committer date를 author date에 동기화 (모든 커밋)
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"

# 특정 author만 통일
if [ "$GIT_AUTHOR_EMAIL" = "old@example.com" ]; then
  export GIT_AUTHOR_NAME="NewName"
  export GIT_AUTHOR_EMAIL="new@example.com"
fi
' <base>..HEAD
```

| 변수 | 의미 |
|---|---|
| `GIT_AUTHOR_DATE` | 코드를 작성한 시점 |
| `GIT_AUTHOR_NAME` / `GIT_AUTHOR_EMAIL` | 작성자 |
| `GIT_COMMITTER_DATE` | 커밋 객체가 만들어진 시점 (rebase 시 자동으로 새로 부여됨) |
| `$GIT_COMMIT` | 처리 중인 원본 커밋 SHA (case 매칭용) |

날짜는 ISO 8601(`YYYY-MM-DDTHH:MM:SS+TZ`)을 권장한다. 작업 후에는 **반드시 정리**한다.

```bash
rm -rf .git/refs/original                 # filter-branch가 남긴 백업 ref
git reflog expire --expire=now --all
git gc --prune=now
```

:bulb: author 변경과 CommitDate 동기화의 더 자세한 방법(`--amend`, `rebase -i`, `git filter-repo` 비교 포함)은 별도 글 [Git History Author 변경 + CommitDate 동기화](/git/git-change-author-and-commitdate/)에서 다룬다. `filter-branch`는 git 공식적으로 deprecated이며, 복잡한 경우에는 `git filter-repo`가 더 빠르고 안전하다.
{: .notice--info}

# [08] Branch 정리

```bash
git branch -d <branch>    # safe — 다른 ref에서 도달 가능할 때만 허용
git branch -D <branch>    # force — 도달 불가능해도 삭제 (orphan 위험)
```

- 검증 끝난 임시 브랜치(예: `main-rebuild`를 main으로 reset한 뒤) → `-d`
- 도달 불가능한 오래된 백업 → `-D`
- **현재 active 브랜치는 삭제 불가** — 다른 브랜치로 checkout한 뒤 삭제

```bash
# main을 작업 브랜치로 교체
git checkout main
git reset --hard main-rebuild

# 백업 일괄 정리
for b in main-pre-* backup-*; do git branch -D "$b"; done
```

# [09] 안전 push

```bash
git push origin main                      # rewrite 후엔 rejected (non-fast-forward)
git push --force origin main              # 위험: 남이 push한 새 커밋도 덮어씀
git push --force-with-lease origin main   # 권장
```

`--force-with-lease`는 remote tip이 내가 마지막으로 fetch한 것과 다르면 거부하여 **다른 사람의 작업을 보호**한다.

- **안전한 경우**: 본인만 쓰는 personal repo, 다른 사람이 fetch하지 않은 게 확실한 stale remote
- **위험한 경우**: 활성 공유 브랜치(main/dev), 다른 사람이 이미 그 브랜치 위에서 작업 중

# [10] 시간순 정렬

rebase·cherry-pick의 default author date가 "지금"이라, 과거에 작업한 커밋이 최근 날짜로 표시되며 시간순이 깨질 수 있다. 매핑 표를 만들어 잘못된 날짜만 재배정한다.

```bash
git filter-branch -f --env-filter '
case "$GIT_COMMIT" in
  hash1*) export GIT_AUTHOR_DATE="2026-05-01T09:00:00+09:00" ;;
  hash2*) export GIT_AUTHOR_DATE="2026-05-01T10:00:00+09:00" ;;
esac
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
' <base>..HEAD

# 검증
git log --reverse <base>..HEAD --format="%h | %ai | %ci | %s"
git log --reverse --format="%at" | awk \
  '{ if (prev != "" && $1 < prev) print "OUT OF ORDER"; prev=$1 }'
```

**시간 분배 가이드**: 날짜 안에서는 30분~1시간 간격, 관련 커밋끼리 가깝게, 마지막 커밋 시각이 너무 늦지 않게.

# [11] 자주 하는 실수 (Gotchas)

**1) `git fetch origin upstream` ≠ "origin + upstream fetch"** — `git fetch --all` 또는 `git fetch origin && git fetch upstream`.

**2) grep no-match → exit 1 → `&&` short-circuit**

```bash
# 의도: 백업 없으면 만든다 — 그러나 grep no-match 시 모든 &&가 실패
git branch | grep "backup" && echo "exists" && git branch backup   # 안 만들어짐

# 해결
git branch | grep -q "backup" || git branch backup
```

**3) awk built-in `match`와 변수명 충돌** — `match`는 내장 함수이므로 변수명으로 쓰지 말고 `status` 등 다른 이름을 쓴다.

**4) filter-branch의 `.git/refs/original/` 잔재** — 정리하지 않으면 다음 실행 시 `--force`가 필요하다. 항상 reflog expire + gc까지 수행.

**5) rebase todo의 hash는 원본 hash** — 작업 중 새 SHA가 생기지만 todo list 매칭은 원본 hash 기준이다.

**6) sed delimiter 충돌(`/`)** — 경로에 `/`가 들어가면 `sed 's|a/b|c|'`처럼 delimiter를 바꾼다.

**7) 부모/자식 git repo 혼동** — `git rev-parse --show-toplevel`로 지금 어느 repo에서 명령을 실행 중인지 항상 확인한다. 부모 디렉토리가 자식을 `.gitignore` 처리하는 경우 자주 헷갈린다.

# [12] 실전 표준 흐름 (end-to-end)

N개 커밋에서 특정 키워드 관련 K개 제거 + upstream 추가 커밋 통합 + 일부 커밋의 author/date 정리를 한 번에 처리하는 표준 순서다.

```bash
# Step 1 — 분석
git fetch --all
git branch -v
git log --oneline upstream/main..<source-branch>
git log --oneline --all | grep -i "<keyword>"

# Step 2 — 백업 + 작업 브랜치
git branch main-pre-rewrite-$(date +%F) main
git branch main-pre-rebuild-$(date +%F) main
git checkout -b main-rebuild <source-branch>

# Step 3 — interactive rebase (drop + reword)
export GIT_SEQUENCE_EDITOR='sed -i \
  -e "/^pick aaa1111 /s/^pick/drop/" \
  -e "/^pick ccc3333 /s/^pick/reword/"'
export GIT_EDITOR='sed -i -e "s|<old-keyword>|<new-keyword>|"'
git rebase --interactive upstream/main

# Step 4 — conflict 해결 루프 (커밋마다)
git status --short
grep -n -E "^<<<<<<<|^=======|^>>>>>>>" <file>
<build-command>
git add <file>; git rebase --continue

# Step 5 — 검증
grep -rln -i "<removed-keyword>" --include="*.<ext>" .        # 코드 잔재 0
git log <base>..HEAD --format=%B | grep -ic "<removed-keyword>"  # 메시지 잔재 0

# Step 6 — main 교체
git checkout main
git reset --hard main-rebuild

# Step 7 — author/date 정리
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f --env-filter '
case "$GIT_COMMIT" in
  hash1*) export GIT_AUTHOR_DATE="2026-05-01T09:00:00+09:00" ;;
esac
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
' upstream/main..HEAD
rm -rf .git/refs/original
git reflog expire --expire=now --all
git gc --prune=now

# Step 8 — 최종 검증
git log <base>..HEAD --format="%H %at %ct %ae %ce" | awk '
  $2!=$3 {print "DATE MISMATCH:", $1}
  $4!=$5 {print "EMAIL MISMATCH:", $1}
  prev!="" && $2<prev {print "OUT OF ORDER:", $1}
  {prev=$2}'

# Step 9 — 브랜치 정리
git branch -d main-rebuild
for b in main-pre-* backup-*; do git branch -D "$b"; done

# Step 10 — push (수동)
git push --force-with-lease origin main
```

# [13] Quick reference card

```text
=== 조사 ===
git branch -v
git log --oneline <range>
git rev-list --count <range>
git merge-base A B
git diff A B --stat

=== 백업 ===
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

:bulb: 더 깊은 참조: `git help rebase`, `git help filter-branch`, 그리고 deprecated된 filter-branch의 대체 도구 [git-filter-repo](https://github.com/newren/git-filter-repo). 관련 글: [Git History Author 변경 + CommitDate 동기화](/git/git-change-author-and-commitdate/), [git commit --amend와 force push](/git/git-amend-force-push/).
{: .notice--info}
