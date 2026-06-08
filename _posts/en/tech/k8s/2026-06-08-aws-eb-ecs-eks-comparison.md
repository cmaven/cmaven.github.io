---
title: "AWS Elastic Beanstalk vs ECS vs EKS — What, When, and How"
description: "A side-by-side comparison of Elastic Beanstalk, ECS, and EKS, where they fall on the PaaS/IaaS/CaaS spectrum, and the exact steps a user takes to deploy a container (Pod)"
excerpt: "Comparing the three services by abstraction level and responsibility boundary, where each sits between IaaS and PaaS, and the 7-step procedure for how a Pod actually gets deployed on EKS"
date: 2026-06-08
categories: K8s
tags: [AWS, Kubernetes, EKS, ECS, ElasticBeanstalk, Fargate, PaaS, IaaS, CaaS, Pod, container, deployment, cloud]
ref: aws-eb-ecs-eks-comparison
---

:bulb: A comparison of the three main AWS services for running apps and containers — **Elastic Beanstalk, ECS, and EKS**. We cover, in order: ① how they differ, ② where they land on the PaaS/IaaS/CaaS spectrum, and ③ how a user actually deploys a container (Pod).
{: .notice--info}

---

# [01] Comparison at a glance

| Aspect | Elastic Beanstalk | ECS (Elastic Container Service) | EKS (Elastic Kubernetes Service) |
|---|---|---|---|
| What it is | Application deployment platform | AWS-native container orchestrator | Managed Kubernetes |
| Standard/engine | AWS proprietary (uses EC2/ECS internally) | AWS proprietary (task/service model) | **Standard Kubernetes** (Pod/Deployment) |
| Abstraction level | **Highest** (just push code) | Medium | **Lowest** (most control) |
| Your responsibility | Code/config | Task definitions + (on EC2) nodes | Manifests + (on self-managed) worker nodes |
| Portability | Low (AWS-locked) | Low (AWS-locked) | **High** (same K8s API anywhere) |
| Learning curve | Low | Medium | **High** |
| Typical use | Simple/traditional web apps, fast deploys | Container workloads that stay inside AWS | Multi-cloud, complex microservices, K8s ecosystem (Helm, etc.) |

:bulb: One-line summary — **"Want it up fast → Beanstalk", "Just run containers inside AWS → ECS", "Need the standard Kubernetes ecosystem → EKS".**
{: .notice--info}

---

# [02] A closer look at each

## 2-1. Elastic Beanstalk — "just throw me the code"

Upload your code (or a Docker image) and AWS automatically provisions the **EC2 instances, load balancer, auto scaling group, and health checks**. You barely touch the infrastructure.

- Supported runtimes: Java, .NET, Node.js, Python, PHP, Go, Ruby + **Docker**
- The infrastructure is hidden but **not fully locked away** — you can still tweak the generated EC2/security groups if needed.
- It is **not** a container orchestration tool. It's a platform that automates "application deployment."

:warning: If you need fine-grained multi-container handling, detailed scheduling, a service mesh, or ecosystem tools like Helm, Beanstalk hits its ceiling quickly. That's when you move to ECS/EKS.
{: .notice--warning}

## 2-2. ECS — "AWS's own container orchestrator"

Not Kubernetes — this is **AWS's own orchestrator**. It works around `Task Definition` (container spec) and `Service` (maintain a desired count). It has two launch types.

| Launch Type | Description | Character |
|---|---|---|
| **EC2** | You manage the EC2 nodes yourself, containers run on top | Closer to IaaS |
| **Fargate** | Serverless — run containers with no node management | Closer to PaaS (serverless) |

- Pros: **seamless integration** with AWS services (IAM, ALB, CloudWatch, …), no need to know Kubernetes, no control-plane cost.
- Cons: **AWS lock-in** (not portable to other clouds), can't use the Kubernetes ecosystem (Helm/operators/etc.).

## 2-3. EKS — "managed Kubernetes"

