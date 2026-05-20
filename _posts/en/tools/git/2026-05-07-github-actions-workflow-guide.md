---
title: "GitHub Actions Workflow Guide — Line-by-Line of deploy.yml and stale.yml"
description: "After clarifying the 5 GitHub Actions terms (workflow/event/job/step/action), dissect two real workflows line by line — deploy.yml (push-triggered site build/deploy) and stale.yml (cron-scheduled inactivity cleanup)"
excerpt: "From a simple bot workflow (stale.yml) to a multi-job build/deploy workflow (deploy.yml) — learn the GitHub Actions execution model by line-by-line analysis of two real YAML files"
date: 2026-05-07
categories: Git
tags: [GitHub-Actions, deploy.yml, stale.yml, GitHub-Pages, schedule, cron, CI-CD, workflow, YAML, VitePress, Node.js, ubuntu-latest, npm-ci, actions-checkout, actions-deploy-pages, actions-stale, OIDC, GITHUB_TOKEN, automation, issue-management, exempt-labels]
ref: github-actions-workflow-guide
---

:bulb: When you first meet GitHub Actions, the YAML can be opaque. This post is a learning note that dissects **two real workflows** in the same repository line by line. (1) **`deploy.yml`** — multi-job workflow that builds and deploys a VitePress site, triggered by `push`. (2) **`stale.yml`** — single-action bot that runs daily via `schedule` cron to clean up inactive issues/PRs. Comparing the two makes the difference between trigger types and job structures crystal clear.
{: .notice--info}

---

# [01] GitHub Actions in One Sentence

> **"A service where, when an event (push, PR, schedule, etc.) happens in your repository, GitHub automatically runs commands written in your YAML file on a virtual machine they lend you."**

- What you care about: write one YAML file and push to `.github/workflows/`
- What GitHub handles: watch the repo → match events → allocate a runner → run commands → display results (Actions tab)

---

# [02] Five Core Terms

| Term | One-line definition | Example in this post |
|------|---------------------|----------------------|
| **Workflow** | One automation scenario (= one YAML file) | `Deploy VitePress site to Pages` / `Close stale issues and PRs` |
| **Event** | A signal that triggers a workflow | `push`, `workflow_dispatch`, `schedule` |
| **Job** | A bundle of tasks running on the same runner | `build`, `deploy`, `stale` |
| **Step** | One command executed sequentially within a job | `npm ci`, `npm run docs:build` |
| **Action** | A pre-built, reusable "step" package | `actions/checkout@v4`, `actions/stale@v3` |

> **Unix analogy**: workflow = shell script, job = function, step = single command, action = external library

:bulb: With these 5 words in your head, you can read 70% of any workflow YAML.
{: .notice--info}

---

# [03] File Location

```
repo root/
└── .github/
    └── workflows/
        ├── deploy.yml      ← workflow ①
        └── stale.yml       ← workflow ②
```

GitHub **automatically watches** this folder. Any YAML added is immediately recognized, and triggers fire from the next matching event.

:warning: Note the folder name is `.github/workflows/` (plural). `.github/workflow/` is ignored.
{: .notice--warning}

---

# [04] Workflow ① — `deploy.yml` (push-triggered build/deploy)

Triggered on push to main: builds the VitePress site and publishes to GitHub Pages.

## 4-1. Header Comment

```yaml
# ============================================================
# deploy.yml: VitePress GitHub Pages auto-deploy
# On push to main: build docs/.vitepress/dist and deploy to Pages
# ============================================================
```

- Lines starting with `#` are YAML comments. No effect on execution.
- Meta info that lets a human grasp the file's purpose in 3 seconds.

## 4-2. Workflow Name

```yaml
name: Deploy VitePress site to Pages
```

- Shown in the **workflow list** in the Actions tab.
- If omitted, the filename is displayed. A one-line descriptive name is recommended for UI readability.

