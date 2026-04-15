---
title: "Linux Firefox 한글 깨짐 해결 — 로케일이 아니라 폰트를 확인하세요"
description: "Ubuntu Firefox에서 한글이 네모(□)로 깨져 보일 때, 로케일 설정이 정상임에도 발생하는 폰트 문제의 원인과 해결 방법"
excerpt: "fc-list :lang=ko 결과가 코딩 폰트뿐이라면 — fonts-noto-cjk, fonts-nanum 설치로 한글 렌더링 해결"
date: 2026-04-15
categories: Linux
tags: [Ubuntu, Firefox, 한글깨짐, 폰트, fontconfig, fc-list, fc-cache, Noto-CJK, 나눔폰트, fonts-noto-cjk]
---

:bulb: Linux 서버의 Firefox에서 한글이 깨져 보이는 문제는 로케일이 아닌 **폰트 부재**가 원인인 경우가 대부분이다. 진단 과정과 해결 방법을 정리한다.
{: .notice--info}

**환경**: Ubuntu 22.04 LTS + Firefox snap 149.0.2 + X11 포워딩

---

# [01] 문제 상황

X11 포워딩으로 Firefox를 실행했을 때, 웹페이지의 한글이 모두 **네모(□), 물음표(?), 빈칸**으로 표시됐다.

- 영문 텍스트는 정상
- 터미널에서 한글 입력/출력은 정상
- 로케일은 `ko_KR.UTF-8`으로 설정됨

처음엔 인코딩이나 로케일 문제라고 생각했지만, 실제 원인은 전혀 다른 곳에 있었다.

---

# [02] 진단 과정

## 2-1. 로케일 확인 — 정상

```bash
$ locale
LANG=ko_KR.UTF-8
LANGUAGE=ko_KR:ko
LC_ALL=ko_KR.UTF-8
LC_CTYPE=ko_KR.UTF-8
...
```

로케일은 완벽하게 한글로 설정되어 있었다. **문제는 인코딩이 아니었다.**

## 2-2. 설치된 한글 폰트 확인 — 원인 발견

```bash
$ fc-list :lang=ko
/home/user/.local/share/fonts/D2CodingLigatureNerdFontMono-Regular.ttf: D2CodingLigature Nerd Font Mono:style=Regular
/home/user/.local/share/fonts/D2CodingLigatureNerdFontPropo-Bold.ttf: D2CodingLigature Nerd Font Propo:style=Bold
/home/user/.local/share/fonts/D2CodingLigatureNerdFont-Bold.ttf: D2CodingLigature Nerd Font:style=Bold
/home/user/.local/share/fonts/D2CodingLigatureNerdFontMono-Bold.ttf: D2CodingLigature Nerd Font Mono:style=Bold
/home/user/.local/share/fonts/D2CodingLigatureNerdFontPropo-Regular.ttf: D2CodingLigature Nerd Font Propo:style=Regular
/home/user/.local/share/fonts/D2CodingLigatureNerdFont-Regular.ttf: D2CodingLigature Nerd Font:style=Regular
```

한글 폰트가 **6개뿐이고, 모두 D2Coding(코딩 전용 폰트)**이었다. 웹 브라우저가 요청하는 `sans-serif`, `serif` 계열 한글 폰트가 전혀 없었다.

---

# [03] 왜 코딩 폰트만으로는 안 되는가

## 3-1. 로케일 문제 vs 폰트 문제

| 구분 | 로케일 문제 | 폰트 문제 |
|------|-----------|-----------|
| 원인 | UTF-8 인코딩 미인식 | 글리프를 그릴 폰트 없음 |
| 증상 | 한글 자체가 표시 안 됨 | 네모(□), 물음표(?) 표시 |
| 터미널 한글 | 안 됨 | 됨 |
| `locale` 확인 | 문제 있음 | 정상 |

이 경우는 **명백한 폰트 문제**였다. UTF-8 디코딩은 정상이지만, 한글 글리프를 그릴 폰트가 없었다.

## 3-2. fontconfig 폴백 메커니즘

웹페이지가 `sans-serif` 폰트를 요청할 때, fontconfig는 다음 순서로 폰트를 찾는다:

