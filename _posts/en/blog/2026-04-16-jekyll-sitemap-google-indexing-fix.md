---
title: "Jekyll SEO Part 2 — Diagnosing Sitemap Stalls and Fixing _config.yml"
description: "Diagnose why Google Search Console's sitemap Last read does not refresh and new posts go unindexed (missing url/future/timezone), with a guide to fix _config.yml"
excerpt: "SEO series Part 2. Empty url → missing canonical, future: false → today's posts excluded from build, missing timezone → KST date-boundary misjudgment. Fixed with 3 lines in _config.yml"
date: 2026-04-16
categories: Github_Blog
tags: [Jekyll, GitHub-Pages, sitemap, jekyll-sitemap, Google-Search-Console, SEO, indexing, canonical, timezone, future-posts, _config.yml, SEO-Series-Part-2, SEO-Series]
ref: jekyll-sitemap-google-indexing-fix
---

:bulb: SEO Series Part 2. **[Part 1](/en/github_blog/gitblog-seo-google-search/)** covered post-level frontmatter, `jekyll-seo-tag`, and permalink optimization. After that, however, even after pushing several new posts, Google Search Console's `sitemap.xml` **Last read** date stayed frozen for weeks and new posts were not getting indexed. Before reaching for generic explanations (crawl budget, content quality), this repository had a concrete code-level problem: **missing settings in `_config.yml`**. This post walks through the diagnosis and the fix.
{: .notice--info}

:bulb: **SEO Series Layout**
- **[Part 1](/en/github_blog/gitblog-seo-google-search/)** — Post-level SEO: frontmatter, `jekyll-seo-tag`, permalink and filename
- **Part 2 (this post)** — Making sitemap refresh properly: `_config.yml` url/future/timezone — 3-line diagnosis and fix
- **[Part 3](/en/github_blog/jekyll-sitemap-seo-audit-fix/)** — Site-wide SEO audit: sitemap quality, verification meta tags, bulk description fix, 404/archive cleanup
- **[Part 4](/en/github_blog/search-console-noindex-redirect-cleanup/)** — Cleaning up Google Search Console residuals: diagnosing 404/redirect/"crawled-not-indexed" and applying `noindex` meta tags
{: .notice}

**Environment**: Jekyll 3.x + minimal-mistakes + GitHub Pages + jekyll-sitemap plugin

---

# [01] The Problem

After pushing several new posts, Google Search Console (GSC) showed these two symptoms continuously.

<pre class="mermaid">
graph LR
    PUSH["push new posts"] -->|1~2 weeks later| GSC["Check Search Console"]
    GSC --> SITEMAP["Sitemap<br/>Last read not refreshed"]
    GSC --> INDEX["Indexed pages<br/>new posts missing"]

    style PUSH fill:#e3f2fd,stroke:#1565c0
    style SITEMAP fill:#ffcccc,stroke:#c62828
    style INDEX fill:#ffcccc,stroke:#c62828
</pre>

| Symptom | Expected | Actual |
|---------|----------|--------|
| Sitemap last read | refresh at least weekly | stuck for weeks |
| Indexed page count | reflects new posts | only old posts |
| `sitemap.xml` contents | latest posts included | possibly missing |

---

# [02] Generic Explanations First (Common AI Answers)

Most answers list these 7 **generic causes**. They are not wrong, but you should inspect your own repository configuration first.

| # | Cause | Verdict |
|---|-------|---------|
| 1 | Site rarely changes | Normal — not the problem |
| 2 | Low `lastmod` reliability (all identical / no real changes) | Worth checking |
| 3 | Low crawl priority (new domain, low traffic) | Time-based resolution |
| 4 | `robots.txt` / redirects / access errors | Worth checking |
| 5 | No change detected vs previous sitemap | Normal |
| 6 | Crawl budget limits | Scale-related |
| 7 | Search Console UI lag | Ignorable |

:warning: The 7 above are **generic**. The actual cause for this repository was different. The next section walks through the diagnosis.
{: .notice--warning}

---

# [03] Actual Root Cause Diagnosis

Inspecting `_config.yml` revealed **3 critical missing settings**.

<pre class="mermaid">
graph TD
    ROOT["sitemap stalled — causes"] --> C1["(1) url: empty<br/>→ canonical URL not generated"]
    ROOT --> C2["(2) future: default false<br/>→ today's posts excluded from build"]
    ROOT --> C3["(3) timezone: empty<br/>→ parsed as UTC, KST date boundary misjudged"]

    C1 --> R1["Sitemap URL incomplete<br/>Google trust drops"]
    C2 --> R2["New posts simply absent<br/>from _site/"]
    C3 --> R3["2026-04-15 post seen as<br/>future when converted to UTC"]

    style ROOT fill:#fff3e0,stroke:#e65100
    style C1 fill:#ffcccc,stroke:#c62828
    style C2 fill:#ffcccc,stroke:#c62828
    style C3 fill:#ffcccc,stroke:#c62828
</pre>

## 3-1. `url:` Is Empty

```yaml
# Before
url                      : # the base hostname & protocol ...
baseurl                  : # the subpath of your site ...
```

- `jekyll-sitemap` generates `sitemap.xml`'s `<loc>` absolute URLs from `site.url`
- If empty, `<loc>/categories/xxx/</loc>` ends up as a **relative path**, or `<loc>` is missing
- From Google's view: "this sitemap looks malformed" → trust drops → recrawl frequency falls
- `jekyll-seo-tag`'s `canonical` and Open Graph URL also fail to generate for the same reason