## 4-3. Trigger — `on:` (push + manual)

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:
```

| Line | Meaning |
|------|---------|
| `on:` | Root key declaring "what events should trigger this workflow" |
| `push:` | git push event |
| `branches: [main]` | **Only when push lands on `main`** (other branches are ignored) |
| `workflow_dispatch:` | Adds a **manual run button** to the Actions UI (for debugging/redeploy) |

:warning: `git push origin feature/foo` does NOT trigger — must be merged to main first.
{: .notice--warning}

## 4-4. Permissions — `permissions:`

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

GitHub Actions uses an auto-issued `GITHUB_TOKEN` to access the GitHub API. This block declares **minimal permissions** for that token.

| Permission | Why needed |
|------------|------------|
| `contents: read` | Read access required to checkout the repo |
| `pages: write` | Write access required to publish to GitHub Pages |
| `id-token: write` | Issues an OIDC token (required by the official Pages action) |

:warning: Without `id-token: write`, `actions/deploy-pages@v4` fails authentication. Required for Pages deployment.
{: .notice--warning}

## 4-5. Concurrency Control

```yaml
concurrency:
  group: pages
  cancel-in-progress: false
```

| Line | Meaning |
|------|---------|
| `group: pages` | Workflows sharing this group name run **one at a time** |
| `cancel-in-progress: false` | If a deploy is in progress, **don't cancel — wait until it finishes** |

:bulb: Even with two rapid pushes, the second deploy starts after the first finishes → prevents tangled Pages artifacts.
{: .notice--info}

## 4-6. Jobs — `build` job

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      ...
```

| Line | Meaning |
|------|---------|
| `jobs:` | Starts all job definitions for this workflow |
| `build:` | Job ID — referenced by other jobs via `needs: build` |
| `runs-on: ubuntu-latest` | OS for the VM this job runs on — Ubuntu latest LTS |

### Step ① Checkout

```yaml
- name: Checkout
  uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

| Line | Meaning |
|------|---------|
| `- name: Checkout` | Step display name (shown in Actions UI) |
| `uses: actions/checkout@v4` | Official checkout action v4 — clones the repo to the runner |
| `fetch-depth: 0` | Fetch full history (required by builds using git metadata like sitemap/last-modified) |

:bulb: Default is `fetch-depth: 1` (last commit only). For VitePress sitemap, Jekyll's git-authors-plugin, etc., `0` (all history) is safe.
{: .notice--info}

### Step ② Setup Node

```yaml
- name: Setup Node
  uses: actions/setup-node@v4
  with:
    node-version: 20
    cache: npm
```

| Line | Meaning |
|------|---------|
| `actions/setup-node@v4` | Official action installing Node.js on the runner |
| `node-version: 20` | LTS version (match `package.json` recommended version) |
| `cache: npm` | Caches `~/.npm` in GitHub cache → speeds up `npm ci` on next runs |

### Step ③ Install Dependencies

```yaml
- name: Install dependencies
  run: npm ci
```

| Item | Meaning |
|------|---------|
| `run:` | Run a command directly in the runner shell (contrasts with `uses:`) |
| `npm ci` | **Clean install** based on `package-lock.json` — ensures build reproducibility. Stricter and faster than `npm install` |

### Step ④ VitePress Build

```yaml
- name: Build with VitePress
  run: npm run docs:build
```

- Invokes `package.json`'s `"docs:build": "vitepress build docs"`
- Output: `docs/.vitepress/dist/` — static HTML/CSS/JS

### Step ⑤ Configure Pages

```yaml
- name: Setup Pages
  uses: actions/configure-pages@v4
