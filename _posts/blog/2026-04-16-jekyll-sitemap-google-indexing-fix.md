---
title: "Jekyll 블로그 sitemap 미갱신·색인 누락 원인 진단과 해결 (_config.yml 3줄 수정)"
description: "Google Search Console에서 sitemap Last read가 갱신되지 않고 새 포스트가 색인되지 않는 문제의 실제 원인(url/future/timezone 누락) 진단과 _config.yml 수정 가이드"
excerpt: "url 비어있음 → canonical 누락, future: false → 오늘 작성 포스트 빌드 제외, timezone 누락 → KST 날짜 경계 오판. _config.yml 3줄로 해결"
date: 2026-04-16
categories: Github_Blog
tags: [Jekyll, GitHub-Pages, sitemap, jekyll-sitemap, Google-Search-Console, SEO, 색인, indexing, canonical, timezone, future-posts, _config.yml]
---

:bulb: Google Search Console에서 `sitemap.xml`의 **마지막 읽은 날짜(Last read)** 가 몇 주째 갱신되지 않고, 새로 작성한 포스트가 색인에 잡히지 않는 문제를 겪었다. 일반론적인 원인(크롤링 예산, 콘텐츠 품질 등)도 맞지만, 이 저장소에는 **설정 누락이라는 명확한 코드 문제**가 있었다. 진단 과정과 해결 방법을 정리한다.
{: .notice--info}

**환경**: Jekyll 3.x + minimal-mistakes + GitHub Pages + jekyll-sitemap 플러그인

---

# [01] 문제 상황

새 포스트를 여러 개 push 했는데도 Google Search Console(GSC)에서 아래 두 가지 증상이 지속됐다.

<pre class="mermaid">
graph LR
    PUSH["새 포스트 push"] -->|1~2주 경과| GSC["Search Console 확인"]
    GSC --> SITEMAP["Sitemap<br/>Last read 갱신 없음"]
    GSC --> INDEX["색인 페이지<br/>신규 포스트 미포함"]

    style PUSH fill:#e3f2fd,stroke:#1565c0
    style SITEMAP fill:#ffcccc,stroke:#c62828
    style INDEX fill:#ffcccc,stroke:#c62828
</pre>

| 증상 | 기대 | 실제 |
|------|------|------|
| Sitemap 마지막 읽은 날짜 | 주 1회 이상 갱신 | 수 주 정지 |
| 색인 페이지 수 | 신규 포스트 반영 | 구 포스트만 존재 |
| `sitemap.xml` 내용 | 최신 포스트 포함 | 일부 누락 가능성 |

---

# [02] 일반론 먼저 정리 (AI가 흔히 알려주는 원인)

대부분의 답변은 아래 7가지 **일반론**을 제시한다. 다 맞는 말이지만, 먼저 본인 저장소 설정을 점검해야 한다.

| # | 원인 | 판단 |
|---|------|------|
| 1 | 사이트에 변화가 거의 없음 | 정상 — 문제 아님 |
| 2 | `lastmod` 신뢰도 낮음 (모두 동일 / 실제 수정 없음) | 점검 필요 |
| 3 | 사이트 크롤링 우선순위 낮음 (신규 도메인, 트래픽 적음) | 시간 해결 |
| 4 | `robots.txt` / 리다이렉트 / 접근 오류 | 점검 필요 |
| 5 | 이전 sitemap 대비 변경 없음으로 판단 | 정상 |
| 6 | 크롤링 예산 제한 | 규모 문제 |
| 7 | Search Console UI 반영 지연 | 무시 가능 |

:warning: 위 7가지는 **일반론**이며, 이 저장소의 실제 원인은 별도였다. 다음 섹션에서 진단 과정을 정리한다.
{: .notice--warning}

---

# [03] 실제 원인 진단

`_config.yml`을 점검한 결과 **3가지 핵심 설정 누락**이 발견됐다.

