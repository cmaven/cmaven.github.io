---
title: "Ubuntu 파일 압축·해제 완전 정리 — zip과 tar(gzip/bzip2)"
description: "Ubuntu/Linux에서 zip과 tar로 파일·디렉토리를 압축하고 해제하는 방법 총정리. zip/unzip 설치, 재귀 압축(-r), 숨김 파일 포함, tar.gz와 tar.bz2 비교 및 옵션 설명"
excerpt: "여러 파일은 zip -r, 디렉토리 묶음은 tar -czvf. gzip과 bzip2의 차이와 압축/해제 명령을 예제로 정리"
date: 2026-05-28
categories: Linux
tags: [Ubuntu, Linux, zip, unzip, tar, gzip, bzip2, 압축, 압축해제, tar-gz, tar-bz2, 명령어, 터미널]
ref: ubuntu-file-compression-zip-tar
---

:bulb: Linux에서 파일을 묶거나 전송할 때 가장 많이 쓰는 두 가지 방식이 `zip`과 `tar`다. `zip`은 Windows와의 호환성이 좋고, `tar`는 Linux/Unix 환경의 표준이다. 이 글은 두 방식의 압축·해제 명령을 예제와 함께 정리한다.
{: .notice--info}

**환경**: Ubuntu (apt 기반 배포판 공통)

---

# [01] zip / unzip 설치

Ubuntu에는 `zip`, `unzip`이 기본 설치되어 있지 않은 경우가 있다. 패키지 목록을 갱신한 뒤 설치한다.

```bash
sudo apt update
sudo apt install zip unzip -y
```

| 패키지 | 용도 |
|--------|------|
| `zip` | 파일·디렉토리를 `.zip`으로 압축 |
| `unzip` | `.zip` 파일을 해제 |

:memo: `tar`와 `gzip`은 대부분의 배포판에 기본 설치되어 있어 별도 설치가 필요 없다.
{: .notice--warning}

---

# [02] zip 으로 압축하기

## 2-1. 단일 파일 압축

`zip <결과파일> <대상파일>` 형식으로 사용한다.

```bash
zip archive.zip file.txt
```

## 2-2. 여러 파일·디렉토리 압축 (-r)

디렉토리를 포함하려면 **하위 폴더까지 재귀적으로 담는 `-r` 옵션**이 필요하다. `-r` 없이 디렉토리를 지정하면 폴더 안 파일이 빠진다.

```bash
zip -r archive.zip folder1 folder2 file1.txt
```

## 2-3. 숨김 파일까지 포함

`.bashrc` 같은 점(`.`)으로 시작하는 숨김 파일은 일반 패턴에 잡히지 않는다. `.[!.]*` 패턴을 함께 지정하면 숨김 파일도 포함된다.

```bash
zip -r archive.zip folder1 folder2 file1.txt .[!.]*
```

:bulb: `.[!.]*` 는 "점으로 시작하되, 두 번째 글자가 점이 아닌" 파일을 뜻한다. `.`(현재 디렉토리)과 `..`(상위 디렉토리)를 제외하면서 숨김 파일만 안전하게 포함하기 위한 패턴이다.
{: .notice--info}

| 옵션 | 설명 |
|------|------|
| `-r` | 디렉토리를 하위까지 재귀적으로 압축 |
| `-e` | 비밀번호로 암호화하여 압축 |
| `-1` ~ `-9` | 압축 강도 (1=빠름, 9=고압축) |
| `-q` | 진행 메시지 출력 안 함(quiet) |

---

# [03] unzip 으로 압축 해제

## 3-1. 현재 디렉토리에 해제

```bash
unzip archive.zip
```

## 3-2. 특정 디렉토리에 해제 (-d)

`-d` 옵션으로 압축을 풀 대상 경로를 지정한다. 디렉토리가 없으면 자동으로 생성된다.

```bash
unzip archive.zip -d /path/to/directory/
```

| 옵션 | 설명 |
|------|------|
| `-d <경로>` | 지정한 디렉토리에 압축 해제 |
| `-l` | 압축을 풀지 않고 내용물 목록만 확인 |
| `-o` | 기존 파일을 묻지 않고 덮어쓰기 |
| `-n` | 기존 파일은 건너뛰고 덮어쓰지 않음 |

---

# [04] tar — gzip vs bzip2

`tar`는 여러 파일을 하나로 묶는 도구이며, 보통 `gzip`(`.tar.gz`)이나 `bzip2`(`.tar.bz2`)와 결합해 압축까지 수행한다.

| 구분 | gzip (`.tar.gz`) | bzip2 (`.tar.bz2`) |
|------|------------------|--------------------|
| 압축률 | 중간 | 높음 |
| 속도 | 빠름 | 느림 |
| 결과 크기 | 보통 | 더 작음 |
| 특징 | 표준 포맷, 호환성·속도 우수 | CPU 사용량 많음 |

:bulb: 일반적으로 **호환성과 속도가 좋은 `tar.gz`를 많이 사용**한다. 용량을 최대한 줄여야 하고 시간 여유가 있다면 `tar.bz2`가 유리하다.
{: .notice--info}

---

# [05] tar.gz 압축·해제

## 5-1. 압축

```bash
tar -czvf archive.tar.gz file1.txt folder1
```

## 5-2. 해제

```bash
# 현재 디렉토리에 해제
tar -xzvf archive.tar.gz

# 특정 경로에 해제
tar -xzvf archive.tar.gz -C /path/to/target/
```

---

# [06] tar.bz2 압축·해제

`gzip`의 `z` 대신 `bzip2`를 뜻하는 **`j` 옵션**만 바꾸면 된다. 나머지 사용법은 동일하다.

## 6-1. 압축

```bash
tar -cjvf archive.tar.bz2 file1.txt folder1
```

## 6-2. 해제

```bash
# 현재 디렉토리에 해제
tar -xjvf archive.tar.bz2

# 특정 경로에 해제
tar -xjvf archive.tar.bz2 -C /opt/data/
```

---

# [07] tar 옵션 정리

| 옵션 | 의미 | 설명 |
|------|------|------|
| `c` | create | 새 아카이브 생성(압축) |
| `x` | extract | 아카이브 해제 |
| `t` | list | 압축 풀지 않고 목록만 보기 |
| `z` | gzip | gzip 압축/해제 (`.tar.gz`) |
| `j` | bzip2 | bzip2 압축/해제 (`.tar.bz2`) |
| `v` | verbose | 처리 과정을 화면에 출력 |
| `f` | file | 아카이브 파일명 지정 (항상 마지막) |
| `-C` | change dir | 해제할 대상 디렉토리 지정 |

:warning: `f` 옵션은 항상 파일명 바로 앞(마지막)에 와야 한다. `tar -cvzf` 처럼 순서를 섞어도 동작하지만, 관례적으로 `tar -czvf <파일명>` 형태로 작성한다.
{: .notice--warning}

---

# [08] 정리 — 언제 무엇을 쓸까

| 상황 | 추천 |
|------|------|
| Windows와 주고받기 | `zip` (호환성 최고) |
| Linux 간 디렉토리 백업·전송 | `tar.gz` (표준, 빠름) |
| 용량을 최대한 줄여야 할 때 | `tar.bz2` (고압축) |
| 단순히 파일 몇 개만 묶기 | `zip` |

:bulb: 핵심만 기억하자. **여러 파일·폴더는 `zip -r`**, **디렉토리 묶음 백업은 `tar -czvf`**. 해제는 압축 옵션의 `c`를 `x`로 바꾸면 된다.
{: .notice--info}
