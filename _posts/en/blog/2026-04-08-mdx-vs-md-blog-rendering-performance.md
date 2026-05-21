---
title: "MDX vs MD-Based Blogs: Rendering Performance Gap and Selection Criteria"
description: "Analyze why an MDX-based documentation portal renders slowly, compare it with MD-based solutions, and review VitePress and other alternatives"
excerpt: "MDX build pipeline 15~30 seconds vs MD rendering hundreds of ms — why the gap is so large, and what to pick for which situation"
date: 2026-04-08
categories: Github_Blog
tags: [MDX, Markdown, VitePress, Fumadocs, Next.js, rendering-performance, SSG, Docker, MkDocs, Hugo]
ref: mdx-vs-md-blog-rendering-performance
---

:bulb: This post analyzes the rendering performance problem I ran into while operating an MDX-based documentation portal (Fumadocs + Next.js) on Docker Compose, compares it against MD-based alternatives, and summarizes the path that led to choosing VitePress.
{: .notice--info}

---

# [01] The Problem

After running a Fumadocs (Next.js + MDX) documentation portal under Docker Compose, I tried editing a single `.md` file and checking the result in the browser.

**Expectation**: file save → browser updates in 1~2 seconds

**Reality**: file save → **30+ seconds** of waiting

<pre class="mermaid">
graph LR
    EDIT[".md file edit"] -->|expected: 1~2s| BROWSER["browser update"]
    EDIT -->|reality: 30s+| WAIT["Waiting..."]
    WAIT --> BROWSER

    style EDIT fill:#e3f2fd,stroke:#1565c0
    style WAIT fill:#ffcccc,stroke:#c62828
    style BROWSER fill:#e8f5e9,stroke:#2e7d32
</pre>

Waiting 30 seconds to see a one-line edit reflected severely hurts developer productivity. I dug into why it is this slow.

---

# [02] Why MDX Rendering Is Slow

## 2-1. The Complexity of the MDX Build Pipeline

MDX is a hybrid of Markdown and React. It is not a simple Markdown → HTML conversion — it must go through a **six-stage pipeline**.

<pre class="mermaid">
graph TD
    A[".mdx file change"] --> B["[1] Fumadocs-mdx scan<br/>.mdx parse, frontmatter extract<br/>.source/ regen (84+ imports)"]
    B --> C["[2] Remark/Rehype<br/>plugin chain"]
    C --> D["[3] TypeScript compile<br/>JSX transform, type check"]
    D --> E["[4] Webpack/Turbopack<br/>bundling, code splitting"]
    E --> F["[5] Next.js SSG<br/>per-page HTML generation"]
    F --> G["[6] Browser update (HMR)<br/>~15~30s"]

    style A fill:#e3f2fd,stroke:#1565c0
    style G fill:#ffcccc,stroke:#c62828
</pre>

In contrast, pure Markdown (`.md`):

<pre class="mermaid">
graph LR
    A[".md file change"] --> B["Markdown → HTML"]
    B --> C["Browser update<br/>~100~300ms"]

    style A fill:#e3f2fd,stroke:#1565c0
    style C fill:#e8f5e9,stroke:#2e7d32
</pre>

**Key difference**: MDX requires React component transformation, TypeScript compilation, and bundling. MD only needs text → HTML conversion.

## 2-2. Next.js Dev Mode JIT Overhead

In Next.js development mode, every page request triggers **on-the-fly compilation**.

<pre class="mermaid">
sequenceDiagram
    participant User as Browser
    participant Next as Next.js Dev Server
    participant MDX as MDX Compiler
    participant TS as TypeScript
    participant WP as Webpack

    User->>Next: Page request
    Next->>MDX: Load .mdx
    MDX->>MDX: Extract frontmatter
    MDX->>TS: JSX → JS transform
    TS->>WP: Bundle request
    WP->>WP: Code splitting
    WP-->>Next: Bundle done
    Next-->>User: HTML response
    Note over User,WP: This entire chain repeats every request
</pre>