AWS runs **standard Kubernetes** for you. AWS manages the control plane (API server, etcd, …) and you focus on the **worker nodes** and your **workloads (Pods)**.

| Node operating mode | Description |
|---|---|
| Managed node groups | AWS manages the EC2 worker node lifecycle |
| Self-managed nodes | You operate the worker nodes (maximum control) |
| **Fargate** | Run Pods serverless, with no nodes |

- Pros: **standard K8s API** → operate identically on-prem/other clouds (portability), access to the huge ecosystem (Helm, operators, Istio, ArgoCD…).
- Cons: steep learning curve, **hourly control-plane cost**, high operational complexity.

---

# [03] PaaS or IaaS? — the precise classification

People often ask "Beanstalk=PaaS, ECS/EKS=?", but precisely speaking all three live on the **CaaS (Container as a Service) spectrum between IaaS and PaaS**. The real question is **"how much does the user remain responsible for (the abstraction level)?"**

```
More managed by you (IaaS) ←──────────────────────────→ Less (PaaS/serverless)

  EC2        ECS(EC2) / EKS(self-nodes)      ECS(Fargate) / EKS(Fargate)      Beanstalk        Lambda
 [IaaS]          [CaaS, IaaS side]              [CaaS, serverless/PaaS side]   [near PaaS]      [FaaS]
```

| Service | Classification | One-liner |
|---|---|---|
| Elastic Beanstalk | **Closest to PaaS** | Give it code, the platform owns the entire runtime |
| ECS / EKS (EC2 / self-nodes) | **CaaS** (IaaS side) | You manage nodes → infra responsibility remains, IaaS-like |
| ECS / EKS (Fargate) | **CaaS** (PaaS/serverless side) | Node management disappears, closer to PaaS |

:bulb: In other words, ECS and EKS **slide between IaaS and PaaS depending on the launch type.** With Fargate you stop seeing servers (nodes), so it leans toward PaaS/serverless; with EC2/self-managed nodes the infra responsibility grows, leaning toward IaaS. That's exactly why flatly declaring "EKS is PaaS" or "EKS is IaaS" is wrong.
{: .notice--info}

---

# [04] How a user deploys a container (Pod) — the EKS (Kubernetes) flow

In Kubernetes the smallest deployable unit is the **Pod**. But you rarely create Pods directly — you manage them through a **Deployment** (a declaration of the desired state). The full flow is these 7 steps.

```
[1] code           [2] build image        [3] push to registry (ECR)
  app.py    ──▶   docker build    ──▶   <acct>.dkr.ecr...amazonaws.com/app:v1
                                              │
                                              ▼
[4] write manifest     [5] kubectl apply        [6] scheduler places Pods on nodes
 deployment.yaml  ──▶   submit to API server ─▶ Node A: [Pod] [Pod]
                                              Node B: [Pod]
                                                  │
                                                  ▼
[7] expose via Service/Ingress + HPA autoscaling + rolling updates
```

## 4-1. Build the image → push to the registry

```bash
# 1) Build the container image
docker build -t my-app:v1 .

# 2) Log in to ECR + tag + push
aws ecr get-login-password --region ap-northeast-2 \
  | docker login --username AWS --password-stdin <acct>.dkr.ecr.ap-northeast-2.amazonaws.com
docker tag my-app:v1 <acct>.dkr.ecr.ap-northeast-2.amazonaws.com/my-app:v1
docker push <acct>.dkr.ecr.ap-northeast-2.amazonaws.com/my-app:v1
```

## 4-2. Write the manifest (Deployment)

Instead of creating Pods directly, you **declare** with a **Deployment** "how many Pods, from which image, to keep running."

```yaml
# deployment.yaml — declare the desired state
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3                 # always keep 3 Pods
  selector:
    matchLabels:
      app: my-app
  template:                   # ↓ this is the Pod template
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: <acct>.dkr.ecr.ap-northeast-2.amazonaws.com/my-app:v1
          ports:
            - containerPort: 8080
```

## 4-3. Apply to the cluster → scheduling

