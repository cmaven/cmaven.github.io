---
title: "Ollama 모델 2개로 AI 코드 리뷰 자동화: OpenCode 서브에이전트로 구현·검토 분리하기"
description: "A30 24GB 두 장에 Qwen3-Coder와 EXAONE을 한 장씩 올리고, OpenCode의 primary/subagent 구조로 구현 모델과 검토 모델을 분리하는 구성. 모델별 num_ctx 분리, 검토자에게서 편집 권한을 뺏는 이유, 무한 핑퐁을 끊는 라운드 상한까지"
excerpt: "같은 모델이 자기 코드를 검토하면 같은 실수를 놓친다. 계열이 다른 두 로컬 모델을 GPU 한 장씩에 상주시켜 저자와 검토자를 분리한다"
date: 2026-07-31
categories: Etc
tags: [OpenCode, Ollama, 로컬LLM, 멀티에이전트, 서브에이전트, 코드리뷰, Qwen3-Coder, EXAONE, A30, 멀티GPU, AI-coding-agent]
ref: opencode-dual-model-review-loop
---

:bulb: [Ollama 로컬 LLM 구축 가이드: A30 GPU 2장으로 OpenCode 한국어 코딩 에이전트 만들기](/etc/opencode-korean-local-llm-a30x2/)의 후속이다. 앞 글이 모델 하나를 두 GPU에 분산해 64K 컨텍스트를 확보하는 구성이었다면, 이 글은 **GPU 한 장에 모델 하나씩 올려 구현 모델과 검토 모델을 분리하는 구성**이다. OpenCode의 primary/subagent 구조로 A가 구현하고 B가 검토하고 다시 A가 반영하는 루프를 만든다.
{: .notice--info}

최종 구성부터.

```text
사용자
  │ 한국어로 작업 지시
  ▼
OpenCode
  ├─ primary agent  "build"     ──▶ Qwen3-Coder 30B-A3B  ──▶ A30 #0
  │    파일 수정·명령 실행·테스트
  │
  └─ subagent       "reviewer"  ──▶ EXAONE 4.0 32B       ──▶ A30 #1
       읽기·git diff 전용, 편집 권한 없음
```

| 항목 | 앞 글 | 이 글 |
|---|---|---|
| 모델 수 | 1개 | 2개 |
| GPU 배치 | 모델 하나를 두 장에 분산 | 모델 하나당 GPU 한 장 |
| 컨텍스트 | 65,536 | 모델별 분리 (구현 32K / 검토 16K에서 시작) |
| GPU 간 통신 | PCIe 경유 발생 | 거의 없음 |
| `OLLAMA_MAX_LOADED_MODELS` | 1 | 2 |

---

# [01] 한 모델의 자기 검토가 실패하는 지점

같은 모델에게 "방금 작성한 코드를 검토해줘"라고 시키면 대체로 통과시킨다. 코드를 생성한 확률 분포가 그대로 검토에도 쓰이기 때문에, 생성 단계에서 잘못 판단한 부분은 검토 단계에서도 같은 방향으로 잘못 판단한다. 누락한 예외 처리는 검토할 때도 눈에 띄지 않고, 잘못 기억한 API 시그니처는 검토할 때도 옳아 보인다.

여기에 대화 컨텍스트가 더해진다. 자기 코드가 이미 컨텍스트에 있는 상태에서 검토를 시키면, 모델은 그 코드를 전제로 삼고 "이 전제 안에서 개선할 점"을 찾는다. 전제 자체가 틀렸을 가능성은 검토 대상에서 빠진다.

계열이 다른 모델을 검토자로 두면 두 조건이 바뀐다. 학습 데이터와 토크나이저가 달라 실수의 분포가 겹치지 않고, 컨텍스트를 공유하지 않아 코드를 결과물로만 본다.