Production optimizations (minification, code splitting, tree shaking) are also disabled in dev mode, making it even slower.

## 2-3. Extra Overhead in Docker

Running on Docker Compose makes performance even worse.

<pre class="mermaid">
graph TD
    subgraph "Local dev (~5ms)"
        L1["Host SSD"] -->|direct access| L2["Node.js"]
    end

    subgraph "Docker dev (~50~100ms+)"
        D1["Host SSD"] -->|FUSE/VPKit| D2["Docker daemon"]
        D2 -->|virtualization layer| D3["Container Node.js"]
    end

    style L2 fill:#e8f5e9,stroke:#2e7d32
    style D3 fill:#ffcccc,stroke:#c62828
</pre>

| Bottleneck | Local | Docker |
|------------|-------|--------|
| File I/O | ~5ms (direct SSD) | ~50~100ms+ (volume mount) |
| File change detection | OS event (instant) | Polling (+1s) |
| Network | direct | container port translation (+10~20ms) |
| node_modules access | local | 10x slower with host mount |

**Volume mount I/O** is especially fatal. Reaching through the virtualization layer for thousands of files in node_modules every time tanks the perceived performance.

---

# [03] MD vs MDX Performance Comparison

The performance gap when processing the same document with an MD-based vs MDX-based stack.

<pre class="mermaid">
graph LR
    subgraph MD["MD-based server (~120ms)"]
        direction LR
        M1["File detect<br/>100ms"] --> M2["MD→HTML<br/>10ms"]
        M2 --> M3["Template<br/>5ms"]
        M3 --> M4["File write<br/>5ms"]
    end

    subgraph MDX["MDX-based Docker (~21.7s)"]
        direction LR
        X1["File detect<br/>500ms"] --> X2["mdx scan<br/>200ms"]
        X2 --> X3[".source/<br/>2s"]
        X3 --> X4["TS compile<br/>5s"]
        X4 --> X5["Bundling<br/>8s"]
        X5 --> X6["SSG<br/>5s"]
        X6 --> X7["Docker I/O<br/>500ms"]
    end

    style MD fill:#e8f5e9,stroke:#2e7d32
    style MDX fill:#ffcccc,stroke:#c62828
</pre>

| Stage | MD-based | MDX-based (Docker) |
|-------|----------|--------------------|
| File detect | 100ms | 500ms |
| Transform | 15ms | 15,200ms |
| Other overhead | 5ms | 6,000ms |
| **Total** | **~120ms** | **~21.7s (real: 30s+)** |

**~180x difference**. Waiting 30 seconds for a one-line doc edit is a patience test, not a productivity workflow.

---

# [04] Alternative Solution Comparison

## 4-1. By Category

<pre class="mermaid">
graph TD
    ROOT["Documentation site tools"] --> RT["Runtime rendering<br/>(zero build)"]
    ROOT --> FAST["Fast SSG<br/>(under 1s)"]
    ROOT --> SLOW["MDX-based SSG<br/>(15s+)"]

    RT --> Docsify["Docsify<br/>0s"]
    RT --> Wiki["Wiki.js<br/>real-time"]

    FAST --> Hugo["Hugo (Go)<br/>~50ms"]
    FAST --> mdBook["mdBook (Rust)<br/>~100ms"]
    FAST --> VP["VitePress (Vite)<br/>~200ms"]
    FAST --> MK["MkDocs (Python)<br/>~300ms"]

    SLOW --> Fuma["Fumadocs<br/>15~30s"]
    SLOW --> Docu["Docusaurus<br/>20~40s"]
    SLOW --> Nextra["Nextra<br/>10~20s"]

    style RT fill:#e8f5e9,stroke:#2e7d32
    style FAST fill:#e3f2fd,stroke:#1565c0
    style SLOW fill:#ffcccc,stroke:#c62828
    style VP fill:#ffffcc,stroke:#f9a825,stroke-width:3px
</pre>

## 4-2. Performance Comparison Table

