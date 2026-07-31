---
title: "로컬 LLM 입문 개념: VRAM·양자화·KV Cache·MoE를 한 번에 정리"
description: "로컬 LLM을 처음 올리기 전에 알아야 할 개념만 모았다. LLM과 에이전트 하네스의 차이, VRAM이 무엇에 쓰이는지, 양자화 표기(Q4_K_M) 읽는 법, 토큰과 Context Length, KV Cache가 커지는 이유, MoE의 A3B 표기, Tool Calling, NVLink 없는 멀티 GPU까지"
excerpt: "GPU와 LLM을 처음 접할 때 막히는 용어를 설치 전에 정리한다. VRAM·양자화·KV Cache·MoE를 알면 이후 튜닝 문서가 전부 읽힌다"
date: 2026-07-31
categories: Etc
tags: [로컬LLM, LLM, VRAM, 양자화, KV-Cache, MoE, GPU, 컨텍스트, Tool-Calling, Ollama, OpenCode, A30]
ref: local-llm-gpu-vram-concepts
---

> **로컬 LLM 코딩 에이전트 시리즈**
> ① **개념편**(현재 글) · ② [Ollama 로컬 LLM 구축 가이드](/etc/opencode-korean-local-llm-a30x2/) · ③ [Ollama 멀티GPU 운영·트러블슈팅](/etc/ollama-multi-gpu-troubleshooting/) · ④ [AI 코드 리뷰 자동화](/etc/opencode-dual-model-review-loop/)
{: .notice--primary}

:bulb: 로컬 LLM을 서버에 올리는 문서는 대부분 `OLLAMA_KV_CACHE_TYPE=q8_0` 같은 설정부터 시작한다. 이 값이 무엇을 바꾸는지 모르면 문제가 생겼을 때 무엇을 조정해야 할지 알 수 없다. 이 글은 설치 명령을 치기 전에 필요한 개념만 모았다. 여기까지 읽으면 이후 구축·튜닝 문서가 전부 읽힌다.
{: .notice--info}

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

이 절만 이해하면 구축편과 운영편의 튜닝 항목이 전부 읽힌다. 처음 접하는 용어가 많다면 여기서 시간을 쓰는 게 오히려 지름길이다.

## 2-1. A30은 어떤 GPU인가?

NVIDIA A30은 데이터센터용 Ampere GPU다.

- GPU 메모리: 24GB HBM2, 대역폭 933GB/s
- 인터페이스: PCIe Gen4, TDP 165W
- MIG 지원, 최대 두 장을 NVLink 브리지로 연결 가능
- 팬 없는 패시브 냉각 — 서버 섀시 풍량에 의존

이 시리즈의 서버는 NVLink를 사용하지 않으므로 두 GPU 사이의 통신은 PCIe를 거친다.

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

이 시리즈의 기본 모델은 Ollama 기준 약 24GB다. 그러나 24GB 모델을 24GB GPU에 그대로 넣을 수 있다고 단정하면 안 된다. 위에서 본 것처럼 실행 공간과 KV Cache가 추가로 필요하기 때문이다.

## 2-4. 양자화란?

양자화(quantization)는 모델 숫자의 정밀도를 낮춰 파일과 메모리 사용량을 줄이는 기술이다. 비유하면 원본 사진을 약간 압축해 파일 크기를 줄이는 것과 비슷하다.

대표적인 표기:

- `BF16`: 품질이 높지만 메모리를 많이 사용
- `Q8`: 8비트 양자화
- `Q5`: 5비트 계열 양자화
- `Q4_K_M`: 4비트 계열의 일반적인 균형형 양자화

이 시리즈는 **Q4_K_M**을 사용한다. 30B급 모델을 A30 두 장에서 현실적으로 실행할 수 있고, BF16보다 훨씬 적은 VRAM으로 일반적인 코딩 작업에서 품질과 속도의 균형이 좋다. 대신 원본 모델보다 일부 정확도가 떨어질 수 있고, 어려운 추론이나 미세한 코드 판단에서 차이가 날 수 있다.

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

따라서 일반 채팅보다 훨씬 긴 컨텍스트가 필요하다. Ollama의 OpenCode 안내는 코딩 에이전트용 로컬 모델에 **64K 이상 컨텍스트**를 권장하며, 구축편도 65,536 토큰으로 시작한다.

```text
32K = 약 32,768 토큰
64K = 약 65,536 토큰
```

