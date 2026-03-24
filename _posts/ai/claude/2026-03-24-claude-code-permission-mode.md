---
title: "Claude Code 권한 모드 5단계: 기본부터 YOLO까지"
description: "Claude Code의 5가지 권한 위임 모드(기본, Accept Edits, Plan, Bypass, YOLO)별 실행 방법과 Docker 격리 안전 사용법 정리"
excerpt: "Claude Code 권한 모드 5단계 비교, 실행 방법, 실제 사고 사례, Docker 격리 안전 가이드"
date: 2026-03-24
categories: Claude
tags: [Claude Code, permission, YOLO, bypassPermissions, Docker, 권한모드, 자동승인, 안전사용]
---

:bulb: Claude Code는 5가지 권한 모드를 제공한다. 작업 성격에 따라 적절한 모드를 선택하면 생산성과 안전성을 동시에 확보할 수 있다.
{: .notice--info}

# [01] 권한 모드 5단계

Claude Code는 도구 실행(파일 수정, 셸 명령 등)마다 사용자 승인을 요청하는 것이 기본이다.
이 승인 수준을 조절하는 것이 **권한 모드**다.

| 모드 | 명령어 / 전환 방법 | 설명 |
|------|---------------------|------|
| **기본** | `claude` | 매번 승인 요청 |
| **Accept Edits** | `Shift+Tab` (대화 중) | 파일 수정만 자동 승인, 셸 명령은 물어봄 |
| **Plan** | `claude --permission-mode plan` | 전체 계획을 먼저 보여주고 실행 |
| **Bypass** | `claude --permission-mode bypassPermissions` | 모든 권한 자동 승인 |
| **YOLO** | `claude --dangerously-skip-permissions` | Bypass와 동일, 더 직관적인 이름 |

:bulb: `Shift+Tab`은 대화 중에 기본 → Accept Edits → Plan 세 가지를 순환 전환한다.
{: .notice--info}

---

# [02] 모드별 실행 방법

## 2-1. 기본 모드

```shell
claude
```

모든 도구 실행 전 승인을 묻는다. 가장 안전하지만, 반복 작업 시 승인 피로가 생길 수 있다.

## 2-2. Accept Edits 모드

대화 중에 `Shift+Tab`을 누르면 전환된다.

- **자동 승인**: 파일 읽기, 수정, 생성
- **승인 필요**: 셸 명령 (`Bash` 도구)

파일 수정은 신뢰하되, 시스템 명령은 확인하고 싶을 때 적합하다.

## 2-3. Plan 모드

```shell
claude --permission-mode plan
```

Claude가 작업을 실행하기 전에 **전체 계획을 먼저 제시**한다.
계획을 검토한 뒤 승인하면 실행이 시작된다.

복잡한 리팩토링이나 여러 파일에 걸친 작업에서 유용하다.

## 2-4. Bypass / YOLO 모드

```shell
# 대화형 실행
claude --dangerously-skip-permissions

# 단일 작업 자동 실행 (-p 와 함께)
claude --dangerously-skip-permissions -p "모든 lint 오류 수정해줘"
```

모든 도구 실행을 자동 승인한다. 승인 없이 파일 수정, 셸 명령이 실행되므로 **격리 환경에서만 사용**해야 한다.

### 특정 도구 차단 (부분 제한)

```shell
# rm 계열 명령 차단하면서 나머지는 자동 승인
claude --dangerously-skip-permissions \
  --disallowedTools "Bash(rm:*)" \
  "Todo 앱 리팩토링해줘"
```

---

# [03] 영구 설정

## 3-1. settings.json으로 기본 모드 변경

매번 플래그를 붙이지 않고 기본 모드를 변경할 수 있다:

```json
// ~/.claude/settings.json
{
  "defaultMode": "bypassPermissions"
}
```

| 값 | 대응 모드 |
|---|---|
| `"default"` | 기본 (매번 승인) |
| `"acceptEdits"` | Accept Edits |
| `"plan"` | Plan |
| `"bypassPermissions"` | Bypass / YOLO |

