---
title: "Jekyll SEO Part 3 — Site-Wide Sitemap Quality Audit and Cleanup"
description: "After the 3-line _config.yml fix in Part 2, audit the whole repository: low-value sitemap URLs, missing verification meta tags, missing descriptions, no 404 page — and how to fix them in bulk"
excerpt: "SEO series Part 3. When categories/tags/pagination get mixed into the sitemap, Google judges the entire sitemap as low quality. A site-wide audit and the fixes that followed"
date: 2026-04-20
categories: Github_Blog
tags: [Jekyll, sitemap, SEO, Google-Search-Console, sitemap-false, description, meta-tags, 404, canonical, indexing-optimization, SEO-Series-Part-3, SEO-Series]
ref: jekyll-sitemap-seo-audit-fix
---

:bulb: SEO Series Part 3. **[Part 1](/en/github_blog/gitblog-seo-google-search/)** covered post-level SEO basics. **[Part 2](/en/github_blog/jekyll-sitemap-google-indexing-fix/)** made the sitemap actually generate and refresh via a 3-line fix in `_config.yml`. Now that the sitemap is working, the next step is **what goes into it — i.e., the quality of the sitemap itself**. This post summarizes 5 issues found while auditing the whole repository and the bulk fixes applied.
{: .notice--info}

:bulb: **SEO Series Layout**
- **[Part 1](/en/github_blog/gitblog-seo-google-search/)** — Post-level SEO: frontmatter, `jekyll-seo-tag`, permalink and filename
- **[Part 2](/en/github_blog/jekyll-sitemap-google-indexing-fix/)** — Making sitemap refresh properly: `_config.yml` url/future/timezone — 3-line diagnosis and fix
- **Part 3 (this post)** — Site-wide SEO audit: sitemap quality, verification meta tags, bulk description fix, 404/archive cleanup
- **[Part 4](/en/github_blog/search-console-noindex-redirect-cleanup/)** — Cleaning up Google Search Console residuals: diagnosing 404/redirect/"crawled-not-indexed" and applying `noindex` meta tags
{: .notice}

**Environment**: Jekyll 3.x + minimal-mistakes + GitHub Pages + jekyll-sitemap plugin

---

# [01] Why Audit

In Part 2, `url`, `future`, and `timezone` were set so the sitemap is generated/refreshed under the correct domain. Before registering with Google Search Console, however, it was worth inspecting **the sitemap's quality itself**.

Opening sitemap.xml showed:

```
Out of 119 URLs total:
  ├── Post URLs: 85 (71%)        ← valuable content
  ├── Category pages: 17 (14%)   ← just lists
  ├── Tag pages: 1
  ├── pagination: 3 (/page2/, /page3/)
  ├── Home page: 1
  └── Other: 12
```

From Google's perspective this looks like **"this sitemap is mostly unchanging low-value URLs with a few updates"** — and it stops re-reading.

---

# [02] Issues Found (5)

<pre class="mermaid">
graph TD
    AUDIT["Repo-wide SEO audit"] --> P1["① Low-value URLs<br/>mixed in sitemap"]
    AUDIT --> P2["② Verification meta tags<br/>not set in _config.yml"]
    AUDIT --> P3["③ 9 posts missing<br/>description"]
    AUDIT --> P4["④ No 404 page"]
    AUDIT --> P5["⑤ Build output (_site)<br/>has localhost URLs"]

    P1 --> S1["Sitemap trust ↓<br/>Google stops re-reading"]
    P2 --> S2["HTML meta tags<br/>not rendered"]
    P3 --> S3["Search results show<br/>generic snippet"]
    P4 --> S4["Bad URL hit shows<br/>default 404 (UX hurt)"]
    P5 --> S5["Local build only<br/>resolved at deploy"]

    style P1 fill:#ffcccc,stroke:#c62828
    style P2 fill:#ffcccc,stroke:#c62828
    style P3 fill:#fff3e0,stroke:#e65100
    style P4 fill:#f5f5f5,stroke:#616161
    style P5 fill:#f5f5f5,stroke:#616161
</pre>