```

- Reads the repo's Pages settings and injects env vars (e.g., `base path`)
- Fails with `HttpError: Not Found` here if Pages isn't enabled on the repo
- Fix: `Settings → Pages → Source = "GitHub Actions"`

### Step ⑥ Upload Artifact

```yaml
- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: docs/.vitepress/dist
```

| Line | Meaning |
|------|---------|
| `actions/upload-pages-artifact@v3` | Packages and uploads build output as a **Pages-specific artifact** |
| `path: docs/.vitepress/dist` | Upload target (= VitePress build output) |

:warning: This is different from generic `actions/upload-artifact`. Pages deployment only accepts this dedicated artifact.
{: .notice--warning}

## 4-7. Jobs — `deploy` job

```yaml
deploy:
  needs: build
  runs-on: ubuntu-latest
  environment:
    name: github-pages
    url: ${{ steps.deployment.outputs.page_url }}
  steps:
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v4
```

| Line | Meaning |
|------|---------|
| `needs: build` | Runs only after `build` job **succeeds** (auto-skipped on failure) |
| `environment:` | Registers deploy target — manage **approval policies/secrets** in Settings → Environments |
| `name: github-pages` | **Reserved environment name** auto-recognized by Pages (don't change) |
| `url: ${{ steps.deployment.outputs.page_url }}` | Site URL shown in Actions UI after deploy — references the step output below |
| `id: deployment` | Step identifier — referenced as `steps.deployment.outputs.page_url` |
| `actions/deploy-pages@v4` | Pulls the artifact uploaded by the previous job and **actually publishes** to Pages |

## 4-8. deploy.yml Execution Flow

<pre class="mermaid">
flowchart TD
    A["git push origin main"] --> B{"on.push.branches<br/>= main?"}
    B -->|No| Z["Ignored"]
    B -->|Yes| C["Allocate runner<br/>ubuntu-latest"]

    C --> D1["build: checkout"]
    D1 --> D2["build: setup-node 20"]
    D2 --> D3["build: npm ci"]
    D3 --> D4["build: vitepress build"]
    D4 --> D5["build: configure-pages"]
    D5 --> D6["build: upload-pages-artifact<br/>(upload dist)"]

    D6 --> E{"build succeeded?"}
    E -->|No| F["Skip deploy"]
    E -->|Yes| G["deploy: deploy-pages<br/>publishes artifact to Pages"]
    G --> H["https://username.github.io updated"]

    style B fill:#fff3e0,stroke:#e65100
    style E fill:#fff3e0,stroke:#e65100
    style Z fill:#f5f5f5,stroke:#616161
    style F fill:#ffcccc,stroke:#c62828
    style H fill:#e8f5e9,stroke:#2e7d32
</pre>

---

# [05] Workflow ② — `stale.yml` (schedule-triggered bot)

A second workflow in the same repo. Runs daily to clean up inactive issues and PRs.

## 5-1. What stale.yml Does in One Sentence

> **"A bot workflow that runs daily at 01:30 UTC, labels issues/PRs with no recent activity as `Status: Stale`, and auto-closes them 7 days later if still inactive."**

Removes accumulated "old, unanswered issues/PRs" without manual effort. Used by popular open-source repos like the minimal-mistakes Jekyll theme to prevent issue trackers from exploding.

## 5-2. How It Differs from deploy.yml

| Aspect | `deploy.yml` | `stale.yml` |
|--------|--------------|-------------|
| Purpose | **Site deployment** | **Repo management** |
| Trigger | `on: push` + `workflow_dispatch` | `on: schedule` (cron) |
| Run time | When someone pushes | **Fixed time, GitHub auto-runs** |
| Main action | `actions/checkout` + `actions/deploy-pages` | Single `actions/stale` |
| Job count | 2 (`build`, `deploy`) | 1 (`stale`) |
| Artifact | `_site` / `dist` (static files) | None — only GitHub API calls |

Key learning points: **how `schedule` triggers work** and **structure of single-action workflows like `actions/stale`**.

## 5-3. Full Code

```yaml
name: "Close stale issues and PRs"
on:
  schedule:
    - cron: "30 1 * * *"

jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v3
        with:
          stale-issue-message: |
            This issue has been automatically marked as stale because it has not had recent activity.

            If this is a **bug** and you can still reproduce this error on the `master` branch, please reply with any additional information you have about it in order to keep the issue open.

            This issue will automatically be closed in 7 days if no further activity occurs. Thank you for all your contributions.
          stale-pr-message: |
            This pull request has been automatically marked as stale because it has not had recent activity.

            This pull request will automatically be closed in 7 days if no further activity occurs. Thank you for all your contributions.
          stale-issue-label: "Status: Stale"
          exempt-issue-labels: "Status: Accepted,Status: Under Consideration,Status: Review Needed,Status: In Progress"
          stale-pr-label: "Status: Stale"
          exempt-pr-labels: "Status: Accepted,Status: Under Consideration,Status: Review Needed,Status: In Progress"
```

28 lines total. Five sections make the structure clear.

## 5-4. Trigger — `on: schedule` + cron

```yaml
on:
  schedule:
    - cron: "30 1 * * *"
