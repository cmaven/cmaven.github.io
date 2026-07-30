---
title: "Building a Korean-Language Local LLM Setup for OpenCode on Two A30s — Ollama + Qwen3.5 35B-A3B"
description: "Running OpenCode entirely offline in Korean on two NVIDIA A30 24GB GPUs (no NVLink) with Ollama and Qwen3.5 35B-A3B Q4_K_M. From beginner concepts (LLM, VRAM, quantization, KV cache, MoE) through systemd tuning, 64K context, staged OOM mitigation, and an AGENTS.md that locks in Korean output quality"
excerpt: "No API keys, just two A30s: OpenCode as a Korean-speaking coding agent. Written so you can follow along even if GPUs and LLMs are new to you — concepts first, tuning after"
date: 2026-07-30
categories: Etc
tags: [OpenCode, Ollama, local-LLM, Qwen3.5, A30, multi-GPU, quantization, KV-Cache, context-length, AGENTS.md, EXAONE, AI-coding-agent]
ref: opencode-korean-local-llm-a30x2
---

:bulb: This post documents a setup that runs OpenCode as a Korean-language coding agent using only two NVIDIA A30 24GB GPUs — no paid API. The conclusion is simple: **load a single Qwen3.5 35B-A3B Q4_K_M on Ollama, split it across both GPUs, and secure a 64K context.** No NVLink required. It's written so someone new to GPUs, LLMs, and OpenCode can follow along: concept explanations first, then systemd tuning, OOM handling, and the AGENTS.md that keeps output consistently in Korean, in actual build order.
{: .notice--info}

The final architecture first:

```text
User
  │ instructions in Korean
  ▼
OpenCode
  │ read/edit files, run commands, test
  ▼
Ollama's OpenAI-compatible API (127.0.0.1:11434)
  │ one model auto-split across two A30s
  ▼
Qwen3.5 35B-A3B Q4_K_M (~24GB)
  ├─ A30 #0 24GB
  └─ A30 #1 24GB
```

- **Cost**: no per-token API fees. Code never leaves the server, so it works on air-gapped networks
- **Model**: Qwen3.5 35B-A3B Q4_K_M — a balance of Korean, coding, tool calling, and long context
- **Context**: 65,536 tokens. Ollama's official docs recommend 64K+ for coding-agent workloads
- **No NVLink**: the goal isn't 2× speed — it's fitting a model + context that won't fit on one card across two

---

# [01] The Big Picture — LLM, OpenCode, Local LLM, Ollama

Before typing any install commands, let's establish what each of the four players actually does.

## 1-1. What Is an LLM?

LLM stands for **Large Language Model**.

Given an input sentence, an LLM generates the most likely next tokens, one after another. At first glance that sounds like very advanced autocomplete, but a sufficiently trained model can also:

- Understand and answer questions in Korean
- Write program code
- Analyze error logs
- Summarize documents
- Draw up work plans
- Call external tools

An LLM by itself, however, cannot edit files on your computer or run commands. That job belongs to an **agent harness** like OpenCode.

## 1-2. What Is OpenCode?

OpenCode is an **AI coding agent** that runs in the terminal. Unlike a chat service, it performs the following within the scope the user allows:

- List project files, read source code
- Edit multiple files, check `git diff`
- Run test commands, analyze build errors
- Fix the error and test again
- Launch separate research subagents

If the LLM is the brain, OpenCode is the execution system that wires that brain to files, the terminal, Git, and test tooling so it can do real development work.

```text
LLM alone      : user question → answer text
With OpenCode  : user request → plan → inspect files → edit code → test → report
```

## 1-3. What Is a Local LLM?

A local LLM is a model that runs **directly on your own server's GPUs**, rather than on an external API service like OpenAI, Anthropic, or OpenRouter.

Advantages:

- No per-token API cost
- Code and documents are never sent to an external model API
- Works in internet-restricted environments
- You control the model and its runtime settings directly

Disadvantages:

- Requires GPUs and storage
- You install and operate the model yourself
- Performance may fall short of large commercial models like Claude or GPT
- Long contexts demand a lot of GPU memory

## 1-4. What Is Ollama?

Ollama is a program that downloads, runs, and serves local LLMs over an API. Its position in this setup:

```text
OpenCode
   │ HTTP requests
   ▼
Ollama API server
   │ model loading, GPU usage, text generation
   ▼
2× A30 GPUs
```