```bash
# Configure cluster access (EKS)
aws eks update-kubeconfig --name my-cluster --region ap-northeast-2

# Apply the manifest — submit the "desired state" to the API server
kubectl apply -f deployment.yaml
```

From here Kubernetes handles the rest on its own.

1. The **API server** receives the request and stores "3 Pods needed" in etcd.
2. A **controller** requests Pod creation to go from 0 → 3.
3. The **scheduler** places each Pod on a node with spare capacity.
4. Each node's **kubelet** pulls the image via the container runtime and starts the containers.

```bash
# Check deployment status
kubectl get pods -o wide      # which node each Pod is Running on
kubectl get deployment my-app # confirm 3/3 READY
```

## 4-4. Expose externally (Service / Ingress)

Pod IPs change constantly, so you put a **Service** (or Ingress) in front as a stable entry point.

```yaml
# service.yaml — give the set of Pods a stable entry point + load balancer
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  type: LoadBalancer          # auto-creates an AWS LB (EKS)
  selector:
    app: my-app               # routes traffic to Pods labeled app=my-app
  ports:
    - port: 80
      targetPort: 8080
```

```bash
kubectl apply -f service.yaml
kubectl get svc my-app        # check the EXTERNAL-IP (the LB address)
```

## 4-5. Scaling & zero-downtime updates

```bash
# Manual scale: 3 Pods → 5
kubectl scale deployment my-app --replicas=5

# Autoscale (HPA): adjust between 2–10 based on 50% CPU
kubectl autoscale deployment my-app --cpu-percent=50 --min=2 --max=10

# Rolling update to a new version (zero downtime): swap the image, it rolls gradually
kubectl set image deployment/my-app my-app=<acct>.dkr.ecr.ap-northeast-2.amazonaws.com/my-app:v2
kubectl rollout status deployment/my-app   # track progress
kubectl rollout undo deployment/my-app     # roll back if something breaks
```

:bulb: The key is that it's **declarative**. You don't say "build it this way" — you declare **"I want it to be in this state"** (replicas: 3, image: v2), and Kubernetes **converges** the current state toward that target. ECS is conceptually similar with tasks/services, and Beanstalk wraps this whole thing one more level so a single `eb deploy` does it all.
{: .notice--info}

---

# [05] So which should you pick?

| Situation | Recommendation |
|---|---|
| You don't know Kubernetes/containers well and want a traditional web app up fast | **Elastic Beanstalk** |
| You run containers only inside AWS and want to avoid K8s operational burden | **ECS** (+ Fargate if you hate managing nodes) |
| You need multi-cloud, portability, and the standard K8s ecosystem (Helm/operators) | **EKS** |
| You want to never see a node (server) at all | **Fargate** (works for both ECS/EKS) |

:warning: "Everyone else uses EKS, so we should too" is a common trap. Kubernetes brings **operational complexity and control-plane cost**. If you're running a handful of containers in a single AWS environment, ECS (Fargate) is often cheaper and simpler.
{: .notice--warning}

---

# [06] Key takeaways

| # | Takeaway |
|---|------|
| 1 | **Beanstalk** = app deployment platform, **ECS** = AWS-native orchestrator, **EKS** = managed standard Kubernetes |
| 2 | Strictly, all three are **CaaS** between IaaS and PaaS — Beanstalk is closest to PaaS |
| 3 | ECS/EKS **shift position by launch type** — Fargate leans PaaS/serverless, EC2/self-nodes lean IaaS |
| 4 | EKS portability ⬆ (standard K8s API); ECS/Beanstalk are more AWS-locked |
| 5 | Pod deployment in 7 steps: **build → push to ECR → manifest → `kubectl apply` → scheduler places → expose via Service → scale/rolling update** |
| 6 | The essence of Kubernetes is **declarative** — declare the "desired state" and the system converges to it |

:bulb: The one-line decision rule — **fast deploys → Beanstalk, AWS-only containers → ECS, standard Kubernetes ecosystem → EKS.**
{: .notice--info}