이 구성이 해결하지 못하는 것도 분명하다. 두 모델 모두 틀린 사실을 믿고 있으면 검토는 통과한다. 로컬 30B급 모델의 판단을 사람 검토의 대체물로 두면 안 되고, **사람이 `git diff`를 보기 전 1차 필터**로 두는 것이 이 루프의 정확한 위치다.

---

# [02] 역할 분담과 모델 선정

앞 글에서 Qwen3.5 35B-A3B 하나를 기본으로 삼은 기준은 "하나로 다 하기"였다. 두 개를 쓰면 기준이 달라진다. 각 역할에 필요한 능력이 다르므로 한 모델이 두 항목 모두에서 평균일 필요가 없다.

| 역할 | 필요 능력 | 선택 | 근거 |
|---|---|---|---|
| A. 구현 | 도구 호출 안정성, 저장소 단위 코드 수정, 테스트 실행 | Qwen3-Coder 30B-A3B Q4_K_M | 코딩 에이전트·저장소 작업 목적으로 배포된 모델 |
| B. 검토 | 한국어 지적의 정확성, 요구사항 대조, 표현 | EXAONE 4.0 32B Q4_K_M | 한국어 전문 지식·표현에 강하고 공식 GGUF 제공 |

앞 글의 모델 비교표에서 Qwen3-Coder의 단점으로 적었던 "일반 한국어 문장 품질"과 EXAONE의 단점으로 적었던 "한 장에 긴 컨텍스트가 빡빡함"이 이 구성에서는 둘 다 문제가 되지 않는다. Qwen3-Coder는 코드를 쓰고 한국어 설명은 EXAONE이 맡으며, EXAONE은 diff만 읽으므로 긴 컨텍스트가 필요 없다.

**두 모델을 같은 계열로 고르면 이 구성의 이유가 사라진다.** Qwen3-Coder와 Qwen3.5를 짝지으면 검토자가 구현자와 비슷한 실수를 놓친다. 계열이 다른 쪽을 우선한다.

VRAM 배치는 이렇게 된다.

```text
A30 #0 24GB ├─ Qwen3-Coder 30B-A3B Q4_K_M  약 19GB
            └─ KV Cache + 실행 공간          약 5GB

A30 #1 24GB ├─ EXAONE 4.0 32B Q4_K_M        약 19.3GB
            └─ KV Cache + 실행 공간          약 4GB
```

Ollama 문서는 모델 배치를 이렇게 설명한다 — 모델 전체를 한 GPU에 올리는 것을 우선하고, 한 장에 들어가지 않을 때만 여러 GPU에 나눈다. 두 모델 모두 24GB 안에 들어가므로 **GPU 지정 없이도 한 장에 하나씩 배치된다.** 앞 글에서 뺐던 `CUDA_VISIBLE_DEVICES`를 다시 넣을 이유가 여기서도 없다.

---

# [03] Ollama — 두 모델을 동시에 상주시키기

## 3-1. systemd 설정 변경

