---
title: "Jekyll 블로그 SEO 감사 — sitemap 품질 개선과 Google 색인 최적화 (2편)"
description: "sitemap에 저가치 URL 혼재, 검증 메타태그 누락, description 미설정 등 Google Search Console 등록 시 발견한 문제와 해결 방법"
excerpt: "sitemap에 카테고리/태그/pagination 페이지가 섞여 있으면 Google이 sitemap 전체를 저품질로 판단한다. 실제 감사 결과와 수정 방법 정리"
date: 2026-04-20
categories: Github_Blog
tags: [Jekyll, sitemap, SEO, Google-Search-Console, sitemap-false, description, 메타태그, 404, canonical, 색인최적화]
---

:bulb: [1편](/github_blog/jekyll-sitemap-google-indexing-fix/)에서 `_config.yml`의 `url`, `future`, `timezone` 누락 문제를 다뤘다. 이 글은 그 이후 **전체 저장소를 SEO 감사**하면서 발견한 추가 문제들과 해결 방법을 정리한다.
{: .notice--info}

**환경**: Jekyll 3.x + minimal-mistakes + GitHub Pages + jekyll-sitemap 플러그인

---

# [01] 감사 배경

1편에서 `url` 설정을 완료하고 sitemap이 올바른 도메인으로 생성되게 했지만, Google Search Console에 등록하기 전에 **sitemap 품질 자체**를 점검할 필요가 있었다.

실제로 sitemap.xml을 열어보니:

```
전체 119개 URL 중:
  ├── 포스트 URL: 85개 (71%) ← 가치 있는 콘텐츠
  ├── 카테고리 페이지: 17개 (14%) ← 목록일 뿐
  ├── 태그 페이지: 1개
  ├── pagination: 3개 (/page2/, /page3/)
  ├── 홈페이지: 1개
  └── 기타: 12개
```

Google 입장에서는 **"이 sitemap은 대부분 변화 없는 low-value URL + 일부 업데이트"**로 판단하여, 재읽기를 하지 않는다.

---

# [02] 발견한 문제 (5가지)

<pre class="mermaid">
graph TD
    AUDIT["전체 저장소 SEO 감사"] --> P1["① sitemap에<br/>저가치 URL 혼재"]
    AUDIT --> P2["② 검증 메타태그<br/>_config.yml에 미설정"]
    AUDIT --> P3["③ 9개 포스트<br/>description 누락"]
    AUDIT --> P4["④ 404 페이지<br/>미존재"]
    AUDIT --> P5["⑤ 빌드 출력(_site)<br/>localhost URL"]

    P1 --> S1["sitemap 신뢰도 ↓<br/>Google 재읽기 안 함"]
    P2 --> S2["HTML meta 태그<br/>렌더링 안 됨"]
    P3 --> S3["검색 결과에<br/>generic snippet 표시"]
    P4 --> S4["잘못된 URL 접근 시<br/>기본 404 (UX 저하)"]
    P5 --> S5["로컬 빌드 전용<br/>배포 시 자동 해결"]

    style P1 fill:#ffcccc,stroke:#c62828
    style P2 fill:#ffcccc,stroke:#c62828
    style P3 fill:#fff3e0,stroke:#e65100
    style P4 fill:#f5f5f5,stroke:#616161
    style P5 fill:#f5f5f5,stroke:#616161
</pre>

| 심각도 | 문제 | 영향 |
|--------|------|------|
| **CRITICAL** | sitemap에 카테고리/태그/pagination URL 포함 | sitemap 전체 품질 하락, Google 재읽기 안 함 |
| **CRITICAL** | `google_site_verification`, `naver_site_verification` 빈 값 | 인증 HTML 파일은 있지만 meta 태그 미렌더링 |
| **WARNING** | 9개 포스트에 `description` frontmatter 누락 | 검색 결과에 사이트 기본 설명("작업노트") 표시 |
| **INFO** | 커스텀 404 페이지 없음 | 잘못된 URL 접근 시 기본 페이지만 표시 |
| **INFO** | `_site/` 빌드 출력에 localhost URL | GitHub Pages 배포 시 자동 재빌드되므로 실제 영향 없음 |

---

# [03] 해결 ① — sitemap에서 저가치 URL 제거

## 3-1. 문제 분석

