---
title: "Netlify vs Vercel and the Static Hosting Landscape — What Are the Real Limits for Personal Users?"
description: "Comparing the free-plan limits of Netlify, Vercel, Cloudflare Pages, and GitHub Pages. The truth behind the 'personal token limit' rumor (build minutes, credits, commercial use) plus a quick deploy guide"
excerpt: "Netlify is limited and Vercel isn't? — Let's fix the terminology first, then map the real boundaries of the free tiers (build minutes, bandwidth, commercial use) and how to deploy on each"
date: 2026-06-08
categories: Hosting
tags: [Netlify, Vercel, CloudflarePages, GitHubPages, hosting, static-site, JAMstack, free-tier, deploy, build-minutes, cloud]
ref: netlify-vercel-static-hosting-comparison
---

:bulb: You often hear "Netlify has limits for personal users and Vercel doesn't." Up front: **it's half right and half wrong.** Let's fix the terminology and lay out the real boundaries of the free tiers (build minutes, bandwidth, **commercial use**) and how to use each service.
{: .notice--info}

---

# [01] At a glance (2026, free plans)

| Item | **Netlify** (Free) | **Vercel** (Hobby) | **Cloudflare Pages** (Free) | **GitHub Pages** |
|---|---|---|---|---|
| Bandwidth | 100 GB/mo | 100 GB/mo | **Unlimited** | 100 GB/mo (soft) |
| Build | **300 min/mo** | **6,000 min/mo** | 500 builds/mo | 10 builds/hr (soft) |
| Serverless functions | ✅ (125K calls) | ✅ (10s timeout) | ✅ (Workers) | ❌ (static only) |
| **Commercial use** | ✅ Allowed | ❌ **Prohibited (non-commercial only)** | ✅ Allowed | ✅ Allowed |
| Billing model | Credit-based (since 2025-09) | Credit-based (since 2025-09) | Flat (paid above limits) | Free (soft limits) |
| Key strength | Integrated features, commercial OK | Generous builds, Next.js-optimized | Unlimited bandwidth, fast | GitHub integration, fully free |

:bulb: One-line summary — **Vercel's build minutes (6,000) are 20× Netlify's (300)**, but **Vercel prohibits revenue-generating sites (non-commercial only)** — a bigger trap. If bandwidth is your concern, Cloudflare Pages is the only one with no cap.
{: .notice--info}

---

# [02] "Personal token limit" — the truth behind the rumor

Let's tackle the heart of the question head-on.

## 2-1. First, there is no "token" limit

Neither Netlify nor Vercel has an official term called a **"token limit."** It probably refers to one of these:

| What you heard | What it actually is |
|---|---|
| "token limit" | **build minutes** or **credits** |
| "Netlify is tight" | Free build time is just **300 min/month** |
| "Vercel has no limit" | Free build time is a generous **6,000 min/month** (≠ unlimited) |

:warning: Since September 2025, **both Netlify and Vercel moved to "credit-based" billing** — builds, bandwidth, function calls, etc. are converted into credits and deducted. "token" is most likely a mishearing of these credits.
{: .notice--warning}

## 2-2. Half true — Vercel's build minutes are far more generous

| | Netlify Free | Vercel Hobby |
|---|---|---|
| Monthly build minutes | **300** | **6,000** (~20×) |

→ For a personal project you deploy often, Netlify's 300 minutes can run out quickly. On this point, the impression that "Vercel is freer" is **correct**.

## 2-3. Half wrong — Vercel isn't unlimited, and has a bigger restriction

```
"Vercel has no limits" ❌

  ① A 6,000-minute build cap exists (generous, but not unlimited)
  ② Bandwidth is 100GB/mo — identical to Netlify
  ③ ★The decisive one★ Vercel Hobby = non-commercial only
     → Ads, monetization, paid-service deploys are prohibited. Violations force Pro ($20/mo).
```

:warning: **The most important difference isn't build minutes — it's whether commercial use is allowed.** Vercel Hobby permits **personal, non-commercial use only** (any revenue-generating deployment is prohibited). In contrast, **Netlify's free plan allows commercial use** — you can even run a money-making site for free. For a portfolio or blog, Vercel is convenient, but for a **revenue site you need Netlify (or a paid plan)**.
{: .notice--warning}