앞 글의 설정에서 두 항목을 바꾼다.

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
Environment="OLLAMA_MODELS=/data/ollama/models"
```

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

| 변경 | 앞 글 | 이 글 | 이유 |
|---|---|---|---|
| `OLLAMA_MAX_LOADED_MODELS` | 1 | 2 | 두 모델이 동시에 상주해야 라운드마다 재적재가 없다 |
| `OLLAMA_CONTEXT_LENGTH` | 65536 | 16384 | 전역 기본값을 낮게 두고, 모델별로 3-2에서 올린다 |

Ollama 문서 기준 `OLLAMA_MAX_LOADED_MODELS`의 기본값은 `GPU 수 × 3`이므로 명시하지 않아도 2개는 적재된다. 앞 글에서 `1`로 고정해 뒀다면 반드시 풀어야 한다. 값이 `1`이면 요청이 올 때마다 상대 모델을 내리고 올리는 동작이 반복된다.

`OLLAMA_MODELS`는 앞 글 5-2에서 모델 저장 경로를 데이터 디스크로 옮겨 둔 설정 그대로다. 이 구성은 모델을 두 개 받고 3-2에서 파생 모델까지 만들기 때문에 디스크 압박이 앞 글보다 크다.

| 항목 | 대략 크기 |
|---|---|
| `qwen3-coder:30b-a3b-q4_K_M` | 19GB |
| EXAONE 4.0 32B Q4_K_M | 19.3GB |
| 앞 글에서 받은 Qwen3.5 35B-A3B를 남겨 둔 경우 | +24GB |

파생 모델(`coder-32k`, `reviewer-16k`)은 원본 가중치를 참조하므로 크기가 두 배가 되지는 않는다. 그래도 세 모델을 함께 두면 60GB를 넘으므로, 루트 파일시스템에 그대로 두는 구성이라면 앞 글 5-2를 먼저 적용한다.

`OLLAMA_KEEP_ALIVE=-1`은 이 구성에서 선택이 아니라 필수다. 두 모델을 합쳐 38GB 가까이 적재하는 데 드는 시간을 라운드마다 다시 치르지 않으려면 상주시켜야 한다. 다만 GPU 48GB 전부가 Ollama에 묶이므로, 같은 서버에서 학습이나 다른 추론을 돌린다면 이 구성 자체가 맞지 않는다.

## 3-2. 모델별 컨텍스트 분리

`OLLAMA_CONTEXT_LENGTH`는 서버 전역 설정이라 모델마다 다른 값을 줄 수 없다. OpenAI 호환 엔드포인트에는 `num_ctx` 파라미터도 없다. 역할별로 컨텍스트를 다르게 주려면 **Modelfile로 파라미터를 고정한 파생 모델을 만든다.**

구현 모델은 소스 파일 여러 개와 테스트 출력을 함께 들고 있어야 하므로 컨텍스트가 필요하다.

```bash
ollama pull qwen3-coder:30b-a3b-q4_K_M

cat > /tmp/coder.Modelfile <<'EOF'
FROM qwen3-coder:30b-a3b-q4_K_M
PARAMETER num_ctx 32768
EOF

ollama create coder-32k -f /tmp/coder.Modelfile
```

`FROM`에 적는 이름은 Ollama 레지스트리의 실제 태그여야 한다. 없는 태그를 적으면 `ollama create`가 매니페스트를 받으려다 실패한다.

```text
Error: pull model manifest: file does not exist
```

`qwen3-coder`의 30B 계열 태그는 `30b`, `30b-a3b-q4_K_M`, `30b-a3b-q8_0`이다. `30b-a3b`는 없다. 양자화가 이름에 박힌 `30b-a3b-q4_K_M`을 쓰면 나중에 `latest`가 옮겨가도 같은 가중치를 받는다. 태그는 [모델 페이지의 Tags 탭](https://ollama.com/library/qwen3-coder/tags)에서 확인하고, `ollama pull`로 먼저 받아 두면 `ollama create`가 로컬 사본을 쓴다.

검토 모델은 `git diff`와 요구사항만 읽으므로 작아도 된다.

```bash
cat > /tmp/reviewer.Modelfile <<'EOF'
FROM hf.co/LGAI-EXAONE/EXAONE-4.0-32B-GGUF:Q4_K_M
PARAMETER num_ctx 16384
EOF

