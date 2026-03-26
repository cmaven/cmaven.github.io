---
title: "WSL 터미널 색상 설정 가이드 — 검은 화면 해결하기"
description: "Windows Terminal에서 WSL Ubuntu를 열었을 때 검은 배경이 나오는 원인과 보라색 Ubuntu 테마 적용 방법"
excerpt: "WSL 프로필과 Ubuntu 프로필의 색 구성표 차이를 이해하고, 원하는 배경색을 설정하는 방법"
date: 2026-03-26
categories: Windows
tags: [WSL, Windows-Terminal, 색상설정, Ubuntu, Color-Scheme, settings.json, 터미널]
---

:bulb: Windows Terminal에서 WSL을 열었을 때 검은 화면이 나오는 원인과, Ubuntu 보라색 배경 테마를 적용하는 방법을 정리한다.
{: .notice--info}

# [01] 문제 상황

Windows에서 WSL을 설치하고 시작 메뉴에서 검색하여 실행하면 Windows Terminal이 열린다.

드롭다운 메뉴를 보면 Windows PowerShell, 명령 프롬프트, Ubuntu 등 여러 프로필이 보인다.

- **Ubuntu 탭을 직접 열면** → 익숙한 **보라색 배경**의 터미널이 나타남
- **WSL을 기본으로 열면** → **검은 배경**이 나타남

기본 프로필을 Ubuntu로 바꿨는데도 여전히 검은 배경이 나오는 경우가 있다.

---

# [02] 원인: 프로필별 색 구성표

Windows Terminal은 **프로필마다 독립적인 색 구성표(Color Scheme)**를 가지고 있다.

| 프로필 | 기본 색 구성표 | 배경색 |
|--------|---------------|--------|
| WSL 프로필 | 기본(Campbell) | 검은색 |
| Ubuntu 프로필 | Ubuntu 전용 | 보라색 (`#300A24`) |

기본 프로필을 Ubuntu로 바꿔도, WSL 프로필의 색상이 적용되면 검은 화면이 나올 수 있다.

---

# [03] 해결 방법

## 3-1. 기본 프로필을 Ubuntu로 변경

Windows Terminal 설정(`Ctrl + ,`)을 열고, **시작** 탭에서 **기본 프로필**을 `Ubuntu`로 변경한다.

이렇게 하면 터미널을 열 때 Ubuntu 프로필이 자동으로 선택된다.

## 3-2. 색 구성표 확인 및 변경

기본 프로필을 바꿨는데도 검은 화면이라면, Ubuntu 프로필의 색 구성표를 직접 설정해야 한다.

### (A) GUI로 변경

1. 설정(`Ctrl + ,`) 열기
2. 좌측 프로필 목록에서 **Ubuntu** 클릭
3. **모양(외형)** 탭 선택
4. **색 구성표**를 `One Half Dark` 또는 원하는 것으로 변경
5. 배경색을 수동으로 `#300A24`(우분투 기본 보라색)로 설정

### (B) settings.json으로 변경

설정 화면 좌측 하단의 `JSON 파일 열기`를 클릭하고, Ubuntu 프로필 항목에 다음을 추가한다.

```json
{
    "name": "Ubuntu",
    "background": "#300A24",
    "colorScheme": "One Half Dark"
}
```

## 3-3. 저장 및 확인

설정을 저장하면 즉시 적용된다. 새 탭을 열어서 보라색 배경이 나오는지 확인한다.

---

# [04] 나만의 색 구성표 만들기

기본 제공 색 구성표가 마음에 들지 않는다면, `settings.json`의 `schemes` 배열에 커스텀 구성표를 추가할 수 있다.

```json
{
    "name": "Ubuntu Custom",
    "background": "#300A24",
    "foreground": "#EEEEEC",
    "cursorColor": "#FFFFFF",
    "black": "#2E3436",
    "red": "#CC0000",
    "green": "#4E9A06",
    "yellow": "#C4A000",
    "blue": "#3465A4",
    "purple": "#75507B",
    "cyan": "#06989A",
    "white": "#D3D7CF",
    "brightBlack": "#555753",
    "brightRed": "#EF2929",
    "brightGreen": "#8AE234",
    "brightYellow": "#FCE94F",
    "brightBlue": "#729FCF",
    "brightPurple": "#AD7FA8",
    "brightCyan": "#34E2E2",
    "brightWhite": "#EEEEEC"
}
```

추가한 뒤 Ubuntu 프로필의 `colorScheme`을 `"Ubuntu Custom"`으로 지정하면 된다.

---

# [05] 정리

| 설정 | 위치 | 효과 |
|------|------|------|
| 기본 프로필 변경 | 설정 → 시작 → 기본 프로필 | 터미널 실행 시 Ubuntu가 바로 열림 |
| 색 구성표 변경 | 설정 → Ubuntu → 모양 | 배경색, 글자색 등 테마 적용 |
| 배경색 직접 지정 | settings.json → background | 원하는 색상으로 정밀 제어 |

핵심은 **"기본 프로필"과 "색 구성표"는 별개 설정**이라는 점이다. 기본 프로필을 Ubuntu로 바꾸는 것과 색상을 맞추는 것, 두 가지를 모두 확인하면 원하는 터미널 환경을 만들 수 있다.
