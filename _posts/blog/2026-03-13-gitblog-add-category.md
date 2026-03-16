---
title: "Jekyll 블로그에 새 카테고리 추가하기 (Minimal Mistakes)"
description: "Minimal Mistakes 테마 Jekyll 블로그에서 사이드바 카테고리를 추가하고 포스트를 연결하는 방법"
excerpt: "navigation.yml, 카테고리 아카이브 페이지, frontmatter 설정으로 새 카테고리를 추가하는 3단계 가이드"
date: 2026-03-13
categories: Github_Blog
tags: [Jekyll, category, sidebar, Minimal-Mistakes, navigation, 카테고리추가, 사이드바]
---

:bulb: Minimal Mistakes 테마 기반 Jekyll 블로그에서 새로운 카테고리를 추가하고, 사이드바에 표시하여 포스트를 확인할 수 있게 하는 방법을 작성한다.
{: .notice--info}

# [01] 전체 흐름

새 카테고리를 추가하려면 **3곳을 수정/생성**해야 한다.

| 순서 | 파일 | 역할 |
|---|---|---|
| 1 | `_data/navigation.yml` | 사이드바에 카테고리 링크 추가 |
| 2 | `_pages/categories/카테고리명.md` | 카테고리 아카이브 페이지 생성 |
| 3 | `_posts/디렉토리/포스트.md` | 포스트의 `categories` frontmatter 설정 |

---

# [02] Step 1: 사이드바에 카테고리 추가

## 2-1. `_data/navigation.yml` 수정

사이드바 메뉴 구조는 `_data/navigation.yml`의 `cmaven_sidebar` 섹션에서 관리된다.

```yaml
# _data/navigation.yml

cmaven_sidebar:
  - title: "운영체제"          # 대분류 (그룹 제목)
    children:
      - title: "Linux"        # 소분류 (카테고리 링크)
        url: /categories/linux
      - title: "Windows"
        url: /categories/windows
  - title: "프로그래밍언어"
    children:
      - title: "Python"
        url: /categories/python
```

**새 카테고리를 추가하는 방법:**

### (A) 기존 그룹에 추가

기존 대분류 아래에 `children` 항목을 추가한다.

```yaml
  - title: "프로그래밍언어"
    children:
      - title: "Python"
        url: /categories/python
      - title: "NewLang"           # 추가
        url: /categories/newlang   # 추가
```

### (B) 새 그룹을 만들어 추가

새로운 대분류를 만들고 그 아래에 카테고리를 배치한다.

```yaml
  - title: "AI"                    # 새 대분류
    children:
      - title: "Claude"           # 새 카테고리
        url: /categories/claude
```

:bulb: `title`은 사이드바에 표시되는 이름이고, `url`은 카테고리 아카이브 페이지의 경로다. `url`은 **Step 2**에서 만드는 페이지의 `permalink`와 일치해야 한다.
{: .notice--info}

---

# [03] Step 2: 카테고리 아카이브 페이지 생성

## 3-1. `_pages/categories/` 에 .md 파일 생성

사이드바 링크를 클릭했을 때 표시되는 페이지를 만든다.

```markdown
---
title: "Claude"
layout: archive
permalink: categories/claude
---

{% raw %}{% assign posts = site.categories.Claude %}
{% for post in posts %}
{% include archive-single-cmaven.html %}
{% endfor %}{% endraw %}
```

**각 항목 설명:**

| 항목 | 값 | 설명 |
|---|---|---|
| `title` | `"Claude"` | 페이지 상단에 표시되는 제목 |
| `layout` | `archive` | Minimal Mistakes의 아카이브 레이아웃 사용 |
| `permalink` | `categories/claude` | 이 페이지의 URL 경로 (`navigation.yml`의 `url`과 일치) |
| `site.categories.Claude` | - | Jekyll이 수집한 `Claude` 카테고리의 포스트 목록 |

:warning: `site.categories.Claude`의 **대소문자**가 포스트 frontmatter의 `categories` 값과 정확히 일치해야 한다. 포스트에 `categories: Claude`로 적었다면, 여기서도 `site.categories.Claude`로 써야 한다.
{: .notice--warning}

## 3-2. 기존 카테고리 페이지 참고

기존 파일들의 패턴을 확인하면 구조를 쉽게 이해할 수 있다.

