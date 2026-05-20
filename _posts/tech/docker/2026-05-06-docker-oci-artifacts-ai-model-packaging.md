---
title: "Docker가 AI 모델 패키징에 OCI Artifacts를 선택한 이유 — ModelPack과 새로운 표준"
description: "Docker가 AI 모델 배포를 위해 OCI Artifacts를 채택한 배경, OCI Image와의 차이, ModelPack 표준, Model Spec/Modelfile/modctl 구조 정리"
excerpt: "AI 모델을 Docker처럼 다루기 — OCI Artifacts로 Docker Hub, Harbor 같은 기존 레지스트리에서 모델을 push/pull 하는 새로운 표준"
date: 2026-05-06
categories: Docker
tags: [Docker, OCI, OCI-Artifacts, AI, ModelPack, ModelRunner, LLM, modctl, Modelfile, GGUF, ContainerRegistry, AI-패키징]
ref: docker-oci-artifacts-ai-model-packaging
---

:bulb: Docker가 AI 모델 패키징을 위해 **OCI Artifacts**를 채택했다. 컨테이너 이미지처럼 모델을 다루는 새로운 표준 **ModelPack**과 그 기술적 배경을 정리한다.
{: .notice--info}

---

# [01] 배경 — 인프라 진화의 4단계

<pre class="mermaid">
graph LR
    HW["1. 하드웨어<br/>중심"] --> VM["2. 가상머신<br/>(VM) 시대"]
    VM --> CT["3. 컨테이너 시대<br/>(Docker / K8s)"]
    CT --> AI["4. AI 모델 중심<br/>인프라 (현재)"]

    style HW fill:#f5f5f5,stroke:#616161
    style VM fill:#e3f2fd,stroke:#1565c0
    style CT fill:#fff3e0,stroke:#e65100
    style AI fill:#e8f5e9,stroke:#2e7d32
</pre>

현재 단계에서 개발자들은 모델 배포 시 다음 문제를 겪고 있다:

| 문제 | 설명 |
|------|------|
| 비표준화된 저장 방식 | Hugging Face, S3, 자체 서버 등 산재 |
| 가중치 파일 산재 | `.bin`, `.safetensors`, `.gguf` 등 포맷 혼재 |
| 환경 불일치 | 모델·코드·메타데이터의 결합이 약함 |
| 벤더 종속 | 특정 플랫폼·기업에 묶이는 배포 방식 |

---

# [02] ModelPack — "AI 모델을 위한 Docker"

ModelPack은 **벤더 중립적 오픈소스 표준**으로, OCI Artifacts 위에 AI 모델 패키징 규약을 정의한 것이다.

## 2-1. Docker 컨테이너 vs ModelPack

| 구분 | Docker 컨테이너 | ModelPack |
|------|----------------|-----------|
| 패키징 대상 | 애플리케이션 + 실행 환경 | **모델 가중치 + 메타데이터 + 추론 코드** |
| 포맷 | OCI Image | OCI Artifacts |
| 레지스트리 | Docker Hub, Harbor 등 | **동일하게 재사용** |
| CLI | `docker` | `modctl` |

:bulb: **핵심 장점** — 기존 Docker Hub, Harbor, GitHub Packages 같은 표준 OCI 레지스트리를 그대로 사용할 수 있어 **별도의 AI 전용 인프라 구축이 불필요**하다.
{: .notice--info}

## 2-2. ModelPack의 3가지 구성 요소

| 요소 | 역할 | 비유 |
|------|------|------|
| **Model Spec** | OCI 이미지 명세 기반의 기술 규칙 (매니페스트, 설정 레이어, 데이터 레이어) | OCI Image Spec |
| **Modelfile** | 메타데이터·파일 매핑 정의 (NAME, ARCH, FAMILY, PARAMSIZE, FORMAT 등) | Dockerfile |
| **modctl** | CLI 도구 (build, push, pull, extract) | `docker` CLI |

## 2-3. 효율성 설계

모델 가중치와 코드를 **별도 레이어**로 분리:

```
Layer 1: model weights (큰 파일, 자주 안 바뀜)
Layer 2: inference code (작은 파일, 자주 바뀜)
Layer 3: metadata (config, license)
```

