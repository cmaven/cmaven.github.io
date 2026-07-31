---
title: "Local LLM Core Concepts: VRAM, Quantization, KV Cache, and MoE Explained"
description: "Everything you need to know before running a local LLM, gathered in one place: what separates an LLM from an agent harness, what VRAM is used for, how to read quantization tags like Q4_K_M, tokens and context length, why the KV cache grows, MoE's A3B notation, tool calling, and multi-GPU without NVLink"
excerpt: "The terms that trip people up before their first local LLM install, explained before you touch a config file. Once you know VRAM, quantization, KV cache, and MoE, every tuning doc after this one reads itself"
date: 2026-07-31
categories: Etc
tags: [local-LLM, LLM, VRAM, quantization, KV-Cache, MoE, GPU, context-length, tool-calling, Ollama, OpenCode, A30]
ref: local-llm-gpu-vram-concepts
---

> **Local LLM Coding Agent series**
> ① **Local LLM Core Concepts** (this post) · ② [Ollama Local LLM Setup Guide](/en/etc/opencode-korean-local-llm-a30x2/) · ③ [Ollama Multi-GPU Operations & Troubleshooting](/en/etc/ollama-multi-gpu-troubleshooting/) · ④ [AI Code Review with Two Local LLMs](/en/etc/opencode-dual-model-review-loop/)
{: .notice--primary}

:bulb: Most guides to running a local LLM start with a setting like `OLLAMA_KV_CACHE_TYPE=q8_0`. If you don't know what that value actually changes, you won't know what to adjust when something breaks. This post collects only the concepts you need before typing an install command. Read through it once, and every setup and tuning post after this one will read itself.
{: .notice--info}

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

Increasing context also increases VRAM use. That trade-off returns in [the Ops & Troubleshooting post's OOM section](/en/etc/ollama-multi-gpu-troubleshooting/) as an actual tuning step.

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

Even if a model's Korean is excellent, unstable tool calling means OpenCode can't actually get work done. That's why an OpenCode model must be judged on Korean ability and tool-calling ability together — the criterion that carries into [the Setup Guide's model selection](/en/etc/opencode-korean-local-llm-a30x2/).

## 2-10. Is It Unusable Without NVLink?

It's usable. But splitting one model across two GPUs routes inter-GPU data over PCIe, which has less bandwidth than NVLink, so you may see:

- Lower token generation speed
- Longer first-response latency
- Two GPUs not translating into exactly 2× speed

The goal of this setup isn't doubling speed — it's **running a model and context too big for one card, stably, split across two**. Think of it as buying memory, not speed.

---

# [03] From Concepts to Settings

Here's how each concept maps to an actual setting:

| Concept | Setting | Effect of tuning it |
|---|---|---|
| Context Length (2-6) | `OLLAMA_CONTEXT_LENGTH` | Raising it enables longer tasks and increases VRAM use |
| KV Cache (2-7) | `OLLAMA_KV_CACHE_TYPE` | `q8_0` is roughly half of `f16`, with a small quality loss |
| Quantization (2-4) | the `Q4_K_M` in the model tag | Lowering it shrinks VRAM use and hurts accuracy |
| VRAM (2-2) | model choice and GPU count | Running short triggers CPU offload and a big slowdown |
| MoE (2-8) | model choice | Reduces compute, but all the weights still load |

Plugging in actual values and loading a model onto two GPUs continues in ② [Ollama Local LLM Setup Guide](/en/etc/opencode-korean-local-llm-a30x2/). What to do when it shows `100% CPU` or runs out of VRAM after that is covered in ③ [Ollama Multi-GPU Operations & Troubleshooting](/en/etc/ollama-multi-gpu-troubleshooting/).

---

## References

- [Ollama Context Length](https://docs.ollama.com/context-length) · [FAQ (multi-GPU, Flash Attention, KV Cache)](https://docs.ollama.com/faq)
- [OpenCode docs](https://opencode.ai/docs/) · [Agents](https://opencode.ai/docs/agents/)
- [Qwen3.5 35B-A3B model card](https://huggingface.co/Qwen/Qwen3.5-35B-A3B) · [EXAONE 4.0 32B](https://huggingface.co/LGAI-EXAONE/EXAONE-4.0-32B)
- [NVIDIA A30 datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/products/a30-gpu/pdf/a30-datasheet.pdf)

---

*Documentation as of 2026-07-31. Model tags and Ollama settings change between versions — re-verify at install time.*
