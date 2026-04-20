---
title: "OCI Registry와 Harbor — Kubernetes/OpenStack 환경의 컨테이너 이미지 관리"
description: "OCI Registry 개념, Harbor의 역할과 주요 기능, Kubernetes/OpenStack에서의 활용, Glance와의 차이점, Nexus/KubeKey 비교 정리"
excerpt: "Harbor는 Enterprise급 Private OCI Registry — Kubernetes와 OpenStack에서 컨테이너 이미지를 표준 방식으로 push/pull하는 저장소"
date: 2026-04-20
categories: Tech
tags: [OCI, Harbor, Registry, Kubernetes, OpenStack, Glance, Docker, 컨테이너이미지, Nexus, CI-CD]
---

:bulb: 컨테이너 이미지를 표준 방식으로 관리하는 OCI Registry의 개념과, 대표적 구현체인 Harbor의 역할, Kubernetes/OpenStack에서의 활용 방법을 정리한다.
{: .notice--info}

---

# [01] OCI Registry란?

OCI(Open Container Initiative) Registry는 컨테이너 이미지를 저장하고 배포하기 위한 **표준 인터페이스**이다.

## 1-1. 핵심 구성 요소

| 구성 요소 | 설명 |
|----------|------|
| **Image** | 컨테이너 실행에 필요한 파일 시스템과 메타데이터의 묶음 |
| **Layer** | 이미지를 구성하는 개별 파일 시스템 변경 단위 (계층 구조) |
| **Manifest** | 이미지의 레이어 목록, 설정, 플랫폼 정보를 기술하는 JSON 문서 |

## 1-2. 동작 원리

<pre class="mermaid">
graph LR
    DEV["개발자 / CI"] -->|"docker push"| REG["OCI Registry<br/>(Harbor 등)"]
    REG -->|"docker pull"| K8S["Kubernetes Pod"]
    REG -->|"docker pull"| VM["OpenStack VM 내부"]

    style REG fill:#e3f2fd,stroke:#1565c0
</pre>

> 컨테이너 이미지를 표준 방식으로 push/pull 하는 저장소

## 1-3. 대표적인 OCI Registry

| Registry | 특징 |
|----------|------|
| **Docker Hub** | 퍼블릭 기본 Registry, 무료 제한 있음 |
| **Harbor** | 엔터프라이즈 Private Registry (오픈소스) |
| **Amazon ECR** | AWS 관리형 |
| **Google GCR / Artifact Registry** | GCP 관리형 |
| **Azure ACR** | Azure 관리형 |
| **GitHub Container Registry (ghcr.io)** | GitHub 통합 |

---

# [02] Harbor — Enterprise급 Private Registry

Harbor는 OCI Registry의 대표적인 **오픈소스 구현체**로, CNCF Graduated 프로젝트이다.

## 2-1. 주요 기능

<pre class="mermaid">
graph TD
    HARBOR["Harbor"] --> IMG["이미지 저장 및 배포<br/>(OCI 표준)"]
    HARBOR --> RBAC["RBAC<br/>프로젝트별 권한 관리"]
    HARBOR --> SCAN["취약점 스캔<br/>(Trivy 내장)"]
    HARBOR --> SIGN["이미지 서명<br/>(Notary / Cosign)"]
    HARBOR --> REPL["이미지 복제<br/>(멀티 사이트 동기화)"]
    HARBOR --> HELM["Helm Chart 저장소<br/>(OCI 기반)"]

    style HARBOR fill:#e3f2fd,stroke:#1565c0
</pre>

| 기능 | 설명 |
|------|------|
| **이미지 저장/배포** | OCI 표준 push/pull |
| **RBAC** | 프로젝트 단위 사용자/팀 권한 관리 |
| **취약점 스캔** | Trivy로 이미지 보안 취약점 자동 검사 |
| **이미지 서명** | Notary/Cosign으로 이미지 무결성 보장 |
| **이미지 복제** | 여러 Harbor 인스턴스 간 이미지 동기화 |
| **Helm Chart** | OCI 기반 Helm Chart 저장소 기능 |

## 2-2. Air-gap 환경 지원

인터넷이 차단된 폐쇄망(Air-gap) 환경에서도 Harbor를 Private Registry로 사용하면, 외부 Docker Hub 없이 이미지를 관리할 수 있다.

---

# [03] Kubernetes에서 Harbor

<pre class="mermaid">
sequenceDiagram
    participant CI as CI/CD Pipeline
    participant Harbor as Harbor Registry
    participant K8s as Kubernetes

    CI->>Harbor: docker push (빌드된 이미지)
    K8s->>Harbor: docker pull (Pod 생성 시)
    Harbor-->>K8s: 이미지 전달
    K8s->>K8s: Pod 실행
</pre>

| 역할 | 설명 |
|------|------|
| Pod 이미지 공급 | Deployment, StatefulSet 등이 참조하는 이미지 저장소 |
| CI/CD 중심 | 빌드 → push → 배포 파이프라인의 중간 저장소 |
| Helm Chart 저장소 | OCI 기반 Helm Chart를 Harbor에 push/pull |
| Air-gap 지원 | 폐쇄망 Kubernetes 클러스터에서 이미지 공급 |

**Kubernetes에서 Harbor 사용 예시:**

