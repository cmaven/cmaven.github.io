---
title: "Kubernetes 업데이트 전략 정리 — Rolling/Blue-Green/Canary"
description: "Rolling Update, Blue/Green, Canary 배포 패턴과 K8s API의 RollingUpdate/Recreate/OnDelete 전략의 차이, 두 추상화 층위 구분, NVIDIA Driver Operator 케이스 분석"
excerpt: "K8s 업데이트는 두 층위로 분리해서 봐야 한다 — API 차원의 strategy(A)와 배포 패턴(B). Rolling/Blue-Green/Canary 비교부터 NVIDIA driver 같은 host kernel 결합 워크로드 실무 적용까지"
date: 2026-05-06
categories: K8s
tags: [Kubernetes, 배포전략, RollingUpdate, BlueGreen, Canary, Recreate, OnDelete, DaemonSet, Argo-Rollouts, NVIDIA-GPU-Operator]
ref: k8s-update-strategies
---

:bulb: K8s 업데이트 전략은 **두 추상화 층위**로 분리해서 보아야 정확히 이해된다 — K8s API의 update strategy(`RollingUpdate`/`Recreate`/`OnDelete`)와 배포 패턴(Rolling/Blue-Green/Canary). NVIDIA Driver Operator 같은 host kernel 결합 워크로드 케이스까지 포함하여 정리한다.
{: .notice--info}

---

# [01] Rolling Update 개요

K8s의 기본 무중단 배포 전략. Deployment의 Pod를 **점진적으로 교체**하여 두 버전이 일시적으로 공존하다가 최종적으로 새 버전으로 완전히 전환된다.

## 1-1. 동작 방식

새 ReplicaSet을 생성하고, 기존 ReplicaSet의 Pod를 줄이면서 새 Pod를 늘려가는 방식이다.

<pre class="mermaid">
graph LR
    OLD["ReplicaSet v1<br/>(10 Pods)"] -->|점진 감소| MID["v1: 8 / v2: 4<br/>(공존)"]
    MID -->|점진 교체| NEW["ReplicaSet v2<br/>(10 Pods)"]

    style OLD fill:#ffcccc,stroke:#c62828
    style MID fill:#fff3e0,stroke:#e65100
    style NEW fill:#e8f5e9,stroke:#2e7d32
</pre>

## 1-2. 핵심 파라미터

`spec.strategy.rollingUpdate` 하위:

| 파라미터 | 의미 | 기본값 |
|---|---|---|
| `maxUnavailable` | 동시에 사용 불가능할 수 있는 최대 Pod 수 | 25% |
| `maxSurge` | desired replica를 초과해 추가로 띄울 수 있는 최대 Pod 수 | 25% |

예: `replicas=10, maxUnavailable=2, maxSurge=2` → 항상 최소 8개 살아 있고, 최대 12개까지 띄우며 교체.

## 1-3. 주요 명령어

```bash
kubectl set image deployment/myapp container=myapp:v2  # 트리거
kubectl rollout status deployment/myapp                # 진행 상황
kubectl rollout history deployment/myapp               # 이력
kubectl rollout undo deployment/myapp                  # 롤백
```

## 1-4. 전제 조건

- Pod에 적절한 `readinessProbe` — 새 Pod의 트래픽 수신 준비 여부 판단
- Stateful 워크로드는 StatefulSet 순차 업데이트 또는 Recreate 전략이 더 적합한 경우 있음

---

# [02] 배포 패턴 비교 — Rolling / Blue-Green / Canary

## 2-1. Blue/Green Deployment

두 개의 동일한 환경(Blue=현재, Green=신규)을 완전히 분리해서 운영하다가 트래픽을 한 번에 스위치한다.

```
[Service] ──► Blue (v1)  ✅ 현재 트래픽
              Green (v2) 🟢 대기 (검증 중)

       ↓ 스위치

[Service] ──► Blue (v1)  ⚪ 대기 (롤백용)
              Green (v2) ✅ 현재 트래픽
```

| 항목 | 내용 |
|------|------|
| 장점 | 즉시 롤백, 두 버전이 트래픽에 동시 노출 안 됨 |
| 단점 | 리소스 2배, DB 스키마 호환성 이슈 |

## 2-2. Canary Deployment

신규 버전에 소수 트래픽을 먼저 흘려보내 검증한 뒤 비율을 점진적으로 증가시킨다.

