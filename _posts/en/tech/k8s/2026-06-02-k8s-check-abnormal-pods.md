---
title: "Checking for Abnormal Pods in a Kubernetes Cluster"
description: "kubectl commands to find abnormal Pods like Error, Pending, CrashLoopBackOff, and Init — covering both with-Completed and without-Completed cases"
excerpt: "What the STATUS column really means, the field-selector pitfall, and how to tell whether Completed is normal — a practical reference for quickly isolating broken Pods in production"
date: 2026-06-02
categories: K8s
tags: [Kubernetes, kubectl, Pod, CrashLoopBackOff, Pending, Completed, troubleshooting, field-selector, get-pods, operations]
ref: k8s-check-abnormal-pods
---

:bulb: A reference for `kubectl` commands that quickly isolate **abnormal Pods only** — `Error`, `Pending`, `CrashLoopBackOff`, `Init:0/1`, and friends — in a running cluster. The core command is given in **two cases: with and without Completed**.
{: .notice--info}

---

# [01] First, what the STATUS column actually is

The **STATUS** column in `kubectl get pods` actually mixes **two different kinds** of values. Miss this and your filters behave unexpectedly.

| STATUS shown | What it really is | Caught by `--field-selector`? |
|---|---|---|
| `Pending` | phase | ✅ |
| `Running` | phase | ✅ |
| `Completed` | phase = `Succeeded` | ✅ |
| `Error` | phase = `Failed` | ✅ |
| `CrashLoopBackOff` | **container reason** | ❌ (phase is `Running`) |
| `Init:0/1` | **container reason** | ❌ (phase is `Pending`) |
| `ImagePullBackOff` | **container reason** | ❌ |
| `Terminating` | has deletionTimestamp | ❌ |

:warning: `CrashLoopBackOff`, `Init:0/1`, and `ImagePullBackOff` are **container reasons, not phases**. So `--field-selector=status.phase!=Running` will **not** catch them. This is the single most common trap.
{: .notice--warning}

For this reason, a **text-based `grep` approach is safer in practice**. Both approaches are covered below.

---

# [02] Listing all Pods (the baseline)

Start by viewing every Pod across all namespaces.

```bash
# All Pods in all namespaces (with extra columns like node/IP)
kubectl get pods -A -o wide
```

| Option | Meaning |
|------|------|
| `-A` | `--all-namespaces` — every namespace |
| `-o wide` | Adds NODE, IP, NOMINATED NODE, etc. |

:bulb: `--sort-by` only **sorts** — it does **not** filter. `kubectl get pods -A --sort-by='.status.phase'` still shows every Pod, `Running` included. To see "broken Pods only" you need **filtering** (below), not sorting.
{: .notice--info}

---

# [03] The core — isolating abnormal Pods

## 3-1. Case A: **without** Completed (treat Completed as normal)

When you want to exclude `Completed` Pods that CronJobs/Jobs finished cleanly, and see **only the truly broken ones**.

```bash
# Exclude both Running and Completed → only the rest (broken Pods)
kubectl get pods -A -o wide | grep -v -E 'Running|Completed'
```

- `grep -v` : **exclude** matching lines
- Removing both `Running` (healthy) and `Completed` (finished cleanly) leaves only `Error`, `Pending`, `CrashLoopBackOff`, `Init`, `ImagePullBackOff`, etc.

:warning: Caveat: `-v` also strips the header line (`NAMESPACE NAME ...`). To keep the header, use the "header-preserving" version below.
{: .notice--warning}

**Header-preserving + without Completed:**

```bash
# Keep the header (NAMESPACE), exclude only Running/Completed
kubectl get pods -A -o wide | grep -E 'NAMESPACE|Error|CrashLoopBackOff|Pending|Init|ImagePullBackOff|Terminating|OOMKilled|ErrImagePull'
```

→ A whitelist approach. Only `NAMESPACE` (the header) plus the problem states pass through. `Completed` isn't on the list, so it's naturally excluded.

## 3-2. Case B: **with** Completed (Completed is also worth inspecting)

When you want every "non-Running" Pod, `Completed` included. (e.g. to also catch the abnormal case where a Deployment Pod fell into `Completed` — see [05].)

```bash
# Exclude only Running → everything else, including Completed
kubectl get pods -A -o wide | grep -v 'Running'
```

