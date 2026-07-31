---
title: "Ollama 멀티GPU 운영·트러블슈팅: 100% CPU, 드라이버 550, 모델 저장 경로"
description: "Ollama가 GPU를 두고도 CPU로 도는 원인 진단(NVIDIA 드라이버 550 미만), ollama ps의 100% CPU와 분할 표기 구분, 모델 저장 경로를 데이터 디스크로 옮기는 절차, OOM 단계별 대응과 CPU offload 판별까지 운영 중 만나는 문제 정리"
excerpt: "설치는 정상인데 nvidia-smi도 멀쩡한데 CPU로 돈다. 로그 한 줄로 원인을 가르는 방법과, 루트 파일시스템이 모델로 차기 전에 해둘 일"
date: 2026-07-31
categories: Etc
tags: [Ollama, 멀티GPU, 트러블슈팅, NVIDIA-드라이버, CUDA, OOM, VRAM, 로컬LLM, A30, OLLAMA_MODELS]
ref: ollama-multi-gpu-troubleshooting
---

> **로컬 LLM 코딩 에이전트 시리즈**
> ① [로컬 LLM 입문 개념](/etc/local-llm-gpu-vram-concepts/) · ② [Ollama 로컬 LLM 구축 가이드](/etc/opencode-korean-local-llm-a30x2/) · ③ **운영·트러블슈팅편**(현재 글) · ④ [AI 코드 리뷰 자동화](/etc/opencode-dual-model-review-loop/)
{: .notice--primary}

:bulb: Ollama를 올린 뒤 실제로 막히는 지점을 모았다. 가장 자주 만나는 것은 **설치도 드라이버도 정상인데 모델이 CPU로 도는** 경우다. `nvidia-smi`가 멀쩡하고 CUDA 버전까지 보이기 때문에 원인을 찾기 어렵다. 로그 한 줄로 이걸 가르는 방법부터, 루트 파일시스템이 모델로 차기 전에 해둘 일까지 순서대로 정리했다.
{: .notice--info}

이 글이 다루는 증상:

```text
ollama ps 가 100% CPU        → [01] 드라이버 버전 문제. 컨텍스트 축소는 무효
루트 파일시스템 용량 부족      → [02] 모델 저장 경로 이전
OOM / VRAM 부족              → [03] 단계별 축소 순서
CPU/GPU 혼합 표기, 첫 응답 지연 → [04] CPU offload 판별
```

---

# [01] 드라이버 550 미만 — 조용히 CPU로 떨어지는 함정

가장 먼저 확인할 것. **최신 Ollama의 CUDA 런너는 NVIDIA 드라이버 550 이상을 요구한다.** 535 같은 구버전이면 Ollama가 GPU를 발견하고도 후보에서 제외한 뒤, 오류 없이 CPU로 실행한다. 설치는 전부 정상이고 `nvidia-smi`도 멀쩡해서 원인을 찾기 어렵다.

증상은 `ollama ps`의 `PROCESSOR` 열에 나타난다.

```text
NAME               SIZE     PROCESSOR    CONTEXT
qwen3.5:35b-a3b    24 GB    100% CPU     65536
```

여기서 중요한 구분이 있다. VRAM이 모자라 일부만 올라간 경우라면 `35%/65% CPU/GPU`처럼 **분할로 표기**된다. 딱 `100% CPU`는 **쓸 수 있는 GPU를 하나도 찾지 못했다**는 뜻이다. 즉 컨텍스트를 줄여도 해결되지 않는다.

확진은 로그 한 줄이다.

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

`inference compute` 줄이 `library=cuda`로 GPU 개수만큼 나와야 정상이다. `id=cpu` 하나뿐이고 `total_vram="0 B"`면 확정이다.

> `grep` 패턴에 `compat`를 넣으면 모델 적재 시 쏟아지는 `compat tensor transform` 로그 수천 줄에 묻혀 정작 시작 시점의 GPU 탐색 라인을 놓친다. 위처럼 먼저 걸러낸다.
{: .notice--warning}

해결은 드라이버 상향뿐이다. `LD_LIBRARY_PATH=/usr/local/cuda/lib64` 추가를 권하는 글이 많지만 이 증상에는 무효다. Ollama는 CUDA Toolkit이 아니라 `/usr/local/lib/ollama/cuda_v12`의 번들 런타임을 쓰고, 외부에서 가져오는 `libcuda.so.1`은 이미 ldconfig 기본 경로에 있다. `ldconfig -p | grep libcuda` 로 확인된다면 그 설정은 붙여도 아무 변화가 없다.

```bash
apt-cache search 'nvidia-driver-5[5-9][0-9]-server' | sort
sudo apt install -y nvidia-driver-570-server   # A30은 데이터센터용 -server 브랜치
sudo reboot
```

Kubernetes 워커 노드라면 먼저 비우고 진행한다. NVIDIA GPU Operator가 드라이버를 관리하는 노드면 호스트에 직접 설치하지 말고 Operator의 드라이버 버전을 올려야 한다.

