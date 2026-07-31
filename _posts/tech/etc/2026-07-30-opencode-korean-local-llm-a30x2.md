---
title: "A30 두 장으로 OpenCode 한국어 로컬 LLM 환경 구축하기 — Ollama + Qwen3.5 35B-A3B"
description: "NVIDIA A30 24GB 두 장(NVLink 없음)에 Ollama와 Qwen3.5 35B-A3B Q4_K_M을 올려 OpenCode를 외부 API 없이 한국어로 쓰는 구성. LLM·VRAM·양자화·KV Cache·MoE 같은 초심자 개념 설명부터 systemd 튜닝, 64K 컨텍스트, OOM 단계별 대응, AGENTS.md 한국어 규칙까지 정리"
excerpt: "외부 API 키 없이 A30 두 장만으로 OpenCode를 한국어 코딩 에이전트로 쓴다. GPU·LLM을 처음 접해도 따라올 수 있게 개념부터 튜닝까지 순서대로"
date: 2026-07-30
categories: Etc
tags: [OpenCode, Ollama, 로컬LLM, Qwen3.5, A30, 멀티GPU, 양자화, KV-Cache, 컨텍스트, AGENTS.md, EXAONE, AI-coding-agent]
ref: opencode-korean-local-llm-a30x2
---

:bulb: 유료 API 없이 서버의 NVIDIA A30 24GB 두 장만으로 OpenCode를 한국어 코딩 에이전트로 쓰는 구성을 정리했다. 결론은 단순하다 — **Ollama에 Qwen3.5 35B-A3B Q4_K_M 하나를 올리고, 두 GPU에 분산해 64K 컨텍스트를 확보한다.** NVLink가 없어도 된다. GPU·LLM·OpenCode를 처음 접하는 사람도 따라올 수 있도록 개념 설명부터 systemd 튜닝, OOM 대응, 한국어 품질을 고정하는 AGENTS.md까지 실제 구축 순서대로 담았다.
{: .notice--info}

먼저 최종 구성부터.

```text
사용자
  │ 한국어로 작업 지시
  ▼
OpenCode
  │ 파일 읽기·수정, 명령 실행, 테스트
  ▼
Ollama의 OpenAI 호환 API (127.0.0.1:11434)
  │ 하나의 모델을 A30 두 장에 자동 분산
  ▼
Qwen3.5 35B-A3B Q4_K_M (약 24GB)
  ├─ A30 #0 24GB
  └─ A30 #1 24GB
```

- **비용**: 토큰당 API 비용 없음. 코드가 외부로 나가지 않아 폐쇄망에서도 동작
- **모델**: Qwen3.5 35B-A3B Q4_K_M — 한국어·코딩·도구 호출·장문 컨텍스트의 균형
- **컨텍스트**: 65,536 토큰. Ollama 공식 문서가 코딩 에이전트용으로 64K 이상을 권장한다
- **NVLink 없음**: 속도 2배가 목적이 아니라, 한 장에 안 들어가는 모델+컨텍스트를 두 장에 나눠 싣는 게 목적

---

# [01] 전체 그림 — LLM, OpenCode, 로컬 LLM, Ollama

설치 명령을 치기 전에, 등장인물 네 명이 각각 무슨 역할인지부터 잡고 가자.

## 1-1. LLM이란?

LLM은 `Large Language Model`, 즉 **대규모 언어 모델**의 약자다.

사용자가 문장을 입력하면 LLM은 다음에 올 가능성이 높은 토큰을 차례로 생성한다. 단순하게 보면 매우 발전된 자동완성처럼 보이지만, 충분히 학습된 모델은 다음 작업도 수행한다.

- 한국어 질문 이해 및 답변
- 프로그램 코드 작성
- 오류 로그 분석
- 문서 요약
- 작업 계획 수립
- 외부 도구 호출

다만 LLM 자체는 컴퓨터의 파일을 직접 수정하거나 명령을 실행하지 못한다. 이 역할을 OpenCode 같은 **에이전트 하네스(agent harness)**가 담당한다.

## 1-2. OpenCode란?

OpenCode는 터미널에서 실행하는 **AI 코딩 에이전트**다. 일반 채팅 서비스와 달리 사용자의 허용 범위 안에서 다음을 수행한다.

- 프로젝트 파일 목록 확인, 소스 코드 읽기
- 여러 파일 수정, `git diff` 확인
- 테스트 명령 실행, 빌드 오류 분석
- 오류를 수정한 뒤 다시 테스트
- 별도 조사용 서브에이전트 실행

LLM이 두뇌라면 OpenCode는 두뇌가 실제 개발 작업을 할 수 있도록 파일, 터미널, Git, 테스트 도구를 연결하는 실행 시스템이다.

