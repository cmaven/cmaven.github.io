---
title: "OCI Registry and Harbor — Container Image Management (K8s & OpenStack)"
description: "OCI Registry concept, Harbor's role and key features, usage in Kubernetes/OpenStack, differences from Glance, comparison with Nexus/KubeKey"
excerpt: "Harbor is an Enterprise-grade Private OCI Registry — a standard repository for pushing/pulling container images in Kubernetes and OpenStack"
date: 2026-04-20
categories: Storage
tags: [OCI, Harbor, Registry, Kubernetes, OpenStack, Glance, Docker, container-image, Nexus, CI-CD]
ref: oci-registry-harbor-kubernetes-openstack
---

:bulb: This post covers the concept of OCI Registry, the role of Harbor as a representative implementation, and how it's used in Kubernetes/OpenStack.
{: .notice--info}

---

# [01] What Is OCI Registry?

OCI (Open Container Initiative) Registry is the **standard interface** for storing and distributing container images.

## 1-1. Core Components

| Component | Description |
|-----------|-------------|
| **Image** | Bundle of filesystem + metadata required to run a container |
| **Layer** | Individual filesystem change unit composing the image (hierarchical) |
| **Manifest** | JSON document listing layers, config, and platform info |

## 1-2. How It Works

<pre class="mermaid">
graph LR
    DEV["Developer / CI"] -->|"docker push"| REG["OCI Registry<br/>(Harbor etc.)"]
    REG -->|"docker pull"| K8S["Kubernetes Pod"]
    REG -->|"docker pull"| VM["Inside OpenStack VM"]

    style REG fill:#e3f2fd,stroke:#1565c0
</pre>

> A standard repository for push/pull of container images

## 1-3. Notable OCI Registries

| Registry | Notes |
|----------|-------|
| **Docker Hub** | Default public registry, free tier limited |
| **Harbor** | Enterprise Private Registry (open source) |
| **Amazon ECR** | AWS managed |
| **Google GCR / Artifact Registry** | GCP managed |
| **Azure ACR** | Azure managed |
| **GitHub Container Registry (ghcr.io)** | GitHub-integrated |

---

# [02] Harbor — Enterprise Private Registry

Harbor is the most prominent **open-source implementation** of OCI Registry — a CNCF Graduated project.

## 2-1. Key Features

<pre class="mermaid">
graph TD
    HARBOR["Harbor"] --> IMG["Image storage and distribution<br/>(OCI standard)"]
    HARBOR --> RBAC["RBAC<br/>per-project access control"]
    HARBOR --> SCAN["Vulnerability scanning<br/>(Trivy built-in)"]
    HARBOR --> SIGN["Image signing<br/>(Notary / Cosign)"]
    HARBOR --> REPL["Image replication<br/>(multi-site sync)"]
    HARBOR --> HELM["Helm Chart repository<br/>(OCI-based)"]

    style HARBOR fill:#e3f2fd,stroke:#1565c0
</pre>

| Feature | Description |
|---------|-------------|
| **Image storage/distribution** | Standard OCI push/pull |
| **RBAC** | Per-project user/team permissions |
| **Vulnerability scanning** | Automatic scans via Trivy |
| **Image signing** | Image integrity via Notary/Cosign |
| **Image replication** | Sync between multiple Harbor instances |
| **Helm Chart** | OCI-based Helm Chart repository |

## 2-2. Air-gap Support

Even in closed networks (air-gap), running Harbor as a Private Registry lets you manage images without external Docker Hub access.

---

# [03] Harbor in Kubernetes

<pre class="mermaid">
sequenceDiagram
    participant CI as CI/CD Pipeline
    participant Harbor as Harbor Registry
    participant K8s as Kubernetes

    CI->>Harbor: docker push (built image)
    K8s->>Harbor: docker pull (on Pod create)
    Harbor-->>K8s: image delivered
    K8s->>K8s: Pod runs
</pre>

| Role | Description |
|------|-------------|
| Supplies Pod images | Repository referenced by Deployments, StatefulSets, etc. |
| CI/CD hub | Intermediate store in the build → push → deploy pipeline |
| Helm Chart store | Push/pull OCI-based Helm Charts to/from Harbor |
| Air-gap support | Image supply for K8s clusters in closed networks |

**K8s Harbor usage example:**