OpenCode connects to the **OpenAI-compatible API** Ollama exposes. "OpenAI-compatible" does not mean using OpenAI's paid models — it means the request/response format matches the OpenAI API.

## 1-5. Provider vs. Model

Two terms you'll see constantly in the OpenCode UI:

- **Provider**: the server or connection method that serves models
- **Model**: the LLM that actually generates the answers

In this setup, `Provider = the local Ollama server` and `Model = qwen3.5:35b-a3b`. No Zen, OpenRouter, or Anthropic API needs to be connected.

---

# [02] Essential GPU and Memory Concepts

Understand this section and every tuning step later reads itself. If most of these terms are new, spending time here is the shortcut, not the detour.

## 2-1. What Kind of GPU Is the A30?

The NVIDIA A30 is a data-center Ampere GPU.

- GPU memory: 24GB HBM2, 933GB/s bandwidth
- Interface: PCIe Gen4, 165W TDP
- MIG support; up to two cards can be joined with an NVLink bridge
- Passive cooling (no fan) — relies on server chassis airflow

The server in this post doesn't use NVLink, so all traffic between the two GPUs goes over PCIe.

## 2-2. What Is VRAM?

VRAM is the GPU's dedicated memory. When running an LLM, VRAM is consumed by:

```text
GPU VRAM
├─ model weights
├─ KV cache
├─ CUDA workspace
└─ temporary input/output buffers
```

Having two A30s does not automatically give you one 48GB GPU. The program has to support splitting the model across GPUs. Ollama loads a model onto a single GPU if it fits entirely, and splits it across the available GPUs if it doesn't.

## 2-3. What Are Model Weights?

The knowledge and behavior a model learned, stored as arrays of numbers, are called **weights**. Bigger models generally mean bigger weight files.

This post's default model is about 24GB in Ollama's release. But never assume a 24GB model fits a 24GB GPU as-is — as shown above, the workspace and KV cache need room too.

## 2-4. What Is Quantization?

Quantization lowers the numeric precision of a model to shrink its file size and memory use. Think of it like compressing an original photo a little to reduce the file size.

Common labels:

- `BF16`: highest quality, heavy memory use
- `Q8`: 8-bit quantization
- `Q5`: 5-bit family
- `Q4_K_M`: the common balanced 4-bit variant

This post uses **Q4_K_M**. It makes a 30B-class model realistic on two A30s, uses far less VRAM than BF16, and balances quality and speed well for everyday coding work. The trade-off: some accuracy loss versus the original model, which can show up in hard reasoning or fine-grained code judgment.

## 2-5. What Is a Token?

An LLM doesn't process text character by character — it splits it into small units called **tokens**. A token can be a single character, part of a word, a symbol, or a code fragment.

```text
Input: Kubernetes 컨트롤러의 오류를 분석해줘.
Processing: split into multiple tokens
```

More tokens means more information the model must read and more memory used.

## 2-6. What Is Context Length?

Context length is the maximum number of tokens the model can hold and reference in a single task. In OpenCode, all of the following can land in context:

- The user's instructions, project rules
- Source code it has read, prior conversation
- Command output, error logs
- Tool descriptions, edit plans

So it needs far more context than casual chat. Ollama's OpenCode guide recommends **64K+ context** for local coding-agent models, and this post starts at 65,536 tokens.

```text
32K = about 32,768 tokens
64K = about 65,536 tokens
```

Increasing context also increases VRAM use. That trade-off returns in the OOM section later.

## 2-7. What Is the KV Cache?

The KV cache is a memory region that stores context the model has already read, so it doesn't recompute it from scratch every time. The longer the context, the bigger the KV cache.

```text
f16 KV cache  = quality first, large memory (default)
q8_0 KV cache = roughly half the memory, very small quality loss
q4_0 KV cache = smaller still, quality degradation may show
```

This post sets it to `q8_0` to cut memory versus the default `f16`. Start with `q8_0`.

## 2-8. What Are MoE and A3B?

Qwen3.5 35B-A3B is an MoE (Mixture of Experts) model.

- Total parameters: ~35B
- Parameters activated per token: ~3B

Read `A3B` as roughly "**Active 3B** parameters." MoE selects only the expert modules it needs for each computation. That reduces compute, but all expert weights must still sit in memory — so the model file doesn't shrink to 3B-model size.

## 2-9. What Is Tool Calling?

Tool calling is the model's ability to request external actions in a fixed format, rather than only answering with text. Tools in OpenCode include:

- Reading, editing, and searching files
- Running shell commands
- Running tests
- Invoking subagents