`jekyll-sitemap` 플러그인은 기본적으로 **모든 페이지**를 sitemap에 포함한다. 카테고리, 태그, pagination 페이지는 콘텐츠가 아닌 **목록 페이지**이므로 Google에 제출할 가치가 없다.

```
sitemap.xml에 포함되어서는 안 되는 URL:
  /categories/           ← 카테고리 목록
  /categories/linux      ← 개별 카테고리 아카이브
  /categories/git        ← 개별 카테고리 아카이브
  /tags/                 ← 태그 목록
  /page2/, /page3/       ← pagination
  /                      ← 홈페이지
```

## 3-2. 해결 방법

`jekyll-sitemap` 플러그인은 frontmatter에 **`sitemap: false`**가 있으면 해당 페이지를 sitemap에서 제외한다.

**수정 대상 파일 (19개):**

| 파일 | 설명 |
|------|------|
| `_pages/categories-archive.md` | 전체 카테고리 목록 |
| `_pages/categories/*.md` (16개) | 개별 카테고리 아카이브 |
| `_pages/tag-archive.md` | 태그 목록 |
| `index.html` | 홈페이지 |

**수정 방법 — frontmatter에 한 줄 추가:**

```yaml
# 수정 전
---
title: "Linux"
layout: archive
permalink: categories/linux
---

# 수정 후
---
title: "Linux"
layout: archive
permalink: categories/linux
sitemap: false              # ← 이 한 줄 추가
---
```

## 3-3. 적용 결과

```
수정 전: sitemap에 119개 URL (포스트 85 + 저가치 34)
수정 후: sitemap에 포스트 URL만 포함
```

---

# [04] 해결 ② — 검증 메타태그 설정

## 4-1. 문제 분석

Google Search Console과 Naver 웹마스터 도구의 **소유권 인증 파일**은 루트에 존재했지만, `_config.yml`의 검증 값이 비어 있어 **HTML meta 태그가 렌더링되지 않았다**.

```yaml
# 문제 상태
google_site_verification :    # ← 비어 있음
naver_site_verification  :    # ← 비어 있음
```

Minimal Mistakes 테마의 `seo.html`은 이 값이 있을 때만 meta 태그를 출력한다:

```html
{% raw %}{% if site.google_site_verification %}
  <meta name="google-site-verification" content="{{ site.google_site_verification }}" />
{% endif %}{% endraw %}
```

## 4-2. 해결 방법

인증 파일명에서 값을 추출하여 `_config.yml`에 설정한다.

```yaml
# 수정 후
google_site_verification : "google6751f2559208d5b3"
naver_site_verification  : "naver62d9a931d0465dfc21a3946c3128be56"
```

이렇게 하면 **인증 파일 + meta 태그** 두 가지 방법 모두로 소유권이 확인되어 더 안정적이다.

---

# [05] 해결 ③ — description 누락 포스트 보완

## 5-1. 문제 분석

전체 81개 포스트 중 **9개(11%)**에 `description` frontmatter가 없었다.

```
누락된 포스트:
  ├── claude-code-multi-agent-part1.md
  ├── claude-code-multi-agent-part2.md
  ├── claude-code-skill-hook-guide-part2.md
  ├── pip-error-no-module.md
  ├── pip-Ignoring-invaild-distribution.md
  ├── selenium-click-error.md
  ├── selenium-chromversion-error.md
  ├── django-simple-password.md
  └── not-null-constraint-failed.md
```

`description`이 없으면 SEO 템플릿이 `excerpt` → `site.description`("작업노트") 순서로 폴백하여, Google 검색 결과에 **내용과 무관한 generic snippet**이 표시된다.

## 5-2. 해결 방법

각 포스트의 내용을 기반으로 50~160자의 `description`과 `excerpt`를 추가한다.

```yaml
# 수정 전
---
title: "pip 'No module named pip' 오류 해결"
date: 2022-02-16
categories: Python
tags: [pip, error]
---

# 수정 후
---
title: "pip 'No module named pip' 오류 해결"
description: "pip 실행 시 'No module named pip' 오류가 발생할 때 get-pip.py로 재설치하여 해결하는 방법"
excerpt: "pip가 깨졌을 때 get-pip.py로 재설치하는 해결법"
date: 2022-02-16
categories: Python
tags: [pip, error]
---
```

---

# [06] 해결 ④ — 404 페이지 생성

## 6-1. 문제

커스텀 404 페이지가 없으면 GitHub Pages 기본 404가 표시되어 사용자가 사이트를 이탈할 확률이 높다.