```yaml
# Reference a Harbor image from a Deployment
spec:
  containers:
    - name: my-app
      image: harbor.example.com/project/my-app:v1.0
  imagePullSecrets:
    - name: harbor-secret
```

---

# [04] Harbor in OpenStack

## 4-1. OpenStack-Helm Environment

In **OpenStack-Helm** (deploying OpenStack on top of Kubernetes), OpenStack services themselves run as containers. Their images are pulled from Harbor.

<pre class="mermaid">
graph LR
    HARBOR["Harbor"] -->|"image pull"| OSH["OpenStack-Helm<br/>(OpenStack on K8s)"]
    OSH --> NOVA["Nova<br/>(container)"]
    OSH --> NEUTRON["Neutron<br/>(container)"]
    OSH --> KEYSTONE["Keystone<br/>(container)"]

    style HARBOR fill:#e3f2fd,stroke:#1565c0
    style OSH fill:#fff3e0,stroke:#e65100
</pre>

## 4-2. VM-based Environment

In traditional VM-based OpenStack, Docker can run inside a VM and pull images from Harbor.

```
Glance → create VM → inside VM: docker pull harbor.example.com/...
```

---

# [05] Harbor vs Glance — Different Roles

| Item | Harbor | Glance |
|------|--------|--------|
| **Purpose** | Container image store | VM disk image store |
| **Image format** | OCI (Docker images) | qcow2, raw, vmdk, etc. |
| **Used in** | Kubernetes, Docker | OpenStack (Nova) |
| **Standard** | OCI Distribution Spec | OpenStack Image API |
| **Commands** | `docker push/pull` | `openstack image create` |

:warning: Harbor and Glance **do not integrate directly** — image formats are completely different. For integration, build each from the same source in your CI/CD pipeline.
{: .notice--warning}

## 5-1. Indirect Integration Patterns

| Method | Description |
|--------|-------------|
| **Convert and upload** | Container image → VM image conversion → Glance registration |
| **CI/CD integration (recommended)** | From the same source: VM images → Glance, container images → Harbor |
| **VM internal usage** | Create VM via Glance, then pull from Harbor inside the VM |

---

# [06] Harbor vs Nexus vs KubeKey

| Item | Harbor | Nexus | KubeKey |
|------|--------|-------|---------|
| **Role** | OCI Registry (container images only) | Unified package repository | Kubernetes installer |
| **Storage target** | Container images, Helm Charts | Maven, npm, Docker, PyPI, etc. | Cluster binaries |
| **K8s relationship** | Image supply | Indirect (npm/Maven, etc.) | Cluster install/management |
| **Strength** | Security (scan/sign), RBAC | Multi-format unified management | Air-gap K8s install |

```
Harbor  = container image warehouse
Nexus   = whole package warehouse (multi-purpose, includes Docker)
KubeKey = Kubernetes installer (not an image store)
```

---

# [07] Overall Architecture

<pre class="mermaid">
graph TB
    subgraph CI_CD["CI/CD Pipeline"]
        BUILD["Source build"]
    end

    subgraph Registry["Image Store"]
        HARBOR["Harbor<br/>(Private OCI Registry)"]
    end

    subgraph K8s["Kubernetes Cluster"]
        POD1["App Pod"]
        POD2["App Pod"]
    end

    subgraph OpenStack["OpenStack"]
        OSH["OpenStack-Helm<br/>(service containers)"]
        VM["Inside VM<br/>(Docker)"]
        GLANCE["Glance<br/>(VM image)"]
    end

    BUILD -->|"docker push"| HARBOR
    BUILD -->|"VM image"| GLANCE
    HARBOR -->|"pull"| POD1
    HARBOR -->|"pull"| POD2
    HARBOR -->|"pull"| OSH
    HARBOR -->|"pull"| VM
    GLANCE -->|"create VM"| VM

    style HARBOR fill:#e3f2fd,stroke:#1565c0
    style GLANCE fill:#fff3e0,stroke:#e65100
</pre>

---

# [08] Summary

| Concept | One-line summary |
|---------|------------------|
| **OCI Registry** | Standard repository for push/pull of container images |
| **Harbor** | Enterprise Private OCI Registry (CNCF Graduated) |
| **Glance** | OpenStack VM disk image store |
| **Nexus** | Unified package store covering Docker and many other formats |

> Harbor for container images, Glance for VM images → **separate roles, unified operation via CI/CD**
