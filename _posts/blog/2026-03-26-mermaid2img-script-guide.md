---
title: "Mermaid 다이어그램을 이미지로 일괄 변환하기 — mermaid2img.sh"
description: "마크다운 파일에 포함된 Mermaid 다이어그램을 JPG/PNG로 한 번에 추출하는 쉘 스크립트의 사용법과 동작 원리"
excerpt: "환경 자동 구성부터 mermaid 블록 추출, mmdc 렌더링, 포맷 변환까지 단일 스크립트로 처리하는 mermaid2img.sh 가이드"
date: 2026-03-26
categories: Github_Blog
tags: [Mermaid, mermaid-cli, mmdc, 이미지변환, 쉘스크립트, WSL, Puppeteer, Chrome, Node.js, Pillow]
---

:bulb: 마크다운 `.md` 파일에 포함된 Mermaid 다이어그램을 JPG 또는 PNG로 한 번에 추출하는 쉘 스크립트 `mermaid2img.sh`의 사용법과 동작 원리를 정리한다.
{: .notice--info}

# [01] 왜 필요한가

Mermaid는 마크다운 안에서 텍스트로 다이어그램을 그릴 수 있는 도구다. GitHub, Notion, Obsidian 같은 플랫폼에서는 자동으로 렌더링되지만, 아래와 같은 상황에서는 이미지 파일이 필요하다.

- PPT, Word 등 오피스 문서에 삽입할 때
- Mermaid 렌더링을 지원하지 않는 블로그 플랫폼에 올릴 때
- 문서를 PDF로 변환하면서 다이어그램을 포함할 때
- 이미지 기반 문서 관리 시스템에 등록할 때

문서 하나에 다이어그램이 1~2개라면 수동 변환해도 되지만, 10개 이상이라면 자동화가 필요하다.

---

# [02] 특징 및 사용법

## 2-1. 주요 특징

| 특징 | 설명 |
|------|------|
| **환경 자동 구성** | Node.js, mermaid-cli, Chrome, Pillow, 한글 폰트가 없으면 자동 설치 |
| **WSL 호환** | Windows PATH 우선순위 문제를 자동 감지하고 해결 |
| **포맷 선택** | JPG / PNG 중 선택 가능 (인터랙티브 또는 옵션) |
| **고해상도** | 기본 2배 스케일로 Retina급 선명한 이미지 생성 |
| **단일 파일** | 별도 설정 파일 없이 스크립트 하나로 완결 |

## 2-2. 사용법

```bash
chmod +x mermaid2img.sh

# 인터랙티브 — 포맷을 물어봄
./mermaid2img.sh document.md

# 옵션으로 포맷 지정 — 물어보지 않고 바로 실행
./mermaid2img.sh -f png document.md

# JPG 품질 조절 + 출력 디렉토리 지정
./mermaid2img.sh -f jpg -q 80 document.md ./output/

# 도움말
./mermaid2img.sh -h
```

옵션 없이 실행하면 포맷을 물어본다.

```
  출력 포맷을 선택하세요:

    1) jpg  — 파일 작음, 문서 삽입에 적합
    2) png  — 무손실, 투명 배경 지원

  선택 [1/2] (기본: 1):
```

## 2-3. 에러 메시지

**인자 없이 실행한 경우:**

```bash
./mermaid2img.sh
```

```
./mermaid2img.sh: line XX: 1: 사용법: ./mermaid2img.sh <input.md> [output_dir]
```

스크립트 내부에서 `${1:?사용법}` 패턴으로 처리되어, 입력 파일을 지정하지 않으면 사용법을 출력하고 종료한다.

**존재하지 않는 파일을 지정한 경우:**

```bash
./mermaid2img.sh not-exist.md
```

```
[✗] 입력 파일을 찾을 수 없습니다: not-exist.md
```

**mermaid 블록이 없는 파일을 지정한 경우:**

```bash
./mermaid2img.sh no-mermaid.md
```

```
mermaid 블록을 찾지 못했습니다.
```