```

| Line | Meaning |
|------|---------|
| `on:` | Trigger declaration (same key as deploy.yml) |
| `schedule:` | **Time-based trigger** — clock fires instead of push/PR |
| `- cron: "30 1 * * *"` | cron expression. Runs daily at **01:30 UTC** |

### Reading 5-Field cron

```
cron: "30 1 * * *"
       │  │ │ │ │
       │  │ │ │ └─ day of week (0=Sun~6=Sat, * = any)
       │  │ │ └─── month (1~12, * = any)
       │  │ └───── day of month (1~31, * = any)
       │  └─────── hour (0~23 UTC)
       └────────── minute (0~59)
```

| Field | Value | Meaning |
|-------|-------|---------|
| Minute | `30` | 30 |
| Hour | `1` | 1 (UTC) |
| Day | `*` | Every day |
| Month | `*` | Every month |
| Day of week | `*` | All days |

**Result**: Runs at 01:30 UTC daily = **10:30 KST** (UTC+9).

:warning: GitHub Actions' `schedule:` is **always UTC**. To run "daily at 09:00 KST", write `0 0 * * *` (00:00 UTC = 09:00 KST).
{: .notice--warning}

:bulb: cron times may be delayed by ±10 minutes — GitHub queues jobs based on runner availability. Not suitable for minute-precise tasks.
{: .notice--info}

### Common cron Patterns

| cron | Meaning |
|------|---------|
| `0 * * * *` | Every hour on the hour |
| `*/15 * * * *` | Every 15 minutes |
| `0 0 * * *` | Daily midnight UTC (= 09:00 KST) |
| `0 0 * * 0` | Sunday midnight UTC |
| `0 0 1 * *` | First day of each month, midnight UTC |

## 5-5. Jobs — `stale` job

```yaml
jobs:
  stale:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v3
```

| Line | Meaning |
|------|---------|
| `jobs:` | Start of all job definitions |
| `stale:` | Job ID — single word is enough (no other job references it) |
| `runs-on: ubuntu-latest` | Ubuntu latest LTS runner. This workflow only calls GitHub API, so OS doesn't really matter |
| `- uses: actions/stale@v3` | **Invoke `actions/stale` v3**. This one line is almost the entire workflow |

:bulb: Compared to deploy.yml's build job, the step has no `name:` field (Actions UI shows the action name directly). Common omission when a job has only one step.
{: .notice--info}

### What `actions/stale@v3` Does

Internally:

1. **Fetch issue/PR list** — REST API to list all open issues/PRs
2. **Check activity** — based on `updated_at`, candidates are those with no change for 60+ days (default)
3. **Check exempt labels** — skip if any `exempt-issue-labels` are attached
4. **Mark stale** — add `stale-issue-label` and post `stale-issue-message` comment
5. **Close** — if stale-labeled and no activity for another 7 days (default), auto-close

Steps 3, 4, 5 are controlled by `with:` block options below.

## 5-6. Stale Messages — Multi-line String in `with:` Block

```yaml
with:
  stale-issue-message: |
    This issue has been automatically marked as stale because it has not had recent activity.
    ...
```

### YAML Multi-line — `|` Meaning

`|` (block scalar / literal style) **preserves line breaks**. Indentation is stripped based on the first line, and blank lines/markdown emphasis are kept.

```yaml
key: |
  Line 1
  Line 2

  Line 4 (after blank)
```

→ Result:
```
Line 1
Line 2