```yaml
# Deployment에서 Harbor 이미지 참조
spec:
  containers:
    - name: my-app
      image: harbor.example.com/project/my-app:v1.0
  imagePullSecrets:
    - name: harbor-secret
```

---

# [04] OpenStack에서 Harbor

## 4-1. OpenStack-Helm 환경

OpenStack을 Kubernetes 위에 배포하는 **OpenStack-Helm** 방식에서는, OpenStack 서비스 자체가 컨테이너로 실행된다. 이 컨테이너 이미지를 Harbor에서 pull한다.

<pre class="mermaid">
graph LR
    HARBOR["Harbor"] -->|"이미지 pull"| OSH["OpenStack-Helm<br/>(K8s 위 OpenStack)"]
    OSH --> NOVA["Nova<br/>(컨테이너)"]
    OSH --> NEUTRON["Neutron<br/>(컨테이너)"]
    OSH --> KEYSTONE["Keystone<br/>(컨테이너)"]

    style HARBOR fill:#e3f2fd,stroke:#1565c0
    style OSH fill:#fff3e0,stroke:#e65100
</pre>

## 4-2. VM 기반 환경

기존 VM 기반 OpenStack에서도 VM 내부에서 Docker를 실행하여 Harbor의 이미지를 사용할 수 있다.

```
Glance → VM 생성 → VM 내부에서 docker pull harbor.example.com/...
```

---

# [05] Harbor vs Glance — 역할이 다르다

| 항목 | Harbor | Glance |
|------|--------|--------|
| **용도** | 컨테이너 이미지 저장소 | VM 디스크 이미지 저장소 |
| **이미지 포맷** | OCI (Docker 이미지) | qcow2, raw, vmdk 등 |
| **사용 위치** | Kubernetes, Docker | OpenStack (Nova) |
| **표준** | OCI Distribution Spec | OpenStack Image API |
| **사용 명령** | `docker push/pull` | `openstack image create` |

:warning: Harbor와 Glance는 **직접 연동하지 않는다.** 이미지 포맷이 완전히 다르기 때문이다. 통합이 필요하면 CI/CD 파이프라인에서 동일 소스로부터 각각 빌드하여 관리한다.
{: .notice--warning}

## 5-1. 간접 활용 방식

| 방법 | 설명 |
|------|------|
| **변환 후 업로드** | 컨테이너 이미지 → VM 이미지 변환 → Glance 등록 |
| **CI/CD 통합 (권장)** | 동일 소스에서 VM 이미지는 Glance로, 컨테이너 이미지는 Harbor로 |
| **VM 내부 활용** | Glance로 VM 생성 후, VM 내부에서 Harbor pull |

---

# [06] Harbor vs Nexus vs KubeKey

| 항목 | Harbor | Nexus | KubeKey |
|------|--------|-------|---------|
| **역할** | OCI Registry (컨테이너 이미지 전용) | 통합 패키지 저장소 | Kubernetes 설치 도구 |
| **저장 대상** | 컨테이너 이미지, Helm Chart | Maven, npm, Docker, PyPI 등 | 클러스터 바이너리 |
| **Kubernetes 관계** | 이미지 공급 | 간접 (npm/Maven 등) | 클러스터 설치/관리 |
| **강점** | 보안(스캔/서명), RBAC | 다양한 포맷 통합 관리 | Air-gap K8s 설치 |

```
Harbor  = 컨테이너 이미지 창고
Nexus   = 전체 패키지 창고 (Docker 포함 다목적)
KubeKey = Kubernetes 설치 도구 (이미지 저장소 아님)
```

---

# [07] 전체 아키텍처

<pre class="mermaid">
graph TB
    subgraph CI_CD["CI/CD Pipeline"]
        BUILD["소스 빌드"]
    end

    subgraph Registry["이미지 저장소"]
        HARBOR["Harbor<br/>(Private OCI Registry)"]
    end

    subgraph K8s["Kubernetes 클러스터"]
        POD1["App Pod"]
        POD2["App Pod"]
    end

    subgraph OpenStack["OpenStack"]
        OSH["OpenStack-Helm<br/>(서비스 컨테이너)"]
        VM["VM 내부<br/>(Docker)"]
        GLANCE["Glance<br/>(VM 이미지)"]
    end

    BUILD -->|"docker push"| HARBOR
    BUILD -->|"VM 이미지"| GLANCE
    HARBOR -->|"pull"| POD1
    HARBOR -->|"pull"| POD2
    HARBOR -->|"pull"| OSH
    HARBOR -->|"pull"| VM
    GLANCE -->|"VM 생성"| VM

    style HARBOR fill:#e3f2fd,stroke:#1565c0
    style GLANCE fill:#fff3e0,stroke:#e65100
</pre>

---

# [08] 정리

| 개념 | 한 줄 요약 |
|------|-----------|
| **OCI Registry** | 컨테이너 이미지를 표준 방식으로 push/pull하는 저장소 |
| **Harbor** | Enterprise급 Private OCI Registry (CNCF Graduated) |
| **Glance** | OpenStack VM 디스크 이미지 저장소 |
| **Nexus** | Docker 포함 다양한 포맷의 통합 패키지 저장소 |

> Harbor는 컨테이너 이미지, Glance는 VM 이미지 → **역할 분리 + CI/CD로 통합 운영**