## 2-4. 실행 결과 예시

16개의 mermaid 블록이 있는 문서를 변환하면 다음과 같은 결과가 나온다.

```
[✓] Chrome: /home/kcloud/.cache/puppeteer/chrome/linux-.../chrome
[✓] 출력 포맷: JPG
  BLOCK 1: ./mermaid_images/document_1.mmd
  BLOCK 2: ./mermaid_images/document_2.mmd
  ...
  BLOCK 16: ./mermaid_images/document_16.mmd

  총 16개 블록 발견

[1] 변환 중: document_1.mmd → document_1.jpg (848x1200, 150KB)
[2] 변환 중: document_2.mmd → document_2.jpg (848x600, 85KB)
...
[16] 변환 중: document_16.mmd → document_16.jpg (848x900, 120KB)

[✓] 변환 완료! 결과: ./mermaid_images/
```

출력 파일명은 `{마크다운파일명}_{순번}.jpg` (또는 `.png`) 형식이며, 블록이 등장하는 순서대로 번호가 매겨진다.

---

# [03] 스크립트 구조

스크립트는 크게 **PART 1 (환경 구성)**과 **PART 2 (변환)** 두 부분으로 나뉜다.

```
PART 1: 환경 검증 및 자동 구성
  ├── 1-1. WSL Windows PATH 우선순위 문제 해결
  ├── 1-2. Node.js v20+ 설치 (NodeSource)
  ├── 1-3. npm 글로벌 경로 설정
  ├── 1-4. mermaid-cli (mmdc) 설치
  ├── 1-5. Chrome 설치 + 의존 라이브러리
  ├── 1-6. Python3 & Pillow 설치
  └── 1-7. 한글 폰트 설치

PART 2: Mermaid → 이미지 변환
  ├── 2-1. 옵션 파싱 및 포맷 선택
  ├── 2-2. Chrome 바이너리 탐색 → Puppeteer 설정
  ├── 2-3. 마크다운에서 Mermaid 블록 추출
  ├── 2-4. 각 블록 변환 (mermaid → PNG → JPG/PNG)
  └── 2-5. 정리 및 결과 출력
```

환경이 이미 갖춰져 있으면 PART 1은 아무것도 출력하지 않고 바로 PART 2로 넘어간다. 뭔가 빠져있으면 `[!] [환경 구성]` 메시지와 함께 자동 설치를 수행한다.

---

# [04] PART 1: 환경 자동 구성

## 4-1. WSL Windows PATH 우선순위 문제

WSL은 기본적으로 Windows의 PATH를 그대로 가져온다. Windows에 Node.js(nvm4w 등)가 설치되어 있으면 Linux의 `node`보다 먼저 잡히면서 `mmdc`가 동작하지 않는 문제가 발생한다.

```bash
which node
# /mnt/c/nvm4w/nodejs/node  ← 이렇게 나오면 문제
```

스크립트는 `/proc/version`에서 WSL 여부를 감지하고, `node` 경로가 `/mnt/c`를 포함하면 Linux 경로를 우선하도록 PATH를 조정한다.

## 4-2. Node.js v20+ 설치

mermaid-cli의 최신 버전은 Node.js v20 이상을 요구한다. Ubuntu 24.04의 `apt install nodejs`는 v18을 설치하기 때문에 버전이 부족하다.

스크립트는 현재 Node.js 버전을 확인하여 v20 미만이면 NodeSource 저장소를 통해 v22 LTS를 설치한다.

```
[!] [환경 구성] Node.js v18.19.1 은 너무 낮습니다. (v20 이상 필요)
[!] [환경 구성] Node.js v22 LTS를 설치합니다...
[✓] [환경 구성] Node.js 설치 완료: v22.x.x
```

## 4-3. npm 글로벌 경로

npm 글로벌 패키지를 `~/.npm-global`에 설치하도록 설정한다. `sudo npm install -g`를 쓰지 않기 위한 조치이며, PATH에도 자동으로 추가된다.

## 4-4. mermaid-cli (mmdc)

