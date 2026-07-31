---
title: "A Build–Review–Apply Loop with Two Local LLMs — OpenCode Subagents on Two A30s"
description: "Pinning Qwen3-Coder and EXAONE to one A30 24GB each and using OpenCode's primary/subagent split to separate the implementing model from the reviewing model. Per-model num_ctx, why the reviewer must lose edit permission, and the round cap that stops infinite ping-pong"
excerpt: "A model reviewing its own code misses its own mistakes. Keep two models from different families resident on one GPU each, and the author is no longer the reviewer"
date: 2026-07-31
categories: Etc
tags: [OpenCode, Ollama, local-LLM, multi-agent, subagent, code-review, Qwen3-Coder, EXAONE, A30, multi-GPU, AI-coding-agent]
ref: opencode-dual-model-review-loop
---

:bulb: A follow-up to [Building a Korean-Language Local LLM Setup for OpenCode on Two A30s](/en/Etc/opencode-korean-local-llm-a30x2/). That post spread a single model across both GPUs to reach a 64K context. This one does the opposite: **one model per GPU, so the implementing model and the reviewing model are different models.** OpenCode's primary/subagent structure turns that into a loop where A implements, B reviews, and A applies.
{: .notice--info}

The end state:

```text
User
  │ task in plain language
  ▼
OpenCode
  ├─ primary agent  "build"     ──▶ Qwen3-Coder 30B-A3B  ──▶ A30 #0
  │    edits files, runs commands, runs tests
  │
  └─ subagent       "reviewer"  ──▶ EXAONE 4.0 32B       ──▶ A30 #1
       read and git diff only, no edit permission
```

| | Previous post | This post |
|---|---|---|
| Models | 1 | 2 |
| GPU layout | one model split across both cards | one model per card |
| Context | 65,536 | split per model (32K implement / 16K review to start) |
| Inter-GPU traffic | goes over PCIe | almost none |
| `OLLAMA_MAX_LOADED_MODELS` | 1 | 2 |

---

# [01] Where self-review breaks down

Ask a model to review the code it just wrote and it will usually pass it. The same probability distribution that produced the code is doing the reviewing, so whatever the model got wrong while generating, it gets wrong again while checking. A missing error path stays invisible; a misremembered API signature still looks correct.

Shared context compounds this. When the model's own code is already sitting in its context, review becomes a search for improvements *within that code's assumptions*. The possibility that the assumptions themselves are wrong never enters the search.

A reviewer from a different model family changes both conditions. Different training data and tokenizer mean the failure distributions don't overlap, and a separate context means the reviewer sees the code only as an artifact.

What this does not fix is equally clear. If both models believe the same wrong fact, the review passes. A 30B-class local model is not a substitute for human review — the correct place for this loop is as **a first-pass filter before a human reads `git diff`**.

---

# [02] Splitting the roles

The previous post picked Qwen3.5 35B-A3B on a "one model does everything" criterion. With two models the criterion changes: each role needs different strengths, so neither model has to be average at both.

| Role | Needs | Choice | Why |
|---|---|---|---|
| A. Implement | tool-calling reliability, repo-scale edits, running tests | Qwen3-Coder 30B-A3B Q4_K_M | shipped for coding-agent and repository work |
| B. Review | precision of written critique, requirement cross-checking | EXAONE 4.0 32B Q4_K_M | strong on Korean domain knowledge and phrasing, official GGUF |

The drawbacks listed in the previous post's comparison table stop mattering here. Qwen3-Coder's weaker general prose doesn't matter because EXAONE writes the critique, and EXAONE's tight context budget doesn't matter because it only reads a diff.

**Picking two models from the same family removes the reason for the setup.** Pairing Qwen3-Coder with Qwen3.5 gives you a reviewer that overlooks the implementer's kind of mistake. Prefer a different lineage.

The VRAM layout:

```text
A30 #0 24GB ├─ Qwen3-Coder 30B-A3B Q4_K_M  ~18.6GB
            └─ KV cache + runtime            ~5GB

A30 #1 24GB ├─ EXAONE 4.0 32B Q4_K_M        ~19.3GB
            └─ KV cache + runtime            ~4GB
```

