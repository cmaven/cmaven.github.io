---
title: "Jekyll Build Error — Fixing the slugify Integer gsub Failure"
description: "Cause and fix for the gsub NoMethodError thrown when an Integer is passed to the slugify filter during a GitHub Pages Jekyll build — solved with append '' as a defensive pipe"
excerpt: "Liquid Exception: undefined method gsub for an instance of Integer — fixed by adding a single append '' before slugify"
date: 2026-04-20
categories: Github_Blog
tags: [Jekyll, Liquid, slugify, gsub, Integer, GitHub-Pages, build-error, frontmatter, YAML, troubleshooting]
ref: jekyll-slugify-integer-build-error-fix
---

:bulb: This post summarizes the cause and fix for an `undefined method 'gsub' for an instance of Integer` error that breaks the Jekyll build on GitHub Pages and blocks deployment.
{: .notice--info}

---

# [01] The Problem

After pushing to GitHub, the blog stopped updating. Checking the GitHub Actions build log revealed the following repeating error.

    Liquid Exception: undefined method `gsub' for an instance of Integer in /_layouts/single.html
    /usr/local/bundle/gems/jekyll-3.10.0/lib/jekyll/utils.rb:367:
      in `replace_character_sequence_with_hyphen':
      undefined method `gsub' for an instance of Integer (NoMethodError)

        string.gsub(replaceable_char, "-")
              ^^^^^

**Symptoms:**
- Site does not update after push
- GitHub Actions build is marked "success" but actually serves the previous cache
- New posts missing from sitemap.xml
- New post URLs return 404

---

# [02] Cause Analysis

## 2-1. Where the Error Occurs

The error originates from the `/_layouts/single.html` layout. Following the stack trace:

    single.html → post__taxonomy.html → slugify filter

The culprit is the part of `_includes/post__taxonomy.html` that iterates over categories and tags and calls the `slugify` Liquid filter.

    {{ category_word | slugify }}
    {{ tag_word | slugify }}

## 2-2. Why an Integer Ended Up There

`slugify` internally calls `gsub` on a string. If YAML in a post's frontmatter **interprets a value as a number (Integer)**, an Integer is handed to `slugify` and triggers the error.

Examples YAML parses as numbers:

    tags: [404]              # ← parsed as Integer 404
    tags: [123, abc]         # ← 123 is Integer, abc is String
    categories: 2026         # ← parsed as Integer

What you intended:

    tags: ["404"]            # ← quoted as String
    tags: [abc, def]         # ← contains letters, treated as String
    categories: "2026"       # ← quoted as String

## 2-3. Why It's Severe

- The **filename of the offending post is not shown in the log** → hard to identify the culprit file
- Jekyll halts the build, so **the entire site fails to deploy** (not just new posts — existing posts also stop updating)
- GitHub Actions sometimes reports "success" anyway, making **it easy to miss the build failure**

---

# [03] Fix

## 3-1. Root Fix — Add `append ''` Before `slugify`

Adding `| append: ''` before `slugify` **coerces any type into a string**.

**Before:**

    {{ category_word | slugify }}

**After:**

    {{ category_word | append: '' | slugify }}

`append: ''` concatenates an empty string, so the value is unchanged in content but the type is forcibly converted from Integer to String.

## 3-2. Files That Need the Fix

| File | Locations |
|------|-----------|
| `_includes/post__taxonomy.html` | `category_word \| slugify`, `tag_word \| slugify` (2 spots) |
| `_includes/category-list.html` | `category_word \| slugify` (1) |
| `_includes/tag-list.html` | `tag_word \| slugify` (1) |
| `_layouts/categories.html` | `category[0] \| slugify` (2) |
| `_layouts/tags.html` | `tag[0] \| slugify` (2) |

## 3-3. Prevention — Frontmatter Authoring Rules

Anything that could be parsed as a number should be **wrapped in quotes**.

    # Dangerous — may parse as Integer
    tags: [404, 500]

    # Safe — explicit String
    tags: ["404", "500"]

---

# [04] Debugging Method

How to track down the offending file the next time this error fires.

## 4-1. Check GitHub Actions Build Logs

1. GitHub repo → **Actions** tab
2. Click the latest **workflow run**
3. Click the **build** step
4. Look for the `Liquid Exception` line

## 4-2. Search All Posts for Numeric Values

    # Find posts whose categories is a number
    grep -rn "^categories:" _posts/ | grep -E ": [0-9]+$"

    # Find tag arrays containing pure numbers
    grep -rn "^tags:" _posts/ | grep -E "[, \[][0-9]+[,\]]"

## 4-3. Watch for Frontmatter Examples Inside Post Bodies

When showing a frontmatter snippet inside a post, if the `---` separators sit outside a code block, Jekyll can parse them as actual frontmatter.

    # Dangerous — the --- inside the code block can be picked up as frontmatter
    ```yaml
    ---
    date: 2022-02-16
    tags: [pip, error]
    ---
    ```

    # Safe — display the code by indenting instead
        date: 2022-02-16
        tags: [pip, error]

---

# [05] Summary

| Item | Detail |
|------|--------|
| **Error message** | `undefined method 'gsub' for an instance of Integer` |
| **Trigger** | `slugify` Liquid filter |
| **Cause** | YAML parsed a frontmatter value as Integer |
| **Fix** | Add `\| append: ''` before `slugify` (8 spots) |
| **Prevention** | Quote numeric values; watch `---` inside code samples |

:warning: This error **does not name the offending file in the log**. When the build fails, first inspect the frontmatter of the most recently changed post — then verify the `slugify` defensive code is in place.
{: .notice--warning}
