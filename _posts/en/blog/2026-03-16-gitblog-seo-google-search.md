---
title: "Jekyll SEO Part 1 — Optimizing Post Frontmatter and Meta Tags"
description: "Guide to frontmatter, jekyll-seo-tag, and permalink settings to drive more Google search traffic to a Jekyll-based GitHub blog at the per-post level"
excerpt: "SEO series Part 1. The per-post SEO basics you can finish in a single post: description/excerpt/tags frontmatter, the jekyll-seo-tag plugin, and permalink and filename conventions"
date: 2026-03-16
categories: Github_Blog
tags: [SEO, Google-Search, Jekyll, frontmatter, sitemap, jekyll-seo-tag, SEO-Series-Part-1, SEO-Series]
ref: gitblog-seo-google-search
---

:bulb: A **4-part series** on SEO for a Jekyll-based GitHub blog. This post (Part 1) covers **per-post frontmatter and meta tag optimization** — the area you address with every post and the one that grows search traffic fastest.
{: .notice--info}

:bulb: **SEO series overview**
- **Part 1 (this post)** — Per-post SEO: frontmatter, `jekyll-seo-tag`, permalink and filenames
- **[Part 2](/en/github_blog/jekyll-sitemap-google-indexing-fix/)** — Making sure the sitemap updates properly: diagnosing and fixing 3 missing lines in `_config.yml` (`url`, `future`, `timezone`)
- **[Part 3](/en/github_blog/jekyll-sitemap-seo-audit-fix/)** — Site-wide SEO audit: sitemap quality, verification meta tags, bulk-filling missing descriptions, 404 and archive cleanup
- **[Part 4](/en/github_blog/search-console-noindex-redirect-cleanup/)** — Clearing remaining Google Search Console issues: diagnosing 404, redirect, and "Crawled - currently not indexed" buckets and applying `noindex` meta tags
{: .notice}

# [01] What is SEO?

> **SEO (Search Engine Optimization)** is the practice of structuring a web page so search engines understand its content well and surface it in higher positions in search results.

- Google sends a web crawler (Googlebot) that visits the page and parses `<title>`, `<meta>` tags, body text, and URL structure
- That information feeds the search result **title**, **snippet (description)**, and **ranking**
- In a Jekyll blog, you control these via **frontmatter** and **plugins**

# [02] Optimizing frontmatter for SEO

Adding SEO-related fields to a Jekyll post's frontmatter helps search engines understand the page more accurately.

## 2-1. Before (default frontmatter)

```yaml
---
title: "Ubuntu 24.04 Korean Input Method Install and Toggle Key Setup"
date: 2026-03-16
categories: Linux
tags: [Ubuntu, fcitx, ibus, hangul, Korean-input]
---
```

What Google shows for this state:

| Item | Source | Issue |
|------|--------|-------|
| Search title | `title` value | Applied (OK) |
| Search snippet | Auto-extracted from body | Google picks arbitrarily; may be inaccurate |
| List preview | First line of body | Unintended content may appear |
| Search keyword coverage | 5 `tags` | Limited inflow paths |

## 2-2. After (SEO-optimized frontmatter)

```yaml
---
title: "Ubuntu 24.04 Korean Input Method Install and Toggle Key Setup"
description: "How to install fcitx and ibus Korean input methods on Ubuntu 24.04, plus the toggle-key shortcut setup"
excerpt: "After installing Ubuntu 24.04 LTS in English, how to install fcitx-hangul and ibus-hangul Korean input methods and configure the Korean/English toggle shortcut"
date: 2026-03-16
categories: Linux
tags: [Ubuntu, Ubuntu-24.04, fcitx, fcitx-hangul, ibus, ibus-hangul, Korean-input, hangul-toggle, Linux-Korean, Korean-input]
---
```

Improved outcome:

| Item | Source | Improvement |
|------|--------|-------------|
| Search title | `title` value | Same |
| Search snippet | `description` value | Your intended description appears |
| List preview | `excerpt` value | Clean rendering on list pages |
| Search keyword coverage | 10 `tags` | More entry-point queries |

## 2-3. Role of each field

### description

```yaml
description: "How to install fcitx and ibus Korean input methods on Ubuntu 24.04, plus the toggle-key shortcut setup"
```

- Converted to the HTML `<meta name="description">` tag
- Used as the **snippet** under the title in Google search results
- Recommended length: **50–160 characters** (too short = insufficient info, too long = truncated)
- Should naturally include key keywords

:warning: If `description` is missing, Google extracts arbitrary text from the body, which often results in an unintended snippet.
{: .notice--warning}

### excerpt

```yaml
excerpt: "After installing Ubuntu 24.04 LTS in English, how to install fcitx-hangul and ibus-hangul Korean input methods and configure the Korean/English toggle shortcut"
```

- Used by Minimal Mistakes as the preview text on **post listing pages**
- When using `jekyll-seo-tag`, `excerpt` falls back as the description if `description` is absent
- Writing a different sentence from `description` covers a wider range of keywords

### Expanded tags

```yaml
# Before
tags: [Ubuntu, fcitx, ibus, hangul, Korean-input]

# After
tags: [Ubuntu, Ubuntu-24.04, fcitx, fcitx-hangul, ibus, ibus-hangul, Korean-input, hangul-toggle, Linux-Korean, Korean-input]
```

- Include the keywords users actually search for
- Mix Korean and English terms to cover both audiences
- Add version info (`Ubuntu-24.04`) for version-specific searches
- Add package names (`fcitx-hangul`) for technical searches