```
v1 (95%) ──┐
v2 (5%)  ──┴──► 메트릭 관찰 (에러율, 레이턴시)
                ↓ 정상이면 비율 ↑
                v1 (50%) / v2 (50%)
                ↓
                v1 (0%)  / v2 (100%)
```

| 항목 | 내용 |
|------|------|
| 장점 | 실 트래픽 검증, 영향 범위 최소화 |
| 단점 | 구현 복잡, 관측(observability) 인프라 필수 |

## 2-3. 비교표

| 항목 | Rolling Update | Blue/Green | Canary |
|---|---|---|---|
| 리소스 부담 | 낮음 (`maxSurge`만큼) | 높음 (2배) | 중간 |
| 롤백 속도 | 느림 (재배포) | 즉시 (스위치) | 즉시 (라우팅 변경) |
| 트래픽 분리 | 불가 (혼재) | 완전 분리 | 비율 제어 |
| 구현 난이도 | 매우 낮음 (K8s 기본) | 중간 | 높음 |
| 검증 방식 | `readinessProbe` 위주 | 사전 스모크 테스트 | 실 트래픽 메트릭 |
| 적합 케이스 | 대부분 stateless 워크로드 | DB/캐시 호환성 검증 필요 | 리스크 큰 변경, A/B 테스트 |

---

# [03] K8s API 차원의 Update Strategy

K8s API spec이 직접 정의한 update enum 값.

| Workload | 사용 가능한 strategy |
|---|---|
| Deployment | `RollingUpdate`, `Recreate` |
| StatefulSet | `RollingUpdate`, `OnDelete` |
| DaemonSet | `RollingUpdate`, `OnDelete` |

## 3-1. 각 전략의 동작

| 전략 | 동작 | K8s 컨트롤러가 자동 처리? |
|---|---|---|
| `RollingUpdate` | 점진 교체, `maxUnavailable`/`maxSurge` 준수 | O |
| `Recreate` | 모든 구버전 Pod 종료 후 신버전 생성 (다운타임 발생) | O |
| `OnDelete` | Pod가 명시적으로 삭제될 때만 새 버전으로 교체 | X — 사람 또는 Operator가 직접 |

## 3-2. DaemonSet에는 Recreate가 없다

DaemonSet은 노드당 1개 Pod 모델이라 `Recreate`가 의미상 부적합하다. 대신 `OnDelete`가 그 역할을 일부 대체하며, 보통 Operator가 노드별 교체 로직을 추가로 구현한다.

---

# [04] 두 추상화 층위의 구분 (핵심 개념)

## 4-1. 흔한 오해

> "K8s resource의 update는 Rolling Update / Blue-Green / Canary 3개로 분류된다"

→ **부정확하다.** 두 다른 추상화 층위가 섞여 있다.

## 4-2. 두 층위의 정의

| 층위 | 정체 | 항목 |
|---|---|---|
| **A: K8s 리소스 update 방법** = K8s API strategy | K8s가 내 리소스 spec을 어떻게 손볼 건가 | `RollingUpdate`, `Recreate`, `OnDelete` |
| **B: 배포 패턴** | 내 애플리케이션의 새 버전을 사용자에게 어떻게 노출할 건가 | Rolling Update, Blue/Green, Canary |

:warning: "K8s API의 update strategy"와 "K8s resource의 업데이트 방법"은 **같은 것**(둘 다 A층위)이다. 표현만 다를 뿐 동일한 대상을 가리킨다. 진짜 구분은 **A층위 vs B층위** 사이에 있다.
{: .notice--warning}

## 4-3. 두 층위의 관계

<pre class="mermaid">
graph TD
    subgraph B["B층위: 배포 패턴 (애플리케이션 버전 전환 방식)"]
        B1["Rolling Update"]
        B2["Blue/Green"]
        B3["Canary"]
    end

    subgraph A["A층위: K8s 리소스 update 방법 (= API strategy)"]
        A1["RollingUpdate"]
        A2["Recreate"]
        A3["OnDelete"]
    end

    B1 -.->|uses| A1
    B2 -.->|uses| A1
    B3 -.->|uses| A1

    style B fill:#e3f2fd,stroke:#1565c0
    style A fill:#fff3e0,stroke:#e65100
</pre>

- A는 K8s가 직접 제공하는 **primitive**
- B는 그 primitive를 빌딩블록 삼아 조합해서 만드는 **상위 패턴**

