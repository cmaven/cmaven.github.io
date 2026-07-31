---
title: "Ollama Multi-GPU Operations & Troubleshooting: 100% CPU, Driver 550, Model Storage Paths"
description: "Diagnosing why Ollama runs on CPU despite having GPUs (NVIDIA driver below 550), telling ollama ps's 100% CPU apart from a partial split, moving model storage to a data disk, and staged OOM response with CPU offload detection — the problems that show up once Ollama is running"
excerpt: "The install looks fine, nvidia-smi looks fine, and it still runs on CPU. One log line tells you why — plus what to do before the root filesystem fills up with models"
date: 2026-07-31
categories: Etc
tags: [Ollama, multi-GPU, troubleshooting, NVIDIA-driver, CUDA, OOM, VRAM, local-LLM, A30, OLLAMA_MODELS]
ref: ollama-multi-gpu-troubleshooting
---

> **Local LLM Coding Agent series**
> ① [Local LLM Core Concepts](/en/etc/local-llm-gpu-vram-concepts/) · ② [Ollama Local LLM Setup Guide](/en/etc/opencode-korean-local-llm-a30x2/) · ③ **Ollama Multi-GPU Operations & Troubleshooting** (this post) · ④ [AI Code Review with Two Local LLMs](/en/etc/opencode-dual-model-review-loop/)
{: .notice--primary}

:bulb: The problems that actually show up once Ollama is running. The most common one: **the install is fine, the driver looks fine, and the model still runs on CPU.** `nvidia-smi` looks healthy and even reports a CUDA version, which makes the cause hard to pin down. This post covers how one log line settles that question, through to what to do before the root filesystem fills up with models.
{: .notice--info}

Symptoms this post covers:

```text
ollama ps shows 100% CPU                    → [01] driver version issue. Shrinking context won't help
Root filesystem running out                 → [02] moving model storage
OOM / VRAM exhaustion                       → [03] staged reduction order
CPU/GPU mixed display, slow first response  → [04] detecting CPU offload
```

---

# [01] Driver below 550 — the trap that silently falls back to CPU

Check this first. **Recent Ollama CUDA runners require NVIDIA driver 550 or newer.** On an older driver such as 535, Ollama discovers the GPUs, drops them from the candidate list, and runs on CPU without raising an error. Every part of the install looks fine and `nvidia-smi` is perfectly healthy, which makes this hard to pin down.

The symptom shows up in the `PROCESSOR` column of `ollama ps`.

```text
NAME               SIZE     PROCESSOR    CONTEXT
qwen3.5:35b-a3b    24 GB    100% CPU     65536
```

The distinction matters here. If VRAM were merely too small, the model would load partially and be reported as a **split** like `35%/65% CPU/GPU`. A flat `100% CPU` means **no usable GPU was found at all** — so shrinking the context will not fix it.

One log line confirms it.

```bash
sudo systemctl restart ollama
sleep 5
sudo journalctl -u ollama --since "2 min ago" --no-pager \
  | grep -viE "compat tensor transform" \
  | grep -iE "inference compute|driver too old"
```

```text
WARN source=cuda_compat.go:65 msg="NVIDIA driver too old"
    device="NVIDIA A30" compute=8.0 driver=535 required_driver="550 or newer"
INFO source=types.go:50 msg="inference compute" id=cpu library=cpu ... total="754.6 GiB"
INFO msg="vram-based default context" total_vram="0 B" default_num_ctx=4096
```

A healthy system prints one `inference compute` line per GPU with `library=cuda`. A single `id=cpu` line plus `total_vram="0 B"` is the confirmation.

> If your `grep` pattern includes `compat`, the thousands of `compat tensor transform` lines emitted during model load will bury the GPU-discovery lines from startup. Filter them out first, as above.
{: .notice--warning}

The only fix is a newer driver. Plenty of write-ups suggest adding `LD_LIBRARY_PATH=/usr/local/cuda/lib64`, but it does nothing for this symptom: Ollama uses its own bundled runtime under `/usr/local/lib/ollama/cuda_v12` rather than the CUDA Toolkit, and the one library it does borrow — `libcuda.so.1` — already sits in the default ldconfig path. If `ldconfig -p | grep libcuda` finds it, that setting changes nothing.

