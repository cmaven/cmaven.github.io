---
title: "Git LF/CRLF 줄바꿈 Warning 원인과 해결 방법"
description: "Git에서 발생하는 LF will be replaced by CRLF 경고의 원인과 .gitattributes, core.autocrlf 설정을 통한 해결 방법"
excerpt: "Windows와 Linux 간 줄바꿈 문자(LF/CRLF) 차이로 인한 Git warning 원인 분석과 .gitattributes, core.autocrlf 설정을 통한 해결 방법 정리"
date: 2026-03-18
categories: Git
tags: [Git, CRLF, LF, gitattributes, autocrlf, 줄바꿈, line-ending, Windows, Linux]
---

:bulb: Git에서 파일을 add할 때 발생하는 `LF will be replaced by CRLF` 경고의 원인과 해결 방법을 작성한다.
{: .notice--info}

# [01] Warning 메시지

```bash
git add 파일명
```

```
warning: in the working copy of '파일명', LF will be replaced by CRLF the next time Git touches it
```

# [02] 원인: OS별 줄바꿈 문자 차이

운영체제마다 텍스트 파일의 줄바꿈(개행) 문자가 다르다.

| OS | 줄바꿈 문자 | 표기 |
|---|---|---|
| Windows | CR + LF | `\r\n` |
| Linux / macOS | LF | `\n` |

- **CR** (Carriage Return): 커서를 줄의 맨 앞으로 이동
- **LF** (Line Feed): 커서를 다음 줄로 이동

Git은 내부적으로 **LF**를 표준으로 사용한다. Windows 환경에서 `core.autocrlf` 설정이 `true`인 경우, checkout 시 LF를 CRLF로 자동 변환하겠다는 의미로 위 경고가 발생한다.

# [03] core.autocrlf 설정값

```bash
# 현재 설정 확인
git config --global core.autocrlf
```

| 값 | checkout (저장소 → 작업 디렉토리) | commit (작업 디렉토리 → 저장소) | 권장 환경 |
|---|---|---|---|
| `true` | LF → CRLF 변환 | CRLF → LF 변환 | Windows 전용 프로젝트 |
| `input` | 변환 없음 | CRLF → LF 변환 | Linux/macOS, 또는 크로스 플랫폼 |
| `false` | 변환 없음 | 변환 없음 | 줄바꿈을 직접 관리할 때 |

# [04] 해결 방법

## 방법 A: `.gitattributes` 파일 설정 (권장)

레포지토리 루트에 `.gitattributes` 파일을 생성하거나 편집하여 아래 내용을 추가한다.

```
* text=auto eol=lf
```

| 속성 | 설명 |
|---|---|
| `text=auto` | Git이 텍스트 파일을 자동 감지하여 줄바꿈 정규화 |
| `eol=lf` | 모든 텍스트 파일의 줄바꿈을 LF로 통일 |

> `.gitattributes`는 레포지토리에 포함되어 **모든 협업자에게 동일하게 적용**되므로, 개인 설정(`core.autocrlf`)보다 우선하며 일관성이 보장된다.
{: .notice--info}

## 방법 B: Git 전역 설정 변경

```bash
git config --global core.autocrlf input
```

커밋 시에만 CRLF → LF 변환을 수행하고, checkout 시에는 변환하지 않는다. warning이 사라진다.

> 이 설정은 **개인 환경에만 적용**되므로, 팀 프로젝트에서는 `.gitattributes` 방식을 권장한다.
{: .notice--warning}

# [05] 기존 파일 줄바꿈 일괄 정규화

`.gitattributes` 설정 후 기존 파일에도 적용하려면 아래 명령어를 실행한다.

```bash
# Git 인덱스 초기화 후 다시 추가
git rm --cached -r .
git reset --hard
```

이후 변경된 파일이 있으면 커밋하면 된다.

# [06] 정리

| 방법 | 적용 범위 | 장점 |
|---|---|---|
| `.gitattributes` | 레포지토리 전체 (모든 협업자) | 일관성 보장, Git에 포함 |
| `core.autocrlf` | 개인 환경 | 간편한 설정 |

**크로스 플랫폼 프로젝트에서는 `.gitattributes`에 `* text=auto eol=lf`를 설정하는 것이 가장 안정적인 방법이다.**