## 3-2. `future:` Flag Not Set (Defaults to false)

By default, Jekyll **excludes future-dated posts from the build**. Why this is critical:

```bash
# Current time (UTC): 2026-04-15 23:10
# Post frontmatter: date: 2026-04-16

$ jekyll build
# → That post is judged "future" and excluded from _site/
# → Naturally missing from sitemap.xml too
```

:warning: When `timezone` is also empty, a post written in the afternoon (KST) gets pushed to the **next day** in UTC and classified as a future post — an edge case to watch for.
{: .notice--warning}

## 3-3. `timezone:` Missing

```yaml
# Before
timezone: # https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
```

- Empty value → Jekyll falls back to the server (or Liquid) default TZ (GitHub Pages builder is UTC)
- If a post only has `date: 2026-04-16`, KST 00:00 ≠ UTC 00:00 → date boundary misjudged
- For stable results, set `future: true` and `timezone: Asia/Seoul` **together**

---

# [04] Fix: 3-Line Change in `_config.yml`

## 4-1. Diff

```yaml
# Site Settings
locale                   : "ko-KR"
title                    : "Blog"
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
+ future: true # include today's and future-dated posts in the build
```

## 4-2. Effect of Each Setting

| Setting | Before | After | Effect |
|---------|--------|-------|--------|
| `url` | (empty) | `https://cmaven.github.io` | sitemap `<loc>` absolute URLs and canonical tags generated |
| `baseurl` | (empty) | `""` (explicit empty string) | Explicit root-domain hosting |
| `timezone` | (empty) | `Asia/Seoul` | Date interpretation in KST |
| `future` | (default false) | `true` | Today's and future-dated posts included in build/index |

## 4-3. Verification Sequence

<pre class="mermaid">
sequenceDiagram
    participant Dev as Author
    participant Repo as GitHub Repo
    participant GHP as GitHub Pages Builder
    participant Site as cmaven.github.io
    participant GSC as Search Console

    Dev->>Repo: push _config.yml change
    Repo->>GHP: Pages build triggered
    GHP->>Site: regenerate _site/sitemap.xml
    Dev->>Site: open sitemap.xml directly (confirm 200 OK)
    Dev->>GSC: resubmit in Sitemaps menu
    GSC->>Site: recrawl sitemap.xml
    GSC-->>Dev: Last read date refreshes
</pre>

---

# [05] Verification Checklist

After the fix, going through the checklist below in order confirms whether the root cause was actually resolved.

| # | Check | How | Expected Result |
|---|-------|-----|-----------------|
| 1 | sitemap accessible | `curl -I https://cmaven.github.io/sitemap.xml` | `200 OK` |
| 2 | absolute URLs in sitemap | Open sitemap.xml in browser | `<loc>https://cmaven.github.io/...</loc>` |
| 3 | latest posts present | Search for new post URLs in sitemap body | Found |
| 4 | `lastmod` variety | Compare `<lastmod>` values across entries | Differ per post |
| 5 | robots.txt permits | `https://cmaven.github.io/robots.txt` | `Sitemap:` line present |
| 6 | GSC indexing request | Search Console → URL Inspection → Request Indexing | Acknowledgement message |
| 7 | Sitemap resubmission | GSC → Sitemaps → resubmit `/sitemap.xml` | "Success" state |

---

# [06] Key Lessons

## 6-1. Check Your Own Config Before Generic Theories

Searching for "sitemap not refreshing" mostly yields **generic explanations** like "low crawl priority" or "Search Console UI delay". Those are valid, but **checking 3 lines in `_config.yml`** first is faster.

## 6-2. Jekyll Default Pitfalls

| Default | Pitfall |
|---------|---------|
| `future: false` | TZ shift makes today's post "future" → missing from sitemap |
| `timezone: (empty)` | UTC interpretation → KST dates misjudged |
| `url: (empty)` | minimal-mistakes template ships with it blank |

## 6-3. GSC "Last read" Is a Result Indicator

Sitemap Last read refresh happens **when Google judges it worth re-reading**. To trigger this:

- sitemap content must show **real changes** (`url`, `lastmod`)
- sitemap format must be **trustworthy** (absolute URLs, correct `<loc>`)
- the site must have **new/edited content** on a steady cadence

:star: This case was not "out of crawl budget" — it was "new posts never made it into the sitemap in the first place". `future: true` + `url` settings are the core fix.
{: .notice--info}

---

# [07] Next in the Series

Once the 3-line `_config.yml` fix gets the sitemap generating and refreshing correctly, the next step is auditing **the sitemap's contents themselves**. The auto-generated sitemap includes not only posts but also **low-value archive URLs like category/tag/pagination pages**, which can lead Google to judge the entire sitemap as low quality.

[Part 3](/en/github_blog/jekyll-sitemap-seo-audit-fix/) covers the 5 issues found while auditing the whole repo (low-value URLs mixed in, missing verification meta tags, 9 posts missing description, no 404 page, old C/C++ posts uncleaned) and the bulk fixes. [Part 4](/en/github_blog/search-console-noindex-redirect-cleanup/) then closes out the 4 residual Search Console categories (404 / redirect / crawled-not-indexed / discovered-not-indexed) using `noindex` meta tags and navigation trailing-slash cleanup.

---

# [08] References

- [Jekyll Configuration Docs](https://jekyllrb.com/docs/configuration/default/) — Check `future`, `timezone` defaults
- [jekyll-sitemap GitHub](https://github.com/jekyll/jekyll-sitemap) — `site.url` dependency
