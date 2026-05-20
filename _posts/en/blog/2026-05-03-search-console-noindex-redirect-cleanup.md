---
title: "Jekyll SEO Part 4 — Cleaning Up Search Console Issues (404, redirect, noindex)"
description: "Diagnose four GSC categories (Not found, Page with redirect, Crawled-currently not indexed, Discovered-currently not indexed) and clean them up with noindex meta tags and navigation trailing slash fixes"
excerpt: "SEO series Part 4. Diagnose remaining Search Console issues by four categories, then apply noindex meta automation in seo.html and trailing slash fixes in navigation"
date: 2026-05-03
categories: Github_Blog
tags: [Jekyll, SEO, Google-Search-Console, noindex, robots-meta, redirect, 404, trailing-slash, minimal-mistakes]
ref: search-console-noindex-redirect-cleanup
---

:bulb: SEO Series Part 4. Even after applying Parts 1~3 (post-level SEO, `_config.yml` 3-line fix for sitemap updates, site-wide sitemap audit), Google Search Console's coverage report still has URLs classified as **issues**. This guide diagnoses those remaining issues across 4 categories and resolves them with **automatic `noindex` meta tag emission** and **navigation trailing slash cleanup**.
{: .notice--info}

**Environment**: Jekyll 3.x + minimal-mistakes + GitHub Pages + jekyll-sitemap plugin

---

# [01] Background — Issues Remaining After Parts 1~3

After applying Parts 1~3 and resubmitting the sitemap to Search Console, after a few weeks the coverage report will accumulate these classifications:

| GSC Category | Meaning |
|--------------|---------|
| Not found (404) | URL previously indexed now returns 404 |
| Page with redirect | URL responds with 301/302 to another URL → excluded from indexing |
| Crawled - currently not indexed | Googlebot fetched body but judged it low value |
| Discovered - currently not indexed | URL seen in sitemap but not yet crawled |

These can be **either site-side problems or normal Google behavior**. Without breaking them down case by case, you're stuck repeating "why isn't this indexed?"

<pre class="mermaid">
graph TD
    GSC["Google Search Console<br/>Coverage Issue Report"] --> C1["① Not found (404)"]
    GSC --> C2["② Page with redirect"]
    GSC --> C3["③ Crawled - not indexed"]
    GSC --> C4["④ Discovered - not indexed"]

    C1 --> A1["Deleted old posts<br/>→ Normal (de-index wait)"]
    C2 --> A2["Missing trailing slash in internal links<br/>→ navigation fix"]
    C3 --> A3["Low-value archive pages<br/>→ noindex meta tag"]
    C3 --> A4["New posts<br/>→ Normal (indexing wait)"]
    C4 --> A5["Crawl budget<br/>→ Request indexing"]

    style C1 fill:#fff3e0,stroke:#e65100
    style C2 fill:#ffcccc,stroke:#c62828
    style C3 fill:#ffcccc,stroke:#c62828
    style C4 fill:#fff3e0,stroke:#e65100
    style A2 fill:#e8f5e9,stroke:#2e7d32
    style A3 fill:#e8f5e9,stroke:#2e7d32
</pre>

This article focuses on **site-side fixable cases** — ② and ③(low-value archive) via code, and explains why ①, ③(new posts), and ④ need no action.

---

# [02] Case ① — Not Found (404)

## 2-1. Symptom

```
https://cmaven.github.io/c++/C++-Class/             → 404
https://cmaven.github.io/c/C-Memory-Structure-Malloc/ → 404
```

In Part 3, old C/C++ posts were moved to `_archive/` and excluded from the build. The URLs correctly return 404, but Google's index still has the old data, so Search Console reports them as **"Not found (404)"**.

## 2-2. Diagnosis — Normal

| Check | Result |
|-------|--------|
| File exists under `_posts/`? | No (moved to `_archive/`) |
| GitHub Pages returns 404? | Yes (normal) |
| Other pages link to these URLs? | No (sidebar/category pages cleaned up) |

**"Return 404 for deleted posts"** is exactly the signal Google wants for natural de-indexing. No code change needed.

## 2-3. To Speed Up Cleanup

Use Search Console → **Removals** → **Temporary URL removal** to hide from search results for 6 months. During that period, Google re-crawls and naturally removes from the index.

:bulb: A 410 (Gone) response is a stronger de-index signal than 404, but GitHub Pages doesn't support custom HTTP status codes. Sticking with 404 is fine.
{: .notice--info}

---

# [03] Case ② — Page with Redirect

## 3-1. Symptom

```
https://cmaven.github.io/categories  → "Page with redirect"
```