`mmdc`가 없거나, Windows 경로(`/mnt/c/...`)에만 있으면 Linux용으로 새로 설치한다.

## 4-5. Chrome + 시스템 라이브러리

mmdc는 내부적으로 Puppeteer를 통해 headless Chrome을 실행한다. Chrome 바이너리가 없으면 Puppeteer로 자동 설치하고, Chrome 실행에 필요한 시스템 라이브러리(libnss3, libgbm1 등)도 함께 확인한다.

WSL이나 최소 설치 Ubuntu에서는 Chrome 바이너리가 있어도 공유 라이브러리가 없어서 실패하는 경우가 흔하다.

```
Error: libnss3.so: cannot open shared object file
```

스크립트는 `ldconfig`로 `libnss3` 유무를 확인하고, 없으면 필요한 라이브러리를 한 번에 설치한다.

## 4-6. Python3 & Pillow

JPG 변환에 Pillow가 필요하다. `pip3`가 있으면 pip으로, 없으면 `apt install python3-pil`로 설치한다.

## 4-7. 한글 폰트

다이어그램에 한글이 포함되어 있으면 폰트가 없을 때 깨진다. `dpkg`로 `fonts-nanum` 또는 `fonts-noto-cjk` 패키지 설치 여부를 확인한다.

:bulb: WSL 환경에서 `fc-list` 명령이 불안정하게 동작하는 문제가 있어서 `dpkg`를 사용한다.
{: .notice--info}

---

# [05] PART 2: Mermaid → 이미지 변환

## 5-1. 인자 검증 및 옵션 파싱

스크립트는 실행 시 입력 파일을 검증한다.

```bash
INPUT="${1:?사용법: $0 <input.md> [output_dir]}"
```

인자가 없으면 사용법을 출력하고 즉시 종료한다. 파일이 존재하지 않는 경우에도 에러 메시지를 출력한다.

`getopts`로 `-f` (포맷), `-q` (JPG 품질), `-h` (도움말) 옵션을 파싱한다. `-h`는 환경 구성(PART 1)보다 먼저 감지되어, 도움말만 보고 싶을 때 불필요한 설치가 실행되지 않는다.

## 5-2. Chrome 바이너리 탐색

Chrome 바이너리의 위치가 환경마다 다르기 때문에 여러 후보 경로를 탐색한다.

| 환경 | Chrome 경로 |
|------|-------------|
| apt로 chromium 설치 | `/usr/bin/chromium-browser` 또는 `/usr/bin/chromium` |
| Google Chrome 직접 설치 | `/usr/bin/google-chrome-stable` |
| Puppeteer 자동 설치 | `~/.cache/puppeteer/chrome/linux-*/chrome-linux64/chrome` |

발견된 경로는 임시 JSON 파일로 만들어 `mmdc`의 `-p` 옵션에 전달된다.

## 5-3. Mermaid 블록 추출

Python 인라인 스크립트로 마크다운에서 mermaid 블록을 추출한다.

```python
blocks = re.findall(r'```mermaid\s*\n(.*?)```', content, re.DOTALL)
```

| 패턴 | 매칭 대상 |
|------|-----------|
| ` ```mermaid ` | 시작 태그 |
| `\s*\n` | 시작 태그 뒤의 공백과 줄바꿈 |
| `(.*?)` | mermaid 코드 본문 캡처 (non-greedy) |
| ` ``` ` | 끝 태그 |

`re.DOTALL` 플래그가 있어서 `.`이 줄바꿈도 포함하므로 여러 줄에 걸친 mermaid 코드를 올바르게 캡처한다. 각 블록은 `{파일명}_{순번}.mmd` 파일로 저장된다.

## 5-4. 렌더링 (Mermaid → PNG → JPG/PNG)

각 `.mmd` 파일에 대해 변환을 수행한다.

```bash
mmdc -i "$mmd_file" -o "$png_file" -b "$BG" -w "$WIDTH" -s "$SCALE" -p "$PUPPETEER_CONFIG" -q
```

