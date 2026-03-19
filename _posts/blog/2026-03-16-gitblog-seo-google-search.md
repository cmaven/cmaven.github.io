---
title: "Jekyll 블로그 포스트 Google 검색 유입 최적화 (SEO)"
description: "Jekyll 기반 GitHub 블로그에서 Google 검색 유입을 높이기 위한 SEO 설정 가이드"
excerpt: "frontmatter 최적화, jekyll-seo-tag 플러그인, 태그 전략 등 Jekyll 블로그 SEO 실전 적용법"
date: 2026-03-16
categories: Github_Blog
tags: [SEO, Google-Search, Jekyll, frontmatter, sitemap, jekyll-seo-tag]
---

:bulb: Jekyll 기반 GitHub 블로그에서 포스트를 작성할 때, Google 검색에 잘 노출되도록 하는 SEO(Search Engine Optimization) 설정 방법을 정리합니다.
{: .notice--info}

# [01] SEO란?

> **SEO(Search Engine Optimization)** 는 검색 엔진이 웹페이지의 내용을 잘 이해하고, 검색 결과에서 높은 순위로 노출시킬 수 있도록 최적화하는 작업입니다.

- Google은 웹 크롤러(Googlebot)가 페이지를 방문하여 `<title>`, `<meta>` 태그, 본문 내용, URL 구조 등을 분석
- 이 정보를 바탕으로 검색 결과의 **제목**, **설명(스니펫)**, **순위**를 결정
- Jekyll 블로그에서는 **frontmatter**와 **플러그인**을 활용하여 이를 제어할 수 있음

# [02] frontmatter SEO 최적화

Jekyll 포스트의 frontmatter에 SEO 관련 필드를 추가하면, 검색 엔진이 페이지를 더 정확하게 이해할 수 있습니다.

## 2-1. 적용 전 (기본 frontmatter)

```yaml
---
title: "Ubuntu 24.04 한글 입력기 설치 및 한영 전환 설정"
date: 2026-03-16
categories: Linux
tags: [Ubuntu, fcitx, ibus, hangul, 한글입력]
---
```

이 상태에서 Google 검색 결과에 표시되는 정보:

| 항목 | 출처 | 문제점 |
|------|------|--------|
| 검색 제목 | `title` 값 | 적용됨 (OK) |
| 검색 설명(스니펫) | 본문에서 자동 추출 | Google이 임의로 선택하므로 부정확할 수 있음 |
| 목록 미리보기 | 본문 첫 줄 | 의도하지 않은 내용이 표시될 수 있음 |
| 검색 키워드 범위 | `tags` 5개 | 검색 유입 경로가 제한적 |

## 2-2. 적용 후 (SEO 최적화 frontmatter)

```yaml
---
title: "Ubuntu 24.04 한글 입력기 설치 및 한영 전환 설정"
description: "Ubuntu 24.04에서 fcitx, ibus 한글 입력기 설치 방법과 한영 전환 단축키 설정 가이드"
excerpt: "Ubuntu 24.04 LTS 영어 설치 후 fcitx-hangul, ibus-hangul 한글 입력기 설치 및 한영 전환 단축키 설정 방법"
date: 2026-03-16
categories: Linux
tags: [Ubuntu, Ubuntu-24.04, fcitx, fcitx-hangul, ibus, ibus-hangul, 한글입력, 한영전환, Linux-한글, Korean-input]
---
```

개선된 결과:

| 항목 | 출처 | 개선점 |
|------|------|--------|
| 검색 제목 | `title` 값 | 동일 |
| 검색 설명(스니펫) | `description` 값 | 의도한 설명이 표시됨 |
| 목록 미리보기 | `excerpt` 값 | 블로그 목록 페이지에서 깔끔하게 표시 |
| 검색 키워드 범위 | `tags` 10개 | 다양한 검색어로 유입 가능 |

## 2-3. 각 필드의 역할

### description

```yaml
description: "Ubuntu 24.04에서 fcitx, ibus 한글 입력기 설치 방법과 한영 전환 단축키 설정 가이드"
```

- HTML의 `<meta name="description">` 태그로 변환됨
- Google 검색 결과의 **스니펫**(제목 아래 설명 텍스트)으로 사용
- **50~160자** 권장 (너무 짧으면 정보 부족, 너무 길면 잘림)
- 핵심 키워드를 자연스럽게 포함

:warning: `description`이 없으면 Google이 본문에서 임의로 추출하므로, 의도하지 않은 내용이 스니펫으로 표시될 수 있습니다.
{: .notice--warning}

### excerpt

```yaml
excerpt: "Ubuntu 24.04 LTS 영어 설치 후 fcitx-hangul, ibus-hangul 한글 입력기 설치 및 한영 전환 단축키 설정 방법"
```

- Minimal Mistakes 테마에서 **포스트 목록 페이지**의 미리보기 텍스트로 사용
- `jekyll-seo-tag` 플러그인 사용 시 `description`이 없으면 `excerpt`를 대신 사용
- `description`과 다른 문장으로 작성하면 더 다양한 키워드를 커버할 수 있음

### tags 확장

```yaml
# Before
tags: [Ubuntu, fcitx, ibus, hangul, 한글입력]

# After
tags: [Ubuntu, Ubuntu-24.04, fcitx, fcitx-hangul, ibus, ibus-hangul, 한글입력, 한영전환, Linux-한글, Korean-input]
```

- 사용자가 실제로 검색할 만한 키워드를 다양하게 포함
- 한글/영문 혼용으로 양쪽 검색어 모두 커버
- 버전 정보(`Ubuntu-24.04`)를 포함하여 특정 버전 검색에 대응
- 패키지명(`fcitx-hangul`)을 포함하여 기술 검색에 대응

