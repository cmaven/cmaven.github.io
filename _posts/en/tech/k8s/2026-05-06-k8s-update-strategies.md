---
title: "Kubernetes Update Strategies — Rolling Update, Blue/Green, and Canary"
description: "Comparison of Rolling Update, Blue/Green, and Canary deployment patterns against K8s API strategies (RollingUpdate/Recreate/OnDelete), with a deep dive into the NVIDIA Driver Operator case"
excerpt: "K8s updates must be understood as two layers — API-level strategy (A) and deployment pattern (B). From Rolling/Blue-Green/Canary comparison to host-kernel-coupled workloads like NVIDIA drivers"
date: 2026-05-06
categories: K8s
tags: [Kubernetes, deployment-strategy, RollingUpdate, BlueGreen, Canary, Recreate, OnDelete, DaemonSet, Argo-Rollouts, NVIDIA-GPU-Operator]
ref: k8s-update-strategies
---

:bulb: Kubernetes update strategies should be analyzed in **two abstraction layers**: the K8s API update strategy (`RollingUpdate`/`Recreate`/`OnDelete`) and the application-level deployment pattern (Rolling/Blue-Green/Canary). This post covers both, plus a real-world case for host-kernel-coupled workloads like the NVIDIA Driver Operator.
{: .notice--info}

---

# [01] Rolling Update Overview

The default zero-downtime deployment strategy in K8s. The Deployment's Pods are **gradually replaced**, with two versions coexisting temporarily until the new version fully takes over.

## 1-1. How It Works

A new ReplicaSet is created, and old ReplicaSet Pods are scaled down while new Pods are scaled up.

<pre class="mermaid">
graph LR
    OLD["ReplicaSet v1<br/>(10 Pods)"] -->|Gradual scale down| MID["v1: 8 / v2: 4<br/>(coexisting)"]
    MID -->|Gradual replacement| NEW["ReplicaSet v2<br/>(10 Pods)"]

    style OLD fill:#ffcccc,stroke:#c62828
    style MID fill:#fff3e0,stroke:#e65100
    style NEW fill:#e8f5e9,stroke:#2e7d32
</pre>

## 1-2. Key Parameters

Under `spec.strategy.rollingUpdate`:

| Parameter | Meaning | Default |
|---|---|---|
| `maxUnavailable` | Max number of Pods that can be unavailable simultaneously | 25% |
| `maxSurge` | Max number of Pods that can be created above the desired replicas | 25% |

Example: `replicas=10, maxUnavailable=2, maxSurge=2` → at least 8 Pods always live, up to 12 Pods running during transition.

## 1-3. Main Commands

```bash
kubectl set image deployment/myapp container=myapp:v2  # Trigger
kubectl rollout status deployment/myapp                # Progress
kubectl rollout history deployment/myapp               # History
kubectl rollout undo deployment/myapp                  # Rollback
```

## 1-4. Prerequisites

- A proper `readinessProbe` on Pods — determines when a new Pod is ready to receive traffic
- Stateful workloads often benefit more from StatefulSet ordered updates or the Recreate strategy

---

# [02] Deployment Pattern Comparison — Rolling / Blue-Green / Canary

## 2-1. Blue/Green Deployment

Two identical environments (Blue=current, Green=new) run completely separately, then traffic is switched at once.

```
[Service] ──► Blue (v1)  ✅ current traffic
              Green (v2) 🟢 standby (under validation)

       ↓ switch

[Service] ──► Blue (v1)  ⚪ standby (rollback ready)
              Green (v2) ✅ current traffic
```

| Aspect | Detail |
|--------|--------|
| Pros | Instant rollback, no simultaneous version exposure |
| Cons | 2x resources, DB schema compatibility issues |

## 2-2. Canary Deployment

A small portion of traffic is routed to the new version first, then the ratio is gradually increased after validation.

```
v1 (95%) ──┐
v2 (5%)  ──┴──► observe metrics (error rate, latency)
                ↓ ratio ↑ if healthy
                v1 (50%) / v2 (50%)
                ↓
                v1 (0%)  / v2 (100%)
```

| Aspect | Detail |
|--------|--------|
| Pros | Validation with real traffic, minimal blast radius |
| Cons | Complex implementation, requires observability infrastructure |

## 2-3. Comparison Table

| Item | Rolling Update | Blue/Green | Canary |
|---|---|---|---|
| Resource overhead | Low (`maxSurge` only) | High (2x) | Medium |
| Rollback speed | Slow (re-deploy) | Instant (switch) | Instant (routing change) |
| Traffic isolation | None (mixed) | Complete | Ratio-controlled |
| Implementation complexity | Very low (K8s native) | Medium | High |
| Validation method | `readinessProbe`-driven | Pre-deploy smoke tests | Live traffic metrics |
| Best for | Most stateless workloads | DB/cache compatibility validation | High-risk changes, A/B testing |