ollama create reviewer-16k -f /tmp/reviewer.Modelfile
```

컨텍스트를 비대칭으로 주는 것이 이 구성의 실질적 이득이다. 두 모델에 32K씩 균등하게 주면 VRAM이 모자라지만, 검토자에게 16K만 주면 구현자가 32K를 쓸 수 있다.

시작값은 위 수치이고, 실제 한계는 측정해서 정한다.

```bash
ollama run coder-32k "테스트"      # 적재만 시키고 /bye
ollama run reviewer-16k "테스트"
ollama ps
nvidia-smi
```

`ollama ps`의 `PROCESSOR`가 두 모델 모두 GPU로 표시되고 `nvidia-smi`에서 GPU 0·1이 각각 20GB대를 점유하면 성공이다. CPU 혼합으로 떨어지면 `num_ctx`를 낮춰 다시 `ollama create` 한다. 두 모델이 한 GPU에 몰렸다면 한쪽 `num_ctx`가 과해 Ollama가 배치를 포기한 것이므로 같은 방향으로 조정한다.

> `PROCESSOR`가 `100% CPU`로 나오면 컨텍스트 문제가 아니라 드라이버 문제다. 앞 글 5-1 참고.
{: .notice--warning}

## 3-3. GPU를 고정해야 한다면

Ollama의 자동 배치는 적재 순서와 여유 메모리에 따라 달라진다. 어느 모델이 어느 GPU에 갈지 고정해야 하는 상황이라면 **Ollama 인스턴스를 두 개 띄우고 각각에 GPU 한 장씩 준다.**

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

기존 `ollama.service`에는 `CUDA_VISIBLE_DEVICES=0`을 주고, 두 인스턴스가 같은 모델 디렉터리(`/usr/share/ollama/.ollama/models`)를 공유하게 둔다. 인스턴스별로 `OLLAMA_CONTEXT_LENGTH`가 분리되므로 3-2의 Modelfile 작업도 필요 없다.

대가는 운영 대상이 둘로 늘어나는 것이다. 포트 두 개, systemd 유닛 두 개, 로그 두 곳을 관리해야 하고 OpenCode 설정에도 provider가 둘 생긴다. 3-1 방식으로 먼저 시도하고, 배치가 실제로 흔들릴 때 옮기는 순서를 권한다.

---

# [04] OpenCode — primary와 subagent 분리

## 4-1. 설정 파일 위치

OpenCode 설정 파일은 두 곳에 둘 수 있다.

| 범위 | 경로 | 적용 대상 |
|---|---|---|
| 전역 | `~/.config/opencode/opencode.json` | 모든 프로젝트 |
| 프로젝트 | 프로젝트 루트의 `opencode.json` | 해당 저장소. 커밋하면 팀과 공유된다 |

주석을 허용하는 `.jsonc` 확장자도 인식한다. 두 파일은 **교체가 아니라 병합**되고, 충돌하는 키만 프로젝트 설정이 이긴다.

Ollama 서버는 사용자 계정과 무관하게 한 대에 하나이므로, provider와 모델 정의는 전역 파일에 둔다. 앞 글에서 이미 `~/.config/opencode/opencode.jsonc`를 만들었다면 그 파일을 아래 내용으로 교체하면 된다.

## 4-2. 전역 설정 전체 내용

3-1 방식(단일 Ollama 인스턴스)의 완성본이다. provider와 agent를 **한 파일에 함께** 넣는다.

```bash
mkdir -p ~/.config/opencode
cat > ~/.config/opencode/opencode.jsonc <<'EOF'
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
          "name": "Qwen3-Coder 30B-A3B - 구현",
          "limit": { "context": 32768, "output": 8192 }
        },
        "reviewer-16k": {
          "name": "EXAONE 4.0 32B - 검토",
          "limit": { "context": 16384, "output": 4096 }
        }
      }
    }
  },

  "agent": {
    "build": {
      "model": "ollama/coder-32k"
    }
  }
}
EOF
```

| 키 | 의미 |
|---|---|
| `model` | 세션 기본 모델. 구현 모델을 지정한다 |
| `small_model` | 세션 제목 생성 같은 가벼운 작업용. 외부 provider를 쓰지 않으려면 같은 로컬 모델로 명시한다 |
| `provider.ollama.models` | 3-2에서 `ollama create`로 만든 파생 모델 이름과 정확히 같아야 한다 |
| `limit.context` | 3-2의 `num_ctx`와 같은 값. 어긋나면 OpenCode가 서버 한계를 넘는 요청을 만들고 Ollama가 앞부분을 잘라낸다 |
| `agent.build` | 기본 구현 에이전트의 모델 고정. 검토 에이전트는 4-3에서 별도 파일로 정의한다 |

검토 모델(`reviewer-16k`)은 `models`에 등록만 하고 `model`로 지정하지 않는다. 4-3의 서브에이전트가 이름으로 가리켜 쓴다.

등록 결과를 확인한다.

```bash
cd /path/to/your/project
opencode
```

```text
/models   # "Qwen3-Coder 30B-A3B - 구현"과 "EXAONE 4.0 32B - 검토" 두 개가 보여야 한다
```

3-3 방식(인스턴스 두 개)이면 `baseURL`이 `http://127.0.0.1:11435/v1`인 provider를 `ollama-reviewer`라는 이름으로 하나 더 만들고, 4-3의 `model`을 `ollama-reviewer/reviewer-16k`로 적는다.