## 4-4. 왜 헷갈리는가 — 이름 충돌

- **"Rolling Update"**는 A층위에도 있고 B층위에도 있다 — 이름이 같지만 다른 추상화 층위
- **"Recreate"**도 A층위(Deployment strategy)와 B층위(개념적 패턴)에 모두 등장

그래서 "K8s 업데이트 분류 = Rolling/Recreate/Blue-Green/Canary"처럼 한 줄로 묶이는 듯 보이지만, 실제로는 두 다른 층위가 섞여 있는 것이다.

## 4-5. 왜 B는 A 한 줄로 표현할 수 없는가

A층위(K8s native strategy)는 **단일 워크로드 리소스의 update 동작**을 정의한다. 반면 Blue/Green과 Canary는 **여러 리소스의 조합 패턴**이라 strategy 한 줄로 표현 불가.

| 패턴 | K8s 표현 | A층위 단독 표현? |
|------|----------|:---:|
| Rolling Update | Deployment 하나의 `.spec.strategy` 필드 | O |
| Blue/Green | Deployment(blue) + Deployment(green) + Service(selector swap) | X |
| Canary | Deployment 둘 + Ingress/VirtualService(weight) + 메트릭 로직 | X |

## 4-6. Blue/Green의 K8s 구현 예시

```yaml
# blue-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
spec:
  strategy:
    type: RollingUpdate    # ← A층위: 이 Deployment의 update strategy
  selector:
    matchLabels:
      app: myapp
      color: blue
  template:
    metadata:
      labels:
        app: myapp
        color: blue
---
# green-deployment.yaml (동일 구조, color: green)
---
# service.yaml — selector를 blue ↔ green으로 스위치
apiVersion: v1
kind: Service
spec:
  selector:
    app: myapp
    color: blue            # ← B층위: 이 selector swap이 Blue/Green 패턴 자체
```

위 예시에서:

- 각 Deployment가 *내부적으로* update될 때의 방식(A) = `RollingUpdate`
- 전체적으로 사용자에게 v1 → v2를 노출하는 *패턴*(B) = Blue/Green

즉 **Blue/Green 패턴을 만들기 위해 사용하는 K8s strategy는 여전히 `RollingUpdate`**이다. B는 A를 빌딩블록으로 사용해서 만든 상위 개념.

## 4-7. 패턴 → K8s 구현 매핑

| 배포 패턴 (B층위) | K8s에서의 구현 | A층위 strategy |
|---|---|---|
| Rolling Update | `Deployment` 단독, strategy=RollingUpdate | `RollingUpdate` |
| Recreate | `Deployment` 단독, strategy=Recreate | `Recreate` |
| Blue/Green | 두 Deployment + Service selector swap, 또는 `Rollout` CRD | 각 Deployment는 `RollingUpdate` |
| Canary | 두 Deployment + Ingress weight / 서비스 메시, 또는 `Rollout` CRD | 각 Deployment는 `RollingUpdate` |

---

# [05] 외부 솔루션

| 도구 | Blue/Green | Canary | 특징 |
|---|:---:|:---:|---|
| **Argo Rollouts** | O | O | `Rollout` CRD가 Deployment 대체. `AnalysisRun`으로 메트릭 기반 자동 promote/rollback |
| **Flagger** | O | O | 기존 Deployment 유지. Prometheus 메트릭 기반 progressive delivery 자동화 |
| **Istio / Linkerd** | O | O | 트래픽 분산 primitive 제공. Argo/Flagger와 조합이 일반적 |
| **ingress-nginx** | 제한적 | O | `nginx.ingress.kubernetes.io/canary` 어노테이션. 메트릭 분석은 별도 |
| **수동 (vanilla K8s)** | 가능 | 사실상 불가 | 두 Deployment + Service patch로 Blue/Green은 그럭저럭 가능, Canary는 트래픽 가중치 제어 불가 |

---

# [06] NVIDIA Driver Operator 케이스 분석

## 6-1. 왜 노드 안에서 Rolling Update가 불가능한가

NVIDIA driver는 본질이 **host kernel module 적재**(`nvidia.ko`, `nvidia-uvm.ko`, `nvidia-modeset.ko`)이며, 이로 인한 제약이 있다.