```text
LLM만 사용     : 사용자 질문 → 답변 텍스트
OpenCode 사용  : 사용자 요청 → 계획 → 파일 확인 → 코드 수정 → 테스트 → 결과 보고
```

## 1-3. 로컬 LLM이란?

로컬 LLM은 OpenAI, Anthropic, OpenRouter 같은 외부 API 서버가 아니라 **내 서버의 GPU에서 직접 실행하는 모델**이다.

장점:

- 토큰당 API 비용이 없다
- 코드와 문서가 외부 모델 API로 전송되지 않는다
- 인터넷이 제한된 환경에서도 사용할 수 있다
- 모델과 실행 설정을 직접 통제할 수 있다

단점:

- GPU와 저장 공간이 필요하다
- 모델 설치와 운영을 직접 해야 한다
- Claude·GPT 같은 대형 상용 모델보다 성능이 낮을 수 있다
- 긴 컨텍스트를 쓰면 GPU 메모리가 많이 필요하다

## 1-4. Ollama란?

Ollama는 로컬 LLM을 쉽게 내려받고 실행하며 API로 제공하는 프로그램이다. 이 구성에서 Ollama의 위치는 이렇다.

```text
OpenCode
   │ HTTP 요청
   ▼
Ollama API 서버
   │ 모델 적재·GPU 사용·텍스트 생성
   ▼
A30 GPU 2장
```

OpenCode는 Ollama가 제공하는 **OpenAI 호환 API**에 연결된다. 여기서 "OpenAI 호환"은 OpenAI의 유료 모델을 사용한다는 뜻이 아니다. 요청과 응답의 형식을 OpenAI API와 비슷하게 맞췄다는 뜻이다.

## 1-5. Provider와 Model의 차이

OpenCode 화면에서 자주 보게 되는 용어다.

- **Provider**: 모델을 제공하는 서버 또는 연결 방식
- **Model**: 실제로 답변을 생성하는 LLM

이 구성에서는 `Provider = 로컬 Ollama 서버`, `Model = qwen3.5:35b-a3b`다. Zen, OpenRouter, Anthropic API를 연결하지 않아도 된다.

---

# [02] GPU와 메모리 필수 개념

이 절만 이해하면 뒤의 튜닝 절이 전부 읽힌다. 처음 접하는 용어가 많다면 여기서 시간을 쓰는 게 오히려 지름길이다.

## 2-1. A30은 어떤 GPU인가?

NVIDIA A30은 데이터센터용 Ampere GPU다.

- GPU 메모리: 24GB HBM2, 대역폭 933GB/s
- 인터페이스: PCIe Gen4, TDP 165W
- MIG 지원, 최대 두 장을 NVLink 브리지로 연결 가능
- 팬 없는 패시브 냉각 — 서버 섀시 풍량에 의존

이 글의 서버는 NVLink를 사용하지 않으므로 두 GPU 사이의 통신은 PCIe를 거친다.

## 2-2. VRAM이란?

VRAM은 GPU가 사용하는 전용 메모리다. LLM 실행 시 VRAM은 크게 다음에 쓰인다.

```text
GPU VRAM
├─ 모델 가중치
├─ KV Cache
├─ CUDA 실행 공간
└─ 입력·출력 처리용 임시 메모리
```

A30 두 장이 있다고 해서 자동으로 하나의 48GB GPU가 되는 것은 아니다. 프로그램이 모델을 두 GPU에 분산하도록 지원해야 한다. Ollama는 모델이 한 GPU에 완전히 들어가면 한 GPU에 적재하고, 완전히 들어가지 않으면 사용 가능한 여러 GPU에 나누어 적재한다.

## 2-3. 모델 가중치란?

모델이 학습한 지식과 동작 방식이 숫자 배열로 저장된 것을 **가중치(weights)**라고 한다. 모델 크기가 클수록 일반적으로 가중치 파일도 커진다.

이 글의 기본 모델은 Ollama 기준 약 24GB다. 그러나 24GB 모델을 24GB GPU에 그대로 넣을 수 있다고 단정하면 안 된다. 위에서 본 것처럼 실행 공간과 KV Cache가 추가로 필요하기 때문이다.

## 2-4. 양자화란?

양자화(quantization)는 모델 숫자의 정밀도를 낮춰 파일과 메모리 사용량을 줄이는 기술이다. 비유하면 원본 사진을 약간 압축해 파일 크기를 줄이는 것과 비슷하다.

대표적인 표기:

- `BF16`: 품질이 높지만 메모리를 많이 사용
- `Q8`: 8비트 양자화
- `Q5`: 5비트 계열 양자화
- `Q4_K_M`: 4비트 계열의 일반적인 균형형 양자화