# [03] jekyll-seo-tag 플러그인

## 3-1. 플러그인 역할

`jekyll-seo-tag`는 frontmatter의 `title`, `description`, `excerpt` 등을 자동으로 HTML `<meta>` 태그로 변환해주는 플러그인입니다.

적용 전후 비교:

```html
<!-- jekyll-seo-tag 없이 (기본) -->
<title>Ubuntu 24.04 한글 입력기 설치 및 한영 전환 설정 - 블로그</title>

<!-- jekyll-seo-tag 적용 후 (자동 생성) -->
<title>Ubuntu 24.04 한글 입력기 설치 및 한영 전환 설정 - 블로그</title>
<meta name="description" content="Ubuntu 24.04에서 fcitx, ibus 한글 입력기 설치 방법과 한영 전환 단축키 설정 가이드">
<meta property="og:title" content="Ubuntu 24.04 한글 입력기 설치 및 한영 전환 설정">
<meta property="og:description" content="Ubuntu 24.04에서 fcitx, ibus ...">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary">
<link rel="canonical" href="https://xxx.github.io/linux/ubuntu-2404-korean-input-setup/">
```

:bulb: `og:title`, `og:description` 등의 **Open Graph** 태그가 자동 생성되어 SNS 공유 시에도 올바른 제목/설명이 표시됩니다.
{: .notice--info}

## 3-2. 설치 방법

**Gemfile**에 추가:

```ruby
gem "jekyll-seo-tag"
```

**_config.yml** plugins 섹션에 추가:

```yaml
plugins:
  - jekyll-paginate
  - jekyll-sitemap
  - jekyll-gist
  - jekyll-feed
  - jekyll-include-cache
  - jemoji
  - jekyll-seo-tag    # 추가
```

터미널에서 설치:

```bash
bundle install
```

:warning: GitHub Pages에서 `jekyll-seo-tag`는 기본 지원 플러그인이므로 별도 설정 없이 `_config.yml`에 추가만 하면 동작합니다.
{: .notice--warning}

## 3-3. _config.yml 사이트 정보 보강

`jekyll-seo-tag`는 `_config.yml`의 사이트 정보도 활용합니다. 다음 항목이 설정되어 있는지 확인합니다.

```yaml
# _config.yml
title: "블로그"
description: "작업노트"
url: "https://cmaven.github.io"   # 사이트 URL (비어 있으면 canonical URL 생성 불가)
author:
  name: "cmaven"
```

:warning: `url` 값이 비어 있으면 `canonical` 태그와 Open Graph URL이 생성되지 않으므로 반드시 설정해야 합니다.
{: .notice--warning}

# [04] sitemap.xml 활용

## 4-1. 자동 생성 확인

`jekyll-sitemap` 플러그인이 이미 설치되어 있다면, 빌드 시 자동으로 `sitemap.xml`이 생성됩니다.

```
https://cmaven.github.io/sitemap.xml
```

## 4-2. 새 포스트 작성 후 인덱싱 요청

새 포스트를 push한 후, Google Search Console에서 빠르게 인덱싱하려면:

1. **Google Search Console** 접속
2. 상단 검색창에 **새 포스트의 URL** 입력
3. **색인 생성 요청** 클릭

또는 **Sitemaps** 메뉴에서 `sitemap.xml`을 재제출하면 전체 사이트를 다시 크롤링합니다.

:bulb: 새 포스트 push 후 Google이 자동으로 크롤링하기까지 수일이 걸릴 수 있습니다. 색인 생성 요청을 하면 더 빨리 반영됩니다.
{: .notice--info}

# [05] URL 구조 최적화

## 5-1. permalink 설정

URL에 의미 있는 키워드가 포함되면 검색 엔진이 페이지 내용을 더 잘 파악합니다.

```yaml
# _config.yml

# 기본값 (날짜 포함)
permalink: /:categories/:year/:month/:day/:title/
# → /linux/2026/03/16/ubuntu-2404-korean-input-setup/

# 간결한 형태 (권장)
permalink: /:categories/:title/
# → /linux/ubuntu-2404-korean-input-setup/
```

:bulb: 파일명 자체가 URL의 일부가 되므로, 파일명에 핵심 키워드를 포함하는 것이 중요합니다.
{: .notice--info}

## 5-2. 파일명 작성 팁

```
# 좋은 예 - 키워드가 명확
2026-03-16-ubuntu-2404-korean-input-setup.md

# 피해야 할 예 - 키워드 부족
2026-03-16-setup-guide.md
2026-03-16-post1.md
```

# [06] 체크리스트

새 포스트를 작성할 때 아래 항목을 확인하면 Google 검색 유입을 높일 수 있습니다.

| 순서 | 항목 | 확인 |
|------|------|------|
| 1 | `title`에 핵심 키워드 포함 | ☐ |
| 2 | `description` 50~160자 작성 | ☐ |
| 3 | `excerpt` 작성 (목록 미리보기용) | ☐ |
| 4 | `tags`에 한글/영문 키워드 다양하게 포함 | ☐ |
| 5 | 파일명에 핵심 키워드 포함 | ☐ |
| 6 | `jekyll-seo-tag` 플러그인 설치 여부 | ☐ |
| 7 | `_config.yml`의 `url` 값 설정 여부 | ☐ |
| 8 | push 후 Google Search Console에서 색인 요청 | ☐ |

:star: frontmatter의 `description`과 `tags` 보강만으로도 검색 유입이 크게 개선될 수 있습니다. `jekyll-seo-tag` 플러그인까지 적용하면 Open Graph, canonical URL 등이 자동으로 생성되어 SEO 효과가 극대화됩니다.
{: .notice--info}