```bash
apt-cache search 'nvidia-driver-5[5-9][0-9]-server' | sort
sudo apt install -y nvidia-driver-570-server   # A30 is a data center GPU — use the -server branch
sudo reboot
```

On a Kubernetes worker, drain the node first. If the NVIDIA GPU Operator manages the driver on that node, raise the Operator's driver version instead of installing on the host.

```bash
kubectl get pods -A -o wide | grep -iE "nvidia|gpu" | grep <node>   # look for driver-daemonset
kubectl cordon <node>
kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
```

If operational constraints rule out a driver upgrade, the only alternative is pinning Ollama to an older release (`OLLAMA_VERSION=<version> sh`) — not recommended, since support for new models keeps moving forward.

The required driver version changes with each Ollama release. This article reflects **Ollama 0.32.5, which requires 550 or newer**; check the release notes for the version you install.

---

# [02] Move model storage to the data disk

Ollama's default model path is `/usr/share/ollama/.ollama/models` — on the root filesystem. The model used in this guide is around 20GB, and pulling a couple more for comparison fills root. Move the storage location before pulling anything.

Start with the disk layout:

```bash
lsblk
df -h /
```

If a large disk is mounted separately from root, put the models there.

```text
NAME                      SIZE MOUNTPOINTS
sda                     446.1G
├─sda1                      1G /boot/efi
├─sda2                      2G /boot
└─sda3                  443.1G
  └─ubuntu--vg-ubuntu--lv 443G /
sdb                       3.6T /data
```

Use the 3.6T `/data` rather than stacking models on the 443G root. Model sizes run like this:

| Model | Approximate size |
|---|---|
| Qwen3.5 35B-A3B Q4_K_M | 24GB |
| Qwen3-Coder 30B-A3B Q4_K_M | 19GB |
| EXAONE 4.0 32B Q4_K_M | 19.3GB |

Three models alone exceed 60GB, and adding quantization variants reaches the hundreds of GB quickly.

**① Confirm the mount survives a reboot**

```bash
findmnt /data
grep -E "\s/data\s" /etc/fstab
```

With no `fstab` entry, `/data` won't mount after a reboot. Ollama then starts against an empty directory and **behaves as though every model vanished.** Register it by UUID:

```bash
sudo blkid /dev/sdb
echo 'UUID=<the-uuid-you-found>  /data  ext4  defaults  0  2' | sudo tee -a /etc/fstab
sudo mount -a
```

**② Create the directory and set ownership**

```bash
sudo mkdir -p /data/ollama/models
sudo chown -R ollama:ollama /data/ollama
```

If `ollama` doesn't own it, the service fails immediately on start — it runs as `User=ollama`.

**③ Move models you already pulled**

Skip this if you haven't pulled anything yet. If models are already sitting on root, nothing is lost — move them instead of re-downloading.

First, **if a download is running, let it finish.** Interrupting an `ollama pull` or `ollama create` leaves incomplete blobs behind, and after relocating the path you may end up pulling from the start again.

Record the list and check free space before copying.

```bash
ollama list          # for comparison afterward; note the names and IDs
du -sh /usr/share/ollama/.ollama/models
df -h /data          # more free space than the size above
```

Stop the service before copying — copying while a model is loaded can produce a torn file.

```bash
sudo systemctl stop ollama
sudo mkdir -p /data/ollama/models
sudo rsync -a /usr/share/ollama/.ollama/models/ /data/ollama/models/
sudo chown -R ollama:ollama /data/ollama
```

`rsync -a` carries both the weights under `blobs/` and the model definitions under `manifests/`. **Models derived with `ollama create` come along too — there's no need to re-run the Modelfile.** Derived models only reference the original blobs, so the copy doesn't double in size either.

`rsync` rather than `mv` keeps the original in place until step ⑤ confirms everything works.

**④ Point systemd at the new path**