```
_pages/categories/
├── c.md           # categories: C
├── c++.md         # categories: C++
├── docker.md      # categories: Docker
├── git.md         # categories: Git
├── linux.md       # categories: Linux
├── python.md      # categories: Python
└── claude.md      # categories: Claude  ← 새로 추가
```

---

# [04] Step 3: 포스트 작성

## 4-1. 포스트 파일 생성

`_posts/` 하위에 원하는 디렉토리 구조로 `.md` 파일을 생성한다.

```
_posts/
├── operating_system/linux/
├── program_language/python/
├── ai/claude/                     ← 새 디렉토리
│   └── 2026-03-13-my-post.md
└── ...
```

:bulb: `_posts/` 하위의 디렉토리 구조는 포스트 분류와 무관하다. Jekyll은 **frontmatter의 `categories` 값**으로 카테고리를 결정한다. 디렉토리는 파일 관리 용도로만 사용된다.
{: .notice--info}

## 4-2. frontmatter 설정

```yaml
---
title: "포스트 제목"
date: 2026-03-13
categories: Claude          # ← 이 값이 카테고리를 결정
tags: [Claude Code, Agent]
---
```

**핵심:** `categories` 값이 Step 2에서 작성한 `site.categories.Claude`와 대소문자까지 일치해야 해당 카테고리 페이지에 포스트가 나타난다.

---

# [05] 연결 관계 요약

3개 파일의 값이 서로 연결되어야 정상 동작한다.

| 파일 | 설정 값 | 연결 대상 |
|---|---|---|
| `_data/navigation.yml` | `url: /categories/claude` | → `_pages`의 `permalink` |
| `_pages/categories/claude.md` | `permalink: categories/claude` | ← `navigation.yml`의 `url` |
| `_pages/categories/claude.md` | `site.categories.Claude` | → 포스트의 `categories` |
| `_posts/.../포스트.md` | `categories: Claude` | ← `_pages`의 `site.categories` |

```
navigation.yml          _pages/categories/claude.md         _posts/.../포스트.md
url: /categories/claude  ←→  permalink: categories/claude
                              site.categories.Claude  ←→  categories: Claude
```

---

# [06] 확인 방법

## 6-1. 로컬 확인

```shell
bundle exec jekyll serve
```

브라우저에서 `http://localhost:4000`에 접속하여:

1. **사이드바**에 새 카테고리가 표시되는지 확인
2. 카테고리 링크를 클릭하면 **아카이브 페이지**에 포스트 목록이 나타나는지 확인
3. 포스트를 클릭하면 **본문**이 정상 표시되는지 확인

## 6-2. 포스트가 나타나지 않을 때 체크리스트

| 증상 | 원인 | 해결 |
|---|---|---|
| 사이드바에 메뉴가 없음 | `navigation.yml` 미수정 | `cmaven_sidebar`에 항목 추가 |
| 메뉴 클릭 시 404 | 카테고리 페이지 미생성 | `_pages/categories/xxx.md` 생성 |
| 페이지는 있지만 포스트 없음 | `categories` 대소문자 불일치 | 포스트 frontmatter와 `site.categories.XXX` 일치 확인 |
| 포스트 날짜가 미래 | Jekyll 기본 설정은 미래 날짜 포스트 미표시 | `_config.yml`에 `future: true` 추가 또는 날짜 수정 |

---

# [07] 실전 예시: Claude 카테고리 추가

실제로 이 블로그에 Claude 카테고리를 추가한 과정이다.

## 7-1. `_data/navigation.yml`에 추가

```yaml
  - title: "AI"
    children:
      - title: "Claude"
        url: /categories/claude
```

## 7-2. `_pages/categories/claude.md` 생성

```markdown
---
title: "Claude"
layout: archive
permalink: categories/claude
---

{% raw %}{% assign posts = site.categories.Claude %}
{% for post in posts %}
{% include archive-single-cmaven.html %}
{% endfor %}{% endraw %}
```

## 7-3. 포스트 frontmatter 확인

```yaml
---
title: "Claude Code 완벽 가이드: Skill, Hook, CLAUDE.md로 코딩 워크플로우 자동화하기"
date: 2026-03-13
categories: Claude
tags: [Claude Code, Skill, Hook, CLAUDE.md, Agent]
---
```

이 3가지를 설정하면 사이드바 "AI > Claude"를 클릭했을 때 해당 포스트들이 목록으로 표시된다.