```bash
kubectl get pods -A -o wide | grep -iE "nvidia|gpu" | grep <노드명>   # driver-daemonset 있는지
kubectl cordon <노드명>
kubectl drain <노드명> --ignore-daemonsets --delete-emptydir-data
```

운영 제약으로 드라이버를 올릴 수 없다면 대안은 Ollama를 구버전으로 고정하는 것 하나뿐이다(`OLLAMA_VERSION=<버전> sh`). 다만 신규 모델 지원이 계속 빠지므로 권하지 않는다.

요구 드라이버 버전은 Ollama 버전마다 달라진다. 이 글은 **Ollama 0.32.5 기준 550 이상**이며, 설치 시점의 릴리스 노트를 확인하는 것이 정확하다.
---

# [02] 모델 저장 위치를 데이터 디스크로

Ollama의 기본 모델 경로는 `/usr/share/ollama/.ollama/models`, 즉 루트 파일시스템이다. 코딩 에이전트용 모델 하나가 20GB 안팎이고 비교용으로 몇 개만 더 받아도 루트가 찬다. 모델을 받기 전에 저장 위치부터 옮긴다.

먼저 디스크 구성을 본다.

```bash
lsblk
df -h /
```

루트와 별도로 큰 디스크가 붙어 있는 구성이라면 그쪽에 둔다.

```text
NAME                      SIZE MOUNTPOINTS
sda                     446.1G
├─sda1                      1G /boot/efi
├─sda2                      2G /boot
└─sda3                  443.1G
  └─ubuntu--vg-ubuntu--lv 443G /
sdb                       3.6T /data
```

루트 443G에 모델을 쌓는 대신 3.6T짜리 `/data`를 쓴다. 모델 파일 크기는 이 정도다.

| 모델 | 대략 크기 |
|---|---|
| Qwen3.5 35B-A3B Q4_K_M | 24GB |
| Qwen3-Coder 30B-A3B Q4_K_M | 19GB |
| EXAONE 4.0 32B Q4_K_M | 19.3GB |

세 개만 비교해도 60GB를 넘고, 양자화 변형까지 받으면 금방 100GB대가 된다.

**① 마운트가 재부팅 후에도 유지되는지 확인**

```bash
findmnt /data
grep -E "\s/data\s" /etc/fstab
```

`fstab`에 항목이 없으면 재부팅 후 `/data`가 붙지 않는다. 그 상태로 Ollama가 뜨면 빈 디렉터리를 보고 **모델이 전부 사라진 것처럼 동작한다.** UUID로 등록해 둔다.

```bash
sudo blkid /dev/sdb
echo 'UUID=<확인한-UUID>  /data  ext4  defaults  0  2' | sudo tee -a /etc/fstab
sudo mount -a
```

**② 디렉터리 생성과 소유권**

```bash
sudo mkdir -p /data/ollama/models
sudo chown -R ollama:ollama /data/ollama
```

소유권이 `ollama`가 아니면 서비스가 시작 직후 실패한다. Ollama는 `User=ollama`로 동작한다.

**③ 이미 받은 모델 이동**

받은 모델이 없다면 건너뛴다. 이미 루트에 받아 둔 뒤라도 늦지 않다. 다시 받을 필요 없이 그대로 옮긴다.

먼저 **받는 중이라면 끝날 때까지 기다린다.** 진행 중인 `ollama pull`이나 `ollama create`를 중단하면 완료되지 않은 blob이 남고, 경로를 옮긴 뒤 처음부터 다시 받게 될 수 있다.

이전 전에 목록을 남겨 두고 여유 공간을 확인한다.

```bash
ollama list          # 이전 후 비교용. 이름과 ID를 기록해 둔다
du -sh /usr/share/ollama/.ollama/models
df -h /data          # 위 크기보다 여유가 큰지
```

서비스를 멈추고 복사한다. 실행 중에 복사하면 적재 중인 파일이 어긋날 수 있다.

```bash
sudo systemctl stop ollama
sudo mkdir -p /data/ollama/models
sudo rsync -a /usr/share/ollama/.ollama/models/ /data/ollama/models/
sudo chown -R ollama:ollama /data/ollama
```

`rsync -a`는 `blobs/`의 가중치와 `manifests/`의 모델 정의를 함께 옮긴다. 따라서 **`ollama create`로 만든 파생 모델도 같이 따라오고, Modelfile을 다시 실행할 필요가 없다.** 파생 모델은 원본 blob을 참조만 하므로 복사량이 두 배가 되지도 않는다.

`mv` 대신 `rsync`를 쓰는 이유는 원본을 남겨 두기 위해서다. ⑤에서 정상 동작을 확인한 뒤에 지운다.

**④ systemd에 경로 지정**

[구축편의 systemd override](/etc/opencode-korean-local-llm-a30x2/)에 이미 포함된 항목이다. 없다면 `sudo systemctl edit ollama`로 추가한다.

```ini
Environment="OLLAMA_MODELS=/data/ollama/models"
```

```bash
sudo systemctl daemon-reload
sudo systemctl start ollama
```

**⑤ 확인 후 원본 삭제**

```bash
ollama list          # ③에서 기록한 목록과 이름·ID가 모두 일치해야 한다
ollama ps            # 모델 적재가 되는지
df -h / /data        # 이후 증가분이 /data 쪽에 잡히는지
```