<pre class="mermaid">
graph TD
    ROOT["sitemap 미갱신 원인"] --> C1["(1) url: 비어 있음<br/>→ canonical URL 미생성"]
    ROOT --> C2["(2) future: 기본값 false<br/>→ 오늘 날짜 포스트 빌드 제외"]
    ROOT --> C3["(3) timezone: 비어 있음<br/>→ UTC로 해석, KST 날짜 경계 오판"]

    C1 --> R1["sitemap URL 불완전<br/>Google 신뢰도 하락"]
    C2 --> R2["새 포스트 자체가<br/>_site/ 에 없음"]
    C3 --> R3["2026-04-15 작성글이<br/>UTC 환산 시 미래로 인식"]

    style ROOT fill:#fff3e0,stroke:#e65100
    style C1 fill:#ffcccc,stroke:#c62828
    style C2 fill:#ffcccc,stroke:#c62828
    style C3 fill:#ffcccc,stroke:#c62828
</pre>

## 3-1. `url:` 값이 비어 있음

```yaml
# 수정 전
url                      : # the base hostname & protocol ...
baseurl                  : # the subpath of your site ...
```

- `jekyll-sitemap`은 `site.url`을 기반으로 `sitemap.xml`의 `<loc>` 절대 URL을 생성
- 값이 비어 있으면 `<loc>/categories/xxx/</loc>` 같이 **상대경로**가 들어가거나 `<loc>` 누락
- Google 입장에서는 "sitemap 형식이 이상함" → 신뢰도 하락 → 재크롤링 빈도 감소
- `jekyll-seo-tag`의 `canonical`, Open Graph URL도 같은 이유로 생성 실패

## 3-2. `future:` 플래그 미설정 (기본값 false)

Jekyll은 기본적으로 **미래 날짜 포스트를 빌드에서 제외**한다. 이것이 치명적인 이유:

```bash
# 현재 시각(UTC 기준): 2026-04-15 23:10
# 포스트 frontmatter: date: 2026-04-16

$ jekyll build
# → 위 포스트는 "미래 글"로 판단되어 _site/ 에 포함 안 됨
# → sitemap.xml 에도 당연히 누락
```

:warning: `timezone`이 함께 비어 있으면 한국(KST) 기준 오후에 작성한 글이 UTC 기준으로 **다음 날**로 환산되어 미래글로 분류되는 엣지 케이스가 발생한다.
{: .notice--warning}

## 3-3. `timezone:` 값 누락

```yaml
# 수정 전
timezone: # https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
```

- 빈 값 → Jekyll은 서버(또는 Liquid) 기본 TZ로 해석 (GitHub Pages 빌더 환경은 UTC)
- 포스트에 `date: 2026-04-16` 만 적은 경우 KST 00:00 ≠ UTC 00:00 → 날짜 경계 오판
- `future: true`와 `timezone: Asia/Seoul`을 **함께** 설정해야 안정적

---

# [04] 해결: `_config.yml` 3줄 수정

## 4-1. 수정 diff

```yaml
# Site Settings
locale                   : "ko-KR"
title                    : "블로그"
# ...
- url                      : # the base hostname & protocol for your site
- baseurl                  : # the subpath of your site
+ url                      : "https://cmaven.github.io"
+ baseurl                  : ""

# Outputting
permalink: /:categories/:title/
paginate: 5
paginate_path: /page:num/
- timezone: # https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
+ timezone: Asia/Seoul
+ future: true # 오늘/미래 날짜 포스트도 빌드에 포함
```

## 4-2. 각 설정의 효과

| 설정 | Before | After | 효과 |
|------|--------|-------|------|
| `url` | (empty) | `https://cmaven.github.io` | sitemap `<loc>` 절대 URL, canonical 태그 생성 |
| `baseurl` | (empty) | `""` (명시적 빈 문자열) | 루트 도메인 운영 명시 |
| `timezone` | (empty) | `Asia/Seoul` | KST 기준 날짜 해석 |
| `future` | (기본값 false) | `true` | 오늘/미래 날짜 포스트도 빌드/색인 |

