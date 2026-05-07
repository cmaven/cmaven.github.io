---
title: "Jekyll SEO 4편 — Search Console 이슈 정리 (404·redirect·noindex)"
description: "1~3편을 적용하고 sitemap을 등록한 뒤 Google Search Console에 남는 4가지 분류(찾을 수 없음, 리디렉션 포함, 크롤링됨-색인 안 됨, 신규 미색인)를 케이스별로 진단하고 noindex 메타태그·navigation trailing slash로 정리하는 방법"
excerpt: "SEO 시리즈 4편. Search Console에 남는 잔여 이슈를 4가지 분류로 진단하고, seo.html에 noindex 자동 출력 로직과 navigation trailing slash 수정으로 깔끔하게 마무리한다"
date: 2026-05-03
categories: Github_Blog
tags: [Jekyll, SEO, Google-Search-Console, noindex, robots-meta, redirect, 404, trailing-slash, minimal-mistakes, SEO-시리즈-4편, SEO-시리즈]
---

:bulb: SEO 시리즈 4편. **[1편](/github_blog/gitblog-seo-google-search/)** 의 포스트 단위 SEO, **[2편](/github_blog/jekyll-sitemap-google-indexing-fix/)** 의 `_config.yml` 3줄 수정으로 sitemap 갱신 확보, **[3편](/github_blog/jekyll-sitemap-seo-audit-fix/)** 의 사이트 단위 sitemap 감사를 모두 적용해도 Google Search Console의 색인 보고서에는 여전히 **이슈로 분류되는 URL**이 남는다. 이 글은 그 잔여 이슈를 4가지 분류로 진단하고, **`noindex` 메타태그 자동 출력**과 **navigation trailing slash 정리**로 마무리하는 과정을 정리한다.
{: .notice--info}

:bulb: **SEO 시리즈 구성**
- **[1편](/github_blog/gitblog-seo-google-search/)** — 포스트 단위 SEO: frontmatter, `jekyll-seo-tag`, permalink·파일명
- **[2편](/github_blog/jekyll-sitemap-google-indexing-fix/)** — sitemap이 제대로 갱신되도록: `_config.yml`의 url·future·timezone 3줄 진단·수정
- **[3편](/github_blog/jekyll-sitemap-seo-audit-fix/)** — 사이트 단위 SEO 감사: sitemap 품질, 검증 메타태그, 누락 description 일괄 보강, 404/아카이브 정리
- **4편 (이 글)** — Google Search Console 잔여 이슈 정리: 404·리디렉션·"크롤링됨-색인 안 됨" 분류 진단과 `noindex` 메타태그 적용
{: .notice}

**환경**: Jekyll 3.x + minimal-mistakes + GitHub Pages + jekyll-sitemap 플러그인

---

# [01] 배경 — 1~3편을 끝냈는데도 남는 이슈

1~3편을 모두 적용한 뒤 Search Console에 sitemap을 재제출하고 몇 주가 지나면, 색인 보고서에 다음과 같은 분류가 쌓이기 시작한다.

| Search Console 분류 | 의미 |
|--------------------|------|
| 찾을 수 없음(404) | 과거에 색인됐던 URL이 지금은 404로 응답 |
| 리디렉션이 포함된 페이지 | URL이 다른 URL로 301/302 응답 → 색인 후보에서 제외 |
| 크롤링됨 - 현재 색인이 생성되지 않음 | Googlebot이 본문은 받았지만 색인 가치가 낮다고 판단 |
| 검색됨 - 현재 색인이 생성되지 않음 | sitemap에서 URL은 봤지만 아직 크롤링 안 함 |

이 분류들은 모두 **사이트 측 문제 신호일 수도 있고, Google의 정상적 판단일 수도 있다.** 케이스별로 끊어 보지 않으면 "왜 안 잡히지?"만 반복하게 된다.