Line 4 (after blank)
```

### Difference from `>`

| Notation | Behavior | Use case |
|----------|----------|----------|
| `key: \|` | Preserve line breaks | **Here** — markdown messages, multi-line code |
| `key: >` | Line breaks → spaces (folded) | Long single sentences |
| `key: "..."` | Single-line string | Short values |

`actions/stale` messages require blank lines and markdown (`**bug**`, `[link](URL)`), so `|` is required.

:bulb: `stale-issue-message` is **what the bot auto-posts as a comment**. It's the interface telling users "why this became stale and what to do". When adopting this workflow, customize tone, language, and contact channels.
{: .notice--info}

## 5-7. Label Policy

```yaml
stale-issue-label: "Status: Stale"
exempt-issue-labels: "Status: Accepted,Status: Under Consideration,Status: Review Needed,Status: In Progress"
stale-pr-label: "Status: Stale"
exempt-pr-labels: "Status: Accepted,Status: Under Consideration,Status: Review Needed,Status: In Progress"
```

| Option | Role |
|--------|------|
| `stale-issue-label` | Label name **applied** to stale-judged issues |
| `exempt-issue-labels` | If any of these labels exist, **exempt from stale processing** (comma-separated) |
| `stale-pr-label` | Stale label for PRs |
| `exempt-pr-labels` | Exempt labels for PRs |

### Why Exempt Labels Matter

Issues/PRs with these 4 labels are **never auto-closed due to inactivity**:

| Label | Meaning |
|-------|---------|
| `Status: Accepted` | Maintainer already accepted to work on it → safe to leave |
| `Status: Under Consideration` | Under review → hard to decide quickly |
| `Status: Review Needed` | Code review pending → maintainer-side responsibility |
| `Status: In Progress` | In progress → keep alive despite time |

:warning: Without these safeguards, **meaningful long-tracked issues get cut down too**. Defining exempt labels is essential when adopting stale.
{: .notice--warning}

## 5-8. stale.yml Execution Flow

<pre class="mermaid">
flowchart TD
    A["GitHub scheduler<br/>daily 01:30 UTC"] --> B["Allocate runner<br/>ubuntu-latest"]
    B --> C["Run actions/stale@v3"]
    C --> D["GitHub API:<br/>fetch open issues/PRs"]
    D --> E{"updated_at<br/>≥ 60 days ago?"}
    E -->|No| F["Next item"]
    E -->|Yes| G{"Exempt label<br/>attached?"}
    G -->|Yes| F
    G -->|No| H{"Already has<br/>stale label?"}
    H -->|No| I["Add stale label<br/>+ post guidance comment"]
    H -->|Yes, 7 days passed| J["Auto-close issue/PR"]
    H -->|Yes, <7 days| F

    style A fill:#e3f2fd,stroke:#1565c0
    style I fill:#fff3e0,stroke:#e65100
    style J fill:#ffcccc,stroke:#c62828
    style F fill:#f5f5f5,stroke:#616161
</pre>

---

# [06] Comparing the Two Workflows

How the same 5 terms (workflow / event / job / step / action) express two different workflows:

| Aspect | `deploy.yml` | `stale.yml` |
|--------|--------------|-------------|
| **Event** | `push` + `workflow_dispatch` | `schedule` (cron) |
| **Trigger source** | Human (push) | GitHub scheduler (clock) |
| **Permissions** | Explicit (`contents`, `pages`, `id-token`) | Default `GITHUB_TOKEN` (not specified) |
| **Concurrency** | `group: pages`, `cancel-in-progress: false` | Not specified (no deploy concurrency issue) |
| **Job count** | 2 (`build` → `deploy`, with `needs:`) | 1 (`stale`) |
| **Step count** | ~7 (checkout/setup-node/npm ci/build/configure-pages/upload/deploy) | 1 (`uses: actions/stale@v3`) |
| **Main actions** | `actions/checkout`, `actions/setup-node`, `actions/configure-pages`, `actions/upload-pages-artifact`, `actions/deploy-pages` | Just `actions/stale` |
| **Behavior** | **Runs build commands** on runner (`run: npm ci`) | **Only GitHub API calls** (no external commands) |
| **Output** | Static site (`docs/.vitepress/dist`) | None (only issue/PR state changes) |
| **Failure impact** | Site not updated | Just misses one day's cleanup |

## Same Mechanism

```
Common structure:
.github/workflows/<file>.yml
│
├─ name:                    # ← both have it
├─ on:                      # ← both have it (different values)
│
└─ jobs:                    # ← both have it
   └─ <job-id>:
       runs-on: ubuntu-latest
       steps:
         - ...              # ← both have it (different content)