Even if a model's Korean is excellent, unstable tool calling means OpenCode can't actually get work done. That's why an OpenCode model must be judged on Korean ability and tool-calling ability together — the criterion that drives the model selection in the next section.

## 2-10. Is It Unusable Without NVLink?

It's usable. But splitting one model across two GPUs routes inter-GPU data over PCIe, which has less bandwidth than NVLink, so you may see:

- Lower token generation speed
- Longer first-response latency
- Two GPUs not translating into exactly 2× speed

The goal of this setup isn't doubling speed — it's **running a model and context too big for one card, stably, split across two**. Think of it as buying memory, not speed.

---

# [03] Model Selection — Korean Fluency Alone Isn't Enough

As 2-9 showed, an OpenCode model needs **tool calling stability** as much as natural Korean. The selection priorities:

```text
1. OpenCode tool calling stability
2. Coding and repository-scale task ability
3. Understanding Korean instructions, writing Korean output
4. Feasibility on two A30s
5. Installation and maintenance effort
```

Comparing the candidates against those criteria:

| Model | Strengths | Weaknesses | Best For |
|---|---|---|---|
| **Qwen3.5 35B-A3B Q4** | Balanced Korean/coding/tool-calling/long context, official Ollama release | PCIe communication overhead when split across two GPUs | **Default main model** |
| Qwen3-Coder 30B-A3B Q4 | Strong at coding-agent and repository work | General Korean prose may trail Korean-specialized models | Coding quality first |
| EXAONE 4.0 32B Q4 | Strong Korean domain knowledge and expression, official GGUF | 19.3GB weights make long context tight on a single A30 | Korean planning/docs/review |
| Kanana-2 30B-A3B | Korean tokenizer, emphasizes Korean agent performance | 32K default context, no simple official Ollama path | Advanced comparison experiments |

Why Qwen3.5 35B-A3B is the default:

- Supports 201 languages and dialects including Korean, with strong multilingual understanding
- A general chat model that also supports coding, tool calling, and agent work
- Official Ollama Q4_K_M release at about 24GB, Apache 2.0 licensed
- One A30 is a tight fit for weights plus long context, but two cards can target a 64K context
- Connecting a single model is the simplest thing a beginner can operate

The same reasoning explains why EXAONE and Kanana aren't the default. They're strong Korean candidates, but the bottleneck in this setup isn't Korean — it's tool calling and long context. It's also hard to objectively crown one "best Korean model": naturalness, domain knowledge, coding, tool calling, and post-quantization quality are all different axes. Stabilize the whole environment on Qwen3.5 first, then compare against EXAONE and Kanana using 10–20 real work tasks (see the final section).

---

# [04] Hardware Preparation

| Item | Value |
|---|---|
| GPU | NVIDIA A30 24GB × 2 (NVLink optional) |
| System RAM | 64GB minimum, 128GB+ recommended |
| Storage | 100GB+ free, 200GB+ if comparing models |
| Power/cooling | Up to 165W × 2 for the GPUs alone; passive cooling demands real chassis airflow |
| OS | Ubuntu 22.04 family |

Why system RAM matters beyond the GPUs: model file loading, OpenCode itself, Git/build/test, container and Kubernetes tooling, and any CPU offload under VRAM pressure all use main memory. CPU offload can keep things running but slows them down badly — avoid it in a healthy setup.

## 4-1. Verify Both GPUs

```bash
nvidia-smi -L
# GPU 0: NVIDIA A30 (...)
# GPU 1: NVIDIA A30 (...)

nvidia-smi          # overall status
nvidia-smi topo -m  # without NVLink the GPUs show a PCIe path — not an error
```

If `nvidia-smi` already works, don't force a driver change. Only on a fresh server with no driver:

```bash
sudo apt update
ubuntu-drivers devices
sudo ubuntu-drivers install
sudo reboot
```

On a Kubernetes node, or where the NVIDIA GPU Operator manages drivers, check for conflicts with the existing configuration before installing anything at the OS level.

## 4-2. Disable MIG

The A30 supports MIG (slicing one GPU into partitions), but this setup uses the full 24GB of both GPUs.

```bash
nvidia-smi -q | grep -A 2 "MIG Mode"

# if enabled, during a maintenance window
sudo nvidia-smi -i 0 -mig 0
sudo nvidia-smi -i 1 -mig 0
sudo reboot
```

MIG changes can fail while the GPU is in use. Stop processes, containers, and Kubernetes pods using the GPU first, and on a production server confirm the blast radius before proceeding.