| Severity | Issue | Impact |
|----------|-------|--------|
| **CRITICAL** | Sitemap includes category/tag/pagination URLs | Entire sitemap quality drops, Google stops re-reading |
| **CRITICAL** | `google_site_verification`, `naver_site_verification` empty | Verification HTML files exist but meta tags not rendered |
| **WARNING** | 9 posts missing `description` frontmatter | Search results show site default ("작업노트") |
| **INFO** | No custom 404 page | Bad URL hits show default page |
| **INFO** | `_site/` build output contains localhost URLs | Auto-rebuilt on GitHub Pages deploy → no real impact |

---

# [03] Fix ① — Remove Low-Value URLs from Sitemap

## 3-1. Diagnosis

The `jekyll-sitemap` plugin includes **every page** in the sitemap by default. Category, tag, and pagination pages are **listing pages**, not content — there is no reason to submit them to Google.

```
URLs that should NOT be in sitemap.xml:
  /categories/           ← category list
  /categories/linux      ← single category archive
  /categories/git        ← single category archive
  /tags/                 ← tag list
  /page2/, /page3/       ← pagination
  /                      ← home page
```

## 3-2. Fix

The `jekyll-sitemap` plugin excludes a page from the sitemap when its frontmatter has **`sitemap: false`**.

**Files to modify (19):**

| File | Purpose |
|------|---------|
| `_pages/categories-archive.md` | All-categories list |
| `_pages/categories/*.md` (16) | Per-category archives |
| `_pages/tag-archive.md` | Tag list |
| `index.html` | Home page |

**Add one line to frontmatter:**

```yaml
# Before
---
title: "Linux"
layout: archive
permalink: categories/linux
---

# After
---
title: "Linux"
layout: archive
permalink: categories/linux
sitemap: false              # ← add this single line
---
```

## 3-3. Result

```
Before: 119 URLs in sitemap (85 posts + 34 low-value)
After: only post URLs in sitemap
```

---

# [04] Fix ② — Set Verification Meta Tags

## 4-1. Diagnosis

Google Search Console and Naver Webmaster ownership **verification files** existed at the root, but `_config.yml`'s verification values were empty so the **HTML meta tags were not rendered**.

```yaml
# Problem state
google_site_verification :    # ← empty
naver_site_verification  :    # ← empty
```

Minimal Mistakes' `seo.html` only emits the meta tag when these values exist:

```html
{% raw %}{% if site.google_site_verification %}
  <meta name="google-site-verification" content="{{ site.google_site_verification }}" />
{% endif %}{% endraw %}
```

## 4-2. Fix

Extract the value from the verification filename and set it in `_config.yml`.

```yaml
# After
google_site_verification : "google6751f2559208d5b3"
naver_site_verification  : "naver62d9a931d0465dfc21a3946c3128be56"
```

With this, ownership is verified by **both verification file and meta tag** — more robust.

---

# [05] Fix ③ — Backfill Missing `description` on Posts

## 5-1. Diagnosis

Out of 81 posts, **9 (11%)** were missing the `description` frontmatter.

```
Posts missing description:
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

Without `description`, the SEO template falls back to `excerpt` → `site.description` ("작업노트"), so Google search results show a **generic snippet unrelated to the content**.

## 5-2. Fix

Add a 50~160 character `description` and `excerpt` based on each post's content.

**Before:**

    title: "Resolving pip 'No module named pip' error"
    date: 2022-02-16
    categories: Python
    tags: [pip, error]

**After:**

    title: "Resolving pip 'No module named pip' error"
    description: "When 'No module named pip' shows up while running pip ..."
    excerpt: "Reinstalling pip with get-pip.py when it breaks"
    date: 2022-02-16
    categories: Python
    tags: [pip, error]

---

# [06] Fix ④ — Create a 404 Page

## 6-1. Problem

Without a custom 404 page, the GitHub Pages default 404 shows up and users are much more likely to leave the site.

## 6-2. Fix

Create `404.md` at the root:

```markdown
---
title: "Page Not Found"
layout: single
permalink: /404.html
author_profile: true
sitemap: false
---