이 글에서는 **Q4_K_M**을 사용한다. 30B급 모델을 A30 두 장에서 현실적으로 실행할 수 있고, BF16보다 훨씬 적은 VRAM으로 일반적인 코딩 작업에서 품질과 속도의 균형이 좋다. 대신 원본 모델보다 일부 정확도가 떨어질 수 있고, 어려운 추론이나 미세한 코드 판단에서 차이가 날 수 있다.

## 2-5. Token이란?

LLM은 문장을 글자 그대로 처리하지 않고 **토큰(token)**이라는 작은 단위로 나눈다. 토큰은 한 글자, 단어 일부, 기호, 코드 조각일 수 있다.

```text
입력: Kubernetes 컨트롤러의 오류를 분석해줘.
처리: 여러 개의 토큰으로 분할
```

토큰 수가 많을수록 모델이 읽어야 하는 정보와 메모리 사용량이 증가한다.

## 2-6. Context Length란?

Context Length는 모델이 한 번의 작업에서 기억하고 참고할 수 있는 최대 토큰 수다. OpenCode에서는 다음 내용이 모두 컨텍스트에 들어갈 수 있다.

- 사용자의 지시, 프로젝트 규칙
- 읽은 소스 코드, 이전 대화
- 명령 실행 결과, 오류 로그
- 도구 설명, 수정 계획

따라서 일반 채팅보다 훨씬 긴 컨텍스트가 필요하다. Ollama의 OpenCode 안내는 코딩 에이전트용 로컬 모델에 **64K 이상 컨텍스트**를 권장하며, 이 글도 65,536 토큰으로 시작한다.

```text
32K = 약 32,768 토큰
64K = 약 65,536 토큰
```

컨텍스트를 늘리면 VRAM 사용량도 증가한다. 이 트레이드오프가 뒤의 OOM 대응 절에서 다시 나온다.

## 2-7. KV Cache란?

KV Cache는 모델이 이미 읽은 문맥을 매번 처음부터 다시 계산하지 않도록 저장해 두는 메모리 영역이다. 컨텍스트가 길어질수록 KV Cache가 커진다.

```text
f16 KV Cache  = 품질 우선, 메모리 큼 (기본값)
q8_0 KV Cache = 메모리 약 절반, 품질 손실 매우 작음
q4_0 KV Cache = 더 작음, 품질 저하가 보일 수 있음
```

이 글에서는 `q8_0`로 설정해 기본 `f16`보다 메모리를 줄인다. 처음에는 `q8_0`을 권장한다.

## 2-8. MoE와 A3B란?

Qwen3.5 35B-A3B는 MoE(Mixture of Experts) 구조다.

- 전체 파라미터: 약 35B
- 한 토큰 처리 시 활성화되는 파라미터: 약 3B

`A3B`는 대략 **활성(Active) 파라미터가 3B**라는 의미로 이해하면 된다. MoE는 여러 전문가 모듈 중 필요한 일부만 선택해 계산한다. 계산량을 줄이는 데 도움이 되지만, 모든 전문가 가중치는 메모리에 적재해야 하므로 모델 파일 자체가 3B 모델만큼 작아지는 것은 아니다.

## 2-9. Tool Calling이란?

Tool Calling은 모델이 단순히 텍스트만 답하는 것이 아니라, 정해진 형식으로 외부 기능 실행을 요청하는 능력이다. OpenCode에서의 도구 예:

- 파일 읽기·수정·검색
- Shell 명령 실행
- 테스트 실행
- 서브에이전트 호출

모델이 한국어를 잘해도 Tool Calling이 불안정하면 OpenCode가 실제 작업을 제대로 수행하지 못한다. 그래서 OpenCode용 모델은 한국어 능력과 도구 호출 능력을 함께 봐야 한다. 이 기준이 다음 절의 모델 선정으로 이어진다.

## 2-10. NVLink가 없으면 사용할 수 없는가?

사용 가능하다. 다만 하나의 모델을 두 GPU에 분산하면 GPU 사이의 데이터가 PCIe를 통해 이동한다. NVLink가 있을 때보다 통신 대역폭이 낮으므로 다음 현상이 있을 수 있다.

- 토큰 생성 속도가 낮아질 수 있음
- 첫 응답 지연이 커질 수 있음
- GPU 두 장을 쓴다고 속도가 정확히 두 배가 되지 않음

이 구성의 목표는 속도를 두 배로 만드는 것이 아니라, **한 장에 넣기 어려운 모델과 긴 컨텍스트를 두 장에 나누어 안정적으로 실행하는 것**이다. 속도가 아니라 메모리를 사는 구성이라고 이해하면 된다.

