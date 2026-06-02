---
title: "Kubernetes 클러스터에서 이상이 있는 Pod 확인하기"
description: "Error, Pending, CrashLoopBackOff, Init 등 비정상 상태 Pod를 찾는 kubectl 명령어 — Completed 포함/비포함 두 가지 케이스 정리"
excerpt: "STATUS 컬럼의 의미, field-selector의 함정, Completed가 정상인지 판단하는 법까지 — 운영 중 문제 Pod를 빠르게 솎아내는 실전 레퍼런스"
date: 2026-06-02
categories: K8s
tags: [Kubernetes, kubectl, Pod, CrashLoopBackOff, Pending, Completed, troubleshooting, field-selector, get-pods, 운영]
ref: k8s-check-abnormal-pods
---

:bulb: 운영 중인 클러스터에서 `Error`, `Pending`, `CrashLoopBackOff`, `Init:0/1` 같은 **비정상 Pod만** 빠르게 솎아내는 `kubectl` 명령어를 정리한다. 핵심 명령어는 **Completed 포함/비포함** 두 가지 케이스로 제공한다.
{: .notice--info}

---

# [01] 먼저 알아야 할 것 — STATUS 컬럼의 정체

`kubectl get pods`의 **STATUS** 컬럼에 보이는 값은 사실 **두 종류**가 섞여 있다. 이걸 모르면 필터가 엉뚱하게 동작한다.

| STATUS 표시 | 실제 정체 | `--field-selector`로 잡히나? |
|---|---|---|
| `Pending` | phase | ✅ |
| `Running` | phase | ✅ |
| `Completed` | phase = `Succeeded` | ✅ |
| `Error` | phase = `Failed` | ✅ |
| `CrashLoopBackOff` | **컨테이너 reason** | ❌ (phase는 `Running`) |
| `Init:0/1` | **컨테이너 reason** | ❌ (phase는 `Pending`) |
| `ImagePullBackOff` | **컨테이너 reason** | ❌ |
| `Terminating` | deletionTimestamp 존재 | ❌ |

:warning: `CrashLoopBackOff`, `Init:0/1`, `ImagePullBackOff`는 **phase가 아니라 컨테이너 reason**이다. 그래서 `--field-selector=status.phase!=Running`으로는 **안 잡힌다.** 이게 가장 흔한 함정이다.
{: .notice--warning}

이 때문에 **텍스트 기반 `grep` 방식이 실무에서 더 안전**하다. 아래에서 두 접근을 모두 다룬다.

---

# [02] 전체 Pod 보기 (기준점)

먼저 모든 네임스페이스의 모든 Pod를 본다.

```bash
# 모든 네임스페이스의 모든 Pod (노드/IP 등 추가 정보 포함)
kubectl get pods -A -o wide
```

| 옵션 | 의미 |
|------|------|
| `-A` | `--all-namespaces` — 전체 네임스페이스 |
| `-o wide` | NODE, IP, NOMINATED NODE 등 추가 컬럼 표시 |

:bulb: `--sort-by`는 **정렬만** 할 뿐 **필터링은 하지 않는다.** `kubectl get pods -A --sort-by='.status.phase'`는 `Running`을 포함한 모든 Pod를 다 보여준다. "문제 Pod만" 보려면 정렬이 아니라 **필터링(아래)**이 필요하다.
{: .notice--info}

---

# [03] 핵심 — 비정상 Pod만 솎아내기

## 3-1. 케이스 A: Completed **비포함** (Completed를 정상으로 간주)

CronJob/Job이 정상적으로 끝낸 `Completed` Pod까지 제외하고, **진짜 문제 Pod만** 보고 싶을 때.

```bash
# Running, Completed 둘 다 제외 → 나머지(문제 Pod)만
kubectl get pods -A -o wide | grep -v -E 'Running|Completed'
```

- `grep -v` : 매칭되는 줄을 **제외**
- `Running`(정상 동작) + `Completed`(정상 완료)를 모두 빼므로 → `Error`, `Pending`, `CrashLoopBackOff`, `Init`, `ImagePullBackOff` 등만 남는다.

:warning: 단점: `-v`는 헤더(`NAMESPACE NAME ...`)줄도 같이 지운다. 헤더를 살리려면 아래 "헤더 보존 버전"을 쓴다.
{: .notice--warning}

**헤더 보존 + Completed 비포함:**

```bash
# 헤더(NAMESPACE)는 남기고, Running/Completed만 제외
kubectl get pods -A -o wide | grep -E 'NAMESPACE|Error|CrashLoopBackOff|Pending|Init|ImagePullBackOff|Terminating|OOMKilled|ErrImagePull'
```

→ 화이트리스트 방식. `NAMESPACE`(헤더) + 문제 상태들만 통과시킨다. `Completed`는 목록에 없으니 자연스럽게 빠진다.

## 3-2. 케이스 B: Completed **포함** (Completed도 점검 대상)

`Completed`까지 포함해서 "Running이 아닌 모든 Pod"를 보고 싶을 때. (예: Deployment의 Pod가 `Completed`로 빠진 비정상 상황까지 잡아내고 싶을 때 — [05] 참고)