| 옵션 | 설명 |
|------|------|
| `-i` | 입력 `.mmd` 파일 |
| `-o` | 출력 파일 (확장자로 포맷 결정) |
| `-b white` | 배경색을 흰색으로 설정 |
| `-w 1200` | 렌더링 캔버스 너비 |
| `-s 2` | 2배 스케일 (고해상도) |
| `-p` | Puppeteer 설정 파일 (Chrome 경로, sandbox 옵션) |
| `-q` | 조용한 모드 (불필요한 로그 억제) |

`mmdc`는 내부적으로 headless Chrome을 실행하여 mermaid.js로 다이어그램을 렌더링한 뒤 스크린샷을 찍는 방식으로 PNG를 생성한다.

**포맷에 따른 분기:**
- **JPG 선택 시**: Pillow로 PNG → JPG 변환 (`.convert('RGB')` 후 저장)
- **PNG 선택 시**: mmdc가 생성한 PNG를 그대로 유지

---

# [06] 전체 처리 흐름

```
./mermaid2img.sh document.md
  │
  ├─ -h 감지 → 도움말 출력 후 종료 (환경 구성 건너뜀)
  │
  ├─ PART 1: 환경 검증 및 자동 구성
  │    ├─ 1-1. WSL PATH 문제 → Linux 우선으로 조정
  │    ├─ 1-2. Node.js v20 미만 → NodeSource v22 설치
  │    ├─ 1-3. npm 글로벌 경로 → ~/.npm-global
  │    ├─ 1-4. mmdc 없음 → npm install -g mermaid-cli
  │    ├─ 1-5. Chrome 없음 → Puppeteer 설치 + 시스템 라이브러리
  │    ├─ 1-6. Pillow 없음 → pip3 또는 apt로 설치
  │    └─ 1-7. 한글 폰트 없음 → fonts-nanum 설치
  │
  ├─ PART 2: 변환
  │    ├─ 2-1. 옵션 파싱 + 포맷 선택 (인터랙티브 or -f)
  │    ├─ 2-2. Chrome 바이너리 탐색 → puppeteer.json 생성
  │    ├─ 2-3. Python 정규식으로 mermaid 블록 추출
  │    ├─ 2-4. 각 .mmd → PNG → JPG/PNG
  │    └─ 2-5. 임시 파일 정리
  │
  └─ 결과: document_1.jpg, document_2.jpg, ... (또는 .png)
```

---

# [07] 의존성 구조

스크립트가 자동 설치하는 도구들의 역할은 다음과 같다.

| 도구 | 역할 | 설치 방법 |
|------|------|-----------|
| Node.js v22 | mmdc 실행 런타임 | NodeSource 저장소 → apt |
| `mmdc` (mermaid-cli) | Mermaid 코드 → PNG 렌더링 | npm install -g |
| Puppeteer + Chrome | mmdc 내부에서 headless 브라우저 실행 | npx puppeteer browsers install |
| Chrome 시스템 라이브러리 | libnss3, libgbm1 등 Chrome 의존성 | apt |
| Python3 | 마크다운에서 mermaid 블록 추출 (정규식) | apt |
| Pillow | PNG → JPG 포맷 변환 | pip3 또는 apt (python3-pil) |
| fonts-nanum | 한글 렌더링 | apt |

:bulb: **왜 이렇게 복잡한가?** mermaid-cli(`mmdc`)는 내부적으로 headless Chrome 브라우저에서 mermaid.js를 실행하여 다이어그램을 렌더링한다. 웹 브라우저가 하는 일을 명령줄에서 재현하는 것이기 때문에, Node.js → Puppeteer → Chrome이라는 의존 체인이 필요하다.
{: .notice--info}

---

# [08] WSL에서 겪은 삽질 기록

## 8-1. "mmdc: 명령어를 찾을 수 없음"

`npm install -g` 후에도 `mmdc`를 못 찾는 경우. WSL에서 Windows의 npm이 먼저 잡히면서 Windows 경로에 mmdc를 설치하고, Linux에서는 실행할 수 없었다.