## 4-3. 검토 에이전트 정의

OpenCode의 에이전트는 `mode`로 성격이 갈린다. `primary`는 사용자가 직접 대화하는 주 에이전트, `subagent`는 primary가 호출하거나 사용자가 `@이름`으로 부르는 보조 에이전트다.

구현 에이전트는 4-2에서 `agent.build`로 모델만 바꿔 끝났다. 검토자는 프롬프트와 권한을 따로 줘야 하므로 markdown 파일로 정의한다. **JSON이 아니라 별도 파일이고, 파일명이 곧 에이전트 이름이 된다.**

```bash
mkdir -p ~/.config/opencode/agents
```

```markdown
<!-- ~/.config/opencode/agents/reviewer.md -->
---
description: 구현된 변경사항을 검토하고 문제를 지적한다. 코드를 수정하지 않는다.
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

당신은 코드 검토자다. 코드를 직접 수정하지 않는다.

## 검토 절차
1. `git diff`로 변경 내용을 확인한다.
2. 변경된 파일의 주변 코드를 읽어 맥락을 파악한다.
3. 요구사항과 대조해 누락과 오류를 찾는다.

## 지적 형식
발견한 항목마다 다음을 적는다.
- 심각도: 치명 / 중대 / 경미 / 제안
- 위치: 파일 경로와 라인
- 문제: 무엇이 잘못되었는지 한 문장
- 근거: 왜 문제인지. 추측이면 추측이라고 명시한다
- 수정 방향: 구체적인 조치. 코드 전체를 다시 쓰지 않는다

## 금지
- 근거 없이 "좋아 보인다"로 통과시키지 않는다.
- 문제가 없으면 "지적 없음"이라고만 답한다. 칭찬을 채워 넣지 않는다.
- 스타일 취향을 치명·중대로 분류하지 않는다.
- 변경되지 않은 파일의 문제는 별도 항목으로 분리한다.
```

`permission`이 이 구성의 핵심이다. **검토자에게서 `edit`과 `write`를 뺏지 않으면 검토자가 직접 코드를 고치기 시작하고, 저자와 검토자를 분리한 의미가 사라진다.** `bash`는 `git diff` 계열만 허용해 검토에 필요한 최소 권한만 남긴다.

정리하면 파일이 두 개다.

```text
~/.config/opencode/opencode.jsonc      provider, 모델 2개, agent.build 모델 지정
~/.config/opencode/agents/reviewer.md  검토 서브에이전트의 프롬프트와 권한
```

OpenCode를 다시 띄워 등록 상태를 확인한다.

```text
/agents   # reviewer 가 subagent 로 보여야 한다
```

---

# [05] 루프 운영

## 5-1. 3단계

라운드 하나는 구현·검토·반영 세 단계다.

```text
① 구현   build(A)     기능 구현 + 테스트 실행 + 커밋하지 않음
② 검토   @reviewer(B) git diff 검토 + 심각도별 지적
③ 반영   build(A)     지적 중 수용할 항목 반영 + 재테스트
④ 게이트 사람          git diff 확인 후 커밋
```

**① 구현**

