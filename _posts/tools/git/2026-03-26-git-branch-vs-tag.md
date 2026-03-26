---
title: "Git Branch vs Tag — 차이점과 활용 전략"
description: "Git의 branch와 tag의 차이를 이해하고, 상황별로 어떤 것을 사용해야 하는지 정리"
excerpt: "branch는 움직이는 포인터, tag는 고정된 포인터 — 개발 흐름과 릴리스 관리에서의 활용법"
date: 2026-03-26
categories: Git
tags: [Git, branch, tag, release, 버전관리, lightweight-tag, annotated-tag, 브랜치전략]
---

:bulb: Git의 branch와 tag는 모두 커밋을 가리키는 포인터지만, 목적과 동작 방식이 다르다. 각각의 차이와 실전 활용법을 정리한다.
{: .notice--info}

# [01] 핵심 차이: 움직이는 포인터 vs 고정된 포인터

```
          branch (움직임)
              ↓
  A ← B ← C ← D ← E     ← 새 커밋이 생기면 branch는 따라감
              ↑
          tag v1.0 (고정)   ← tag는 항상 C를 가리킴
```

| 구분 | Branch | Tag |
|------|--------|-----|
| **본질** | 움직이는 포인터 | 고정된 포인터 |
| **커밋 추가 시** | 자동으로 최신 커밋을 따라감 | 생성 시점의 커밋에 고정 |
| **목적** | 개발 흐름 (작업 분기) | 특정 시점 기록 (릴리스, 마일스톤) |
| **수명** | 머지 후 삭제하는 것이 일반적 | 영구 보존 |
| **비유** | 포스트잇 (옮겨 붙일 수 있음) | 도장 (한번 찍으면 고정) |

---

# [02] Branch — 개발 흐름을 분리한다

## 2-1. 개념

branch는 **작업을 분리**하기 위한 도구다. 기능 개발, 버그 수정, 실험 등을 메인 코드에 영향 없이 진행할 수 있다.

```bash
# 브랜치 생성 및 이동
git checkout -b feature/login

# 작업 후 커밋
git add .
git commit -m "로그인 기능 구현"

# 메인에 합치기
git checkout main
git merge feature/login

# 머지 완료 후 삭제
git branch -d feature/login
```

## 2-2. 브랜치는 언제 사용하는가

| 상황 | 브랜치 이름 예시 |
|------|-----------------|
| 새 기능 개발 | `feature/login`, `feature/search` |
| 버그 수정 | `fix/login-error`, `hotfix/payment` |
| 실험/프로토타입 | `experiment/new-ui`, `spike/redis` |
| 릴리스 준비 | `release/1.2.0` |
| 환경별 분리 | `develop`, `staging` |

## 2-3. 브랜치 목록 확인

```bash
# 로컬 브랜치 목록
git branch

# 원격 포함 전체 목록
git branch -a

# 머지 완료된 브랜치만 (삭제 대상)
git branch --merged
```

---

# [03] Tag — 특정 시점을 기록한다

## 3-1. 개념

tag는 **특정 커밋에 이름을 붙여 고정**하는 도구다. 릴리스 버전, 배포 시점, 마일스톤 등 "이 시점을 기억해야 한다"는 용도로 사용한다.

```bash
# 태그 생성 (현재 커밋에)
git tag v1.0.0

# 태그를 원격에 푸시
git push origin v1.0.0
```

## 3-2. Lightweight Tag vs Annotated Tag

Git에는 두 종류의 태그가 있다.

### (A) Lightweight Tag — 단순 포인터

```bash
git tag v1.0.0
```

커밋을 가리키는 포인터만 생성한다. 작성자, 날짜, 메시지 등의 메타데이터가 없다.

### (B) Annotated Tag — 메타데이터 포함 (권장)

```bash
git tag -a v1.0.0 -m "첫 번째 정식 릴리스"
```

| 포함 정보 | 예시 |
|-----------|------|
| 태그 이름 | `v1.0.0` |
| 작성자 | `user <user@email.com>` |
| 생성 날짜 | `2026-03-26` |
| 메시지 | `첫 번째 정식 릴리스` |

:bulb: **Annotated Tag를 권장한다.** 누가, 언제, 왜 이 시점을 태그했는지 기록이 남기 때문이다. GitHub Releases도 annotated tag 기반으로 동작한다.
{: .notice--info}

## 3-3. 태그는 언제 사용하는가

| 상황 | 태그 이름 예시 |
|------|---------------|
| 정식 릴리스 | `v1.0.0`, `v2.1.3` |
| 베타/RC 릴리스 | `v1.0.0-beta.1`, `v1.0.0-rc.1` |
| 배포 시점 기록 | `deploy-2026-03-26` |
| 마일스톤 | `milestone-mvp`, `sprint-5-done` |