Ollama's documented placement rule is to load a model entirely onto one GPU and to spread it only when it doesn't fit. Both models fit inside 24GB, so **one lands on each card without any device pinning.** That is the same reason the previous post dropped `CUDA_VISIBLE_DEVICES`, and it still applies.

---

# [03] Ollama — keeping both models resident

## 3-1. systemd changes

Two values change from the previous post.

```bash
sudo systemctl edit ollama
```

```ini
[Service]
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_CONTEXT_LENGTH=16384"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_LOADED_MODELS=2"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
Environment="OLLAMA_KEEP_ALIVE=-1"
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

| Change | Previous | Here | Reason |
|---|---|---|---|
| `OLLAMA_MAX_LOADED_MODELS` | 1 | 2 | both models must stay resident or every round pays a reload |
| `OLLAMA_CONTEXT_LENGTH` | 65536 | 16384 | keep the global default low; raise per model in 3-2 |

Per the Ollama docs the default for `OLLAMA_MAX_LOADED_MODELS` is `3 × number of GPUs`, so two models load without setting anything. The value only needs attention if you pinned it to `1` following the previous post — leave it there and Ollama evicts one model to load the other on every single request.

`OLLAMA_KEEP_ALIVE=-1` is mandatory rather than optional in this setup. Loading nearly 38GB across two models is not a cost you want to pay per round. The flip side is that all 48GB of GPU memory stays committed to Ollama, so if the same server also runs training or other inference, this layout is the wrong one.

## 3-2. Per-model context

`OLLAMA_CONTEXT_LENGTH` is a server-wide setting, and the OpenAI-compatible endpoint has no `num_ctx` parameter. To give each role a different context, **bake the parameter into a derived model with a Modelfile.**

The implementer holds several source files plus test output, so it needs the room:

```bash
cat > /tmp/coder.Modelfile <<'EOF'
FROM qwen3-coder:30b-a3b
PARAMETER num_ctx 32768
EOF

ollama create coder-32k -f /tmp/coder.Modelfile
```

The reviewer reads a diff and a requirement, so it doesn't:

```bash
cat > /tmp/reviewer.Modelfile <<'EOF'
FROM hf.co/LGAI-EXAONE/EXAONE-4.0-32B-GGUF:Q4_K_M
PARAMETER num_ctx 16384
EOF

ollama create reviewer-16k -f /tmp/reviewer.Modelfile
```

The asymmetry is the practical gain. Give both models 32K and VRAM runs out; give the reviewer 16K and the implementer gets to keep 32K.

Those numbers are starting points. Measure the real ceiling:

```bash
ollama run coder-32k "test"      # just load it, then /bye
ollama run reviewer-16k "test"
ollama ps
nvidia-smi
```

Success looks like `PROCESSOR` reading GPU for both models and `nvidia-smi` showing roughly 20GB on each of GPU 0 and 1. If either falls back to a CPU split, lower `num_ctx` and `ollama create` again. If both models pile onto one card, one `num_ctx` is large enough that Ollama gave up on the clean placement — adjust the same way.

> `100% CPU` is not a context problem, it's a driver problem. See 5-1 of the previous post.
{: .notice--warning}

## 3-3. When placement has to be pinned

Ollama's automatic placement depends on load order and free memory. If you need a specific model on a specific card, **run two Ollama instances and give each one GPU.**

```ini
# /etc/systemd/system/ollama-reviewer.service
[Unit]
Description=Ollama Service (reviewer, GPU1)
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ollama
Group=ollama
Restart=always
Environment="CUDA_VISIBLE_DEVICES=1"
Environment="OLLAMA_HOST=127.0.0.1:11435"
Environment="OLLAMA_CONTEXT_LENGTH=16384"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
Environment="OLLAMA_KEEP_ALIVE=-1"

