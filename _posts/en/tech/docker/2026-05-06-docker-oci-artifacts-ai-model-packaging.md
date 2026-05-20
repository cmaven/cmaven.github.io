---
title: "Why Docker Chose OCI Artifacts for AI Model Packaging — ModelPack and the New Standard"
description: "Background on Docker's adoption of OCI Artifacts for AI model packaging, differences from OCI Images, the ModelPack standard, and its Model Spec/Modelfile/modctl structure"
excerpt: "Treating AI models like Docker — push/pull models from existing registries like Docker Hub and Harbor via OCI Artifacts, the new standard"
date: 2026-05-06
categories: Docker
tags: [Docker, OCI, OCI-Artifacts, AI, ModelPack, ModelRunner, LLM, modctl, Modelfile, GGUF, ContainerRegistry, AI-packaging]
ref: docker-oci-artifacts-ai-model-packaging
---

:bulb: Docker chose **OCI Artifacts** for AI model packaging. This post covers the **ModelPack** standard and the technical reasoning behind it — a new way to treat models like container images.
{: .notice--info}

---

# [01] Background — 4 Eras of Infrastructure Evolution

<pre class="mermaid">
graph LR
    HW["1. Hardware-<br/>centric"] --> VM["2. Virtual<br/>Machines"]
    VM --> CT["3. Containers<br/>(Docker / K8s)"]
    CT --> AI["4. AI Model-<br/>centric (now)"]

    style HW fill:#f5f5f5,stroke:#616161
    style VM fill:#e3f2fd,stroke:#1565c0
    style CT fill:#fff3e0,stroke:#e65100
    style AI fill:#e8f5e9,stroke:#2e7d32
</pre>

In the current era, developers face these problems when deploying models:

| Problem | Description |
|---------|-------------|
| Non-standard storage | Scattered across Hugging Face, S3, custom servers |
| Weight file formats | Mixed `.bin`, `.safetensors`, `.gguf`, etc. |
| Environment drift | Loose coupling between model, code, and metadata |
| Vendor lock-in | Distribution tied to specific platforms |

---

# [02] ModelPack — "Docker for AI Models"

ModelPack is a **vendor-neutral open-source standard** defining AI model packaging conventions on top of OCI Artifacts.

## 2-1. Docker Container vs ModelPack

| Aspect | Docker Container | ModelPack |
|--------|------------------|-----------|
| Packaging target | Application + runtime | **Model weights + metadata + inference code** |
| Format | OCI Image | OCI Artifacts |
| Registry | Docker Hub, Harbor, etc. | **Same registries reused** |
| CLI | `docker` | `modctl` |

:bulb: **Key advantage** — existing OCI registries (Docker Hub, Harbor, GitHub Packages) work as-is. **No dedicated AI infrastructure needed**.
{: .notice--info}

## 2-2. Three Components of ModelPack

| Component | Role | Analogy |
|-----------|------|---------|
| **Model Spec** | Technical rules based on OCI image spec (manifest, config layer, data layer) | OCI Image Spec |
| **Modelfile** | Metadata and file mapping definition (NAME, ARCH, FAMILY, PARAMSIZE, FORMAT) | Dockerfile |
| **modctl** | CLI tool (build, push, pull, extract) | `docker` CLI |

## 2-3. Efficiency Design

Separates model weights and code into **distinct layers**:

```
Layer 1: model weights (large, rarely changes)
Layer 2: inference code (small, changes often)
Layer 3: metadata (config, license)
```

When code changes, you don't re-transfer huge weight files — maximizing **layer caching effects**.

---

# [03] OCI Image vs OCI Artifacts — Why Artifacts?

Docker chose **OCI Artifacts**, not OCI Image. The reasoning is the core of this decision.

## 3-1. Two Format Differences

| Item | OCI Image | OCI Artifacts |
|------|-----------|---------------|
| Purpose | Container execution | Arbitrary content storage/distribution |
| Layer format | TAR archive (filesystem) | Free-form (domain-specific) |
| Metadata | Container runtime info | Domain-specific (free JSON) |
| Media type | Fixed (image config, layer) | **Custom definition allowed** |

## 3-2. Four Reasons for Choosing Artifacts

<pre class="mermaid">
graph TD
    OCI["Choose OCI Artifacts"] --> R1["① Domain-specific<br/>metadata"]
    OCI --> R2["② Performance<br/>optimization"]
    OCI --> R3["③ Separation from<br/>inference engine"]
    OCI --> R4["④ Clear intent<br/>expression"]

    style OCI fill:#e3f2fd,stroke:#1565c0
</pre>

### ① Domain-Specific Metadata

Model size, parameter count, quantization info defined in JSON. **Download only the small metadata file first to compare and select models**.

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

### ② Performance Optimization