<pre class="mermaid">
graph TD
    GSC["Google Search Console<br/>색인 이슈 보고서"] --> C1["① 찾을 수 없음(404)"]
    GSC --> C2["② 리디렉션이 포함된 페이지"]
    GSC --> C3["③ 크롤링됨 - 색인 안 됨"]
    GSC --> C4["④ 검색됨 - 크롤링 안 됨"]

    C1 --> A1["삭제된 옛 글<br/>→ 정상 (de-index 대기)"]
    C2 --> A2["내부 링크에 trailing slash 누락<br/>→ navigation 수정"]
    C3 --> A3["저가치 archive 페이지<br/>→ noindex 메타태그"]
    C3 --> A4["신규 포스트<br/>→ 정상 (인덱싱 대기)"]
    C4 --> A5["크롤링 예산<br/>→ 색인 요청"]

    style C1 fill:#fff3e0,stroke:#e65100
    style C2 fill:#ffcccc,stroke:#c62828
    style C3 fill:#ffcccc,stroke:#c62828
    style C4 fill:#fff3e0,stroke:#e65100
    style A2 fill:#e8f5e9,stroke:#2e7d32
    style A3 fill:#e8f5e9,stroke:#2e7d32
</pre>

이 글에서는 **"사이트 측에서 정리할 수 있는 케이스"** 인 ②·③(저가치 archive)을 코드 수정으로 마무리하고, ①·③(신규 포스트)·④는 왜 손대지 않아도 되는지 정리한다.

---

# [02] 케이스 ① — 찾을 수 없음(404)

## 2-1. 증상

```
https://cmaven.github.io/c++/C++-Class/             → 404
https://cmaven.github.io/c/C-Memory-Structure-Malloc/ → 404
```

3편에서 C/C++ 옛 글들을 `_archive/` 디렉토리로 옮겨 빌드에서 제외했다. 그 결과 위 URL들은 정상적으로 404를 응답하지만, Google 인덱스에는 옛 데이터가 남아 있어 Search Console이 **"찾을 수 없음(404)"** 으로 보고한다.

## 2-2. 진단 — 정상 동작

| 점검 항목 | 결과 |
|----------|------|
| 파일이 `_posts/` 안에 존재? | 아니오 (`_archive/`로 이동 완료) |
| GitHub Pages가 404를 반환? | 예 (정상) |
| 다른 페이지에서 이 URL로 링크? | 아니오 (사이드바·카테고리 페이지 모두 정리됨) |

**"삭제된 글에 대해 404를 반환"** 은 Google이 인덱스에서 자연스럽게 빼라고 의도한 신호다. 별도 코드 수정은 필요 없다.

## 2-3. 더 빨리 정리하고 싶다면

Search Console → **삭제(Removals)** 도구 → **임시 URL 삭제 요청** 으로 6개월간 검색 결과에서 숨길 수 있다. 그동안 Google이 재크롤하면서 자연스럽게 인덱스에서 제거된다.

:bulb: 410(Gone) 응답이 404보다 de-index 신호로 더 강하지만, GitHub Pages는 사용자 정의 HTTP 상태 코드를 지원하지 않는다. 404 그대로 두면 된다.
{: .notice--info}

---

# [03] 케이스 ② — 리디렉션이 포함된 페이지

## 3-1. 증상

```
https://cmaven.github.io/categories  → "리디렉션이 포함된 페이지"
```

Search Console은 `/categories`(trailing slash 없음)에 접근했는데 GitHub Pages가 **301로 `/categories/`(trailing slash 있음)** 로 보낸 것을 보고, 색인 후보에서 제외한다.

## 3-2. 원인 — 내부 링크가 slash 없는 형태로 걸려 있음

`_data/navigation.yml`을 보면 메인 메뉴가 trailing slash 없이 적혀 있었다.

```yaml
# 수정 전
- title: "Categories"
  url: /categories
- title: "Tags"
  url: /tags
```

반면 실제 페이지의 permalink는 다음과 같다.

```yaml
# _pages/categories-archive.md
permalink: /categories/   # ← trailing slash 있음

# _pages/tag-archive.md
permalink: /tags/         # ← trailing slash 있음
```

GitHub Pages는 `/categories` → `/categories/` 로 자동 301 리디렉트한다. 사용자 입장에서는 문제 없지만, **Googlebot은 리디렉트되는 URL을 색인하지 않는다.** 사이트 안에서 리디렉트되는 URL을 메인 메뉴에 그대로 두면 Search Console이 **"리디렉션이 포함된 페이지"** 로 계속 보고한다.

## 3-3. 해결 — navigation에 trailing slash 추가

