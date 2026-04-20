---
title: "Jekyll 빌드 에러: undefined method gsub for an instance of Integer — slugify 오류 해결"
description: "GitHub Pages Jekyll 빌드 시 slugify 필터에 Integer가 전달되어 발생하는 gsub NoMethodError의 원인과 append '' 방어 코드 해결법"
excerpt: "Liquid Exception: undefined method gsub for an instance of Integer — slugify 앞에 append '' 한 줄 추가로 해결"
date: 2026-04-20
categories: Github_Blog
tags: [Jekyll, Liquid, slugify, gsub, Integer, GitHub-Pages, 빌드에러, frontmatter, YAML, troubleshooting]
---

:bulb: GitHub Pages에서 Jekyll 빌드 시 `undefined method 'gsub' for an instance of Integer` 에러가 발생하여 사이트가 배포되지 않는 문제의 원인과 해결 방법을 정리한다.
{: .notice--info}

---

# [01] 문제 상황

GitHub에 push 후 블로그가 갱신되지 않았다. GitHub Actions 빌드 로그를 확인하니 아래 에러가 반복되고 있었다.

    Liquid Exception: undefined method `gsub' for an instance of Integer in /_layouts/single.html
    /usr/local/bundle/gems/jekyll-3.10.0/lib/jekyll/utils.rb:367:
      in `replace_character_sequence_with_hyphen':
      undefined method `gsub' for an instance of Integer (NoMethodError)

        string.gsub(replaceable_char, "-")
              ^^^^^

**증상:**
- push 후 사이트가 갱신되지 않음
- GitHub Actions 빌드는 "성공"으로 표시되지만 실제로는 이전 캐시 배포
- sitemap.xml에 새 포스트가 포함되지 않음
- 새 포스트 URL 접근 시 404

---

# [02] 원인 분석

## 2-1. 에러 발생 위치

에러는 `/_layouts/single.html` 레이아웃에서 발생했고, 스택 트레이스를 따라가면:

    single.html → post__taxonomy.html → slugify 필터

`_includes/post__taxonomy.html`에서 카테고리와 태그를 순회하면서 `slugify` Liquid 필터를 호출하는 부분이 원인이었다.

    {{ category_word | slugify }}
    {{ tag_word | slugify }}

## 2-2. 왜 Integer가 들어갔는가

`slugify`는 문자열의 `gsub` 메서드를 호출한다. 그런데 포스트의 frontmatter에서 **YAML이 특정 값을 숫자(Integer)로 해석**하면, `slugify`에 Integer가 전달되어 에러가 발생한다.

YAML에서 숫자로 해석되는 예:

    tags: [404]              # ← Integer 404로 해석됨
    tags: [123, abc]         # ← 123은 Integer, abc는 String
    categories: 2026         # ← Integer로 해석됨

의도한 것:

    tags: ["404"]            # ← 따옴표로 감싸면 String
    tags: [abc, def]         # ← 문자가 포함되면 String
    categories: "2026"       # ← 따옴표로 감싸면 String

## 2-3. 문제가 심각한 이유

- 에러가 발생한 **포스트 파일명이 로그에 표시되지 않음** → 어떤 파일이 원인인지 특정이 어려움
- Jekyll이 빌드를 중단하므로 **전체 사이트가 배포되지 않음** (새 포스트뿐 아니라 기존 포스트도 갱신 안 됨)
- GitHub Actions에서 "성공"으로 표시되는 경우도 있어 **빌드 실패를 알아차리기 어려움**

---

# [03] 해결 방법

## 3-1. 근본 해결 — slugify 앞에 append '' 추가

`slugify` 호출 전에 `| append: ''`를 추가하면 **어떤 타입이든 문자열로 변환**된다.

**수정 전:**

    {{ category_word | slugify }}

**수정 후:**

    {{ category_word | append: '' | slugify }}

`append: ''`는 빈 문자열을 붙이는 것이므로 값 자체는 변하지 않지만, Integer를 String으로 강제 변환하는 효과가 있다.

## 3-2. 수정이 필요한 파일 목록

| 파일 | 수정 위치 |
|------|----------|
| `_includes/post__taxonomy.html` | `category_word \| slugify`, `tag_word \| slugify` (2곳) |
| `_includes/category-list.html` | `category_word \| slugify` (1곳) |
| `_includes/tag-list.html` | `tag_word \| slugify` (1곳) |
| `_layouts/categories.html` | `category[0] \| slugify` (2곳) |
| `_layouts/tags.html` | `tag[0] \| slugify` (2곳) |

## 3-3. 예방 — frontmatter 작성 규칙

숫자로 해석될 수 있는 값은 **따옴표로 감싼다.**

    # ❌ 위험 — Integer로 해석될 수 있음
    tags: [404, 500]

    # ✅ 안전 — 명시적 String
    tags: ["404", "500"]

---

# [04] 디버깅 방법

이 에러가 다시 발생했을 때 원인 파일을 찾는 방법이다.

## 4-1. GitHub Actions 빌드 로그 확인

1. GitHub 저장소 → **Actions** 탭
2. 가장 최근 **workflow run** 클릭
3. **build** 단계 클릭
4. `Liquid Exception` 에러 메시지 확인

## 4-2. 모든 포스트에서 숫자 값 검색

    # categories에 숫자만 있는 포스트 찾기
    grep -rn "^categories:" _posts/ | grep -E ": [0-9]+$"

    # tags 배열에 숫자만 있는 태그 찾기
    grep -rn "^tags:" _posts/ | grep -E "[, \[][0-9]+[,\]]"

## 4-3. 포스트 본문 안의 frontmatter 예시 확인

코드 예시로 frontmatter를 포함할 때, `---` 구분자가 코드블록 밖에 있으면 Jekyll이 이를 실제 frontmatter로 파싱할 수 있다.

    # ❌ 위험 — 코드블록 안의 ---가 frontmatter로 인식될 수 있음
    ```yaml
    ---
    date: 2022-02-16
    tags: [pip, error]
    ---
    ```

    # ✅ 안전 — 들여쓰기 방식으로 코드 표시
        date: 2022-02-16
        tags: [pip, error]

---

# [05] 정리

| 항목 | 내용 |
|------|------|
| **에러 메시지** | `undefined method 'gsub' for an instance of Integer` |
| **발생 위치** | `slugify` Liquid 필터 |
| **원인** | YAML이 frontmatter 값을 Integer로 해석 |
| **해결** | `slugify` 앞에 `\| append: ''` 추가 (8곳) |
| **예방** | 숫자 값은 따옴표로 감싸기, 코드 예시에 `---` 주의 |

:warning: 이 에러는 **어떤 파일이 원인인지 로그에 표시되지 않는다.** 빌드 실패 시 최근 변경한 포스트의 frontmatter를 먼저 점검하고, 그래도 안 되면 `slugify` 방어 코드가 적용되어 있는지 확인한다.
{: .notice--warning}