Search Console accessed `/categories` (no trailing slash) and saw GitHub Pages **301 redirect to `/categories/`** (with slash), so it excluded the URL from indexing candidates.

## 3-2. Cause — Internal Links Without Trailing Slash

`_data/navigation.yml` had main menu entries without trailing slashes.

```yaml
# Before
- title: "Categories"
  url: /categories
- title: "Tags"
  url: /tags
```

But the actual page permalinks are:

```yaml
# _pages/categories-archive.md
permalink: /categories/   # ← with trailing slash

# _pages/tag-archive.md
permalink: /tags/         # ← with trailing slash
```

GitHub Pages auto-301s `/categories` → `/categories/`. No issue for users, but **Googlebot does not index redirecting URLs**. Leaving redirecting URLs in your main menu causes Search Console to keep reporting **"Page with redirect"**.

## 3-3. Fix — Add Trailing Slash to Navigation

```yaml
# _data/navigation.yml (after)
- title: "Categories"
  url: /categories/    # ← added trailing slash
- title: "Tags"
  url: /tags/          # ← added trailing slash
```

| Before | After | Effect |
|--------|-------|--------|
| `/categories` (301 redirect) | `/categories/` (200) | Googlebot reaches directly without redirect |
| `/tags` (301 redirect) | `/tags/` (200) | Same |

:bulb: Trailing slash policy must be consistent site-wide. If your permalink is `/foo/`, all internal links must also be `/foo/`.
{: .notice--info}

---

# [04] Case ③ — Crawled, Currently Not Indexed

This category is the most confusing. It means **"Googlebot got the page but didn't index it"**, with multiple possible reasons. For this site, three sub-cases.

## 4-1. (a) Low-Value Archive Pages — Need Site-Side Fix

Target URLs:

```
/categories/         (all categories list)
/categories/docker   (individual category archive)
/tags                (tags list)
/page7/              (pagination)
```

What these pages share:

| Trait | Description |
|-------|-------------|
| Content is a **list** | Hub for navigating to other posts |
| **Almost no unique text** | Title + link list |
| **Duplicated info across multiple URLs** | Same posts linked from sitemap.xml + category page + tag page |

From Google's perspective, "crawled but not worth indexing". They keep accumulating in this category. In Part 3, `sitemap: false` was applied to exclude from sitemap, but **`sitemap: false` only removes from the sitemap — it does NOT prevent Googlebot from following internal links and crawling them**.

Solution: emit **`<meta name="robots" content="noindex,follow">`** to explicitly tell Google "do not index this page (but feel free to follow links)".

## 4-2. (b) New Posts — Normal (Indexing Wait)

```
/claude/claude-code-skill-hook-guide-part1/   (crawled: 2026-04-28)
/claude/claude-code-multi-agent-part1/         (crawled: 2026-04-28)
/blog/mdx-vs-md-blog-rendering-performance/    (crawled: 2026-04-28)
...
```

Recently published posts are **crawled by Google but pending indexing decision**. The decision usually comes within days to weeks based on content quality, site authority, and crawling budget. **No fix needed** — accelerate via Search Console **URL Inspection → Request indexing**.

## 4-3. (c) Already-Deleted Old Posts — Same as Case ①

```
/c++/C++-Template/                       (crawled 2025-12-15)
/c++/C++-Static-Const-Explicit-Mutalbe/  (crawled 2025-11-21)
```

Posts moved to `_archive/` in Part 3. They remain in the index as stale data and will be cleaned up naturally. **No fix needed**.

---

# [05] Solution — Auto-Emit `noindex` Meta Tag

## 5-1. Design

We want `noindex` on archive/pagination pages, satisfying these conditions:

| Condition | Reason |
|-----------|--------|
| **Category archive pages** (`/categories/`, `/categories/docker`) | Low-value list |
| **Tag archive page** (`/tags/`) | Low-value list |
| **Pagination 2+** (`/page2/`, `/page7/`) | Variant of home page 1, duplicate content |
| **404 page** (`/404.html`) | No indexing value |
| ~~Home page 1 (`/`)~~ | **Must stay indexed** |
| ~~Individual posts (`/categories/foo/post-name/`)~~ | **Must stay indexed** |

Combine explicit flag (`page.noindex`) with auto-detection (paginator, URL).

## 5-2. Modify `_includes/seo.html`

In minimal-mistakes' `_includes/seo.html`, add this right before other meta tag outputs:

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

Three conditions are handled with separate `assign`s because **Liquid's `or`/`and` precedence evaluates right-to-left**, making one-liners error-prone.