**In short:** "Netlify is limited and Vercel isn't" is more accurately stated as → **"Vercel has far more generous build minutes, but Vercel prohibits commercial use."**

---

# [03] Quick usage guide

All three support **① Git-integrated auto-deploy** (recommended) and **② CLI deploy**. The examples assume static sites (React/Vue build output, Jekyll, Hugo, etc.).

## 3-1. Netlify

**Option A — Git integration (recommended):**

1. Log in at [app.netlify.com](https://app.netlify.com) → **Add new site → Import an existing project**
2. Connect a GitHub/GitLab repository
3. Enter build settings:
   - Build command: `npm run build` (for Jekyll, `jekyll build`)
   - Publish directory: `dist` (or `_site`, `build`)
4. **Deploy** → re-deploys automatically on every `git push`

**Option B — CLI:**

```bash
npm install -g netlify-cli
netlify login
netlify deploy            # draft (preview) deploy
netlify deploy --prod     # production deploy
```

## 3-2. Vercel

**Option A — Git integration (recommended):**

1. Log in at [vercel.com](https://vercel.com) → **Add New → Project**
2. Import the repo → **framework auto-detected** (Next.js, Vite, Astro, etc.)
3. Keep most settings as-is and **Deploy** → auto-deploys on every `git push` + a preview URL per PR

**Option B — CLI:**

```bash
npm install -g vercel
vercel login
vercel            # preview deploy
vercel --prod     # production deploy
```

## 3-3. Cloudflare Pages

1. Cloudflare dashboard → **Workers & Pages → Create → Pages**
2. Connect a Git repo → set build command / output directory → deploy
3. Strengths: **unlimited bandwidth**, global CDN by default, extend with Workers for dynamic features

## 3-4. GitHub Pages

The simplest and fully free option. **This blog itself runs on GitHub Pages.**

1. Repo **Settings → Pages**
2. Set the source to the `main` branch (or GitHub Actions)
3. Published at `https://<username>.github.io/<repo>`
4. Static files only (no serverless functions). GitHub builds Jekyll for you automatically.

:bulb: The core flow is the same for all three — **connect the repo → set the build command/output folder → auto-deploy on push.** Once connected, all you do afterward is `git push`.
{: .notice--info}

---

# [04] So which should you pick?

| Situation | Recommendation |
|---|---|
| Next.js/frontend + frequent deploys, **non-commercial** personal project | **Vercel** (6,000 build min, Next.js-optimized) |
| Revenue site (ads/paid/SaaS) but want to start free | **Netlify** (free commercial use allowed) |
| High traffic (bandwidth) and worried about cost | **Cloudflare Pages** (unlimited bandwidth) |
| Blog/docs/portfolio, just want fully free | **GitHub Pages** |

:warning: "Vercel has generous build minutes, so just use Vercel" is a trap. **For a money-making site, Vercel Hobby is a terms violation.** If you have a revenue model, it's safer to start on Netlify free or a paid plan from the beginning.
{: .notice--warning}

---

# [05] Key takeaways

| # | Takeaway |
|---|------|
| 1 | There's no official "token limit" — it's really about **build minutes / credits** |
| 2 | Since September 2025, both Netlify and Vercel switched to **credit-based billing** |
| 3 | Build minutes: **Netlify 300 vs Vercel 6,000** → on this point Vercel is 20× more generous (true) |
| 4 | But **Vercel isn't unlimited either** (same 100GB bandwidth) + **Vercel Hobby is non-commercial only** (the wrong part) |
| 5 | **Revenue sites are fine on Netlify free, prohibited on Vercel Hobby** — the most important practical difference |
| 6 | Unlimited bandwidth → **Cloudflare Pages**; simplest and fully free → **GitHub Pages** |

:bulb: One-line conclusion — **personal non-commercial → Vercel (generous builds), revenue site → Netlify (commercial OK), traffic-heavy → Cloudflare Pages (unlimited bandwidth), blog → GitHub Pages.**
{: .notice--info}

---

> Sources: [Netlify Pricing](https://www.netlify.com/pricing/) · [Vercel Pricing](https://vercel.com/pricing) · [Vercel Hobby Plan](https://vercel.com/docs/plans/hobby) · [Cloudflare Pages Limits](https://developers.cloudflare.com/pages/platform/limits/) · [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
