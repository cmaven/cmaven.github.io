---
title: "Git Pull 시 로컬 변경사항 보존하기 — git stash 활용법"
description: "운영 서버에서 로컬 수정사항이 있을 때 git pull을 충돌 없이 수행하는 git stash 사용법 정리"
excerpt: "git stash로 로컬 변경사항을 임시 저장하고, pull 후 복원하여 충돌 없이 원격 변경사항을 받는 방법"
date: 2026-04-09
categories: Git
tags: [Git, git-stash, git-pull, merge충돌, 운영서버, 로컬변경보존]
---

:bulb: 운영 서버에서 설정 파일 등을 로컬 수정한 상태에서, 원격 저장소의 변경사항을 충돌 없이 받는 방법을 정리한다.
{: .notice--info}

---

# [01] 문제 상황

운영 서버에서 Docker 설정 등을 직접 수정해서 사용하고 있다. 이 상태에서 `git pull`을 하면 merge 충돌이 발생할 수 있다.

```bash
user@server:~/project$ git status
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   docker-compose.dev.yml
        modified:   package-lock.json

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        docs/2025/project-alpha/
        docs/2025/project-beta/
        docs/2026/project-gamma/
```

이때 원격에서는 `config.ts` 같은 다른 파일이 변경되었다. 로컬에서 수정한 `docker-compose.dev.yml`, `package-lock.json`은 그대로 유지하면서, 원격 변경사항만 받고 싶다.

```
원격: config.ts 변경됨
로컬: docker-compose.dev.yml, package-lock.json 변경됨
      → 서로 다른 파일이므로 충돌 없이 가능해야 함
```

그런데 `git pull`을 바로 실행하면:

```bash
user@server:~/project$ git pull
error: Your local changes to the following files would be overwritten by merge:
        package-lock.json
Please commit your changes or stash them before you can merge.
```

Git은 **커밋되지 않은 변경사항이 있으면 pull을 거부**한다.

---

# [02] 해결: git stash

## 2-1. 한 줄 명령어

```bash
git stash && git pull && git stash pop
```

이 한 줄로 끝난다. 각 단계가 하는 일:

| 단계 | 명령 | 동작 |
|------|------|------|
| 1 | `git stash` | 로컬 변경사항을 임시 저장소에 보관 |
| 2 | `git pull` | 원격 변경사항 다운로드 및 반영 |
| 3 | `git stash pop` | 임시 저장한 로컬 변경사항 복원 |

## 2-2. 실행 결과

```bash
# 1. 로컬 변경사항 임시 저장
user@server:~/project$ git stash
Saved working directory and index state WIP on main: abc1234 latest commit message

# 2. 원격 변경사항 받기 (이제 로컬이 깨끗하므로 정상 동작)
user@server:~/project$ git pull
Updating abc1234..def5678
Fast-forward
 config.ts | 5 +++--
 1 file changed, 3 insertions(+), 2 deletions(-)

# 3. 로컬 변경사항 복원
user@server:~/project$ git stash pop
On branch main
Changes not staged for commit:
        modified:   docker-compose.dev.yml
        modified:   package-lock.json

Dropped refs/stash@{0} (a1b2c3d4...)
```

원격의 `config.ts` 변경이 반영되고, 로컬의 `docker-compose.dev.yml`, `package-lock.json` 수정사항도 그대로 유지된다.

---

# [03] git stash 상세

## 3-1. 동작 원리

```
작업 디렉토리 (수정된 파일들)
    ↓ git stash
임시 저장소 (stash stack)    ← 변경사항 보관
작업 디렉토리 (깨끗한 상태)  ← git pull 가능
    ↓ git pull
원격 변경사항 반영
    ↓ git stash pop
임시 저장소에서 복원         ← 로컬 변경사항 + 원격 변경사항 공존
```

## 3-2. 주요 명령어

| 명령어 | 설명 |
|--------|------|
| `git stash` | 변경사항 임시 저장 (tracked 파일만) |
| `git stash -u` | untracked 파일도 포함하여 저장 |
| `git stash list` | 저장된 stash 목록 확인 |
| `git stash show` | 가장 최근 stash의 변경 내용 요약 |
| `git stash show -p` | 가장 최근 stash의 diff 확인 |
| `git stash pop` | 가장 최근 stash 복원 후 삭제 |
| `git stash apply` | 가장 최근 stash 복원 (삭제하지 않음) |
| `git stash drop` | 가장 최근 stash 삭제 |
| `git stash clear` | 모든 stash 삭제 |

## 3-3. pop vs apply

| 명령 | 복원 | stash 삭제 | 용도 |
|------|------|-----------|------|
| `git stash pop` | O | O | 일반적 사용 (1회성) |
| `git stash apply` | O | X | 여러 브랜치에 같은 변경 적용 시 |

---

# [04] stash pop 시 충돌이 발생하면

로컬과 원격이 **같은 파일의 같은 부분**을 수정했다면, `stash pop` 시 충돌이 발생한다.

```bash
user@server:~/project$ git stash pop
Auto-merging docker-compose.dev.yml
CONFLICT (content): Merge conflict in docker-compose.dev.yml
```

이 경우:

```bash
# 1. 충돌 파일 확인
git status

# 2. 충돌 부분 수동 해결 (에디터로 열어서 <<<< ==== >>>> 부분 정리)
vi docker-compose.dev.yml

# 3. 해결 후 stash 정리
git stash drop
```

:warning: `stash pop`에서 충돌이 발생하면 stash가 자동 삭제되지 않는다. 충돌 해결 후 `git stash drop`으로 직접 삭제해야 한다.
{: .notice--warning}

---

# [05] 다른 방법들

## 5-1. 특정 파일만 stash

모든 변경사항이 아닌, 특정 파일만 stash하고 싶을 때:

```bash
# 특정 파일만 stash
git stash push docker-compose.dev.yml package-lock.json

# pull 후 복원
git pull
git stash pop
```

## 5-2. git pull --rebase --autostash

Git 2.9 이상에서는 stash를 자동으로 처리하는 옵션이 있다.

```bash
git pull --rebase --autostash
```

이 명령 하나로 `stash → pull → rebase → stash pop`을 자동 수행한다.

영구 설정:

```bash
git config --global rebase.autoStash true
```

이후 `git pull --rebase`만 하면 자동으로 stash/pop이 적용된다.

---

# [06] 정리

| 상황 | 명령어 |
|------|--------|
| 로컬 변경 보존 + pull | `git stash && git pull && git stash pop` |
| 자동 stash + rebase | `git pull --rebase --autostash` |
| 특정 파일만 stash | `git stash push <파일1> <파일2>` |
| stash 충돌 시 | 수동 해결 후 `git stash drop` |

:bulb: 운영 서버처럼 로컬 설정 파일을 수정해서 사용하는 환경에서는, `git stash && git pull && git stash pop` 패턴을 습관화하면 충돌 걱정 없이 원격 변경사항을 받을 수 있다.
{: .notice--info}