**Header-preserving + with Completed:**

```bash
# Keep the header, exclude only Running
kubectl get pods -A -o wide | grep -v -w 'Running' | grep -E 'NAMESPACE|[A-Za-z]'
```

Or, more simply, filter by phase with a field-selector:

```bash
# Pods whose phase isn't Running (includes Completed=Succeeded, Error=Failed, Pending)
kubectl get pods -A -o wide --field-selector=status.phase!=Running
```

:warning: Again — this field-selector **misses** `CrashLoopBackOff` (phase=Running). To catch it reliably, prefer the `grep` form in Case B.
{: .notice--warning}

---

# [04] Viewing a specific state only

```bash
kubectl get pods -A -o wide | grep CrashLoopBackOff
kubectl get pods -A -o wide | grep -E 'Error|CrashLoopBackOff|ImagePullBackOff'
kubectl get pods -A -o wide | grep Pending
kubectl get pods -A -o wide | grep Init          # Init:0/1 — stuck initializing
kubectl get pods -A -o wide | grep Terminating   # Pods hung while terminating
kubectl get pods -A -o wide | grep Completed
```

**By phase (the precise filter):**

```bash
kubectl get pods -A --field-selector=status.phase=Pending    -o wide
kubectl get pods -A --field-selector=status.phase=Failed     -o wide   # Error
kubectl get pods -A --field-selector=status.phase=Succeeded  -o wide   # Completed
```

---

# [05] Is Completed normal?

`Completed` can be normal — or the trace of a problem — **depending on context**. There's exactly one test: **"Was this Pod designed to run to completion?"**

| Owner (Controller) | What `Completed` means |
|---|---|
| Job / CronJob | ✅ Normal (work finished, exit 0) |
| Init Container | ✅ Normal (exits after init) |
| Deployment / ReplicaSet | ⚠️ Abnormal (it shouldn't die, yet it ended) |
| StatefulSet / DaemonSet | ⚠️ Abnormal (the main process exited) |

**Command to check the owner:**

```bash
# Find which controller kind created this Pod
kubectl get pod <pod-name> -n <namespace> \
  -o jsonpath='{.metadata.ownerReferences[0].kind}'
```

- Result is `Job` → `Completed` is normal 👍
- Result is `ReplicaSet` (= Deployment) / `StatefulSet` → a `Completed` Pod is suspicious 🔍 (likely the entrypoint exited instead of staying in the foreground)

:bulb: CronJobs deliberately keep successful Pods around (`successfulJobsHistoryLimit`). A pile of `Completed` Pods is usually natural. That's why **Case A (without Completed)** has less noise for routine checks.
{: .notice--info}

---

# [06] Diagnosing the root cause

Once you've found a broken Pod, look at why.

```bash
# Check the Events section for the cause (scheduling failure, image pull error, etc.)
kubectl describe pod <pod-name> -n <namespace>

# Check the logs
kubectl logs <pod-name> -n <namespace>

# Key for CrashLoopBackOff debugging — logs of the previous (crashed) container
kubectl logs <pod-name> -n <namespace> --previous

# Find Pods restarting frequently (sort by RESTARTS)
kubectl get pods -A --sort-by='.status.containerStatuses[0].restartCount' -o wide
```

---

# [07] Key takeaways

| # | Takeaway |
|---|------|
| 1 | The STATUS column mixes **phase** (Pending/Running/Succeeded/Failed) and **container reason** (CrashLoopBackOff/Init, etc.) |
| 2 | `--field-selector=status.phase!=Running` **misses CrashLoopBackOff** — because its phase is Running |
| 3 | **Case A (without Completed):** `kubectl get pods -A -o wide \| grep -v -E 'Running\|Completed'` |
| 4 | **Case B (with Completed):** `kubectl get pods -A -o wide \| grep -v 'Running'` |
| 5 | `--sort-by` only sorts — it doesn't filter out Running; use `grep`/`field-selector` to filter |
| 6 | Whether `Completed` is normal depends on the owning controller — Job/CronJob is fine, Deployment/StatefulSet is suspicious |

:bulb: The one-liner you'll use most — **`kubectl get pods -A -o wide | grep -v -E 'Running|Completed'`** — catches every non-healthy Pod at once.
{: .notice--info}