| Optimization | Description |
|--------------|-------------|
| No compression | Models are **high-entropy files** — compression provides almost no benefit |
| Single file format | Memory mapping (mmap) possible — faster inference startup |
| Deterministic blobs | Same model file always yields same blob → **deduplication** efficiency |

### ③ Separation from Inference Engine

Models and inference engines (llama.cpp, vLLM, etc.) are deployed separately.

```
Model (OCI Artifact)
  ↓ pull
User environment
  ↓
Engine optimized for the system (installed separately)
```

Benefits:

- User picks the engine matching their GPU/CPU
- No need to package the model with every possible engine combination

### ④ Clear Intent Expression

Explicitly indicates "this is not an OCI Image" via **media types**:

- Attempts to run it as a container fail
- Makes clear it can't run without an inference engine
- Prevents confusion and unexpected errors

---

# [04] Technical Details — Media Types and Structure

## 4-1. Docker AI Model Media Types

```
application/vnd.docker.ai.model.config.v0.1+json   ← model config
application/vnd.docker.ai.gguf.v3                  ← GGUF model file
application/vnd.docker.ai.license                  ← license file
```

## 4-2. Model Layer Characteristics

| Trait | Description |
|-------|-------------|
| Not a filesystem layer | Just a file storage |
| Identification | **By media type, not filename** |
| Usage | Docker Model Runner looks up the model store |

## 4-3. Information in Model Config

| Item | Example |
|------|---------|
| Format | `gguf`, `safetensors`, `onnx` |
| Quantization | `Q4_K_M`, `Q8_0`, `FP16` |
| Parameters | `7B`, `13B`, `70B` |
| Architecture | `llama`, `mistral`, `qwen` |
| Created timestamp | ISO 8601 |
| File digest | SHA256 for integrity |

---

# [05] Real Workflow

## 5-1. ModelPack — Using modctl

```bash
# 1. Install modctl, prepare model files
modctl --version

# 2. Write a Modelfile (define metadata)
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

# 3. Build as OCI layers
modctl build -t harbor.example.com/models/llama-3-8b:q4 .

# 4. Push to remote registry
modctl push harbor.example.com/models/llama-3-8b:q4

# 5. Pull and extract on the consuming environment
modctl pull harbor.example.com/models/llama-3-8b:q4
modctl extract harbor.example.com/models/llama-3-8b:q4 ./model/
```

## 5-2. Using Docker Model Runner

Docker also provides its own tool, **Docker Model Runner**.

```bash
# Auto-convert from Hugging Face and push as OCI Artifact
docker model pull hf://meta-llama/Llama-3-8B-Instruct

# Run LLM locally
docker model run llama-3-8b-instruct
```

---

# [06] Enterprise Benefits

| Area | Benefit |
|------|---------|
| **Reuse DevOps infra** | Existing Docker Hub, Artifactory, Harbor work as-is |
| **Security** | Registry Access Management (RAM) policy-based access control |
| **Versioning** | Use OCI tag system directly |
| **Cloud-native** | Deep integration with containerd, Kubernetes |
| **First-class object** | Treat models as first-class citizens in cloud-native env |

---

# [07] Future Plans

Docker's announced upcoming features:

| Feature | Description |
|---------|-------------|
| **Runtime config** | Templates, context size, default parameters |
| **LoRA adapters** | Add fine-tuning per use case |
| **Multimodal projectors** | Support for vision-language models (VLM) |
| **Model index** | List of parameter/quantization variants |
| **Deeper containerd integration** | Manage models at the container runtime level |
| **ModelPack interop** | Improved compatibility with other standards |

---

# [08] Summary

| Key point | Content |
|-----------|---------|
| **Goal** | Standardize AI model distribution like Docker |
| **Choice** | OCI Artifacts (not OCI Image) |
| **Reason** | Domain-specific metadata, no compression, engine separation, clear intent |
| **Infra** | Reuse existing OCI registries (Docker Hub, Harbor) |
| **CLI** | ModelPack's `modctl` or `docker model` |
| **Format ID** | Media type, not filename |

:bulb: Just as container tech standardized software distribution, OCI Artifacts-based ModelPack/Docker Model Runner aims to **standardize AI model distribution**. A practical approach that leverages existing cloud infrastructure while ensuring model consistency, portability, and performance.
{: .notice--info}

---

# References

- [ModelPack — AI/ML Model Packaging Standard (PyTorch KR)](https://discuss.pytorch.kr/t/modelpack-ai-ml-ai-docker-feat-oci/8437)
- [Why Docker Chose OCI Artifacts for AI Model Packaging (LinkedIn)](https://kr.linkedin.com/pulse/why-docker-chose-oci-artifacts-ai-model-packaging-docker-f9wpe)