코드 수정 시 거대한 가중치 파일을 다시 전송할 필요가 없어 **레이어 캐싱 효과**를 극대화한다.

---

# [03] OCI Image vs OCI Artifacts — 왜 Artifacts인가

Docker는 **OCI Image**가 아닌 **OCI Artifacts**를 선택했다. 그 이유가 핵심이다.

## 3-1. 두 형식의 차이

| 항목 | OCI Image | OCI Artifacts |
|------|-----------|---------------|
| 목적 | 컨테이너 실행 | 임의 콘텐츠 저장·배포 |
| 레이어 형식 | TAR 아카이브 (파일시스템) | 자유 형식 (도메인별 정의) |
| 메타데이터 | 컨테이너 실행 환경 | 도메인 특화 (JSON 자유) |
| 미디어 타입 | 고정 (image config, layer) | **커스텀 정의 가능** |

## 3-2. Artifacts를 선택한 4가지 이유

<pre class="mermaid">
graph TD
    OCI["OCI Artifacts 선택"] --> R1["① 도메인 특화<br/>메타데이터"]
    OCI --> R2["② 성능 최적화"]
    OCI --> R3["③ 인퍼런스 엔진<br/>과 분리"]
    OCI --> R4["④ 명확한 의도<br/>표현"]

    style OCI fill:#e3f2fd,stroke:#1565c0
</pre>

### ① 도메인 특화 메타데이터

모델 크기, 파라미터 수, 양자화 정보 등을 JSON으로 정의. **작은 메타데이터 파일만 먼저 받아 모델 비교·선택**이 가능하다.

```json
{
  "format": "gguf",
  "quantization": "Q4_K_M",
  "parameters": "7B",
  "architecture": "llama",
  "created": "2026-05-06T...",
  "digests": {...}
}
```

### ② 성능 최적화

| 최적화 | 설명 |
|--------|------|
| 비압축 저장 | 모델은 **고엔트로피 파일**이라 압축 효율 극히 낮음 — 압축하지 않음 |
| 단일 파일 형식 | 메모리 맵핑(mmap) 가능 — 추론 시작 시간 단축 |
| 결정적 블롭 | 동일 모델 파일은 항상 동일한 블롭 → **중복 제거** 효율 증대 |

### ③ 인퍼런스 엔진과 분리

모델과 실행 엔진(llama.cpp, vLLM 등)을 별도로 배포한다.

```
모델 (OCI Artifact)
  ↓ pull
사용자 환경
  ↓
시스템에 최적화된 엔진 (별도 설치)
```

장점:
- 사용자가 GPU/CPU 환경에 맞는 엔진을 선택
- 매번 모든 엔진 조합으로 모델을 패키징할 필요 없음

### ④ 명확한 의도 표현

OCI Image가 아니라는 점을 **미디어 타입으로 명시**:

- 컨테이너처럼 실행 시도하면 실패
- 인퍼런스 엔진 없이 독립 실행 불가능함이 명확
- 혼동과 예기치 않은 오류 방지

---

# [04] 기술적 상세 — 미디어 타입과 구조

## 4-1. Docker AI 모델 미디어 타입

```
application/vnd.docker.ai.model.config.v0.1+json   ← 모델 설정
application/vnd.docker.ai.gguf.v3                  ← GGUF 모델 파일
application/vnd.docker.ai.license                  ← 라이선스 파일
```

## 4-2. 모델 레이어의 특성

| 특성 | 설명 |
|------|------|
| 파일시스템 레이어 아님 | 단순 파일 저장소 |
| 식별 방법 | **파일명이 아닌 미디어 타입**으로 식별 |
| 활용 | Docker Model Runner가 모델 스토어에서 검색 |

## 4-3. 모델 설정에 포함되는 정보

| 항목 | 예시 |
|------|------|
| 포맷 | `gguf`, `safetensors`, `onnx` |
| 양자화 수준 | `Q4_K_M`, `Q8_0`, `FP16` |
| 파라미터 수 | `7B`, `13B`, `70B` |
| 아키텍처 | `llama`, `mistral`, `qwen` |
| 생성 타임스탬프 | ISO 8601 |
| 파일 다이제스트 | 무결성 검증용 SHA256 |