```yaml
# _data/navigation.yml (수정 후)
- title: "Categories"
  url: /categories/    # ← trailing slash 추가
- title: "Tags"
  url: /tags/          # ← trailing slash 추가
```

| 변경 전 | 변경 후 | 효과 |
|--------|--------|------|
| `/categories` (301 리디렉트) | `/categories/` (200) | Googlebot이 리디렉트 없이 직접 도달 |
| `/tags` (301 리디렉트) | `/tags/` (200) | 동일 |

:bulb: trailing slash 정책은 사이트 전체에서 일관되게 유지하는 것이 중요하다. permalink가 `/foo/` 형태라면 모든 내부 링크도 `/foo/` 형태로 통일해야 한다.
{: .notice--info}

---

# [04] 케이스 ③ — 크롤링됨, 현재 색인이 생성되지 않음

이 분류가 가장 헷갈린다. **"Googlebot이 페이지를 받아갔지만 색인은 안 함"** 이라는 뜻인데, 이유가 여러 가지다. 이번 사이트의 경우 3가지 하위 케이스로 갈렸다.

## 4-1. (a) 저가치 archive 페이지 — 사이트 측에서 정리해야 함

대상 URL:

```
/categories/         (전체 카테고리 목록)
/categories/docker   (개별 카테고리 아카이브)
/tags                (태그 목록)
/page7/              (pagination)
```

이 페이지들의 공통점:

| 특성 | 설명 |
|------|------|
| 콘텐츠 자체가 **목록** | 다른 포스트로 이동하기 위한 허브일 뿐 |
| 본문에 **고유 텍스트가 거의 없음** | 제목 + 링크 리스트 |
| 같은 정보가 **여러 URL에 중복** | sitemap.xml + 카테고리 페이지 + 태그 페이지에 동일 포스트 링크 |

Google 입장에서는 "크롤은 했지만 색인할 가치는 없는 페이지"이며, 이 분류로 계속 쌓인다. 3편에서 `sitemap: false`를 적용해 sitemap에서 제외했지만, **`sitemap: false`는 sitemap에서만 빼는 것일 뿐, Googlebot이 내부 링크를 따라가서 크롤하는 것을 막지는 못한다.**

해결책: **`<meta name="robots" content="noindex,follow">`** 메타태그를 출력해서 Google에게 명시적으로 "이 페이지는 색인하지 마라(단, 링크는 따라가도 좋다)" 고 신호를 보낸다.

## 4-2. (b) 신규 포스트 — 정상 (인덱싱 대기)

```
/claude/claude-code-skill-hook-guide-part1/   (크롤링 날짜: 2026-04-28)
/claude/claude-code-multi-agent-part1/         (크롤링 날짜: 2026-04-28)
/blog/mdx-vs-md-blog-rendering-performance/    (크롤링 날짜: 2026-04-28)
... (이번 달 발행 글 다수)
```

발행한 지 얼마 안 된 포스트는 **Google이 크롤은 했지만 색인 결정은 보류** 상태다. 콘텐츠 품질·사이트 권위·crawling budget 등을 종합해 며칠~몇 주 안에 결정된다. 이 케이스는 **수정 불필요**, 다만 Search Console에서 **URL 검사 → 색인 생성 요청** 으로 가속화 가능.

## 4-3. (c) 이미 삭제된 옛 글 — 케이스 ①과 동일

```
/c++/C++-Template/                       (2025-12-15 크롤링)
/c++/C++-Static-Const-Explicit-Mutalbe/  (2025-11-21 크롤링)
```

3편에서 `_archive/` 로 옮긴 글들이다. 인덱스에 stale 데이터로 남아 있을 뿐이고, 시간이 지나면 자동 정리된다. **수정 불필요**.

---

# [05] 해결 — `noindex` 메타태그 자동 출력

## 5-1. 설계

archive·pagination 페이지에 `noindex`를 emit해야 하는데, 다음 조건을 만족시켜야 한다.

| 조건 | 이유 |
|------|------|
| **카테고리 archive 페이지** (`/categories/`, `/categories/docker` 등) | 저가치 목록 |
| **태그 archive 페이지** (`/tags/`) | 저가치 목록 |
| **pagination 2페이지 이상** (`/page2/`, `/page7/`) | 홈 첫 페이지의 변형, 중복 콘텐츠 |
| **404 페이지** (`/404.html`) | 색인 가치 없음 |
| ~~홈 첫 페이지 (`/`)~~ | **반드시 색인 유지** |
| ~~개별 포스트 (`/categories/foo/post-name/`)~~ | **반드시 색인 유지** |