```
웹페이지 CSS: "font-family: -apple-system, sans-serif"
    ↓
fontconfig: sans-serif 카테고리에서 한글 폰트 검색
    ↓
없음 → 영문 sans-serif로 폴백
    ↓
그마저도 한글 지원 안 됨 → 다른 카테고리로 폴백
    ↓
D2Coding (monospace) 선택 → 한글 글리프 일부만 포함
    ↓
렌더링 실패 → □, ?, 빈칸
```

D2Coding은 **터미널 코드 표시용 모노스페이스 폰트**로, 웹 렌더링에 필요한 모든 한글 문자를 포함하지 않는다.

---

# [04] 해결 — 한글 폰트 설치

## 4-1. 폰트 패키지 설치

```bash
sudo apt-get update
sudo apt-get install -y fonts-noto-cjk fonts-nanum fonts-nanum-extra
```

| 패키지 | 주요 폰트 | 용도 |
|--------|----------|------|
| `fonts-noto-cjk` | Noto Sans CJK, Noto Serif CJK | Google CJK 통합 폰트, 웹 표준 |
| `fonts-nanum` | 나눔고딕, 나눔명조, 나눔고딕코딩 | 한국어 대표 폰트, 가독성 우수 |
| `fonts-nanum-extra` | 나눔스퀘어, 나눔스퀘어라운드 등 | 모던 UI 디자인용 |

## 4-2. 폰트 캐시 갱신

```bash
fc-cache -fv
```

## 4-3. 설치 결과 확인

```bash
$ fc-list :lang=ko | wc -l
69
```

설치 전 6개 → 설치 후 **69개**의 한글 폰트가 등록됐다.

```bash
$ fc-list :lang=ko | grep -E '(Noto Sans|Noto Serif|나눔고딕|나눔명조)' | head -6
/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc: Noto Sans CJK KR:style=Regular
/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc: Noto Sans CJK KR:style=Bold
/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc: Noto Serif CJK KR:style=Regular
/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc: Noto Serif CJK KR:style=Bold
/usr/share/fonts/truetype/nanum/NanumGothic.ttf: 나눔고딕:style=Regular
/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf: 나눔명조:style=Regular
```

## 4-4. Firefox 재시작

```bash
pkill -f firefox
firefox &
```

한글이 정상적으로 렌더링된다.

---

# [05] fontconfig 주요 명령어

| 명령어 | 설명 |
|--------|------|
| `fc-list` | 전체 설치된 폰트 목록 |
| `fc-list :lang=ko` | 한글 폰트만 조회 |
| `fc-list :lang=ko \| wc -l` | 한글 폰트 개수 |
| `fc-list \| grep "Noto Sans"` | 특정 폰트 패밀리 검색 |
| `fc-cache -fv` | 폰트 캐시 강제 갱신 (상세 출력) |
| `fc-cache -fr` | 폰트 캐시 초기화 (재구성) |
| `fc-cache -fv ~/.local/share/fonts/` | 특정 디렉토리만 갱신 |

---

# [06] 서버 초기 설정 체크리스트

:bulb: 새로운 Linux 서버에서 GUI 앱을 사용할 계획이라면, 초기 구성 시 아래 항목을 확인한다.
{: .notice--info}

```bash
# 1. 로케일 확인
locale | grep LANG

# 2. 한글 폰트 설치
sudo apt-get install -y fonts-noto-cjk fonts-nanum fonts-nanum-extra

# 3. 폰트 캐시 갱신
fc-cache -fv

# 4. 설치 확인 (최소 5개 이상이면 정상)
fc-list :lang=ko | wc -l
```

---

# [07] 정리

| 상황 | 추천 폰트 |
|------|----------|
| 일반 웹 렌더링 | Noto Sans CJK (가장 포괄적) |
| 문서, 보고서 | 나눔고딕, 나눔명조 |
| 모던 UI | 나눔스퀘어 |
| 코딩, 터미널 | D2Coding, 나눔고딕코딩 |

:warning: **로케일이 완벽해도 폰트가 없으면 한글이 깨진다.** `fc-list :lang=ko`로 확인했을 때 코딩 폰트만 나온다면, `fonts-noto-cjk`와 `fonts-nanum`을 설치해야 한다.
{: .notice--warning}