## 3-2. 특정 도구만 허용

settings.json에서 특정 도구를 자동 승인 목록에 추가할 수도 있다:

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Edit",
      "Write",
      "Glob",
      "Grep"
    ]
  }
}
```

이 방식은 YOLO처럼 전부 허용하지 않으면서, 자주 쓰는 도구의 승인을 생략할 수 있다.

---

# [04] 실제 사고 사례

:warning: **YOLO 모드를 격리 없이 사용하면 시스템이 파괴될 수 있다.** 아래는 실제 보고된 사례다.
{: .notice--danger}

## 4-1. 사례 1 — 시스템 디렉토리 삭제 (2025.10)

개발자 Mike Wolak이 Ubuntu/WSL2에서 중첩 디렉토리 작업 중, Claude Code가 **루트(`/`)에서 `rm -rf`를 실행**하여 `/bin`, `/boot`, `/etc` 등 시스템 경로 전체를 삭제 시도한 사건이 발생했다.

## 4-2. 사례 2 — 홈 디렉토리 삭제 (2025.12)

다른 사용자가 패키지 정리를 요청했을 때, Claude Code가 아래 명령을 실행했다:

```shell
rm -rf tests/ patches/ plan/ ~/
```

`~/`(홈 디렉토리)가 포함되어 **개인 파일 전체가 삭제**되었다.

## 4-3. 교훈

두 사례 모두 **YOLO 모드를 격리 없이 사용**한 것이 원인이다.
Claude Code는 강력하지만, 맥락을 잘못 해석하면 의도하지 않은 파괴적 명령을 실행할 수 있다.

---

# [05] 안전하게 쓰는 방법 — Docker 격리

공식 문서는 `bypassPermissions` 모드를 **컨테이너나 VM 같은 격리된 환경에서만 사용할 것**을 권장한다.

## 5-1. Docker 격리 실행

```shell
# 1. 실행 전 반드시 git 체크포인트
git add -A && git commit -m "checkpoint before claude YOLO"

# 2. Docker 컨테이너 안에서만 실행
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  --network none \
  ubuntu:22.04 \
  claude --dangerously-skip-permissions "기능 구현해줘"

# 3. 문제 생기면 롤백
git reset --hard HEAD
```

| 옵션 | 역할 |
|------|------|
| `-v $(pwd):/workspace` | 현재 디렉토리만 컨테이너에 마운트 |
| `--network none` | 네트워크 차단 (외부 접근 방지) |
| `--rm` | 컨테이너 종료 시 자동 삭제 |

## 5-2. git 체크포인트 패턴

Docker 없이 YOLO 모드를 쓸 때도 최소한 이 패턴은 지켜야 한다:

```shell
# 작업 전 커밋 → YOLO 모드 → 결과 검토 → 커밋 or 롤백
git add -A && git commit -m "before"
claude --dangerously-skip-permissions -p "할 일 앱 구현해줘"
git diff   # 변경 내용 확인
git add -A && git commit -m "after"   # 또는 git reset --hard HEAD
```

---

# [06] 상황별 권장 모드

| 상황 | 권장 모드 | 이유 |
|------|-----------|------|
| 일반 개발 (승인 피로 없음) | 기본 | 가장 안전 |
| 매번 승인이 귀찮다 | `Shift+Tab` (Accept Edits) | 파일 수정은 자동, 셸은 확인 |
| 복잡한 작업, 계획 먼저 보고 싶다 | `--permission-mode plan` | 실행 전 전체 계획 검토 |
| 자동화 파이프라인, CI/CD | `--dangerously-skip-permissions` | 사람 없이 실행해야 할 때 |
| 혼자 개발, 장시간 자율 실행 | Docker 격리 + YOLO | 격리 환경에서만 전체 승인 |

:warning: **YOLO/Bypass 모드를 호스트 OS에서 직접 사용하는 것은 위험하다.** 반드시 Docker나 VM 격리, 또는 최소한 git 체크포인트를 병행해야 한다.
{: .notice--danger}
