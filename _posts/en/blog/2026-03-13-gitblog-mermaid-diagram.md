---
title: "Adding Mermaid Diagrams to a Jekyll Blog"
description: "How to configure Mermaid CDN in a Jekyll (Minimal Mistakes) blog so you can use code-based diagrams"
excerpt: "Use the Mermaid v11 CDN to draw flowcharts, sequence diagrams, Gantt charts and more in a Jekyll blog"
date: 2026-03-13
categories: Github_Blog
tags: [Jekyll, Mermaid, diagram, flowchart, CDN, Minimal-Mistakes]
ref: gitblog-mermaid-diagram
---

:bulb: This post explains how to set up Mermaid in a Jekyll (Minimal Mistakes) blog so you can draw code-based diagrams.
{: .notice--info}

# [01] What is Mermaid?

Mermaid is a JavaScript library that **generates diagrams from text**.
With simple syntax inside Markdown you can draw flowcharts, sequence diagrams, class diagrams, and more.

| Feature | Description |
|---|---|
| Code-based | Author diagrams as text — no image files |
| Live rendering | Converted to SVG in the browser via JavaScript |
| Git-friendly | Because it's text, you can track diffs |
| Many diagram types | Flowchart, sequence, Gantt, pie, class, etc. |

---

# [02] Setup

## 2-1. Edit `_includes/head/custom.html`

In the Minimal Mistakes theme, custom scripts can be added in `_includes/head/custom.html`. Append the Mermaid CDN script at the bottom of that file.

```html
<!-- ======= mermaid diagram ======= -->
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true, theme: 'default' });
</script>
```

**Explanation:**

| Item | Description |
|---|---|
| `type="module"` | Loaded as an ES Module |
| `mermaid@11` | Uses Mermaid v11 (latest stable) |
| `startOnLoad: true` | Automatically renders diagrams on page load |
| `theme: 'default'` | Applies the default theme (changeable to `dark`, `forest`, `neutral`, etc.) |

:bulb: `_includes/head/custom.html` is included in the `<head>` of every page, so a one-time setup enables Mermaid for all posts.
{: .notice--info}

---

## 2-2. Confirm the setup

No separate plugin install or `_config.yml` change is required. Because it's loaded directly from a CDN, it also works on GitHub Pages out of the box.

---

# [03] Usage

Inside a post (.md), write Mermaid syntax inside a `<pre class="mermaid">` tag as shown below.

## 3-1. Flowchart

**Example:**

```html
<pre class="mermaid">
graph LR
    A[Start] --> B{Check condition}
    B -->|Yes| C[Execute]
    B -->|No| D[End]
    C --> D
</pre>
```

**Result:**

<pre class="mermaid">
graph LR
    A[Start] --> B{Check condition}
    B -->|Yes| C[Execute]
    B -->|No| D[End]
    C --> D
</pre>

---

## 3-2. Sequence diagram

**Example:**

```html
<pre class="mermaid">
sequenceDiagram
    participant Client
    participant Server
    participant DB
    Client->>Server: Request
    Server->>DB: Query
    DB-->>Server: Result
    Server-->>Client: Response
</pre>
```

**Result:**

<pre class="mermaid">
sequenceDiagram
    participant Client
    participant Server
    participant DB
    Client->>Server: Request
    Server->>DB: Query
    DB-->>Server: Result
    Server-->>Client: Response
</pre>

---

## 3-3. Gantt chart

**Example:**

```html
<pre class="mermaid">
gantt
    title Project Schedule
    dateFormat  YYYY-MM-DD
    section Design
    Requirements analysis    :a1, 2026-01-01, 7d
    System design            :a2, after a1, 5d
    section Development
    Implementation           :b1, after a2, 14d
    Testing                  :b2, after b1, 7d
</pre>
```

**Result:**

<pre class="mermaid">
gantt
    title Project Schedule
    dateFormat  YYYY-MM-DD
    section Design
    Requirements analysis    :a1, 2026-01-01, 7d
    System design            :a2, after a1, 5d
    section Development
    Implementation           :b1, after a2, 14d
    Testing                  :b2, after b1, 7d
</pre>

---

# [04] Supported Diagram Types

| Diagram | Keyword | Use case |
|---|---|---|
| Flowchart | `graph` / `flowchart` | Process flow |
| Sequence | `sequenceDiagram` | API call flow, communication order |
| Class | `classDiagram` | Class structure, inheritance |
| State | `stateDiagram-v2` | State transitions |
| ER | `erDiagram` | Database relationships |
| Gantt | `gantt` | Scheduling |
| Pie | `pie` | Proportions |
| Mindmap | `mindmap` | Idea structuring |

:bulb: Full syntax is documented at the [Mermaid official docs](https://mermaid.js.org/intro/).
{: .notice--info}

---

# [05] Changing the Theme

Use the `theme` option in `mermaid.initialize` to change the diagram style.

| Theme | Description |
|---|---|
| `default` | Default (light background, blue tones) |
| `dark` | Dark mode |
| `forest` | Green tones |
| `neutral` | Black-and-white |

```javascript
mermaid.initialize({ startOnLoad: true, theme: 'neutral' });
```

---

# [06] Caveats

:warning: You must use **`<pre class="mermaid">`** tags, not Markdown code fences (````mermaid`). Jekyll's kramdown treats fenced contents as code, so Mermaid never sees the actual source to parse.
{: .notice--warning}

| Item | Description |
|---|---|
| Use the tag | Use `<pre class="mermaid">` instead of ````mermaid` |
| Indentation | Watch indentation inside `<pre>` (extra whitespace can cause parse errors) |
| CDN dependency | Requires internet (won't render offline) |