목록이 일치하고 새 모델 pull까지 성공한 뒤에 원본을 지운다. 하나라도 빠졌다면 지우지 말고 `rsync`를 다시 실행한다.

```bash
sudo rm -rf /usr/share/ollama/.ollama/models
```

심볼릭 링크로 대체하는 방법도 있지만, 환경변수 쪽이 설정 파일에 드러나서 나중에 원인을 찾기 쉽다.
---

# [03] OOM이 나면 이 순서로

OOM은 `Out Of Memory`, 즉 GPU 메모리 부족이다. 발생하면 품질 손실이 작은 것부터 조정한다.

```text
1단계  nvidia-smi로 다른 GPU 프로세스 확인·종료
2단계  OLLAMA_CONTEXT_LENGTH=49152 (48K로 축소)
3단계  OLLAMA_CONTEXT_LENGTH=32768 (32K로 축소)
4단계  OLLAMA_KV_CACHE_TYPE=q4_0   (마지막 수단 — 품질 저하 가능)
```

컨텍스트를 줄였으면 OpenCode 설정의 `limit.context`도 같은 값으로 맞춘다. 32K까지 내리면 긴 프로젝트에서 컨텍스트 부족이 생길 수 있으므로, 불필요한 대화를 새 세션으로 분리하고 한 번에 너무 많은 파일을 읽히지 않는다.

# [04] CPU offload와 첫 응답 지연

`ollama ps`에서 GPU 100%가 아니라 CPU/GPU 혼합으로 보이면 모델 일부가 시스템 RAM으로 내려간 것이다(CPU offload). 원인은 컨텍스트 과대, 다른 프로세스의 VRAM 점유, 동시 다중 모델 적재, 병렬 요청 수다. 동작은 하지만 토큰 생성이 크게 느려지므로, 병렬 1·모델 1 설정과 컨텍스트 축소로 GPU 안에 다시 밀어 넣는 게 우선이다.

첫 응답이 느린 건 고장이 아니라 적재 시간이다.

```text
모델 파일 읽기 → GPU 메모리 할당 → 두 GPU에 분산 → KV Cache 생성 → 첫 토큰 생성
```

`OLLAMA_KEEP_ALIVE=-1`이면 이후 요청부터는 이 시간이 줄어든다.
---

# [05] 자주 만나는 문제

| 증상 | 확인 |
|---|---|
| `ollama ps`가 `100% CPU` | VRAM 부족이 아니라 GPU 미채택. 컨텍스트 축소는 무효다. `journalctl -u ollama \| grep -i "driver too old"` 확인 후 드라이버가 550 미만이면 상향 ([01] 참고) |
| Connection refused | `sudo systemctl status ollama` → `journalctl -e -u ollama` |
| 재부팅 후 모델이 전부 사라짐 | `OLLAMA_MODELS`가 가리키는 디스크가 마운트되지 않았을 가능성. `findmnt /data`와 `/etc/fstab` 확인 ([02] ① 참고) |
| `ollama create`에서 `pull model manifest: file does not exist` | `FROM`에 적은 태그가 레지스트리에 없음. 모델 페이지의 Tags 탭에서 실제 태그 확인 후 `ollama pull`로 먼저 받기 |
| 서비스가 시작 직후 죽음 | `OLLAMA_MODELS` 경로의 소유자가 `ollama`가 아닐 가능성 ([02] ② 참고) |
| CPU/GPU 혼합 표기 | CPU offload. 컨텍스트 과대, 다른 프로세스의 VRAM 점유, 동시 다중 모델 적재 ([04] 참고) |
| 두 GPU인데 생각보다 안 빠름 | NVLink 없는 분산의 정상 특성. 멀티 GPU의 이득은 속도가 아니라 큰 모델 + 긴 컨텍스트 + CPU offload 방지 ([개념편 2-10](/etc/local-llm-gpu-vram-concepts/) 참고) |

---

## 참고 자료

- [Ollama FAQ (멀티 GPU·Flash Attention·KV Cache)](https://docs.ollama.com/faq) · [Linux 설치](https://docs.ollama.com/linux) · [Context Length](https://docs.ollama.com/context-length)
- [Ollama 릴리스 노트](https://github.com/ollama/ollama/releases) — 요구 드라이버 버전 변경 확인
- [NVIDIA 드라이버 아카이브](https://www.nvidia.com/en-us/drivers/unix/) · [A30 데이터시트](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/products/a30-gpu/pdf/a30-datasheet.pdf)
- 시리즈: ① [개념편](/etc/local-llm-gpu-vram-concepts/) · ② [구축편](/etc/opencode-korean-local-llm-a30x2/) · ④ [AI 코드 리뷰 자동화](/etc/opencode-dual-model-review-loop/)

---

*환경: Ubuntu 22.04 / NVIDIA A30 24GB × 2 (NVLink 미사용) / Ollama 0.32.5. 2026-07-31 기준이며, 요구 드라이버 버전과 로그 문구는 Ollama 버전에 따라 달라진다.*