---

# [03] K8s API-Level Update Strategy

These are update enum values defined directly by the K8s API spec.

| Workload | Available strategies |
|---|---|
| Deployment | `RollingUpdate`, `Recreate` |
| StatefulSet | `RollingUpdate`, `OnDelete` |
| DaemonSet | `RollingUpdate`, `OnDelete` |

## 3-1. Strategy Behavior

| Strategy | Behavior | Auto-handled by K8s controller? |
|---|---|---|
| `RollingUpdate` | Gradual replacement, honors `maxUnavailable`/`maxSurge` | Yes |
| `Recreate` | Terminates all old Pods, then creates new ones (downtime occurs) | Yes |
| `OnDelete` | Replacement happens only when Pods are explicitly deleted | No — requires manual action or an Operator |

## 3-2. DaemonSet Has No Recreate

A DaemonSet runs one Pod per node, so `Recreate` doesn't make semantic sense. Instead, `OnDelete` partially fills that role, and an Operator usually adds per-node replacement logic on top.

---

# [04] Distinguishing the Two Abstraction Layers (Core Concept)

## 4-1. Common Misconception

> "K8s resource updates are classified into Rolling Update / Blue-Green / Canary"

→ **Incorrect.** Two different abstraction layers are mixed together.

## 4-2. The Two Layers

| Layer | Identity | Items |
|---|---|---|
| **A: K8s resource update method** = K8s API strategy | How K8s manipulates my resource spec | `RollingUpdate`, `Recreate`, `OnDelete` |
| **B: Deployment pattern** | How my application's new version is exposed to users | Rolling Update, Blue/Green, Canary |

:warning: "K8s API update strategy" and "K8s resource update method" are **the same thing** (both Layer A). They just have different names. The real distinction is between **Layer A and Layer B**.
{: .notice--warning}

## 4-3. Relationship Between Layers

<pre class="mermaid">
graph TD
    subgraph B["Layer B: Deployment Pattern (application version transition)"]
        B1["Rolling Update"]
        B2["Blue/Green"]
        B3["Canary"]
    end

    subgraph A["Layer A: K8s resource update method (= API strategy)"]
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

- A = K8s-provided **primitives**
- B = **higher-level patterns** built from those primitives as building blocks

## 4-4. Why It's Confusing — Name Collision

- **"Rolling Update"** exists in both Layer A and Layer B — same name, different abstraction levels
- **"Recreate"** also appears in Layer A (Deployment strategy) and Layer B (conceptual pattern)

That's why "K8s update classification = Rolling/Recreate/Blue-Green/Canary" looks like a single list, but it's actually mixing two different layers.

## 4-5. Why B Cannot Be Expressed in a Single A Line

Layer A (K8s native strategy) defines **the update behavior of a single workload resource**. Blue/Green and Canary, however, are **multi-resource composition patterns** and cannot be expressed in a single strategy line.

| Pattern | K8s representation | Expressible by Layer A alone? |
|------|----------|:---:|
| Rolling Update | A single Deployment's `.spec.strategy` field | Yes |
| Blue/Green | Deployment(blue) + Deployment(green) + Service(selector swap) | No |
| Canary | Two Deployments + Ingress/VirtualService(weight) + metrics logic | No |

## 4-6. K8s Implementation of Blue/Green

```yaml
# blue-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
spec:
  strategy:
    type: RollingUpdate    # ← Layer A: this Deployment's update strategy
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
# green-deployment.yaml (same structure, color: green)
---
# service.yaml — swap selector between blue ↔ green
apiVersion: v1
kind: Service
spec:
  selector:
    app: myapp
    color: blue            # ← Layer B: this selector swap IS the Blue/Green pattern
```

In the example above:

- The way each Deployment updates *internally* (A) = `RollingUpdate`
- The *pattern* of exposing v1 → v2 to users (B) = Blue/Green

In other words, **the K8s strategy used to implement Blue/Green is still `RollingUpdate`**. B uses A as a building block to construct higher-level concepts.

## 4-7. Pattern → K8s Implementation Mapping

| Deployment pattern (Layer B) | K8s implementation | Layer A strategy |
|---|---|---|
| Rolling Update | `Deployment` alone, strategy=RollingUpdate | `RollingUpdate` |
| Recreate | `Deployment` alone, strategy=Recreate | `Recreate` |
| Blue/Green | Two Deployments + Service selector swap, or `Rollout` CRD | Each Deployment uses `RollingUpdate` |
| Canary | Two Deployments + Ingress weight / service mesh, or `Rollout` CRD | Each Deployment uses `RollingUpdate` |

---

# [05] External Solutions