| Condition | Action |
|-----------|--------|
| `page.noindex == true` | Page explicitly flagged in frontmatter |
| `page.url == "/404.html"` | 404 page |
| `paginator.page > 1` | Pagination page 2+ |

:warning: Pagination page 1 (`paginator.page == 1`) IS the home (`/`), so it must NEVER be noindex. The `paginator.page != 1` check is critical.
{: .notice--warning}

## 5-3. Add `noindex: true` to Archive Page Frontmatter

Since the Liquid checks `page.noindex`, add it to archive pages.

```yaml
# _pages/categories-archive.md
---
title: "Posts by Category"
layout: categories
permalink: /categories/
author_profile: true
sitemap: false
noindex: true        # ← add
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
noindex: true        # ← add
---
```

```yaml
# _pages/categories/*.md (all 16 category pages)
---
title: "Docker"
layout: archive
permalink: categories/docker
sitemap: false
noindex: true        # ← add
---
```

| Target | File count |
|--------|------------|
| `_pages/categories-archive.md` | 1 |
| `_pages/tag-archive.md` | 1 |
| `_pages/categories/*.md` | 16 |
| **Total** | **18 files** |

:bulb: Apply both `sitemap: false` (exclude from sitemap) + `noindex: true` (block indexing via meta tag). With only one, Google may still try to index via internal links.
{: .notice--info}

---

# [06] Verification

## 6-1. Check HTML

After build, archive pages like `_site/categories/docker.html` should contain in `<head>`:

```html
<meta name="robots" content="noindex,follow">
```

Regular posts (e.g., `_site/claude/claude-code-skill-hook-guide-part1/index.html`) should **NOT** have this tag.

## 6-2. URL Behavior Matrix

| URL | `noindex` emitted? | Intent |
|-----|:---:|--------|
| `/` (home page 1) | No | Keep indexed |
| `/page2/`, `/page7/` | Yes | Pagination noindex |
| `/categories/` | Yes | Archive noindex |
| `/categories/docker` | Yes | Individual category noindex |
| `/tags/` | Yes | Tag archive noindex |
| `/claude/claude-code-skill-hook-guide-part1/` | No | Keep post indexed |
| `/404.html` | Yes | 404 noindex |

## 6-3. Search Console Follow-Up

| Step | Action |
|------|--------|
| 1 | Push changes to GitHub (Pages auto-builds) |
| 2 | Search Console → **URL Inspection** → enter `/categories/`, `/categories/docker` → request indexing |
| 3 | Search Console → **Removals** → temporary delete for stale URLs from Case ① (optional) |
| 4 | After days/weeks, re-check coverage report. **"Crawled - not indexed"** → **"Excluded by 'noindex' tag"** (correct outcome) |

:bulb: Goal: archive pages move to the **"Excluded by 'noindex' tag"** category. "Crawled - not indexed" is an ambiguous gray area, while "Excluded by 'noindex'" is an explicit normal category.
{: .notice--info}

---

# [07] Summary

| # | Task | File |
|---|------|------|
| ① | Add trailing slash to navigation | `_data/navigation.yml` |
| ② | noindex emission logic in `seo.html` | `_includes/seo.html` |
| ③ | Add `noindex: true` to archive pages | `_pages/categories-archive.md`, `_pages/tag-archive.md`, `_pages/categories/*.md` (16) |
| | **Total** | **20 files** |

---

# [08] Key Lessons

## 8-1. `sitemap: false` vs `noindex` Are Different Signals

| Signal | Effect |
|--------|--------|
| `sitemap: false` (frontmatter) | Exclude from sitemap.xml only. Googlebot still crawls via internal links |
| `<meta name="robots" content="noindex">` | Allow crawl but **refuse indexing** |

For pages like archives/pagination that you want users to see but Google to ignore, **apply both**.

## 8-2. Trailing Slash Consistency

If permalinks and internal links differ in trailing slash format, users don't notice but **Search Console accumulates them as "Page with redirect"**. Pick one format and use it site-wide.

## 8-3. Search Console Classifications Are Diagnostic Tools

"Crawled - not indexed" not shrinking doesn't always mean a site problem. Archive pages belonging there is Google's correct judgment. The site's job is to send an explicit signal (`noindex`) saying **"yes, please don't index"**, so those pages move to the **Excluded by 'noindex'** category.

:star: Applying Series Parts 1 (post-level) → 2 (`_config.yml` for sitemap refresh) → 3 (site-wide sitemap quality) → 4 (Search Console residuals) lets you classify almost every coverage report URL as either **Indexed** or **intentionally noindex/404**.
{: .notice--info}