```bash
which mmdc
# /mnt/c/nvm4w/nodejs/mmdc  ← Windows 경로
```

**해결:** Linux PATH를 Windows보다 우선하도록 조정 (스크립트 1-1에서 자동 처리).

## 8-2. "node: not found"

mmdc는 있는데 `node`를 찾지 못하는 경우. mmdc 실행 파일이 Windows 경로에 있고, 그 안에서 `node`를 호출하는데 Linux의 node와 연결되지 않았다.

**해결:** Linux용 Node.js를 설치하고 PATH 우선순위 조정 (1-1, 1-2에서 자동 처리).

## 8-3. "Unsupported engine: required node >= 20"

Ubuntu 24.04의 기본 apt 패키지는 Node.js v18을 설치한다. mermaid-cli 최신 버전의 의존성들이 v20+를 요구하기 때문에 경고가 발생한다.

**해결:** NodeSource 저장소에서 v22 LTS 설치 (1-2에서 자동 처리).

## 8-4. "libnss3.so: cannot open shared object file"

Chrome 바이너리는 있는데 실행에 필요한 시스템 라이브러리가 없는 경우. 최소 설치 Ubuntu나 WSL에서 자주 발생한다.

**해결:** Chrome 의존 라이브러리 일괄 설치 (1-5에서 자동 처리).

## 8-5. 한글 폰트 설치 체크가 매번 실행됨

`fc-list`으로 폰트를 확인했는데, WSL 환경에서 fontconfig가 없거나 캐시가 갱신되지 않아서 이미 설치된 폰트를 감지하지 못했다.

**해결:** `fc-list` 대신 `dpkg -l fonts-nanum`으로 패키지 설치 여부를 직접 확인 (1-7에서 수정).

---

# [09] 커스터마이징

| 옵션/변수 | 기본값 | 설명 |
|-----------|--------|------|
| `-f` | (물어봄) | `jpg` 또는 `png`. 지정하면 물어보지 않음 |
| `-q` | `95` | JPG 품질 (1-100). 90이면 파일 크기 약 절반 |
| `SCALE` | `2` | 렌더링 배율. 1이면 일반, 2이면 고해상도(Retina급) |
| `WIDTH` | `1200` | 캔버스 너비(px). 좁은 다이어그램은 800, 넓은 건 1600 |
| `BG` | `white` | 배경색. PNG에서 `transparent`로 하면 투명 배경 |

`SCALE`, `WIDTH`, `BG`는 스크립트 상단(PART 2)에서 직접 수정한다.

---

# [10] 별도 환경 구성 스크립트

환경 구성만 미리 해두고 싶을 때 사용하는 독립 스크립트 `setup-mermaid-env.sh`도 제공된다. `mermaid2img.sh`의 PART 1과 동일한 내용이며, 환경 상태를 한눈에 확인할 수 있다.

```bash
chmod +x setup-mermaid-env.sh
./setup-mermaid-env.sh
```

```
========================================
  mermaid2img 환경 구성 스크립트
========================================

[✓] PATH 우선순위 정상
[✓] Node.js 설치됨: v22.x.x
[✓] mmdc 설치됨: OK
[✓] Chrome 발견: /home/kcloud/.cache/puppeteer/chrome/...
[✓] Python3 설치됨: Python 3.12.x
[✓] Pillow 설치됨
[✓] 한글 폰트 설치됨

========================================
  환경 구성 완료!
========================================
```

---

# [11] 정리

이 스크립트는 **환경 자동 구성 → mermaid 블록 추출 → mmdc로 렌더링 → 포맷 변환**이라는 파이프라인을 하나의 쉘 스크립트로 묶은 것이다. WSL PATH 문제, Node.js 버전, Chrome 라이브러리 누락 등 실제 환경에서 마주치는 문제를 모두 자동 처리하기 때문에, 아무것도 설치되어 있지 않은 Ubuntu에서도 한 줄이면 된다.

```bash
./mermaid2img.sh my-document.md
```