---

# [05] Installing and Tuning Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama -v
sudo systemctl status ollama
```

The systemd override is the heart of the setup. Open it with `sudo systemctl edit ollama` and add:

```ini
[Service]
Environment="CUDA_VISIBLE_DEVICES=0,1"
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_CONTEXT_LENGTH=65536"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
Environment="OLLAMA_KEEP_ALIVE=-1"
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

| Setting | Meaning |
|---|---|
| `CUDA_VISIBLE_DEVICES=0,1` | use both GPU 0 and 1 |
| `OLLAMA_HOST=127.0.0.1:11434` | API reachable only locally (see security section) |
| `OLLAMA_CONTEXT_LENGTH=65536` | 64K default context (see 2-6) |
| `OLLAMA_NUM_PARALLEL=1` | one concurrent request to save VRAM |
| `OLLAMA_MAX_LOADED_MODELS=1` | one model resident at a time |
| `OLLAMA_FLASH_ATTENTION=1` | reduces long-context memory use |
| `OLLAMA_KV_CACHE_TYPE=q8_0` | 8-bit KV cache — roughly half of f16 (see 2-7) |
| `OLLAMA_KEEP_ALIVE=-1` | keep the model resident on the GPUs |

`OLLAMA_KEEP_ALIVE=-1` may not suit a server that shares GPUs with other workloads. Change it to something like `30m` if needed.

---

# [06] Pulling the Model and Verifying the Two-GPU Split

```bash
ollama pull qwen3.5:35b-a3b   # ~24GB — takes a while depending on network and disk
ollama list                   # confirm installation
ollama run qwen3.5:35b-a3b
```

A Korean smoke test:

```text
앞으로 모든 설명은 자연스러운 한국어로 작성해줘.
코드, 함수명, 명령어, API 이름은 원문을 유지해줘.
Kubernetes Controller가 무엇인지 초보자에게 설명해줘.
```

(Exit with `/bye`.) While it generates, watch both GPUs from another terminal.

```bash
watch -n 1 nvidia-smi   # VRAM and utilization should rise on GPU 0 and 1
ollama ps
```

What to check in `ollama ps`:

- `PROCESSOR` shows GPU usage
- `CONTEXT` is near 65536
- No excessive CPU/GPU mixed offload

If only one GPU is used, Ollama may have decided the model plus context fits on one card — which can be normal. The real problem is VRAM exhaustion or CPU offload at 64K. In that case work through: ① stop other GPU processes → ② restart Ollama → ③ confirm `CUDA_VISIBLE_DEVICES=0,1` is applied → ④ check `journalctl -e -u ollama` → ⑤ re-check `nvidia-smi` during generation.

Finally, verify the OpenAI-compatible API.

```bash
curl http://127.0.0.1:11434/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen3.5:35b-a3b",
    "messages": [
      { "role": "user", "content": "한국어로 한 문장만 답해줘. 로컬 LLM 연결 시험이야." }
    ]
  }'
```

A JSON response with a Korean answer means you're ready to connect OpenCode.

---

# [07] Installing and Connecting OpenCode

```bash
curl -fsSL https://opencode.ai/install | bash
source ~/.bashrc
opencode --version
```

One config file completes the connection.

```bash
mkdir -p ~/.config/opencode
cat > ~/.config/opencode/opencode.jsonc <<'EOF'
{
  "$schema": "https://opencode.ai/config.json",

  "model": "ollama/qwen3.5:35b-a3b",
  "small_model": "ollama/qwen3.5:35b-a3b",

  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama Local - A30 x2",
      "options": {
        "baseURL": "http://127.0.0.1:11434/v1"
      },
      "models": {
        "qwen3.5:35b-a3b": {
          "name": "Qwen3.5 35B-A3B Q4 - Local A30 x2",
          "limit": {
            "context": 65536,
            "output": 8192
          }
        }
      }
    }
  }
}
EOF
```

- No API key. Requests only go to the local Ollama at `127.0.0.1`
- `small_model` is the slot OpenCode uses for lightweight jobs like session titles. It's pinned to the same local model so no external provider is ever touched
- The config schema can change between OpenCode versions. On errors, check the schema at `https://opencode.ai/config.json` first

Run it inside the Git project you'll work on:

```bash
cd /path/to/your/project
opencode
```

```text
/models   # confirm "Ollama Local - A30 x2 / Qwen3.5 35B-A3B Q4" is selected
/init     # analyze the project and generate AGENTS.md
```