| Tool | Blue/Green | Canary | Notes |
|---|:---:|:---:|---|
| **Argo Rollouts** | Yes | Yes | `Rollout` CRD replaces Deployment. `AnalysisRun` enables metric-based auto promote/rollback |
| **Flagger** | Yes | Yes | Keeps existing Deployments. Automates progressive delivery based on Prometheus metrics |
| **Istio / Linkerd** | Yes | Yes | Provides traffic-splitting primitives. Commonly combined with Argo/Flagger |
| **ingress-nginx** | Limited | Yes | `nginx.ingress.kubernetes.io/canary` annotation. Metric analysis is separate |
| **Vanilla K8s (manual)** | Possible | Practically impossible | Blue/Green is feasible with two Deployments + Service patch. Canary lacks fine-grained traffic weighting |

---

# [06] NVIDIA Driver Operator Case

## 6-1. Why Rolling Update Is Impossible Inside a Node

The NVIDIA driver is fundamentally about **loading kernel modules on the host** (`nvidia.ko`, `nvidia-uvm.ko`, `nvidia-modeset.ko`), which imposes these constraints:

| # | Constraint | Description |
|---|------|------|
| 1 | Kernel module singleton | Cannot load two versions of the same module into the host kernel at the same time. v1 and v2 driver Pods cannot coexist on the same node — rejected at the OS level |
| 2 | Module unload requires ref count zero | `rmmod` only succeeds when the reference count is 0. If GPU is in use by containers, `nvidia-persistenced`, or X server, you get EBUSY → reboot required |
| 3 | container-toolkit dependency chain | `nvidia-container-toolkit`, `libnvidia-container`, and device plugin all reference the current driver. Swapping only the driver breaks the chain |
| 4 | Forced reboot cases | Secure boot + signed module changes, persistent mode, driver-firmware coupling |

All these constraints directly conflict with Rolling Update, which assumes "two versions coexist temporarily."

## 6-2. Cluster-Wide Zero-Downtime Rollout Is Still Possible

```
for each node (typically maxUnavailable=1):
  cordon                           # block new GPU pod scheduling
  drain GPU workloads              # honor PDB
  wait module ref_count == 0
  unload old module                # failure → reboot branch
  delete old driver pod (OnDelete)
  reconcile new driver pod
  wait Ready + module loaded + smoke test
  uncordon
```

## 6-3. Key Separation — K8s vs Operator

| Component | Who defines / implements |
|---|---|
| `OnDelete` enum value | K8s API |
| DaemonSet manifest's `updateStrategy.type: OnDelete` | User declaration on top of K8s API spec |
| Per-node cordon/drain/unload/replace state machine | **Operator** |
| Cluster-wide sequential rollout policy (maxUnavailable, drainTimeout, rebootStrategy) | **Operator** |
| Validation gates (`nvidia-smi`, device plugin health) | **Operator** |

`OnDelete` is the **"blank canvas"** K8s provides, and what the Operator paints on it is the logic for **"how to safely replace the driver on each node"**.

## 6-4. Behavioral Classification

| Perspective | Actual appearance |
|---|---|
| K8s API level (Layer A) | `OnDelete` strategy |
| Behavior inside a node | "Looks like Recreate" — two versions cannot coexist |
| Cluster-wide behavior | "Looks like Rolling Update" — nodes are processed sequentially |

## 6-5. Design Decision Order

1. **Layer A decision** — Set the DaemonSet's `updateStrategy.type` to `RollingUpdate` or `OnDelete` (drivers need `OnDelete`)
2. **Layer B decision** — What deployment pattern to mimic on top (drivers cannot use Blue/Green or Canary due to host kernel coupling — **per-node Recreate processed sequentially** is essentially the only option)

---

# [07] Summary

| # | Takeaway |
|---|------|
| 1 | Two abstraction layers exist separately — Layer A (K8s API strategy) and Layer B (deployment pattern) |
| 2 | Layer A items: `RollingUpdate`, `Recreate`, `OnDelete` (available values vary by workload type) |
| 3 | Layer B items: Rolling Update, Blue/Green, Canary (+ Recreate, A/B, Shadow, etc.) |
| 4 | K8s-native patterns provided directly are only Rolling Update and Recreate. Blue/Green and Canary require external CRDs (Argo Rollouts, Flagger) or multi-resource composition. Each Deployment's Layer A strategy is typically still `RollingUpdate` |
| 5 | `OnDelete` is a Layer A enum value, and the orchestration logic when it's active must be **implemented by an Operator** |
| 6 | For workloads coupled with the host kernel (like NVIDIA drivers), Rolling Update is physically impossible inside a node. **"Recreate inside the node, controlled Rolling between nodes"** is essentially the only correct pattern |

:bulb: "K8s API update strategy" and "K8s resource update method" are the same thing under different names. The real distinction is between Layer A and Layer B (deployment patterns).
{: .notice--info}