| # | 제약 | 설명 |
|---|------|------|
| 1 | 커널 모듈 싱글톤 | 동일 모듈의 두 버전을 host kernel에 동시 로드 불가. 같은 노드에서 v1·v2 driver pod 공존이 OS 레벨에서 거부됨 |
| 2 | 모듈 unload의 ref count 조건 | `rmmod`은 reference count가 0이어야 성공. GPU 사용 중인 컨테이너, `nvidia-persistenced`, X server 등이 붙어 있으면 EBUSY → 재부팅 필요 |
| 3 | container-toolkit 의존성 사슬 | `nvidia-container-toolkit`, `libnvidia-container`, device plugin이 모두 현재 driver 참조. driver만 갈아끼우면 사슬 붕괴 |
| 4 | 재부팅 강제 케이스 | secure boot + signed module 변경, persistent mode, driver-firmware coupling |

이 모든 제약이 "두 버전 일시 공존"을 전제하는 Rolling Update와 정면 충돌한다.

## 6-2. 그래도 클러스터 단위 무중단 롤아웃은 가능

```
for each node (보통 maxUnavailable=1):
  cordon                           # 새 GPU pod 스케줄 차단
  drain GPU workloads              # PDB 준수
  wait module ref_count == 0
  unload old module                # 실패 → reboot 분기
  delete old driver pod (OnDelete)
  reconcile new driver pod
  wait Ready + module loaded + smoke test
  uncordon
```

## 6-3. 핵심 분리 — K8s vs Operator

| 요소 | 누가 정의 / 구현 |
|---|---|
| `OnDelete` enum 값 | K8s API |
| DaemonSet 매니페스트의 `updateStrategy.type: OnDelete` | K8s API spec 위에 사용자가 선언 |
| 노드별 cordon/drain/unload/replace 상태머신 | **Operator** |
| 클러스터 전체 노드 순차 롤아웃 정책 (maxUnavailable, drainTimeout, rebootStrategy) | **Operator** |
| 검증 게이트 (`nvidia-smi`, device plugin health) | **Operator** |

`OnDelete`는 K8s가 준 **"빈 칠판"**이고, Operator가 그 위에 그린 그림이 **"노드별로 어떻게 안전하게 driver를 교체할 것인가"**의 로직이다.

## 6-4. 행위적 분류

| 관점 | 실제 모습 |
|---|---|
| K8s API 레벨 (A층위) | `OnDelete` 전략 |
| 노드 안에서의 동작 | "Recreate처럼 보임" — 두 버전 공존 불가 |
| 클러스터 전체에서의 동작 | "Rolling Update처럼 보임" — 노드별 순차 처리 |

## 6-5. 설계 의사결정 순서

1. **A층위 결정** — DaemonSet의 `updateStrategy.type`을 `RollingUpdate`로 둘 거냐 `OnDelete`로 둘 거냐 (driver는 `OnDelete`)
2. **B층위 결정** — 그 위에서 어떤 배포 패턴을 흉내낼 거냐 (driver는 host kernel 결합 때문에 Blue/Green·Canary 사실상 불가, **노드별 Recreate를 순차 진행**이 사실상 유일 옵션)

---

# [07] 핵심 요약

| # | 요약 |
|---|------|
| 1 | 두 추상화 층위가 따로 존재한다 — A층위(K8s API strategy)와 B층위(배포 패턴) |
| 2 | A층위 항목: `RollingUpdate`, `Recreate`, `OnDelete` (워크로드 종류별로 사용 가능 값 상이) |
| 3 | B층위 항목: Rolling Update, Blue/Green, Canary (+ Recreate, A/B, Shadow 등) |
| 4 | K8s native로 직접 제공되는 패턴은 Rolling Update와 Recreate뿐. Blue/Green·Canary는 외부 CRD(Argo Rollouts, Flagger) 또는 multi-resource 조합으로 구현 |
| 5 | `OnDelete`는 A층위의 enum 값이고, 그것이 활성화됐을 때의 오케스트레이션 로직은 **Operator가 직접 구현**해야 함 |
| 6 | NVIDIA driver처럼 host kernel과 결합된 워크로드는 Rolling Update가 노드 안에서 물리적으로 불가능. **"노드 안은 Recreate, 노드 간은 통제된 Rolling"** 패턴이 사실상 유일한 정답 |

:bulb: **"K8s API의 update strategy"와 "K8s resource의 업데이트 방법"은 같은 것을 다르게 부른 것**이다. 진짜 구분은 그 사이가 아니라 **A층위 vs B층위(배포 패턴)** 사이에 있다.
{: .notice--info}