---

# [08] AGENTS.md: Locking In Korean Output Quality

`AGENTS.md` holds the working rules the AI agent follows in that project: which language to answer in, build and test commands, files it must not touch, approval rules for dangerous commands, and the report format. The key benefit: you stop repeating "answer in Korean" in every conversation.

Place this at the project root:

```markdown
# Project AI Working Rules

## Response language
- Write explanations, plans, progress, and reports in Korean.
- Keep code, variable/function names, API names, and CLI commands in their original form.
- Keep technical terms that lose meaning in translation in English, explaining them in Korean on first appearance.

## Working style
- On any request, inspect the relevant files and current implementation first.
- Present a short plan of what will change before changing it.
- Don't modify an unnecessarily large number of files at once.
- Never invent APIs from guesswork; check the repository's actual code and docs.

## Verification
- After edits, run build, lint, and unit tests where possible.
- On failure, explain the cause in Korean, fix, and rerun.
- If tests couldn't run, state why and which commands are needed.

## Safety
- Never auto-run dangerous commands: rm -rf, disk formatting, git push --force.
- Ask for approval before operationally impactful Kubernetes commands: delete, drain, cordon.
- Never print or commit .env files, certificates, private keys, or tokens.

## Reporting
- Summarize in Korean: files changed / key changes / tests run and results / remaining risks.
```

If answers start mixing Korean and English, check this file's language rules and start a fresh session. Some English remaining while the model reads English library docs or error logs is normal.

---

# [09] Operations — Workflow and OOM Response

## 9-1. Plan First, Build Later

OpenCode has two working modes. **Plan** investigates the project, finds relevant files, and writes a change plan — file edits are restricted. **Build** does the actual edits, code generation, shell commands, builds, and tests. Local models make more mistakes than large commercial ones, so this ordering matters even more here.

```text
Investigate with Plan → human reviews the plan → implement with Build → test → human reviews git diff
```

How you phrase requests also drives the success rate. Bad versus good:

```text
Bad:  Fix this.

Good: This repository is a Kubernetes Operator project.
      Check the current status.conditions update logic.
      Find the relevant files first, explain the current behavior in Korean,
      then write only an edit plan. Don't change any files yet.
```

Not handing over huge tasks at once follows the same logic. Not "build the whole system" but "step 1: review only the CRD type definitions → step 2: implement only the Validate logic → step 3: add unit tests." Local models succeed far more often when work is sliced into small steps.

And always pair it with Git. Branch before working — `git switch -c ai/test-local-opencode` — so even if OpenCode edits something badly, `git diff` shows it and you can roll back.

## 9-2. When OOM Hits, Adjust in This Order

OOM means Out Of Memory — the GPU ran out. Start with the changes that cost the least quality.

```text
Step 1  check and stop other GPU processes via nvidia-smi
Step 2  OLLAMA_CONTEXT_LENGTH=49152 (shrink to 48K)
Step 3  OLLAMA_CONTEXT_LENGTH=32768 (shrink to 32K)
Step 4  OLLAMA_KV_CACHE_TYPE=q4_0   (last resort — quality may degrade)
```

After shrinking the context, match `limit.context` in the OpenCode config to the same value. Down at 32K, large projects can run out of context — split unrelated conversations into new sessions and don't have it read too many files at once.

## 9-3. CPU Offload and Slow First Responses

If `ollama ps` shows a CPU/GPU mix instead of 100% GPU, part of the model has spilled to system RAM (CPU offload). Causes: oversized context, other processes holding VRAM, multiple models loaded, or too many parallel requests. It still works, but token generation slows dramatically — the priority is pushing it back onto the GPUs via parallel=1, one model, and a smaller context.

A slow first response isn't a fault — it's loading time:

```text
read model file → allocate GPU memory → split across two GPUs → create KV cache → first token
```

With `OLLAMA_KEEP_ALIVE=-1`, subsequent requests skip most of that cost.

---

# [10] Security

- **API binding**: keep `OLLAMA_HOST=127.0.0.1:11434`. Binding `0.0.0.0:11434` lets anyone on the network reach the model API without authentication
- **Remote use**: if a laptop's OpenCode needs the server's Ollama, don't open the port — tunnel it: `ssh -L 11434:127.0.0.1:11434 user@server`, then connect the laptop to `http://127.0.0.1:11434/v1`
- **Run as**: OpenCode executes shell commands and edits files, so run it as a regular user, never root
- **Kubernetes permissions**: give OpenCode a least-privilege kubeconfig — dev namespaces only, mostly read-only, no delete. Never the production cluster-admin kubeconfig
- **Secrets**: block printing/committing `.env`, kubeconfig, SSH/TLS private keys, API tokens, cloud credentials, and DB passwords via AGENTS.md rules