컨텍스트를 늘리면 VRAM 사용량도 증가한다. 이 트레이드오프는 [운영편의 OOM 대응](/etc/ollama-multi-gpu-troubleshooting/)에서 실제 조정 단계로 다시 나온다.

## 2-7. KV Cache란?

KV Cache는 모델이 이미 읽은 문맥을 매번 처음부터 다시 계산하지 않도록 저장해 두는 메모리 영역이다. 컨텍스트가 길어질수록 KV Cache가 커진다.

```text
f16 KV Cache  = 품질 우선, 메모리 큼 (기본값)
q8_0 KV Cache = 메모리 약 절반, 품질 손실 매우 작음
q4_0 KV Cache = 더 작음, 품질 저하가 보일 수 있음
```

이 시리즈는 `q8_0`로 설정해 기본 `f16`보다 메모리를 줄인다. 처음에는 `q8_0`을 권장한다.

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

모델이 한국어를 잘해도 Tool Calling이 불안정하면 OpenCode가 실제 작업을 제대로 수행하지 못한다. 그래서 OpenCode용 모델은 한국어 능력과 도구 호출 능력을 함께 봐야 한다. 이 기준이 [구축편의 모델 선정](/etc/opencode-korean-local-llm-a30x2/)으로 이어진다.

## 2-10. NVLink가 없으면 사용할 수 없는가?

사용 가능하다. 다만 하나의 모델을 두 GPU에 분산하면 GPU 사이의 데이터가 PCIe를 통해 이동한다. NVLink가 있을 때보다 통신 대역폭이 낮으므로 다음 현상이 있을 수 있다.

- 토큰 생성 속도가 낮아질 수 있음
- 첫 응답 지연이 커질 수 있음
- GPU 두 장을 쓴다고 속도가 정확히 두 배가 되지 않음

이 구성의 목표는 속도를 두 배로 만드는 것이 아니라, **한 장에 넣기 어려운 모델과 긴 컨텍스트를 두 장에 나누어 안정적으로 실행하는 것**이다. 속도가 아니라 메모리를 사는 구성이라고 이해하면 된다.

---

# [03] 개념을 설정값으로 옮기면

각 개념이 실제 설정의 어느 항목으로 이어지는지 정리하면 이렇다.

| 개념 | 대응 설정 | 조정했을 때 |
|---|---|---|
| Context Length (2-6) | `OLLAMA_CONTEXT_LENGTH` | 늘리면 긴 작업이 가능해지고 VRAM이 늘어난다 |
| KV Cache (2-7) | `OLLAMA_KV_CACHE_TYPE` | `q8_0`이면 `f16` 대비 약 절반, 품질 손실은 작다 |
| 양자화 (2-4) | 모델 태그의 `Q4_K_M` | 낮출수록 VRAM이 줄고 정확도가 떨어진다 |
| VRAM (2-2) | 모델 선택과 GPU 수 | 부족하면 CPU offload가 걸려 크게 느려진다 |
| MoE (2-8) | 모델 선택 | 계산량은 줄지만 가중치는 전부 적재된다 |

값을 실제로 넣고 두 GPU에 모델을 올리는 과정은 ② [Ollama 로컬 LLM 구축 가이드](/etc/opencode-korean-local-llm-a30x2/)에서 이어진다. 올린 뒤 `100% CPU`로 뜨거나 VRAM이 모자라는 상황은 ③ [Ollama 멀티GPU 운영·트러블슈팅](/etc/ollama-multi-gpu-troubleshooting/)에서 다룬다.

---

## 참고 자료

- [Ollama Context Length](https://docs.ollama.com/context-length) · [FAQ (멀티 GPU·Flash Attention·KV Cache)](https://docs.ollama.com/faq)
- [OpenCode 문서](https://opencode.ai/docs/) · [Agents](https://opencode.ai/docs/agents/)
- [Qwen3.5 35B-A3B 모델 카드](https://huggingface.co/Qwen/Qwen3.5-35B-A3B) · [EXAONE 4.0 32B](https://huggingface.co/LGAI-EXAONE/EXAONE-4.0-32B)
- [NVIDIA A30 데이터시트](https://www.nvidia.com/content/dam/en-zz/Solutions/data-center/products/a30-gpu/pdf/a30-datasheet.pdf)

---

*2026-07-31 기준 문서다. 모델 태그와 Ollama 설정 항목은 버전에 따라 달라지므로 설치 시점에 다시 확인한다.*