---

# [05] 실무 워크플로우

## 5-1. ModelPack — modctl 사용

```bash
# 1. modctl 설치 및 모델 파일 준비
modctl --version

# 2. Modelfile 작성 (메타데이터 정의)
cat > Modelfile <<'EOF'
NAME llama-3-8b
ARCH llama
FAMILY llama-3
PARAMSIZE 8B
FORMAT gguf

CONFIG ./config.json
MODEL  ./llama-3-8b-q4.gguf
CODE   ./inference.py
DOC    ./README.md
EOF

# 3. OCI 레이어로 빌드
modctl build -t harbor.example.com/models/llama-3-8b:q4 .

# 4. 원격 레지스트리 배포
modctl push harbor.example.com/models/llama-3-8b:q4

# 5. 사용 환경에서 다운로드
modctl pull harbor.example.com/models/llama-3-8b:q4
modctl extract harbor.example.com/models/llama-3-8b:q4 ./model/
```

## 5-2. Docker Model Runner 사용

Docker는 자체 도구 **Docker Model Runner**도 제공한다.

```bash
# Hugging Face에서 자동 변환하여 OCI Artifact로 push
docker model pull hf://meta-llama/Llama-3-8B-Instruct

# 로컬에서 LLM 실행
docker model run llama-3-8b-instruct
```

---

# [06] 엔터프라이즈 관점의 장점

| 영역 | 효과 |
|------|------|
| **DevOps 인프라 재사용** | Docker Hub, Artifactory, Harbor 등 기존 인프라 그대로 사용 |
| **보안** | Registry Access Management(RAM) 정책 기반 접근 제어 |
| **버전 관리** | OCI 태그 시스템 그대로 활용 |
| **클라우드 네이티브** | containerd, Kubernetes와 깊은 연계 |
| **1급 객체화** | 모델을 클라우드 네이티브 환경의 1급 시민으로 취급 |

---

# [07] 향후 계획

Docker가 발표한 다음 버전 지원 예정 사항:

| 기능 | 설명 |
|------|------|
| **런타임 설정** | 템플릿, 컨텍스트 크기, 기본 파라미터 |
| **LoRA 어댑터** | 사용 사례별 파인튜닝 추가 |
| **멀티모달 프로젝터** | 비전-언어 모델(VLM) 지원 |
| **모델 인덱스** | 파라미터·양자화 변형 목록 |
| **containerd 깊은 통합** | 컨테이너 런타임 레벨에서 모델 관리 |
| **ModelPack 상호 운용** | 다른 표준과의 호환성 개선 |

---

# [08] 정리

| 핵심 | 내용 |
|------|------|
| **목표** | AI 모델 배포를 Docker처럼 표준화 |
| **선택** | OCI Image가 아닌 **OCI Artifacts** |
| **이유** | 도메인 특화 메타데이터, 비압축 저장, 엔진 분리, 명확한 의도 |
| **인프라** | 기존 OCI 레지스트리(Docker Hub, Harbor) 그대로 사용 |
| **CLI** | ModelPack의 `modctl` 또는 `docker model` |
| **포맷 식별** | 파일명 아닌 **미디어 타입**으로 |

:bulb: 컨테이너 기술이 소프트웨어 배포를 표준화했듯이, OCI Artifacts 기반의 ModelPack/Docker Model Runner는 **AI 모델 배포의 표준화**를 시도한다. 기존 클라우드 인프라를 활용하면서도 모델의 일관성·이식성·성능을 모두 확보하는 실용적 접근이다.
{: .notice--info}

---

# 참고

- [ModelPack — AI/ML 모델 패키징 표준 (PyTorch KR)](https://discuss.pytorch.kr/t/modelpack-ai-ml-ai-docker-feat-oci/8437)
- [Why Docker Chose OCI Artifacts for AI Model Packaging (LinkedIn)](https://kr.linkedin.com/pulse/why-docker-chose-oci-artifacts-ai-model-packaging-docker-f9wpe)
- [OCI Registry와 Harbor 가이드](/storage/oci-registry-harbor-kubernetes-openstack/) (이전 포스트)