[Install]
WantedBy=default.target
```

Give the original `ollama.service` `CUDA_VISIBLE_DEVICES=0` and let both instances share the same model directory (`/usr/share/ollama/.ollama/models`). Because `OLLAMA_CONTEXT_LENGTH` is now per-instance, the Modelfile work in 3-2 becomes unnecessary.

The cost is two of everything: two ports, two units, two log streams, and a second provider in the OpenCode config. Start with 3-1 and move here only if placement actually drifts.

---

# [04] OpenCode — primary and subagent

## 4-1. Registering both models

With the single instance from 3-1, one provider carries both models.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",

  "model": "ollama/coder-32k",
  "small_model": "ollama/coder-32k",

  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama Local - A30 x2",
      "options": {
        "baseURL": "http://127.0.0.1:11434/v1"
      },
      "models": {
        "coder-32k": {
          "name": "Qwen3-Coder 30B-A3B - implement",
          "limit": { "context": 32768, "output": 8192 }
        },
        "reviewer-16k": {
          "name": "EXAONE 4.0 32B - review",
          "limit": { "context": 16384, "output": 4096 }
        }
      }
    }
  }
}
```

Keep `limit.context` equal to the `num_ctx` set in 3-2. If they disagree, OpenCode builds requests past the server's limit and Ollama truncates from the front.

With the two-instance layout from 3-3, add a second provider with the other `baseURL` and point the agent below at `ollama-reviewer/...`.

## 4-2. Defining the agents

OpenCode agents differ by `mode`. A `primary` agent is one the user talks to directly; a `subagent` is invoked by a primary agent or called by hand with `@name`.

Define the reviewer as a markdown file — the filename becomes the agent name.

```bash
mkdir -p ~/.config/opencode/agents
```

```markdown
<!-- ~/.config/opencode/agents/reviewer.md -->
---
description: Reviews implemented changes and reports problems. Does not modify code.
mode: subagent
model: ollama/reviewer-16k
temperature: 0.1
permission:
  edit: deny
  write: deny
  webfetch: deny
  bash:
    "git diff*": allow
    "git show*": allow
    "git status*": allow
    "*": deny
---

You are a code reviewer. You never modify code directly.

## Procedure
1. Run `git diff` to see what changed.
2. Read the surrounding code in the changed files for context.
3. Compare against the stated requirement and find omissions and errors.

## Finding format
For each finding, state:
- Severity: critical / major / minor / suggestion
- Location: file path and line
- Problem: one sentence on what is wrong
- Evidence: why it is wrong. If you are guessing, say so
- Fix direction: the concrete change. Do not rewrite the whole file

## Prohibited
- Never pass something with "looks good" and no evidence.
- If there are no problems, answer only "No findings." Do not pad with praise.
- Never classify a style preference as critical or major.
- Report problems in unchanged files as a separate section.
```

`permission` is the load-bearing part. **Leave `edit` and `write` open and the reviewer starts fixing the code itself, which dissolves the author/reviewer separation the whole setup exists for.** Restricting `bash` to the `git diff` family leaves exactly the access review needs.

The implementing agent is the stock `build` agent with the model overridden.

```jsonc
{
  "agent": {
    "build": {
      "model": "ollama/coder-32k"
    }
  }
}
```

Check registration with `/agents`.

---

# [05] Running the loop

## 5-1. Three steps

One round is implement, review, apply.

```text
① implement  build(A)      make the change, run tests, do NOT commit
② review     @reviewer(B)  read git diff, report findings by severity
③ apply      build(A)      apply accepted findings, re-run tests
④ gate       human         read git diff, then commit
```

**① Implement**

```text
Add a Ready condition to this repo's status.conditions update logic.
First check how the existing conditions are handled and follow the same pattern.
After the change, run the related unit tests and report the result.
Do not commit.
```

Blocking the commit matters: the reviewer reads `git diff`, which needs the changes still sitting in the working tree.

**② Review**

```text
@reviewer Review what just changed.
The requirement was: "add a Ready condition to status.conditions, following the existing condition pattern."
```

Calling `@reviewer` runs the subagent in its own context and returns the result into the session. You can let the primary agent invoke it automatically through the `task` tool, but then it's hard to control when review happens. Manual invocation is the better default.

**③ Apply**

```text
Apply only the "critical" and "major" findings.
For "minor" and "suggestion", tell me whether you accept or reject each and why — don't touch the code.
Re-run the tests afterward.
```

Not applying everything is the point. Findings from a 30B local model include false positives, and applying those makes the code worse. Filter by severity and take only a judgment on the rest.

## 5-2. Cap the rounds

**Stop at two rounds.** Without a cap the two models trade responses indefinitely: the reviewer is prompted to find something every time, and the implementer tries to apply it every time, so the loop has no natural fixed point.