---

# [03] 모델 선정 — 한국어만 잘해서는 안 된다

2-9에서 본 것처럼 OpenCode용 모델은 한국어 자연스러움만이 아니라 **도구 호출 안정성**이 핵심이다. 선정 우선순위는 이렇게 잡았다.

```text
1. OpenCode 도구 호출 안정성
2. 코딩 및 저장소 단위 작업 능력
3. 한국어 지시 이해와 한국어 결과 작성
4. A30 2장에서의 실행 가능성
5. 설치와 유지관리 난이도
```

이 기준으로 후보를 비교하면:

| 모델 | 장점 | 단점 | 권장 용도 |
|---|---|---|---|
| **Qwen3.5 35B-A3B Q4** | 한국어·코딩·도구 호출·장문 컨텍스트 균형, Ollama 공식 배포 | 두 GPU 분산 시 PCIe 통신 오버헤드 | **기본 메인 모델** |
| Qwen3-Coder 30B-A3B Q4 | 코딩 에이전트·저장소 작업에 강함 | 일반 한국어 문장 품질은 한국어 특화 모델보다 낮을 수 있음 | 코딩 품질 최우선 |
| EXAONE 4.0 32B Q4 | 한국어 전문 지식·표현에 강함, 공식 GGUF 제공 | 가중치 19.3GB라 A30 한 장에선 긴 컨텍스트가 빡빡함 | 한국어 계획·문서·리뷰 |
| Kanana-2 30B-A3B | 한국어 토크나이저, 한국어 에이전트 성능 강조 | 기본 컨텍스트 32K, 공식 Ollama 경로가 단순하지 않음 | 고급 비교 실험 |

Qwen3.5 35B-A3B를 기본으로 삼은 이유:

- 한국어를 포함한 201개 언어·방언을 지원하고 다국어 이해가 좋다
- 일반 대화 모델이면서 코딩·도구 호출·에이전트 작업을 함께 지원한다
- Ollama에 공식 배포된 Q4_K_M이 약 24GB, Apache 2.0 라이선스
- A30 한 장에는 가중치+긴 컨텍스트가 빡듯하지만, 두 장이면 64K 컨텍스트를 목표로 구성할 수 있다
- 모델 하나만 연결하면 되므로 초심자가 운영하기 가장 단순하다

EXAONE·Kanana를 기본으로 정하지 않은 이유도 같다. 한국어 자연스러움은 강력한 후보지만, 이 구성의 병목은 한국어가 아니라 도구 호출과 긴 컨텍스트다. "한국어를 가장 잘하는 모델"을 객관적으로 하나로 단정하기도 어렵다 — 한국어 자연스러움, 전문 지식, 코딩, 도구 호출, 양자화 후 성능의 평가 기준이 서로 다르기 때문이다. 먼저 Qwen3.5로 전체 환경을 안정화한 뒤, 실제 업무 작업 10~20개로 EXAONE·Kanana와 비교하는 순서를 권한다(마지막 절 참고).

---

# [04] 하드웨어 준비

| 항목 | 값 |
|---|---|
| GPU | NVIDIA A30 24GB × 2 (NVLink 없어도 가능) |
| 시스템 RAM | 최소 64GB, 권장 128GB 이상 |
| 저장 공간 | 최소 100GB 여유, 모델 비교 시 200GB 이상 |
| 전원·냉각 | GPU만 최대 165W × 2, 패시브 냉각이라 서버 풍량 필수 |
| OS | Ubuntu 22.04 계열 |

GPU 외에 시스템 RAM이 필요한 이유: 모델 파일 로딩, OpenCode 실행, Git·빌드·테스트, 컨테이너·Kubernetes 도구, 그리고 VRAM 부족 시 CPU offload가 전부 일반 메모리를 쓴다. CPU offload는 실행 가능성을 높이지만 속도가 크게 느려지므로 정상 구성에서는 피하는 것이 좋다.

## 4-1. GPU 두 장 인식 확인

```bash
nvidia-smi -L
# GPU 0: NVIDIA A30 (...)
# GPU 1: NVIDIA A30 (...)

nvidia-smi          # 전체 상태
nvidia-smi topo -m  # NVLink 없으면 PCIe 경로로 표시됨 — 오류 아님
```

`nvidia-smi`가 동작하더라도 **Driver Version이 550 이상인지** 함께 확인한다. 최신 Ollama의 CUDA 런너가 550 이상을 요구하고, 그 미만이면 GPU가 멀쩡해도 CPU로 실행된다(5-1 참고). 드라이버가 없거나 버전이 낮은 서버에서:

