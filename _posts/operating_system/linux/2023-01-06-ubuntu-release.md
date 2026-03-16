---
title: "Ubuntu Release(LTS, ESM)"
description: "Ubuntu 릴리즈 주기, LTS와 interim 차이, ESM 확장 보안 유지보수 정리"
excerpt: "Ubuntu LTS 2년 주기 릴리즈, 5년 기본 지원, ESM 10년 보안 유지보수 정리"
categories: Linux
tags: [Ubuntu, LTS, ESM, Release, 릴리즈, 보안패치, 버전관리]
date: 2023-01-06
---

:bulb: Ubuntu Release 주기, LTS와 interim의 차이, ESM(확장 보안 유지보수)에 대해 정리한다.
{: .notice--info}

# [01] LTS(Long Term Support)와 interim

Ubuntu는 2가지 Release 타입을 지원한다.

- Release 버전은 Year.Month
  - ex) Ubuntu 20.10 은 2020년 10월에 Release

| 타입 | 주기 | 지원 기간 | 특징 |
|---|---|---|---|
| LTS | 2년 주기, 4월 Release | 5년 (기본) | `enterprise grade` = 안정화 버전 |
| interim | 6개월 주기 | 9개월 | `production-quality`, 신규 기능 및 오픈소스 시험용 |

# [02] ESM(Extended Security Maintenance)

LTS Release의 경우, 10년 동안 아래 사항을 지원한다.

- 기본 패키지 관리
- 보안 패치(Security Updates)
  - 커널 라이브패치(Kernel Live Patch)
- 초기 5년은 기본 제공
- 이후 5년은 ESM으로 제공
  - 무료: personal subscription(개인 사용자)
  - 유료: Ubuntu Advantage subscription(그 외)

# [03] Release Plan

2023.01.06 기준:

![2023-01-06 14 11 54](https://user-images.githubusercontent.com/76153041/210934649-ea8e88d0-ebf5-469e-8440-80131416b042.png)

LTS, ESM 기간 및 비용 정보:

![2023-01-06 14 12 02](https://user-images.githubusercontent.com/76153041/210934650-ecb1b907-a3ce-4b44-b17b-8b30b7afb789.png)