Already included in [the Setup Guide's systemd override](/en/etc/opencode-korean-local-llm-a30x2/).

```ini
Environment="OLLAMA_MODELS=/data/ollama/models"
```

```bash
sudo systemctl daemon-reload
sudo systemctl start ollama
```

**⑤ Verify, then delete the original**

```bash
ollama list          # names and IDs must match the list recorded in ③
ollama ps            # models still load
df -h / /data        # further growth now lands on /data
```

Delete the original only after the list matches and a fresh pull succeeds. If anything is missing, leave it alone and re-run the `rsync`.

```bash
sudo rm -rf /usr/share/ollama/.ollama/models
```

A symlink works too, but the environment variable is visible in the service config, which makes it easier to trace later.

---

# [03] When OOM Hits, Adjust in This Order

OOM means Out Of Memory — the GPU ran out. Start with the changes that cost the least quality.

```text
Step 1  check and stop other GPU processes via nvidia-smi
Step 2  OLLAMA_CONTEXT_LENGTH=49152 (shrink to 48K)
Step 3  OLLAMA_CONTEXT_LENGTH=32768 (shrink to 32K)
Step 4  OLLAMA_KV_CACHE_TYPE=q4_0   (last resort — quality may degrade)
```

After shrinking the context, match `limit.context` in the OpenCode config to the same value. Down at 32K, large projects can run out of context — split unrelated conversations into new sessions and don't have it read too many files at once.

---

# [04] CPU Offload and Slow First Responses

If `ollama ps` shows a CPU/GPU mix instead of 100% GPU, part of the model has spilled to system RAM (CPU offload). Causes: oversized context, other processes holding VRAM, multiple models loaded, or too many parallel requests. It still works, but token generation slows dramatically — the priority is pushing it back onto the GPUs via parallel=1, one model, and a smaller context.

A slow first response isn't a fault — it's loading time:

```text
read model file → allocate GPU memory → split across two GPUs → create KV cache → first token
```

With `OLLAMA_KEEP_ALIVE=-1`, subsequent requests skip most of that cost.

---

# [05] Common Problems

| Symptom | Check |
|---|---|
| `ollama ps` shows `100% CPU` | Not a VRAM shortage — no GPU was accepted. Shrinking context won't help. Check `journalctl -u ollama \| grep -i "driver too old"` and upgrade if the driver is below 550 (see [01]) |
| Connection refused | `sudo systemctl status ollama` → `journalctl -e -u ollama` |
| All models gone after reboot | The disk `OLLAMA_MODELS` points to may not be mounted. Check `findmnt /data` and `/etc/fstab` (see [02] ①) |
| `ollama create` fails with `pull model manifest: file does not exist` | The tag in `FROM` doesn't exist in the registry. Check the real tag on the model page's Tags tab, then `ollama pull` it first |
| Service dies right after starting | The `OLLAMA_MODELS` path may not be owned by `ollama` (see [02] ②) |
| CPU/GPU mixed display | CPU offload. Oversized context, other processes holding VRAM, or multiple models loaded at once (see [04]) |
| Two GPUs but not much faster | Normal for a no-NVLink split. The multi-GPU win is a bigger model + longer context + no CPU offload, not speed (see [Core Concepts 2-10](/en/etc/local-llm-gpu-vram-concepts/)) |

---

## References

- [Ollama FAQ (multi-GPU, Flash Attention, KV Cache)](https://docs.ollama.com/faq) · [Linux install](https://docs.ollama.com/linux) · [Context Length](https://docs.ollama.com/context-length)
- [Ollama release notes](https://github.com/ollama/ollama/releases) — check for driver-requirement changes
- [NVIDIA driver archive](https://www.nvidia.com/en-us/drivers/unix/) · [A30 datasheet](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/products/a30-gpu/pdf/a30-datasheet.pdf)
- Series: ① [Core Concepts](/en/etc/local-llm-gpu-vram-concepts/) · ② [Setup Guide](/en/etc/opencode-korean-local-llm-a30x2/) · ④ [AI Code Review with Two Local LLMs](/en/etc/opencode-dual-model-review-loop/)

---

*Environment: Ubuntu 22.04 / NVIDIA A30 24GB × 2 (no NVLink) / Ollama 0.32.5. Documentation current as of 2026-07-31; required driver versions and log wording change between Ollama releases.*
