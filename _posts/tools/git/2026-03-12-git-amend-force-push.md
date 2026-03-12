---
title: "Git 이전 커밋에 변경사항 끼워넣기 (amend + force push)"
date: 2026-03-12
categories: Git
tags: [git, amend, force-push]
---

:bulb: 이미 원격에 push한 직전 커밋의 내용이나 메시지를 수정하고 싶을 때, `--amend`로 직전 커밋에 합치고 force push하는 방법을 작성한다.
{: .notice--info}

# [01] 언제 사용하는가?

- 원격에 push한 직후 **오타, 누락 파일, 소소한 수정**을 발견했을 때
- **커밋 메시지를 고치고 싶을 때**
- 새 커밋을 만들어 이력을 늘리고 싶지 않을 때

---

# [02] 사용 방법

## 2-1. 파일 수정 후 스테이징

수정할 파일을 편집한 뒤, staging area에 추가한다.

```shell
git add 수정한_파일_경로
```

**출력 예:**

```shell
$ git add _posts/2026-03-05-my-post.md
```

출력 없이 정상 완료된다.

---

## 2-2. 직전 커밋에 합치기

### (A) 커밋 메시지를 유지하는 경우

```shell
git commit --amend --no-edit
```

**출력 예:**

```
[main a9b8c7d] docs: add git author change post
 Date: Wed Mar 12 10:00:00 2026 +0900
 1 file changed, 5 insertions(+), 2 deletions(-)
```

### (B) 커밋 메시지도 함께 변경하는 경우

```shell
git commit --amend -m "docs: fix heading level in git post"
```

**출력 예:**

```
[main b8c7d6e] docs: fix heading level in git post
 Date: Wed Mar 12 10:00:00 2026 +0900
 1 file changed, 5 insertions(+), 2 deletions(-)
```

### (C) 에디터에서 메시지를 수정하는 경우

```shell
git commit --amend
```

에디터(vi 등)가 열리며, 기존 커밋 메시지를 직접 편집할 수 있다. 저장 후 종료하면 반영된다.

:bulb: 파일 변경 없이 **커밋 메시지만 고치고 싶다면**, `git add` 없이 바로 `git commit --amend -m "새 메시지"`를 실행하면 된다.
{: .notice--info}

**옵션 설명:**

| 옵션 | 설명 |
|---|---|
| `--amend` | 새 커밋을 만들지 않고 **직전 커밋에 변경사항을 합침** |
| `--no-edit` | 커밋 메시지를 수정하지 않고 그대로 유지 |
| `-m "메시지"` | 커밋 메시지를 지정한 내용으로 변경 |
| (옵션 없음) | 에디터가 열려 기존 메시지를 직접 편집 |

---

## 2-3. 원격에 강제 push

이미 push한 커밋을 수정했으므로, 일반 push는 거부된다. force push가 필요하다.

```shell
git push --force-with-lease origin main
```

**옵션 설명:**

| 옵션 | 설명 |
|---|---|
| `--force-with-lease` | 내가 마지막으로 fetch한 이후 다른 사람이 push한 내역이 없을 때만 강제 push 허용. `--force`보다 안전 |

**출력 예:**

```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Writing objects: 100% (3/3), 320 bytes | 320.00 KiB/s, done.
Total 3 (delta 1), reused 0 (delta 0), pack-reused 0
To https://github.com/testuser/test-repo.git
 + a1b2c3d...a9b8c7d main -> main (forced update)
```

---

# [03] 전체 흐름 요약

```shell
# --- 파일 + 메시지 모두 유지, 내용만 추가 ---
git add 수정한_파일_경로
git commit --amend --no-edit
git push --force-with-lease origin main

# --- 파일 수정 + 메시지도 변경 ---
git add 수정한_파일_경로
git commit --amend -m "새로운 커밋 메시지"
git push --force-with-lease origin main

# --- 파일 변경 없이 메시지만 변경 ---
git commit --amend -m "새로운 커밋 메시지"
git push --force-with-lease origin main
```

---

# [04] 주의사항

:warning: **혼자 쓰는 repo에서만 자유롭게 사용**한다. 팀원이 있는 브랜치에서는 반드시 사전 협의 후 진행한다.
{: .notice--warning}

| 상황 | 권장 방법 |
|---|---|
| 혼자 쓰는 repo / 브랜치 | `--amend` + `--force-with-lease` 자유롭게 사용 |
| 팀원과 공유하는 브랜치 | 새 커밋으로 push (amend 사용 자제) |

- `--amend`는 **커밋 해시가 변경**되므로, 다른 사람이 이미 pull한 상태에서 force push하면 충돌이 발생한다.
- `--force-with-lease`는 `--force`보다 안전하지만, 여전히 원격 이력을 덮어쓰는 동작이다.
- 직전 커밋이 아닌 **더 오래된 커밋**을 수정하고 싶다면 `git rebase -i`를 사용해야 한다.
