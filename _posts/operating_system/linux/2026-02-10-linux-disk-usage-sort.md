---
title: "디렉토리 용량 크기별로 정렬하여 출력하기 (du + sort)"
description: "Ubuntu/Linux에서 du 명령어와 sort를 조합해 디렉토리별 용량을 크기순으로 정렬하여 확인하는 방법 정리"
excerpt: "du -h --max-depth=1 | sort -hr 명령어로 디렉토리 용량을 한눈에 파악하는 방법"
date: 2026-02-10
categories: Linux
tags: [Linux, Ubuntu, du, sort, 디스크용량, 디렉토리, 용량확인]
---

:bulb: Linux 서버에서 디스크 용량이 부족할 때, 어느 디렉토리가 큰지 빠르게 파악하는 `du` + `sort` 조합을 정리한다.
{: .notice--info}

# [01] 현재 디렉토리 용량 확인

## 1-1. 기본 명령어

현재 위치한 디렉토리의 하위 폴더를 **용량 큰 순서대로** 출력한다.

```bash
du -h --max-depth=1 | sort -hr
```

| 옵션 | 설명 |
|---|---|
| `du -h` | 용량을 사람이 읽기 쉬운 단위(K, M, G)로 표시 |
| `--max-depth=1` | 현재 디렉토리 바로 아래 수준까지만 표시 |
| `sort -h` | 사람이 읽기 쉬운 단위를 고려한 정렬 (K < M < G) |
| `sort -r` | 내림차순 정렬 (큰 것부터) |

**출력 예시:**

```
15G     .
8.2G    ./data
4.1G    ./logs
2.3G    ./backup
512M    ./config
```

## 1-2. 특정 디렉토리 지정

`/var` 자리에 원하는 경로를 넣어 특정 디렉토리를 분석할 수 있다.

```bash
du -h --max-depth=1 /var | sort -hr
```

---

# [02] 디렉토리만 필터링

## 2-1. 파일 제외, 디렉토리만 출력

`grep`을 추가하면 파일을 제외하고 디렉토리 항목만 볼 수 있다.

```bash
du -h --max-depth=1 | grep '/$' | sort -hr
```

:bulb: `grep '/$'`는 `/`로 끝나는 항목(디렉토리)만 필터링한다.
{: .notice--info}

## 2-2. depth 조정

`--max-depth` 값을 높이면 더 깊은 하위 디렉토리까지 확인할 수 있다.

```bash
# 2단계 깊이까지 확인
du -h --max-depth=2 | sort -hr | head -20
```

:bulb: `head -20`을 붙이면 상위 20개만 출력해 가독성을 높일 수 있다.
{: .notice--info}

---

# [03] 활용 예시

## 3-1. 루트 디렉토리에서 큰 폴더 찾기

디스크 용량 부족 시 가장 먼저 실행할 명령어다.

```bash
sudo du -h --max-depth=1 / | sort -hr | head -15
```

:warning: 루트(`/`) 탐색 시 `sudo`가 필요하며, 시간이 걸릴 수 있다.
{: .notice--warning}

## 3-2. 홈 디렉토리 정리

```bash
du -h --max-depth=1 ~ | sort -hr
```

## 3-3. 로그 디렉토리 점검

```bash
sudo du -h --max-depth=2 /var/log | sort -hr | head -10
```