```bash
sudo apt update
ubuntu-drivers devices
sudo ubuntu-drivers install
sudo reboot
```

서버가 Kubernetes 노드이거나 NVIDIA GPU Operator로 드라이버를 관리한다면, OS에 직접 설치하기 전에 기존 구성과 충돌하지 않는지 먼저 확인한다.

## 4-2. MIG 비활성화

A30은 MIG(GPU를 여러 조각으로 나누는 기능)를 지원하지만, 이 구성은 두 GPU의 전체 24GB를 쓴다.

```bash
nvidia-smi -q | grep -A 2 "MIG Mode"

# 활성화돼 있다면 유지보수 시간에
sudo nvidia-smi -i 0 -mig 0
sudo nvidia-smi -i 1 -mig 0
sudo reboot
```

MIG 변경은 GPU 사용 중에는 실패할 수 있다. 해당 GPU를 사용하는 프로세스, 컨테이너, Kubernetes Pod를 먼저 종료하고, 운영 서버에서는 영향 범위를 확인한 뒤 진행한다.

---

# [05] Ollama 설치와 튜닝

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama -v
sudo systemctl status ollama
```

핵심은 systemd override다. `sudo systemctl edit ollama`로 열고 다음을 넣는다.

```ini
[Service]
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

| 설정 | 의미 |
|---|---|
| `OLLAMA_HOST=127.0.0.1:11434` | 로컬에서만 API 접속 허용 (보안 절 참고) |
| `OLLAMA_CONTEXT_LENGTH=65536` | 기본 컨텍스트 64K (2-6 참고) |
| `OLLAMA_NUM_PARALLEL=1` | 동시 요청 1개로 VRAM 절약 |
| `OLLAMA_MAX_LOADED_MODELS=1` | 동시 적재 모델 1개 |
| `OLLAMA_FLASH_ATTENTION=1` | 긴 컨텍스트 메모리 사용량 감소 |
| `OLLAMA_KV_CACHE_TYPE=q8_0` | KV Cache 8비트 — f16 대비 약 절반 (2-7 참고) |
| `OLLAMA_KEEP_ALIVE=-1` | 모델을 내리지 않고 GPU에 상주 |

`OLLAMA_KEEP_ALIVE=-1`은 GPU를 다른 작업과 공유하는 서버에선 부적합할 수 있다. 필요하면 `30m`처럼 바꾼다.

`CUDA_VISIBLE_DEVICES`를 넣지 않은 것은 의도다. GPU가 두 장뿐이면 `0,1`은 아무것도 제한하지 않으면서 Ollama의 자동 탐색만 방해하고, 로그에도 경고가 남는다.

```text
WARN msg="user overrode visible devices" CUDA_VISIBLE_DEVICES=0,1
WARN msg="if GPUs are not correctly discovered, unset and try again"
```

GPU 일부만 Ollama에 할당해야 하는 서버에서만 명시한다.

## 5-1. 드라이버 550 미만 — 조용히 CPU로 떨어지는 함정

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

# [06] 모델 받기와 두 GPU 분산 확인

```bash
ollama pull qwen3.5:35b-a3b   # 약 24GB — 네트워크·디스크 속도에 따라 시간 소요
ollama list                   # 설치 확인
ollama run qwen3.5:35b-a3b
```

한국어 시험:

```text
앞으로 모든 설명은 자연스러운 한국어로 작성해줘.
코드, 함수명, 명령어, API 이름은 원문을 유지해줘.
Kubernetes Controller가 무엇인지 초보자에게 설명해줘.
```

(종료는 `/bye`.) 답변이 생성되는 동안 다른 터미널에서 GPU 두 장이 모두 쓰이는지 본다.

```bash
watch -n 1 nvidia-smi   # GPU 0·1 모두 VRAM·사용률이 올라가야 함
ollama ps
```

`ollama ps`에서 확인할 항목:

- `PROCESSOR`가 GPU 사용으로 표시되는가
- `CONTEXT`가 65536에 가깝게 표시되는가
- CPU와 GPU 혼합 offload가 과도하지 않은가

한 GPU만 쓰인다면 모델+컨텍스트가 한 장에 들어간다고 판단한 정상 동작일 수 있다. 문제는 64K에서 VRAM 부족이나 CPU offload가 생길 때다. 그때는 ① 다른 GPU 프로세스 종료 → ② Ollama 재시작 → ③ 로그의 `inference compute` 줄에 `library=cuda`가 나오는지 확인(5-1 참고) → ④ `journalctl -e -u ollama` 로그 → ⑤ 실행 중 `nvidia-smi` 재확인 순으로 본다.