# [03] The jekyll-seo-tag Plugin

## 3-1. What the plugin does

`jekyll-seo-tag` automatically converts your `title`, `description`, `excerpt`, etc. into HTML `<meta>` tags.

Before/after comparison:

```html
<!-- Without jekyll-seo-tag (default) -->
<title>Ubuntu 24.04 Korean Input Method Install and Toggle Key Setup - Blog</title>

<!-- With jekyll-seo-tag (auto-generated) -->
<title>Ubuntu 24.04 Korean Input Method Install and Toggle Key Setup - Blog</title>
<meta name="description" content="How to install fcitx and ibus Korean input methods on Ubuntu 24.04, plus the toggle-key shortcut setup">
<meta property="og:title" content="Ubuntu 24.04 Korean Input Method Install and Toggle Key Setup">
<meta property="og:description" content="How to install fcitx and ibus ...">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary">
<link rel="canonical" href="https://xxx.github.io/linux/ubuntu-2404-korean-input-setup/">
```

:bulb: **Open Graph** tags like `og:title` and `og:description` are emitted automatically, so social shares display the correct title and description.
{: .notice--info}

## 3-2. Installation

Add to **Gemfile**:

```ruby
gem "jekyll-seo-tag"
```

Add to the plugins section of **_config.yml**:

```yaml
plugins:
  - jekyll-paginate
  - jekyll-sitemap
  - jekyll-gist
  - jekyll-feed
  - jekyll-include-cache
  - jemoji
  - jekyll-seo-tag    # added
```

Install from the terminal:

```bash
bundle install
```

:warning: GitHub Pages supports `jekyll-seo-tag` by default, so it works just by adding the entry in `_config.yml` — no additional configuration required.
{: .notice--warning}

## 3-3. Strengthen site-level info in _config.yml

`jekyll-seo-tag` also pulls from your `_config.yml` site metadata. Make sure these fields are set.

```yaml
# _config.yml
title: "Blog"
description: "Work notes"
url: "https://cmaven.github.io"   # Site URL (without this, canonical URL cannot be generated)
author:
  name: "cmaven"
```

:warning: If `url` is empty, the `canonical` tag and Open Graph URL won't be generated, so you must set it.
{: .notice--warning}

# [04] Using sitemap.xml

## 4-1. Verify auto-generation

If `jekyll-sitemap` is already installed, `sitemap.xml` is generated automatically on build.

```
https://cmaven.github.io/sitemap.xml
```

## 4-2. Request indexing after a new post

After pushing a new post, to get it indexed quickly via Google Search Console:

1. Open **Google Search Console**
2. Paste the **URL of the new post** into the top search bar
3. Click **Request Indexing**

Alternatively, resubmit `sitemap.xml` from the **Sitemaps** menu to re-crawl the entire site.

:bulb: After a push, Google can take several days to crawl automatically. Requesting indexing speeds things up considerably.
{: .notice--info}

# [05] URL Structure Optimization

## 5-1. permalink settings

Including meaningful keywords in the URL helps search engines grasp what the page is about.

```yaml
# _config.yml

# Default (with date)
permalink: /:categories/:year/:month/:day/:title/
# → /linux/2026/03/16/ubuntu-2404-korean-input-setup/

# Compact form (recommended)
permalink: /:categories/:title/
# → /linux/ubuntu-2404-korean-input-setup/
```

:bulb: The filename itself becomes part of the URL, so it's important to include core keywords in the filename.
{: .notice--info}

## 5-2. Filename tips

```
# Good — clear keywords
2026-03-16-ubuntu-2404-korean-input-setup.md

# Bad — keyword-poor
2026-03-16-setup-guide.md
2026-03-16-post1.md
```

# [06] Checklist

When writing a new post, going through this list will boost search traffic from Google.

| # | Item | Done |
|---|------|------|
| 1 | `title` contains core keywords | ☐ |
| 2 | `description` is 50–160 characters | ☐ |
| 3 | `excerpt` is written (for list previews) | ☐ |
| 4 | `tags` covers multiple keywords in Korean and English | ☐ |
| 5 | Filename contains core keywords | ☐ |
| 6 | `jekyll-seo-tag` plugin is installed | ☐ |
| 7 | `url` is set in `_config.yml` | ☐ |
| 8 | After push, indexing requested from Google Search Console | ☐ |

:star: Just bolstering `description` and `tags` in frontmatter can significantly improve search traffic. Add `jekyll-seo-tag` on top of that and Open Graph and canonical URLs are emitted automatically — maximizing SEO impact.
{: .notice--info}

---

# [07] Up Next

Part 1 covered only what you can finish at the **per-post level**. However, you may notice that pushing new posts does **not refresh the sitemap `Last read` in Google Search Console and new posts go un-indexed**. Before chasing generic causes (crawl budget, content quality), this can be a concrete code-level issue: missing `_config.yml` settings.

In [Part 2](/en/github_blog/jekyll-sitemap-google-indexing-fix/), I walk through the diagnosis and fix for **3 missing lines in `_config.yml`** (`url`, `future`, `timezone`) that turn out to be the real cause of stale sitemaps and missing indexing.

Then [Part 3](/en/github_blog/jekyll-sitemap-seo-audit-fix/) raises **sitemap quality** itself site-wide (removing low-value URLs, verification meta tags, filling missing descriptions, 404 pages, etc.) now that the sitemap actually updates. [Part 4](/en/github_blog/search-console-noindex-redirect-cleanup/) wraps up the 4 remaining Search Console issue categories with `noindex` and trailing-slash cleanup.