```text
이 저장소의 status.conditions 갱신 로직에 Ready 컨디션을 추가해줘.
기존 컨디션 처리 방식을 먼저 확인하고 같은 패턴을 따라줘.
수정 후 관련 단위 테스트를 실행하고 결과를 알려줘.
커밋은 하지 마.
```

커밋을 막는 것이 중요하다. 검토자가 `git diff`로 변경을 보려면 작업 트리에 변경이 남아 있어야 한다.

**② 검토**

```text
@reviewer 방금 변경된 내용을 검토해줘.
요구사항은 "status.conditions에 Ready 컨디션 추가, 기존 컨디션 처리 패턴 준수"였어.
```

`@reviewer`로 호출하면 서브에이전트가 별도 컨텍스트에서 실행되고 결과가 세션에 돌아온다. primary가 `task` 도구로 자동 호출하게 둘 수도 있지만, 언제 검토가 도는지 사람이 통제하기 어려워진다. 수동 호출을 권한다.

**③ 반영**

```text
검토 지적 중 "치명"과 "중대"만 반영해줘.
"경미"와 "제안"은 각각 수용/거부 여부와 이유만 한국어로 알려주고 코드는 건드리지 마.
반영 후 테스트를 다시 실행해줘.
```

전부 반영시키지 않는 것이 요점이다. 로컬 30B 모델의 지적에는 오탐이 섞이고, 그 오탐까지 반영하면 코드가 나빠진다. 심각도로 거르고 나머지는 판단만 받는다.

## 5-2. 라운드 상한

**라운드는 2회로 끊는다.** 상한을 두지 않으면 두 모델이 서로의 지적에 반응하며 무한히 왕복한다. 검토자는 매번 무언가를 찾아내도록 프롬프트되어 있고, 구현자는 매번 반영하려 하기 때문에 자연히 수렴하지 않는다.

```text
1라운드: 구현 → 검토 → 반영     대부분의 실질적 문제가 여기서 잡힌다
2라운드: 재검토 → 반영          1라운드 반영이 새 문제를 만들었는지만 확인
3라운드 이상                     사람이 개입. 요구사항 자체가 모호하다는 신호
```

2라운드에서도 치명·중대가 계속 나오면 모델을 더 돌리는 것보다 요구사항을 쪼개는 쪽이 빠르다. 앞 글 9-1의 작업 분할 원칙이 그대로 적용된다.

## 5-3. 사람 게이트

커밋 직전에 `git diff`를 사람이 본다. 두 모델이 합의했다는 것은 두 모델이 같은 오해를 하지 않았다는 뜻일 뿐, 코드가 맞다는 뜻이 아니다.

```bash
git switch -c ai/two-model-loop
# 루프 실행
git diff
git add <파일>
```

---

# [06] 실패 모드

| 증상 | 원인 | 대응 |
|---|---|---|
| 검토자가 "전반적으로 좋습니다"만 반복 | 지적 형식과 금지 항목이 프롬프트에 없음 | 4-3의 심각도 형식과 "칭찬 금지"를 명시. `temperature`를 0.1 수준으로 |
| 검토자가 코드를 직접 수정 | `permission.edit`이 열려 있음 | `edit: deny`, `write: deny` 확인 |
| 검토자가 diff를 못 봄 | `bash` 전면 차단, 또는 이미 커밋됨 | `git diff*` 허용 확인. 구현 단계에서 커밋 금지 |
| 라운드마다 응답이 수십 초 지연 | 모델 스왑 발생 | `ollama ps`에 두 모델이 함께 떠 있는지 확인. `MAX_LOADED_MODELS`와 `KEEP_ALIVE` 재확인 |
| 지적이 변경과 무관한 파일에 쏠림 | 검토 범위가 프롬프트에 없음 | 요구사항을 호출 시 함께 전달. 4-3의 "변경되지 않은 파일은 별도 항목" 규칙 |
| 3라운드 이상 왕복 | 요구사항이 모호 | 5-2에 따라 중단하고 작업을 쪼갬 |
| 반영 후 테스트가 깨짐 | 오탐 지적까지 반영 | 심각도로 필터. 5-1 ③의 프롬프트 형태 유지 |