| Solution | Engine | Rebuild | Components | SEO | Notes |
|----------|--------|---------|------------|-----|-------|
| **Hugo** | Go | ~50ms | limited | O | Fastest SSG |
| **mdBook** | Rust | ~100ms | limited | O | Used by Rust official docs |
| **VitePress** | Vue/Vite | ~200ms | Vue | O | Instant HMR |
| **MkDocs Material** | Python | ~300ms | limited | O | #1 for technical docs |
| **Docsify** | JS (browser) | 0s | X | X | No build needed |
| **Nextra** | Next.js | 10~20s | React | O | Fastest of the MDX stacks |
| **Fumadocs** | React | 15~30s | React | O | Currently in use |
| **Docusaurus** | React | 20~40s | React | O | Meta-led |

---

# [05] Why VitePress

## 5-1. Selection Criteria

<pre class="mermaid">
graph TD
    Q1{"Need instant<br/>reload after edit?"}
    Q1 -->|Yes| Q2{"Require React<br/>components?"}
    Q1 -->|No| KEEP["Keep current stack<br/>(must optimize)"]

    Q2 -->|Yes| NEXTRA["Consider Nextra<br/>(fastest MDX)"]
    Q2 -->|No| Q3{"Need modern DX<br/>(TS, HMR)?"}

    Q3 -->|Yes| VITEPRESS["VitePress"]
    Q3 -->|No| MKDOCS["MkDocs / Hugo"]

    style Q1 fill:#fff3e0,stroke:#e65100
    style VITEPRESS fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    style KEEP fill:#ffcccc,stroke:#c62828
</pre>

| Question | Answer | Result |
|----------|--------|--------|
| Need instant (under 1s) reload after edit? | **Yes** | MDX family eliminated |
| Are custom React components essential? | **No** | Vue components are an acceptable substitute |
| Need modern DX (TypeScript, HMR)? | **Yes** | Edge over Hugo, MkDocs |

## 5-2. Fumadocs vs VitePress

| Item | Fumadocs (current) | VitePress (target) |
|------|--------------------|--------------------|
| Rebuild time | 15~30s (Docker: 30s+) | ~200ms |
| HMR | Slow (full build) | Instant (Vite native) |
| Components | React (MDX required) | Vue 3 (optional) |
| Production build | several minutes | under 1s |
| Configuration complexity | High (Next.js + Fumadocs) | Low |
| Docker compatibility | Volume mount bottleneck | Lightweight, less impact |

## 5-3. Basic VitePress Structure

```bash
npm create vitepress
npm run docs:dev
```

```
docs/
├── .vitepress/
│   └── config.ts          # Site config
├── index.md               # Landing page
├── guide/
│   ├── getting-started.md
│   └── advanced.md
└── api/
    └── reference.md
```

```typescript
// docs/.vitepress/config.ts
export default {
  title: 'Tech Docs Portal',
  lang: 'ko-KR',
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/' }
    ]
  }
}
```

---

# [06] Key Lessons

## 6-1. When MDX Is Necessary

- When **interactive React components** are required inside documents
- When **live code previews** are needed (e.g., design system documentation)
- When using documentation as a **Storybook replacement** in a React-based project

## 6-2. When MD-Based Is Better (Most Cases)

- **Text-centric content** like technical docs, API references, guides
- Workflows where **immediate verification** after edits matters
- Development/deployment in Docker environments
- When non-frontend team members write documentation

## 6-3. Decision Tree

<pre class="mermaid">
graph TD
    Q{"Do docs really need<br/>React interactions?"}
    Q -->|Yes| MDX["MDX-based<br/>(Fumadocs, Docusaurus)<br/>Accept 30s+ build"]
    Q -->|No| MD["MD-based<br/>(VitePress, MkDocs, Hugo)<br/>200~300ms instant reload"]

    style Q fill:#fff3e0,stroke:#e65100
    style MDX fill:#ffcccc,stroke:#c62828
    style MD fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
</pre>

:bulb: Most technical documentation only needs **text + code blocks + images**. Choosing MDX on the chance that "we might need React components later" means paying a daily 30-second wait tax.
{: .notice--info}