```

**Every workflow can be expressed with these 5 terms.** Site deployment, issue cleanup, test automation, releases, secret rotation — all on this same structure.

---

# [07] Common Errors and Pitfalls

## 7-1. Three Common `deploy.yml` Errors

### `HttpError: Not Found` (configure-pages step)

- **Cause**: Pages not enabled, or Source set to `Deploy from a branch`
- **Fix**: `Settings → Pages → Source = GitHub Actions`

### `Resource not accessible by integration`

- **Cause**: Missing `pages: write` or `id-token: write` in `permissions:`
- **Fix**: Specify all 3 permissions from 4-4

### CSS/Images Broken (404)

- **Cause**: Project Pages (`username.github.io/repo-name/`) without `base` config
- **Fix**: Add `base: '/repo-name/'` to `docs/.vitepress/config.ts`
  - For Jekyll: add `baseurl: "/repo-name"` to `_config.yml`

## 7-2. Three Common `stale.yml` Pitfalls

### cron Is UTC, Not KST

```yaml
# WRONG — "want to run at 9 AM KST daily"
- cron: "0 9 * * *"   # actually UTC 09:00 = KST 18:00

# CORRECT
- cron: "0 0 * * *"   # UTC 00:00 = KST 09:00
```

GitHub Actions has no timezone option. Convert to UTC.

### schedule Doesn't Run on Forks

`schedule:` is **auto-disabled on forks**. Otherwise, fork cron would cause unintended load across GitHub. For private forks, use `workflow_dispatch:` or external schedulers.

### Default 60/7 Days Are Used If Not Specified

```yaml
# Defaults not shown in stale.yml
days-before-stale: 60         # days of no activity before stale
days-before-close: 7          # days after stale before close
operations-per-run: 30        # max items per run
```

For low-activity repos, 60 days may be too short. Safer to specify explicitly.

```yaml
with:
  days-before-stale: 180       # 6 months of inactivity → stale
  days-before-close: 14        # +2 weeks → close
```

---

# [08] Debugging Tips

| Situation | Approach |
|-----------|----------|
| Workflow doesn't trigger | Check file location (`.github/workflows/`), extension (`.yml`), and `on:` block |
| Only one step fails | Click the step in Actions UI → expand console logs |
| Schedule doesn't fire | Check if repo is a fork / repos inactive for 60+ days have some schedules auto-disabled |
| Reproduce locally | Use [`act`](https://github.com/nektos/act) to run workflows in local Docker |
| Need secrets (API keys, etc.) | Register at `Settings → Secrets and variables → Actions` and reference as `${{ secrets.MY_KEY }}` |
| Manual test run | If `workflow_dispatch:` is set, **Run workflow** button appears in Actions UI |

---

# [09] One-Page Summary

```
.github/workflows/
│
├── deploy.yml                                   ← push-triggered build/deploy
│   │
│   ├─ on: push(main) | workflow_dispatch        # ① when?
│   ├─ permissions: contents:r pages:w id-token:w
│   ├─ concurrency: group=pages
│   │
│   └─ jobs:
│      ├─ build:                                 # ② what?
│      │   1. checkout (full history)
│      │   2. setup-node 20 + npm cache
│      │   3. npm ci
│      │   4. npm run docs:build  → docs/.vitepress/dist
│      │   5. configure-pages
│      │   6. upload-pages-artifact (dist)
│      │
│      └─ deploy: needs=build
│          1. deploy-pages → https://*.github.io updated
│
└── stale.yml                                    ← schedule-triggered bot
    │
    ├─ on: schedule (cron: 30 1 * * * = daily 01:30 UTC)
    │
    └─ jobs:
       └─ stale: ubuntu-latest
           └─ uses: actions/stale@v3
               with:
                 stale-*-message:    "..."        # guidance message
                 stale-*-label:      "Status: Stale"
                 exempt-*-labels:    "Accepted, ..."
```

Whether triggered by one push or one clock tick — GitHub Actions runs both workflows on the same model: **event → allocate runner → sequential step execution**.

:star: Jekyll, Hugo, Next.js, Astro and other SSGs can reuse the `deploy.yml` pattern by swapping build commands and artifact paths. Beyond issue/PR cleanup, secret rotation, release notes generation, and DB backups all fit the `stale.yml` schedule pattern. **5 terms + 2 patterns (event-driven/schedule-driven) cover almost every automation scenario.**
{: .notice--info}