명시 플래그(`page.noindex`)와 자동 판정(paginator·URL)을 결합한다.

## 5-2. `_includes/seo.html` 수정

minimal-mistakes 테마의 `_includes/seo.html`에 `<title>` 다음, 다른 meta 출력 직전에 다음을 추가한다.

```liquid
{% raw %}{%- comment -%}
  Emit noindex for archive/pagination pages so Google stops listing them as
  "Crawled - currently not indexed" or "Page with redirect" in Search Console.
  Real posts (page.noindex unset) remain indexable.
{%- endcomment -%}
{% assign is_noindex = false %}
{% if page.noindex %}{% assign is_noindex = true %}{% endif %}
{% if page.url == "/404.html" %}{% assign is_noindex = true %}{% endif %}
{% if paginator.page and paginator.page != 1 %}{% assign is_noindex = true %}{% endif %}
{% if is_noindex %}
<meta name="robots" content="noindex,follow">
{% endif %}{% endraw %}
```

세 조건을 따로 `assign`으로 처리한 이유는 **Liquid의 `or`/`and` 우선순위가 우→좌 평가**라 한 줄로 묶으면 가독성이 떨어지고 실수하기 쉽기 때문이다.

| 조건 | 동작 |
|------|------|
| `page.noindex == true` | frontmatter에 명시한 페이지 |
| `page.url == "/404.html"` | 404 페이지 |
| `paginator.page > 1` | pagination 2페이지 이상 (`/page2/`...) |

:warning: pagination 첫 페이지(`paginator.page == 1`)는 홈(`/`)이므로 절대 noindex가 되면 안 된다. `paginator.page != 1` 조건이 핵심.
{: .notice--warning}

## 5-3. archive 페이지 frontmatter에 `noindex: true` 추가

위 Liquid가 `page.noindex` 를 검사하므로, archive 페이지들에 frontmatter 한 줄을 추가한다.

```yaml
# _pages/categories-archive.md
---
title: "Posts by Category"
layout: categories
permalink: /categories/
author_profile: true
sitemap: false
noindex: true        # ← 추가
---
```

```yaml
# _pages/tag-archive.md
---
title: "Posts by Tag"
permalink: /tags/
layout: tags
author_profile: true
sitemap: false
noindex: true        # ← 추가
---
```

```yaml
# _pages/categories/*.md (16개 카테고리 페이지 모두)
---
title: "Docker"
layout: archive
permalink: categories/docker
sitemap: false
noindex: true        # ← 추가
---
```

| 수정 대상 | 파일 수 |
|----------|---------|
| `_pages/categories-archive.md` | 1 |
| `_pages/tag-archive.md` | 1 |
| `_pages/categories/*.md` | 16 |
| **합계** | **18 파일** |

:bulb: `sitemap: false`(sitemap에서 제외) + `noindex: true`(meta 태그로 색인 거부) 를 함께 적용하는 게 핵심. 둘 중 하나만 있으면 Google이 다른 경로(내부 링크)로 색인 시도를 계속한다.
{: .notice--info}

---

# [06] 검증

## 6-1. HTML 확인

빌드 후 `_site/categories/docker.html` 같은 archive 페이지를 열면 `<head>` 안에 다음이 들어 있어야 한다.

```html
<meta name="robots" content="noindex,follow">
```

반면 일반 포스트 (예: `_site/claude/claude-code-skill-hook-guide-part1/index.html`) 에는 **이 태그가 없어야 한다.**

## 6-2. URL별 동작 매트릭스

| URL | `noindex` 출력? | 의도 |
|-----|----------------|------|
| `/` (홈 첫 페이지) | ❌ 없음 | 색인 유지 |
| `/page2/`, `/page7/` | ✅ 출력 | pagination noindex |
| `/categories/` | ✅ 출력 | archive noindex |
| `/categories/docker` | ✅ 출력 | 개별 카테고리 noindex |
| `/tags/` | ✅ 출력 | tag archive noindex |
| `/claude/claude-code-skill-hook-guide-part1/` | ❌ 없음 | 포스트 색인 유지 |
| `/404.html` | ✅ 출력 | 404 noindex |