---

# [11] Common Problems

| Symptom | Check |
|---|---|
| Model missing in OpenCode | Model ID in `opencode.jsonc` must exactly match the name from `curl http://127.0.0.1:11434/api/tags` (`qwen3.5:35b-a3b`) |
| Connection refused | `sudo systemctl status ollama` → `journalctl -e -u ollama` |
| Answers but can't call file-edit tools | Latest OpenCode/Ollama, official model tag, Build agent selected, context not too small, AGENTS.md not over-restricting tool use |
| Quality drops in long conversations | New session per feature. Rules live in AGENTS.md, not chat. Commit finished work and hand over a short status to the next session |
| Two GPUs but not much faster | Normal for a no-NVLink split (see 2-10). The win is a bigger model + longer context + no CPU offload, not speed |

---

# [12] Next Steps — Model Comparison and Per-GPU Split

Once the environment is stable, comparing Korean quality on real work is worth the time. EXAONE 4.0 32B's official GGUF Q4_K_M is about 19.3GB.

```bash
ollama stop qwen3.5:35b-a3b
ollama run hf.co/LGAI-EXAONE/EXAONE-4.0-32B-GGUF:Q4_K_M
```

Evaluate with actual tasks, not model-card scores:

| Axis | Test |
|---|---|
| Korean comprehension | Does it drop conditions from long requirements? |
| Korean expression | Awkward translationese or unnecessary English mixing? |
| Code editing | Multi-file edits succeeding in a real repository? |
| Tool calling | Success rate on file/shell/test tool calls |
| Error recovery | Does it fix itself from failing test logs? |
| Speed/memory | Time to first token; GPU load behavior at 32K/48K/64K |

Once comfortable, a per-GPU dual-model setup is also possible:

```text
A30 #0 └─ EXAONE 4.0 32B Q4      → Korean requirements analysis, docs, review
A30 #1 └─ Qwen3-Coder 30B-A3B Q4 → code implementation, tests
```

The upside: the two models are independent, so there's almost no inter-GPU traffic, and the Korean model and coding model split roles cleanly. The costs: running two Ollama servers, fitting model + KV cache into 24GB per GPU (start contexts at 24K–32K), and more complex provider config. Start with the baseline — one Qwen3.5 split across both cards — and try this afterward.

Eight operating principles to close:

1. Never blindly trust a local model's output
2. Always review the commands OpenCode ran and the files it changed
3. Never hand it production cluster permissions
4. Slice features into small tasks
5. Manage project rules in AGENTS.md
6. Split overly long sessions into new ones
7. Evaluate model performance on real work tasks
8. Without NVLink, two GPUs buy memory, not speed

---

## References

- [OpenCode docs](https://opencode.ai/docs/) · [Providers](https://opencode.ai/docs/providers/) · [Config](https://opencode.ai/docs/config/) · [Agents](https://opencode.ai/docs/agents/)
- [Ollama × OpenCode integration](https://docs.ollama.com/integrations/opencode) · [Linux install](https://docs.ollama.com/linux) · [Context Length](https://docs.ollama.com/context-length) · [FAQ (multi-GPU, Flash Attention, KV Cache)](https://docs.ollama.com/faq)
- [Qwen3.5 35B-A3B model card](https://huggingface.co/Qwen/Qwen3.5-35B-A3B) · [Ollama release](https://ollama.com/library/qwen3.5:35b-a3b) · [Qwen3-Coder 30B-A3B](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct)
- [EXAONE 4.0 32B](https://huggingface.co/LGAI-EXAONE/EXAONE-4.0-32B) · [Official GGUF](https://huggingface.co/LGAI-EXAONE/EXAONE-4.0-32B-GGUF) · [Kanana-2 30B-A3B](https://huggingface.co/kakaocorp/kanana-2-30b-a3b-instruct)
- [NVIDIA A30 datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/products/a30-gpu/pdf/a30-datasheet.pdf)

---

*Environment: Ubuntu 22.04 / NVIDIA A30 24GB × 2 (no NVLink) / Ollama / OpenCode. Docs and model tags are as of 2026-07-30; re-verify the OpenCode config schema and Ollama's Hugging Face GGUF support against the versions at install time.*