`100% CPU`로 표시된다면 이 절이 아니라 5-1의 드라이버 문제다.

마지막으로 OpenAI 호환 API를 확인한다.

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

JSON 응답에 한국어 답변이 오면 OpenCode 연결 준비 끝.

---

# [07] OpenCode 설치와 연결

```bash
curl -fsSL https://opencode.ai/install | bash
source ~/.bashrc
opencode --version
```

설정 파일 하나면 연결된다.

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

- API 키는 입력하지 않는다. 요청은 `127.0.0.1`의 로컬 Ollama로만 간다
- `small_model`은 OpenCode가 세션 제목 생성 같은 가벼운 작업에 쓰는 별도 소형 모델 자리다. 외부 provider를 아예 안 쓰기 위해 이것도 같은 로컬 모델로 명시한다
- OpenCode 버전에 따라 설정 스키마가 다를 수 있다. 오류가 나면 `https://opencode.ai/config.json` 스키마를 먼저 확인한다

작업할 Git 프로젝트에서 실행하고 확인한다.

```bash
cd /path/to/your/project
opencode
```

```text
/models   # "Ollama Local - A30 x2 / Qwen3.5 35B-A3B Q4" 선택 확인
/init     # 프로젝트 분석 후 AGENTS.md 생성
```

---

# [08] 한국어 품질을 고정하는 AGENTS.md

`AGENTS.md`는 그 프로젝트에서 AI 에이전트가 따라야 할 작업 규칙 파일이다. 어떤 언어로 답할지, 빌드·테스트 명령, 수정하면 안 되는 파일, 위험 명령 승인 규칙, 결과 보고 형식을 적는다. 매 대화마다 "한국어로 답해줘"를 반복하지 않아도 된다는 게 핵심 장점이다.

프로젝트 루트에 이렇게 둔다.

```markdown
# 프로젝트 AI 작업 규칙

## 응답 언어
- 설명, 계획, 진행 상황, 결과 보고는 한국어로 작성한다.
- 코드, 변수명, 함수명, API 이름, CLI 명령은 원문을 유지한다.
- 번역하면 의미가 불분명해지는 기술 용어는 영문을 유지하고 처음 등장할 때 한국어로 설명한다.

## 작업 방식
- 요청을 받으면 먼저 관련 파일과 현재 구현을 확인한다.
- 변경 전에 무엇을 바꿀지 짧은 계획을 제시한다.
- 한 번에 불필요하게 많은 파일을 수정하지 않는다.
- 추측으로 API를 만들지 말고 저장소의 실제 코드와 문서를 확인한다.

## 검증
- 수정 후 가능한 범위에서 빌드, lint, 단위 테스트를 실행한다.
- 실패하면 원인을 한국어로 설명하고 수정 후 다시 실행한다.
- 테스트를 실행하지 못했다면 이유와 필요한 명령을 명확히 적는다.

## 안전
- rm -rf, 디스크 초기화, git push --force 등 위험 명령은 자동 실행하지 않는다.
- Kubernetes의 delete, drain, cordon 등 운영 영향 명령은 실행 전에 승인을 요청한다.
- .env, 인증서, 개인키, 토큰을 출력하거나 커밋하지 않는다.

## 결과 보고
- 변경한 파일 / 핵심 변경 내용 / 실행한 테스트와 결과 / 남은 위험을 한국어로 정리한다.
```

답변에 한국어·영어가 섞이면 이 파일의 응답 언어 규칙을 확인하고 새 세션에서 시작한다. 영문 라이브러리 문서나 오류 로그를 읽을 때 일부 영어가 남는 것은 정상이다.

---

# [09] 운영 — 작업 흐름과 OOM 대응

## 9-1. Plan 먼저, Build는 나중에

OpenCode에는 두 가지 작업 모드가 있다. **Plan**은 프로젝트 조사, 관련 파일 찾기, 변경 계획 작성까지만 하고 파일 수정은 제한된다. **Build**가 실제 파일 수정, 코드 생성, Shell 명령 실행, 빌드·테스트를 맡는다. 로컬 모델은 상용 대형 모델보다 실수가 잦으므로 이 순서가 특히 중요하다.

```text
Plan으로 조사 → 사람이 계획 검토 → Build로 구현 → 테스트 → 사람이 git diff 검토
```

요청 방식도 성공률을 좌우한다. 나쁜 요청과 좋은 요청:

```text
나쁨: 이거 고쳐줘.

좋음: 이 저장소는 Kubernetes Operator 프로젝트야.
      현재 status.conditions 갱신 로직을 확인해줘.
      먼저 관련 파일을 찾고 현재 동작을 한국어로 설명한 뒤,
      수정 계획만 작성해줘. 아직 파일은 변경하지 마.
```