## 6-3. Search Console 후속 조치

| 단계 | 작업 |
|------|------|
| 1 | 변경사항을 GitHub에 push (Pages 빌드 자동) |
| 2 | Search Console → **URL 검사** 에서 `/categories/`, `/categories/docker` 등 입력 → 색인 요청 |
| 3 | Search Console → **삭제(Removals)** 에서 케이스 ①의 stale URL을 임시 삭제 (선택) |
| 4 | 며칠~몇 주 후 색인 보고서 재확인. **"크롤링됨 - 색인 안 됨"** → **"`noindex` 태그로 제외됨"** 으로 분류 이동 (정상) |

:bulb: archive 페이지가 **"`noindex` 태그로 제외됨"** 분류로 이동하는 것이 목표 상태다. "크롤링됨 - 색인 안 됨"은 모호한 회색지대 분류이지만, "`noindex`로 제외"는 명시적 정상 분류다.
{: .notice--info}

---

# [07] 전체 변경 요약

<pre class="mermaid">
graph LR
    subgraph Before["수정 전 (3편 적용 후 상태)"]
        B1["Search Console:<br/>리디렉션 포함 페이지"]
        B2["Search Console:<br/>크롤링됨 - 색인 안 됨<br/>(archive 페이지 다수)"]
        B3["sitemap: false 만 설정<br/>→ Googlebot은 여전히<br/>내부 링크 따라가 크롤"]
    end

    subgraph After["수정 후"]
        A1["navigation에<br/>trailing slash 추가"]
        A2["seo.html에<br/>noindex 자동 출력"]
        A3["archive 18개에<br/>noindex: true 추가"]
    end

    B1 -->|navigation.yml 수정| A1
    B2 -->|seo.html + frontmatter| A2
    B3 -->|noindex 메타태그| A3

    style Before fill:#ffcccc,stroke:#c62828
    style After fill:#e8f5e9,stroke:#2e7d32
</pre>

| # | 작업 | 파일 |
|---|------|------|
| ① | navigation trailing slash 추가 | `_data/navigation.yml` |
| ② | `seo.html`에 noindex 출력 로직 | `_includes/seo.html` |
| ③ | archive 페이지에 `noindex: true` | `_pages/categories-archive.md`, `_pages/tag-archive.md`, `_pages/categories/*.md` (16개) |
| | **합계** | **20 파일** |

---

# [08] 핵심 교훈

## 8-1. `sitemap: false`와 `noindex`는 다른 신호

| 신호 | 효과 |
|------|------|
| `sitemap: false` (frontmatter) | sitemap.xml에서만 제외. Googlebot은 내부 링크로 여전히 크롤 |
| `<meta name="robots" content="noindex">` | 크롤은 허용하되 **색인은 거부** |

archive·pagination 페이지처럼 **사용자에게는 보여줘야 하지만 Google에게는 보여주고 싶지 않은 페이지** 는 둘 다 적용해야 한다.

## 8-2. trailing slash 일관성

permalink와 내부 링크의 trailing slash 형식이 달라지면 사용자에게는 보이지 않지만 **Search Console에서는 "리디렉션 포함" 분류로 누적**된다. 사이트 전체에서 한 가지 형식으로 통일하는 게 안전하다.

## 8-3. Search Console 분류는 진단 도구다

"크롤링됨 - 색인 안 됨" 이 줄지 않는다고 해서 무조건 사이트 문제는 아니다. archive 페이지가 거기 들어 있는 건 Google이 정상적으로 판단한 것이며, 사이트 측에서 할 일은 **"맞아, 색인하지 마"** 라고 명시 신호(`noindex`)를 보내서 그 페이지들이 **`noindex`로 제외됨** 분류로 옮겨가게 하는 것이다.

:star: 시리즈 1편(포스트 단위) → 2편(`_config.yml`로 sitemap 갱신 확보) → 3편(사이트 단위 sitemap 품질) → 4편(Search Console 잔여 이슈) 까지 적용하면, 색인 보고서의 거의 모든 항목을 **"색인됨"** 또는 **"의도된 noindex/404"** 둘 중 하나로 깔끔하게 정리할 수 있다.
{: .notice--info}