The requested page does not exist or has moved.

- [Back to Home](/)
- [Browse Categories](/categories/)
- [Browse Tags](/tags/)
```

:bulb: Set `sitemap: false` so the 404 page itself is excluded from the sitemap.
{: .notice--info}

---

# [07] Extra — Archive C/C++ Posts

While auditing, 20 C/C++ posts from 2018 were sitting in the sitemap, reinforcing the **"mostly unchanging site"** impression. They were moved to `_archive/` to exclude from the build.

```
_posts/program_language/c/    (8 files)  → _archive/program_language/c/
_posts/program_language/c++/  (12 files) → _archive/program_language/c++/
```

| Item | Treatment |
|------|-----------|
| Post files | Moved to `_archive/` (preserved, excluded from build) |
| Sidebar | C, C++ entries removed |
| Category pages | `_pages/categories/c.md`, `c++.md` deleted |
| sitemap | Outside `_posts` so auto-excluded |
| Restore path | Move back from `_archive/` to `_posts/` to restore instantly |

---

# [08] Total Change Summary

<pre class="mermaid">
graph LR
    subgraph Before["Before"]
        B1["sitemap: 119 URLs<br/>(incl. 34 low-value)"]
        B2["Verification meta: not rendered"]
        B3["Missing description: 9"]
        B4["404: default page"]
        B5["20 C/C++: in sitemap"]
    end

    subgraph After["After"]
        A1["sitemap: posts only<br/>(high-quality URLs)"]
        A2["Verification meta: rendered"]
        A3["description: 100% coverage"]
        A4["404: custom page"]
        A5["C/C++: _archive<br/>(excluded from build)"]
    end

    B1 -->|sitemap: false| A1
    B2 -->|_config.yml set| A2
    B3 -->|frontmatter added| A3
    B4 -->|404.md created| A4
    B5 -->|moved to _archive/| A5

    style Before fill:#ffcccc,stroke:#c62828
    style After fill:#e8f5e9,stroke:#2e7d32
</pre>

| # | Task | Files |
|---|------|-------|
| ① | `sitemap: false` for category/tag/home | 19 |
| ② | Set verification meta tags | 1 (`_config.yml`) |
| ③ | Backfill missing descriptions | 9 |
| ④ | Create 404 page | 1 |
| ⑤ | Move C/C++ to archive | 22 (20 posts + 2 categories) |
| | **Total** | **52 files** |

---

# [09] Google Search Console Registration Checklist

After applying all the above, this is the final pre-registration checklist.

| Check | How | Expected |
|-------|-----|----------|
| sitemap URL | Open `https://cmaven.github.io/sitemap.xml` | Only post URLs, no localhost |
| canonical URL | Post page source → `<link rel="canonical">` | `https://cmaven.github.io/...` |
| Verification meta tags | Page source → search `google-site-verification` | Meta tag present |
| robots.txt | `https://cmaven.github.io/robots.txt` | Contains `Sitemap: https://cmaven.github.io/sitemap.xml` |
| 404 page | Hit a non-existent URL | Custom 404 shown |
| Open Graph | Post source → search `og:title`, `og:description` | Unique values per post |

:bulb: Applying Part 1 (post-level SEO) → Part 2 (`_config.yml` for sitemap refresh) → this post (sitemap quality) dramatically raises the chance Google trusts the sitemap and re-reads it regularly.
{: .notice--info}

---

# [10] Next in the Series

Once you submit/resubmit the sitemap to Search Console with everything above applied, the coverage report will start accumulating results over the next few days/weeks. At that point you can see **"the residual issues Google sees on this site"**:

- **Not found (404)** — old posts removed but still in Google's index
- **Page with redirect** — internal links written without trailing slash, hit GitHub Pages 301 responses
- **Crawled - currently not indexed** — low-value pages like category/tag/pagination where Google saw the content but did not index

[Part 4](/en/github_blog/search-console-noindex-redirect-cleanup/) interprets these 4 categories and finishes the cleanup with **automatic `noindex` meta tag emission** and **navigation trailing-slash cleanup**.