한 번에 큰 작업을 주지 않는 것도 같은 맥락이다. "전체 시스템을 완성해줘"가 아니라 "1단계로 CRD 타입 정의만 검토해줘 → 2단계에서 Validate 로직만 구현해줘 → 3단계에서 단위 테스트 추가"처럼 쪼갠다. 로컬 모델은 작업을 작은 단계로 나눌수록 성공률이 올라간다.

그리고 Git을 반드시 함께 쓴다. 작업 전 `git switch -c ai/test-local-opencode`로 브랜치를 파 두면, OpenCode가 잘못 수정해도 `git diff`로 확인하고 되돌릴 수 있다.

## 9-2. OOM이 나면 이 순서로

OOM은 `Out Of Memory`, 즉 GPU 메모리 부족이다. 발생하면 품질 손실이 작은 것부터 조정한다.

```text
1단계  nvidia-smi로 다른 GPU 프로세스 확인·종료
2단계  OLLAMA_CONTEXT_LENGTH=49152 (48K로 축소)
3단계  OLLAMA_CONTEXT_LENGTH=32768 (32K로 축소)
4단계  OLLAMA_KV_CACHE_TYPE=q4_0   (마지막 수단 — 품질 저하 가능)
```

컨텍스트를 줄였으면 OpenCode 설정의 `limit.context`도 같은 값으로 맞춘다. 32K까지 내리면 긴 프로젝트에서 컨텍스트 부족이 생길 수 있으므로, 불필요한 대화를 새 세션으로 분리하고 한 번에 너무 많은 파일을 읽히지 않는다.

## 9-3. CPU offload와 첫 응답 지연

`ollama ps`에서 GPU 100%가 아니라 CPU/GPU 혼합으로 보이면 모델 일부가 시스템 RAM으로 내려간 것이다(CPU offload). 원인은 컨텍스트 과대, 다른 프로세스의 VRAM 점유, 동시 다중 모델 적재, 병렬 요청 수다. 동작은 하지만 토큰 생성이 크게 느려지므로, 병렬 1·모델 1 설정과 컨텍스트 축소로 GPU 안에 다시 밀어 넣는 게 우선이다.

첫 응답이 느린 건 고장이 아니라 적재 시간이다.

```text
모델 파일 읽기 → GPU 메모리 할당 → 두 GPU에 분산 → KV Cache 생성 → 첫 토큰 생성
```

`OLLAMA_KEEP_ALIVE=-1`이면 이후 요청부터는 이 시간이 줄어든다.

---

# [10] 보안

- **API 바인딩**: `OLLAMA_HOST=127.0.0.1:11434` 유지. `0.0.0.0:11434`로 열면 네트워크의 다른 사용자가 인증 없이 모델 API에 접근할 수 있다
- **원격 사용**: 노트북의 OpenCode가 서버 Ollama를 써야 하면 포트를 여는 대신 SSH 터널 — `ssh -L 11434:127.0.0.1:11434 user@server`. 이후 노트북은 `http://127.0.0.1:11434/v1`에 연결
- **실행 계정**: OpenCode는 Shell 명령과 파일 수정을 수행하므로 root가 아닌 일반 사용자로 실행
- **Kubernetes 권한**: OpenCode에 주는 kubeconfig는 개발 namespace 한정, 기본 읽기 전용, 삭제 권한 제외. 운영 cluster-admin kubeconfig 금지
- **비밀정보**: `.env`, kubeconfig, SSH/TLS private key, API token, cloud credential, DB password는 AGENTS.md 규칙으로 출력·커밋을 막는다

---

# [11] 자주 만나는 문제

| 증상 | 확인 |
|---|---|
| OpenCode에 모델이 안 보임 | `opencode.jsonc`의 모델 ID와 `curl http://127.0.0.1:11434/api/tags`의 모델명이 정확히 같은지 (`qwen3.5:35b-a3b`) |
| Connection refused | `sudo systemctl status ollama` → `journalctl -e -u ollama` |
| 답은 하는데 파일 수정 도구를 못 씀 | OpenCode·Ollama 최신 버전, 공식 모델 태그, Build 에이전트인지, 컨텍스트가 너무 작지 않은지, AGENTS.md가 도구 사용을 과도하게 제한하지 않는지 |
| 대화가 길어지면 품질 저하 | 기능 단위로 새 세션. 규칙은 대화가 아니라 AGENTS.md에. 완료 작업은 commit으로 남기고 다음 세션에 짧게 인계 |
| `ollama ps`가 `100% CPU` | VRAM 부족이 아니라 GPU 미채택. 컨텍스트 축소는 무효다. `journalctl -u ollama \| grep -i "driver too old"` 로 확인하고 드라이버가 550 미만이면 상향 (5-1 참고) |
| 두 GPU인데 생각보다 안 빠름 | NVLink 없는 분산의 정상 특성(2-10 참고). 이 구성의 이득은 속도가 아니라 큰 모델 + 긴 컨텍스트 + CPU offload 방지 |