## 3-4. 태그 관련 명령어

```bash
# 태그 목록 확인
git tag

# 패턴으로 필터링
git tag -l "v1.*"

# 태그 상세 정보
git show v1.0.0

# 과거 커밋에 태그 달기
git tag -a v0.9.0 -m "베타 릴리스" abc1234

# 원격에 모든 태그 푸시
git push origin --tags

# 태그 삭제 (로컬)
git tag -d v1.0.0

# 태그 삭제 (원격)
git push origin --delete v1.0.0

# 특정 태그 시점으로 체크아웃
git checkout v1.0.0
```

:warning: 태그를 체크아웃하면 **detached HEAD** 상태가 된다. 이 상태에서 커밋하면 어떤 브랜치에도 속하지 않으므로, 작업이 필요하면 브랜치를 생성해야 한다.
{: .notice--warning}

```bash
# 태그 시점에서 핫픽스 브랜치 생성
git checkout v1.0.0
git checkout -b hotfix/v1.0.1
```

---

# [04] 실전 비교: 같은 상황에서 뭘 쓸까?

| 상황 | Branch | Tag | 권장 |
|------|--------|-----|------|
| 로그인 기능 개발 시작 | `feature/login` | - | **Branch** |
| v1.0.0 정식 배포 완료 | - | `v1.0.0` | **Tag** |
| 배포 후 긴급 버그 발견 | `hotfix/payment` | - | **Branch** |
| 긴급 버그 수정 후 배포 | - | `v1.0.1` | **Tag** |
| 다음 버전 개발 시작 | `release/1.1.0` | - | **Branch** |
| "이 커밋으로 돌아갈 수 있게 해줘" | - | `backup-before-refactor` | **Tag** |
| A/B 테스트를 위해 코드를 분기 | `experiment/new-checkout` | - | **Branch** |

:bulb: **판단 기준은 간단하다:**
- **앞으로 커밋을 추가할 거면** → Branch
- **이 시점을 고정해서 기억할 거면** → Tag
{: .notice--info}

---

# [05] 실전 워크플로우 예시

일반적인 개발-릴리스 흐름에서 branch와 tag가 함께 사용되는 예시다.

```bash
# 1. 기능 개발 (branch)
git checkout -b feature/search
# ... 작업 ...
git commit -m "검색 기능 구현"

# 2. 메인에 머지
git checkout main
git merge feature/search
git branch -d feature/search

# 3. 릴리스 태그 (tag)
git tag -a v1.2.0 -m "검색 기능 추가"
git push origin main --tags

# 4. 배포 후 버그 발견 → 핫픽스 (branch)
git checkout -b hotfix/search-crash
# ... 수정 ...
git commit -m "검색 크래시 수정"

# 5. 머지 + 패치 태그 (tag)
git checkout main
git merge hotfix/search-crash
git branch -d hotfix/search-crash
git tag -a v1.2.1 -m "검색 크래시 수정"
git push origin main --tags
```

```
main:  A ─ B ─ C ─ D(merge) ─ E ─ F(merge)
              │         ↑              ↑
              │      v1.2.0         v1.2.1
              │
feature/search: C1 ─ C2
                         hotfix: E1
```

---

# [06] Semantic Versioning (태그 네이밍)

태그 이름은 **Semantic Versioning(SemVer)** 규칙을 따르는 것이 표준이다.

```
v MAJOR . MINOR . PATCH
  │       │       │
  │       │       └─ 버그 수정 (하위 호환)
  │       └───────── 기능 추가 (하위 호환)
  └───────────────── 호환성 깨지는 변경
```

| 변경 내용 | 버전 변화 | 예시 |
|-----------|-----------|------|
| 오타 수정, 버그 픽스 | PATCH +1 | `v1.0.0` → `v1.0.1` |
| 새 기능 추가 (기존 호환) | MINOR +1 | `v1.0.1` → `v1.1.0` |
| API 변경 (기존 호환 깨짐) | MAJOR +1 | `v1.1.0` → `v2.0.0` |

---

# [07] 정리

| 항목 | Branch | Tag |
|------|--------|-----|
| **한 줄 요약** | 개발 중인 작업 흐름 | 완료된 시점의 스냅샷 |
| **포인터** | 커밋 추가 시 자동 이동 | 고정 |
| **생성 시점** | 작업 시작 전 | 릴리스/배포 완료 후 |
| **삭제** | 머지 후 삭제 권장 | 삭제하지 않음 (영구 보존) |
| **주 용도** | feature, fix, release 분기 | 버전 릴리스, 마일스톤 |
| **원격 푸시** | `git push origin branch` | `git push origin tag` |

```
Branch = "작업 중" 표시
Tag    = "완료" 도장
```