## 4-3. 반영 확인 절차

<pre class="mermaid">
sequenceDiagram
    participant Dev as 작성자
    participant Repo as GitHub Repo
    participant GHP as GitHub Pages 빌더
    participant Site as cmaven.github.io
    participant GSC as Search Console

    Dev->>Repo: _config.yml 수정 push
    Repo->>GHP: Pages 빌드 트리거
    GHP->>Site: _site/sitemap.xml 재생성
    Dev->>Site: sitemap.xml 직접 열기 (200 OK 확인)
    Dev->>GSC: Sitemaps 메뉴에서 재제출
    GSC->>Site: sitemap.xml 재크롤링
    GSC-->>Dev: Last read 날짜 갱신
</pre>

---

# [05] 검증 체크리스트

수정 후 다음 항목을 순서대로 확인하면 원인이 제대로 해결됐는지 확실히 판단할 수 있다.

| 순서 | 확인 항목 | 방법 | 기대 결과 |
|------|-----------|------|-----------|
| 1 | sitemap 접근 가능 | `curl -I https://cmaven.github.io/sitemap.xml` | `200 OK` |
| 2 | sitemap 내 절대 URL | 브라우저로 sitemap.xml 열기 | `<loc>https://cmaven.github.io/...</loc>` |
| 3 | 최신 포스트 포함 | sitemap 본문에서 신규 포스트 URL 검색 | 존재 |
| 4 | `lastmod` 다양성 | sitemap 내 `<lastmod>` 값 비교 | 포스트별로 상이 |
| 5 | robots.txt 허용 | `https://cmaven.github.io/robots.txt` | `Sitemap:` 라인 존재 |
| 6 | GSC 색인 요청 | Search Console → URL 검사 → 색인 생성 요청 | 요청 완료 메시지 |
| 7 | Sitemap 재제출 | GSC → Sitemaps → `/sitemap.xml` 재제출 | "성공" 상태 |

---

# [06] 핵심 교훈

## 6-1. 일반론보다 내 저장소 설정부터

sitemap 미갱신 문제를 검색하면 "크롤링 우선순위가 낮다", "Search Console UI 지연이다" 같은 **일반론**이 대부분이다. 맞는 말이지만, **먼저 `_config.yml` 3줄을 확인**하는 것이 빠르다.

## 6-2. Jekyll 기본값의 함정

| 기본값 | 함정 |
|--------|-----|
| `future: false` | 오늘 작성한 글이 TZ 차이로 미래글 분류 → sitemap 누락 |
| `timezone: (empty)` | UTC 해석 → KST 기준 날짜 오판 |
| `url: (empty)` | minimal-mistakes 템플릿은 비어있는 채로 배포됨 |

## 6-3. GSC "Last read"는 결과 지표

Sitemap Last read 갱신은 **Google이 "다시 읽을 가치가 있다"고 판단했을 때** 일어난다. 이를 유도하려면:

- sitemap 내용에 **실제 변화**가 있어야 함 (`url`, `lastmod`)
- sitemap 형식이 **신뢰 가능**해야 함 (절대 URL, 올바른 `<loc>`)
- 사이트에 **새로운/수정된 콘텐츠**가 꾸준히 있어야 함

:star: 이번 케이스는 "크롤링 예산 부족"이 아니라 "sitemap에 신규 포스트가 애초에 포함되지 않았던" 문제였다. `future: true` + `url` 설정이 핵심 해결책.
{: .notice--info}

---

# [07] 참고

- [Jekyll Configuration Docs](https://jekyllrb.com/docs/configuration/default/) — `future`, `timezone` 기본값 확인
- [jekyll-sitemap GitHub](https://github.com/jekyll/jekyll-sitemap) — `site.url` 의존성
- 관련 포스트: [Jekyll 블로그 포스트 Google 검색 유입 최적화 (SEO)]({% post_url /blog/2026-03-16-gitblog-seo-google-search %})