가장 자주 보게 되는 것은 첫 번째 항목이다. 검토자 프롬프트가 짧으면 모델은 무난한 총평을 생성하는 쪽으로 기운다. 형식을 강제하는 문장이 프롬프트 분량의 절반을 차지해도 과하지 않다.

---

# [07] 검증

구성이 의도대로 도는지 확인할 지점은 네 곳이다.

```bash
# 1. 두 모델이 각각 다른 GPU에 상주하는가
ollama ps
nvidia-smi

# 2. 검토자가 실제로 B 모델을 쓰는가
sudo journalctl -u ollama -f      # @reviewer 호출 중 reviewer-16k 요청이 찍히는지

# 3. 검토자가 편집 도구를 못 쓰는가
#    @reviewer 에게 "이 파일을 직접 수정해줘"라고 지시 → 거부되어야 정상

# 4. 스왑이 없는가
#    라운드 2회 실행 후 ollama ps 의 UNTIL 이 Forever 유지, 응답 지연 없음
```

3번은 반드시 한 번 확인한다. `permission` 설정이 적용되지 않은 상태에서 루프를 돌리면 검토자가 조용히 코드를 고치고, 그 수정은 아무도 검토하지 않은 채로 남는다.

---

# [08] 이 글에서 검증하지 않은 것

이 구성은 앞 글의 [12]절에서 다음 단계로 제시했던 GPU 분리 운영을 구체화한 것이다. 다음 항목은 문서 기준으로 작성했고 이 서버에서 측정하지 않았다.

- **VRAM 수치와 컨텍스트 상한**: 19GB·19.3GB는 각각 Ollama·Hugging Face에 표기된 배포본 크기이고, KV Cache를 더한 실제 점유량과 32K·16K가 A30 24GB에 들어가는지는 3-2의 절차로 각자 측정해야 한다. 시작값일 뿐 검증된 상한이 아니다.
- **두 모델의 배치 결과**: 한 장에 하나씩 놓이는 것은 Ollama 문서의 배치 규칙에서 따라 나오는 기대값이다. 적재 순서에 따라 달라지면 3-3으로 고정한다.
- **검토 품질**: EXAONE의 지적이 Qwen3-Coder의 실수를 실제로 얼마나 잡아내는지는 저장소와 작업 성격에 따라 다르다. 앞 글 [12]의 비교 방법대로 실제 작업 10~20개로 측정하는 것이 유일한 판단 근거다.
- **OpenCode 설정 스키마**: `agent`, `mode`, `permission` 키는 OpenCode 문서 기준이며 버전에 따라 달라진다. 오류가 나면 `https://opencode.ai/config.json` 스키마를 먼저 확인한다.

---

## 참고 자료

- [OpenCode Agents](https://opencode.ai/docs/agents/) · [Config](https://opencode.ai/docs/config/) · [Providers](https://opencode.ai/docs/providers/)
- [Ollama FAQ (동시 적재·멀티 GPU 배치)](https://docs.ollama.com/faq) · [Modelfile](https://docs.ollama.com/modelfile) · [Context Length](https://docs.ollama.com/context-length)
- [Qwen3-Coder 30B-A3B](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct) · [EXAONE 4.0 32B GGUF](https://huggingface.co/LGAI-EXAONE/EXAONE-4.0-32B-GGUF)
- 앞 글: [Ollama 로컬 LLM 구축 가이드: A30 GPU 2장으로 OpenCode 한국어 코딩 에이전트 만들기](/etc/opencode-korean-local-llm-a30x2/)

---

*환경: Ubuntu 22.04 / NVIDIA A30 24GB × 2 (NVLink 미사용) / Ollama / OpenCode. 2026-07-31 기준 문서이며, [08]에 적은 항목은 이 서버에서 측정하지 않았다.*