---

# [12] 다음 단계 — 모델 비교와 GPU 분리 운영

환경이 안정화되면 한국어 품질을 실제 업무로 비교해 볼 가치가 있다. EXAONE 4.0 32B는 공식 GGUF Q4_K_M이 약 19.3GB다.

```bash
ollama stop qwen3.5:35b-a3b
ollama run hf.co/LGAI-EXAONE/EXAONE-4.0-32B-GGUF:Q4_K_M
```

비교할 때는 모델 카드 점수가 아니라 실제 작업을 쓴다.

| 항목 | 시험 내용 |
|---|---|
| 한국어 이해 | 긴 요구사항에서 조건 누락 여부 |
| 한국어 표현 | 어색한 번역투와 불필요한 영어 혼용 여부 |
| 코드 수정 | 실제 저장소에서 여러 파일 수정 성공 여부 |
| 도구 호출 | 파일·Shell·테스트 도구 호출 성공률 |
| 오류 복구 | 실패 로그를 보고 스스로 수정하는지 |
| 속도·메모리 | 첫 토큰 시간, 32K·48K·64K에서 GPU 적재 상태 |

익숙해진 뒤에는 GPU별로 다른 모델을 올리는 구성도 가능하다.

```text
A30 #0 └─ EXAONE 4.0 32B Q4      → 한국어 요구사항 분석·문서·리뷰
A30 #1 └─ Qwen3-Coder 30B-A3B Q4 → 코드 구현·테스트
```

두 모델이 독립적이라 GPU 간 통신이 거의 없고, 한국어 모델과 코딩 모델의 역할을 나눌 수 있다. 대신 Ollama 서버 두 개 운영, GPU당 24GB 안에서 모델+KV Cache 해결(컨텍스트는 24K~32K 시작), provider 설정 복잡화를 감수해야 한다. 처음에는 Qwen3.5 하나를 두 장에 분산하는 기본안으로 시작하고, 이 구성은 그다음에 시도하는 것을 권한다.

마지막으로 운영 원칙 여덟 가지.

1. 로컬 모델의 결과를 무조건 신뢰하지 않는다
2. OpenCode가 실행한 명령과 변경 파일을 항상 확인한다
3. 운영 클러스터 권한을 직접 주지 않는다
4. 기능을 작은 작업으로 나눈다
5. 프로젝트 규칙은 AGENTS.md로 관리한다
6. 한 세션이 너무 길어지면 새 세션으로 분리한다
7. 모델 성능은 실제 업무 작업으로 평가한다
8. NVLink 없는 두 GPU는 속도 향상보다 메모리 확보 목적으로 이해한다

---

## 참고 자료

- [OpenCode 문서](https://opencode.ai/docs/) · [Providers](https://opencode.ai/docs/providers/) · [Config](https://opencode.ai/docs/config/) · [Agents](https://opencode.ai/docs/agents/)
- [Ollama × OpenCode 연동](https://docs.ollama.com/integrations/opencode) · [Linux 설치](https://docs.ollama.com/linux) · [Context Length](https://docs.ollama.com/context-length) · [FAQ (멀티 GPU·Flash Attention·KV Cache)](https://docs.ollama.com/faq)
- [Qwen3.5 35B-A3B 모델 카드](https://huggingface.co/Qwen/Qwen3.5-35B-A3B) · [Ollama 배포본](https://ollama.com/library/qwen3.5:35b-a3b) · [Qwen3-Coder 30B-A3B](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct)
- [EXAONE 4.0 32B](https://huggingface.co/LGAI-EXAONE/EXAONE-4.0-32B) · [공식 GGUF](https://huggingface.co/LGAI-EXAONE/EXAONE-4.0-32B-GGUF) · [Kanana-2 30B-A3B](https://huggingface.co/kakaocorp/kanana-2-30b-a3b-instruct)
- [NVIDIA A30 데이터시트](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/products/a30-gpu/pdf/a30-datasheet.pdf)

---

*환경: Ubuntu 22.04 / NVIDIA A30 24GB × 2 (NVLink 미사용) / Ollama / OpenCode. 2026-07-30 기준 문서·모델 태그이며, OpenCode 설정 스키마와 Ollama의 Hugging Face GGUF 지원 방식은 설치 시점 버전에서 다시 확인이 필요하다.*
