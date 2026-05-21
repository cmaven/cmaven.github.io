---
title: "Adding a New Category to a Jekyll Blog (Minimal Mistakes)"
description: "How to add a sidebar category to a Minimal Mistakes Jekyll blog and link posts to it"
excerpt: "A 3-step guide for adding a new category via navigation.yml, a category archive page, and post frontmatter"
date: 2026-03-13
categories: Github_Blog
tags: [Jekyll, category, sidebar, Minimal-Mistakes, navigation, add-category, sidebar-menu]
ref: gitblog-add-category
---

:bulb: This post walks through how to add a new category in a Minimal Mistakes based Jekyll blog, expose it in the sidebar, and have posts show up under it.
{: .notice--info}

# [01] Overall Flow

To add a new category, you need to **modify or create 3 things**.

| Order | File | Role |
|---|---|---|
| 1 | `_data/navigation.yml` | Add the category link to the sidebar |
| 2 | `_pages/categories/<category>.md` | Create the category archive page |
| 3 | `_posts/<dir>/<post>.md` | Set the `categories` frontmatter on the post |

---

# [02] Step 1: Add the Category to the Sidebar

## 2-1. Edit `_data/navigation.yml`

The sidebar menu structure is managed in the `cmaven_sidebar` section of `_data/navigation.yml`.

```yaml
# _data/navigation.yml

cmaven_sidebar:
  - title: "운영체제"          # Top-level group (group title)
    children:
      - title: "Linux"        # Sub-item (category link)
        url: /categories/linux
      - title: "Windows"
        url: /categories/windows
  - title: "프로그래밍언어"
    children:
      - title: "Python"
        url: /categories/python
```

**How to add a new category:**

### (A) Add to an existing group

Add a `children` entry under an existing top-level group.

```yaml
  - title: "프로그래밍언어"
    children:
      - title: "Python"
        url: /categories/python
      - title: "NewLang"           # added
        url: /categories/newlang   # added
```

### (B) Create a new group

Create a new top-level group and place the category underneath it.

```yaml
  - title: "AI"                    # New top-level group
    children:
      - title: "Claude"           # New category
        url: /categories/claude
```

:bulb: `title` is the name shown in the sidebar, and `url` is the path of the category archive page. The `url` must match the `permalink` of the page you'll create in **Step 2**.
{: .notice--info}

---

# [03] Step 2: Create the Category Archive Page

## 3-1. Create an .md file in `_pages/categories/`

This is the page displayed when the sidebar link is clicked.

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

**Field-by-field explanation:**

| Field | Value | Description |
|---|---|---|
| `title` | `"Claude"` | Title displayed at the top of the page |
| `layout` | `archive` | Uses the Minimal Mistakes archive layout |
| `permalink` | `categories/claude` | URL path for this page (must match `url` in `navigation.yml`) |
| `site.categories.Claude` | - | The list of posts Jekyll has collected under the `Claude` category |

:warning: The **case** of `site.categories.Claude` must exactly match the `categories` value in the post frontmatter. If the post uses `categories: Claude`, you must use `site.categories.Claude` here as well.
{: .notice--warning}

## 3-2. Reference existing category pages

Looking at the existing files makes the structure easy to follow.

```
_pages/categories/
├── c.md           # categories: C
├── c++.md         # categories: C++
├── docker.md      # categories: Docker
├── git.md         # categories: Git
├── linux.md       # categories: Linux
├── python.md      # categories: Python
└── claude.md      # categories: Claude  ← newly added
```

---

# [04] Step 3: Write the Post

## 4-1. Create the post file

Create the `.md` file under `_posts/` with whatever directory structure you prefer.

```
_posts/
├── operating_system/linux/
├── program_language/python/
├── ai/claude/                     ← new directory
│   └── 2026-03-13-my-post.md
└── ...
```

:bulb: The directory layout under `_posts/` is unrelated to how posts are classified. Jekyll determines the category from the **`categories` value in frontmatter**. Directories are only for file management convenience.
{: .notice--info}

## 4-2. frontmatter settings

```yaml
---
title: "Post Title"
date: 2026-03-13
categories: Claude          # ← this determines the category
tags: [Claude Code, Agent]
---
```

**Key point:** the `categories` value must match `site.categories.Claude` from Step 2 exactly, case included, for the post to appear on that category page.

---

# [05] Summary of the Wiring

The values across the 3 files must line up for everything to work correctly.

| File | Value | Linked To |
|---|---|---|
| `_data/navigation.yml` | `url: /categories/claude` | → `permalink` in `_pages` |
| `_pages/categories/claude.md` | `permalink: categories/claude` | ← `url` in `navigation.yml` |
| `_pages/categories/claude.md` | `site.categories.Claude` | → `categories` in posts |
| `_posts/.../post.md` | `categories: Claude` | ← `site.categories` in `_pages` |

```
navigation.yml          _pages/categories/claude.md         _posts/.../post.md
url: /categories/claude  ←→  permalink: categories/claude
                              site.categories.Claude  ←→  categories: Claude
```

---

# [06] Verification

## 6-1. Local check

```shell
bundle exec jekyll serve
```

Open `http://localhost:4000` in a browser and confirm:

1. The new category appears in the **sidebar**
2. Clicking the link shows the post list on the **archive page**
3. Clicking a post shows the **body** correctly

## 6-2. Checklist when posts don't appear

| Symptom | Cause | Fix |
|---|---|---|
| No menu in sidebar | `navigation.yml` not updated | Add entry to `cmaven_sidebar` |
| 404 on menu click | Category page not created | Create `_pages/categories/xxx.md` |
| Page exists but no posts | `categories` case mismatch | Check that post frontmatter and `site.categories.XXX` match |
| Post date in the future | Jekyll hides future-dated posts by default | Add `future: true` to `_config.yml` or fix the date |

---

# [07] Real Example: Adding the Claude Category

The actual process used to add the Claude category to this blog.

## 7-1. Add to `_data/navigation.yml`

```yaml
  - title: "AI"
    children:
      - title: "Claude"
        url: /categories/claude
```

## 7-2. Create `_pages/categories/claude.md`

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

## 7-3. Verify the post frontmatter

```yaml
---
title: "Claude Code Complete Guide: Automating Coding Workflows with Skill, Hook, and CLAUDE.md"
date: 2026-03-13
categories: Claude
tags: [Claude Code, Skill, Hook, CLAUDE.md, Agent]
---
```

With those three pieces in place, clicking the sidebar "AI > Claude" displays the matching posts as a list.