```bash
# Running만 제외 → Completed 포함 나머지 전부
kubectl get pods -A -o wide | grep -v 'Running'
```

**헤더 보존 + Completed 포함:**

```bash
# 헤더는 남기고 Running만 제외
kubectl get pods -A -o wide | grep -v -w 'Running' | grep -E 'NAMESPACE|[A-Za-z]'
```

또는 더 단순하게, field-selector로 phase 필터:

```bash
# phase가 Running이 아닌 Pod (Completed=Succeeded, Error=Failed, Pending 포함)
kubectl get pods -A -o wide --field-selector=status.phase!=Running
```

:warning: 다시 강조 — 이 field-selector는 `CrashLoopBackOff`(phase=Running)를 **놓친다.** 정확히 잡으려면 `grep` 케이스 B를 쓰는 것이 안전하다.
{: .notice--warning}

---

# [04] 특정 상태만 콕 집어 보기

```bash
kubectl get pods -A -o wide | grep CrashLoopBackOff
kubectl get pods -A -o wide | grep -E 'Error|CrashLoopBackOff|ImagePullBackOff'
kubectl get pods -A -o wide | grep Pending
kubectl get pods -A -o wide | grep Init          # Init:0/1 등 초기화 멈춤
kubectl get pods -A -o wide | grep Terminating   # 종료 안 되고 매달린 Pod
kubectl get pods -A -o wide | grep Completed
```

**phase 기준(정확한 필터):**

```bash
kubectl get pods -A --field-selector=status.phase=Pending    -o wide
kubectl get pods -A --field-selector=status.phase=Failed     -o wide   # Error
kubectl get pods -A --field-selector=status.phase=Succeeded  -o wide   # Completed
```

---

# [05] Completed는 정상인가?

`Completed`는 **맥락에 따라** 정상일 수도, 비정상의 흔적일 수도 있다. 판단 기준은 단 하나 — **"이 Pod는 원래 끝나도록 설계됐는가?"**

| 소유자(Controller) | `Completed`의 의미 |
|---|---|
| Job / CronJob | ✅ 정상 (작업 완료, exit 0) |
| Init Container | ✅ 정상 (초기화 후 종료) |
| Deployment / ReplicaSet | ⚠️ 비정상 (죽으면 안 되는데 끝남) |
| StatefulSet / DaemonSet | ⚠️ 비정상 (메인 프로세스가 종료됨) |

**소유자 확인 명령어:**

```bash
# 이 Pod를 누가 만들었는지(소유 컨트롤러 종류) 확인
kubectl get pod <pod-name> -n <namespace> \
  -o jsonpath='{.metadata.ownerReferences[0].kind}'
```

- 결과가 `Job` → `Completed`는 정상 👍
- 결과가 `ReplicaSet`(=Deployment) / `StatefulSet` → `Completed`면 의심 🔍 (엔트리포인트가 foreground로 안 돌고 끝났을 가능성)

:bulb: CronJob은 성공한 Pod를 일부러 남겨둔다(`successfulJobsHistoryLimit`). `Completed` Pod가 여러 개 쌓여 있는 건 대개 자연스러운 현상이다. 그래서 평소 점검에서는 **케이스 A(Completed 비포함)**가 노이즈가 적다.
{: .notice--info}

---

# [06] 문제 Pod 원인 진단

비정상 Pod를 찾았다면 원인을 본다.

```bash
# Events 섹션에서 원인 확인 (스케줄링 실패, 이미지 못 받음 등)
kubectl describe pod <pod-name> -n <namespace>

# 로그 확인
kubectl logs <pod-name> -n <namespace>

# CrashLoopBackOff 디버깅의 핵심 — 이전(크래시된) 컨테이너 로그
kubectl logs <pod-name> -n <namespace> --previous

# 재시작 횟수가 많은 Pod 찾기 (RESTARTS 컬럼 정렬)
kubectl get pods -A --sort-by='.status.containerStatuses[0].restartCount' -o wide
```

---

# [07] 핵심 요약

| # | 요약 |
|---|------|
| 1 | STATUS 컬럼은 **phase**(Pending/Running/Succeeded/Failed)와 **컨테이너 reason**(CrashLoopBackOff/Init 등)이 섞여 있다 |
| 2 | `--field-selector=status.phase!=Running`은 **CrashLoopBackOff를 놓친다** — phase가 Running이기 때문 |
| 3 | **케이스 A (Completed 비포함):** `kubectl get pods -A -o wide \| grep -v -E 'Running\|Completed'` |
| 4 | **케이스 B (Completed 포함):** `kubectl get pods -A -o wide \| grep -v 'Running'` |
| 5 | `--sort-by`는 정렬만 할 뿐 Running을 걸러주지 않는다 — 필터링은 `grep`/`field-selector`로 |
| 6 | `Completed`가 정상인지는 소유 컨트롤러로 판단 — Job/CronJob이면 정상, Deployment/StatefulSet이면 의심 |

:bulb: 가장 자주 쓰는 한 줄 — **`kubectl get pods -A -o wide | grep -v -E 'Running|Completed'`** — 정상이 아닌 모든 Pod를 한 번에 잡아낸다.
{: .notice--info}