```text
Round 1: implement → review → apply    most real problems surface here
Round 2: re-review → apply             only checks whether round 1 introduced new problems
Round 3+                               human steps in; the requirement itself is ambiguous
```

If critical and major findings keep appearing in round 2, splitting the requirement is faster than another round. The task-decomposition principle from 9-1 of the previous post applies unchanged.

## 5-3. The human gate

Read `git diff` before committing. Two models agreeing means they did not share a misunderstanding — not that the code is correct.

```bash
git switch -c ai/two-model-loop
# run the loop
git diff
git add <files>
```

---

# [06] Failure modes

| Symptom | Cause | Response |
|---|---|---|
| Reviewer only says "looks good overall" | no finding format or prohibitions in the prompt | use the severity format and the "no praise" rule from 4-2; keep `temperature` near 0.1 |
| Reviewer edits code | `permission.edit` is open | confirm `edit: deny` and `write: deny` |
| Reviewer can't see the diff | `bash` fully denied, or the change was already committed | allow `git diff*`; don't commit during the implement step |
| Tens of seconds of lag each round | model swapping | check both models appear in `ollama ps`; re-check `MAX_LOADED_MODELS` and `KEEP_ALIVE` |
| Findings drift to unrelated files | no review scope in the prompt | pass the requirement with the call; keep the "unchanged files as a separate section" rule |
| Three or more rounds | ambiguous requirement | stop per 5-2 and split the task |
| Tests break after applying | false-positive findings were applied | filter by severity; keep the 5-1 ③ prompt shape |

The first row is the one you will hit most. A short reviewer prompt pushes the model toward generating an inoffensive summary. It is not excessive for format-enforcing instructions to take up half the prompt.

---

# [07] Verification

Four things to check:

```bash
# 1. Both models resident, on different GPUs
ollama ps
nvidia-smi

# 2. The reviewer actually uses model B
sudo journalctl -u ollama -f      # look for reviewer-16k requests during an @reviewer call

# 3. The reviewer cannot use edit tools
#    Tell @reviewer "edit this file directly" — it must refuse

# 4. No swapping
#    After two rounds, UNTIL still reads Forever in ollama ps and responses stay fast
```

Do check number 3 at least once. If `permission` never took effect, the reviewer quietly edits code, and that edit is the one change nobody reviewed.

---

# [08] What this post did not verify

This setup makes concrete the per-GPU split floated as a next step in section [12] of the previous post. The following is written from documentation and was not measured on this server.

- **VRAM figures and context ceilings.** 18.6GB and 19.3GB are distribution sizes; actual occupancy with KV cache, and whether 32K/16K fit in 24GB, has to be measured with the procedure in 3-2. These are starting values, not verified limits.
- **Where the two models land.** One-per-card is the expected outcome of Ollama's documented placement rule. If load order changes it, pin with 3-3.
- **Review quality.** How much of Qwen3-Coder's error surface EXAONE actually catches depends on the repository and the kind of work. The comparison method in section [12] of the previous post — 10 to 20 real tasks — is the only basis for judging it.
- **OpenCode config schema.** The `agent`, `mode`, and `permission` keys follow the OpenCode docs and change between versions. On an error, check the `https://opencode.ai/config.json` schema first.

---

## References

- [OpenCode Agents](https://opencode.ai/docs/agents/) · [Config](https://opencode.ai/docs/config/) · [Providers](https://opencode.ai/docs/providers/)
- [Ollama FAQ (concurrent models, multi-GPU placement)](https://docs.ollama.com/faq) · [Modelfile](https://docs.ollama.com/modelfile) · [Context Length](https://docs.ollama.com/context-length)
- [Qwen3-Coder 30B-A3B](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct) · [EXAONE 4.0 32B GGUF](https://huggingface.co/LGAI-EXAONE/EXAONE-4.0-32B-GGUF)
- Previous post: [Building a Korean-Language Local LLM Setup for OpenCode on Two A30s](/en/Etc/opencode-korean-local-llm-a30x2/)

---

*Environment: Ubuntu 22.04 / NVIDIA A30 24GB × 2 (no NVLink) / Ollama / OpenCode. Documentation current as of 2026-07-31; the items listed in [08] were not measured on this server.*