## 6-2. 해결

루트에 `404.md` 생성:

```markdown
---
title: "페이지를 찾을 수 없습니다"
layout: single
permalink: /404.html
author_profile: true
sitemap: false
---

요청하신 페이지가 존재하지 않거나 이동되었습니다.

- [홈으로 돌아가기](/)
- [카테고리 보기](/categories/)
- [태그 보기](/tags/)
```

:bulb: `sitemap: false`를 설정하여 404 페이지 자체는 sitemap에 포함되지 않게 한다.
{: .notice--info}

---

# [07] 추가 작업 — C/C++ 포스트 아카이브 이동

감사 과정에서 2018년 C/C++ 포스트 20개가 sitemap에 포함되어 **"대부분 안 변하는 사이트"** 인상을 강화하고 있었다. 이 포스트들을 `_archive/` 디렉토리로 이동하여 빌드에서 제외했다.

```
_posts/program_language/c/    (8개)  → _archive/program_language/c/
_posts/program_language/c++/  (12개) → _archive/program_language/c++/
```

| 항목 | 처리 |
|------|------|
| 포스트 파일 | `_archive/`로 이동 (파일 보존, 빌드 제외) |
| 사이드바 | C, C++ 항목 제거 |
| 카테고리 페이지 | `_pages/categories/c.md`, `c++.md` 삭제 |
| sitemap | `_posts` 밖이므로 자동 제외 |
| 복구 방법 | `_archive/` → `_posts/`로 다시 이동하면 즉시 복원 |

---

# [08] 전체 변경 요약

<pre class="mermaid">
graph LR
    subgraph Before["수정 전"]
        B1["sitemap: 119개 URL<br/>(저가치 34개 포함)"]
        B2["검증 meta 태그: 미렌더링"]
        B3["description 누락: 9개"]
        B4["404: 기본 페이지"]
        B5["C/C++ 20개: sitemap 포함"]
    end

    subgraph After["수정 후"]
        A1["sitemap: 포스트만<br/>(고품질 URL만)"]
        A2["검증 meta 태그: 렌더링됨"]
        A3["description: 전체 100%"]
        A4["404: 커스텀 페이지"]
        A5["C/C++: _archive<br/>(빌드 제외)"]
    end

    B1 -->|sitemap: false| A1
    B2 -->|_config.yml 설정| A2
    B3 -->|frontmatter 추가| A3
    B4 -->|404.md 생성| A4
    B5 -->|_archive/ 이동| A5

    style Before fill:#ffcccc,stroke:#c62828
    style After fill:#e8f5e9,stroke:#2e7d32
</pre>

| # | 작업 | 수정 파일 수 |
|---|------|------------|
| ① | 카테고리/태그/홈에 `sitemap: false` | 19개 |
| ② | 검증 메타태그 설정 | 1개 (`_config.yml`) |
| ③ | description 누락 보완 | 9개 |
| ④ | 404 페이지 생성 | 1개 |
| ⑤ | C/C++ 아카이브 이동 | 22개 (포스트 20 + 카테고리 2) |
| | **합계** | **52개 파일** |

---

# [09] Google Search Console 등록 체크리스트

위 수정을 모두 적용한 뒤, Search Console 등록 전 최종 확인 항목이다.

| 확인 항목 | 확인 방법 | 기대 결과 |
|----------|----------|----------|
| sitemap URL | `https://cmaven.github.io/sitemap.xml` 접속 | 포스트 URL만 포함, localhost 없음 |
| canonical URL | 포스트 페이지 소스 보기 → `<link rel="canonical">` | `https://cmaven.github.io/...` |
| 검증 meta 태그 | 페이지 소스 → `google-site-verification` 검색 | meta 태그 존재 |
| robots.txt | `https://cmaven.github.io/robots.txt` 접속 | `Sitemap: https://cmaven.github.io/sitemap.xml` 포함 |
| 404 페이지 | 존재하지 않는 URL 접속 | 커스텀 404 표시 |
| Open Graph | 포스트 소스 → `og:title`, `og:description` 검색 | 각 포스트별 고유 값 |

:bulb: 1편의 `url`, `future`, `timezone` 설정과 이 글의 sitemap 품질 개선을 모두 적용하면, Google이 sitemap을 신뢰하고 정기적으로 재읽기할 가능성이 크게 높아진다.
{: .notice--info}
