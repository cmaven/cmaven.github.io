---
title: "Netlify vs Vercel, 그리고 정적 호스팅 서비스 총정리 — 개인 사용자의 진짜 제한은?"
description: "Netlify·Vercel·Cloudflare Pages·GitHub Pages 무료 플랜 제한 비교. '개인 사용자 token 제한' 소문의 진실(빌드 시간·크레딧·상업적 사용)과 간단 배포 가이드"
excerpt: "Netlify는 제한이 있고 Vercel은 없다? — 용어부터 바로잡고, 빌드 시간·대역폭·상업적 사용까지 무료 플랜의 진짜 경계선과 각 서비스 배포 방법을 정리한다"
date: 2026-06-08
categories: Hosting
tags: [Netlify, Vercel, CloudflarePages, GitHubPages, hosting, 정적사이트, JAMstack, 무료플랜, 배포, deploy, 빌드시간, 클라우드]
ref: netlify-vercel-static-hosting-comparison
---

:bulb: "Netlify는 개인 사용자에게 제한이 있고 Vercel은 없다"는 말을 자주 듣는다. 결론부터: **반은 맞고 반은 틀리다.** 용어를 바로잡고, 무료 플랜의 진짜 경계선(빌드 시간·대역폭·**상업적 사용**)과 각 서비스 사용법을 정리한다.
{: .notice--info}

---

# [01] 한눈에 비교 (2026 기준, 무료 플랜)

| 항목 | **Netlify** (Free) | **Vercel** (Hobby) | **Cloudflare Pages** (Free) | **GitHub Pages** |
|---|---|---|---|---|
| 대역폭(Bandwidth) | 100 GB/월 | 100 GB/월 | **무제한** | 100 GB/월 (soft) |
| 빌드(Build) | **300분/월** | **6,000분/월** | 500 빌드/월 | 10 빌드/시간 (soft) |
| 서버리스 함수 | ✅ (125K 호출) | ✅ (10초 타임아웃) | ✅ (Workers) | ❌ (정적만) |
| **상업적 사용** | ✅ 허용 | ❌ **금지(비상업 전용)** | ✅ 허용 | ✅ 허용 |
| 과금 방식 | 크레딧 기반(2025.9~) | 크레딧 기반(2025.9~) | 정액(초과 시 유료 전환) | 무료(soft limit) |
| 대표 강점 | 통합 기능·상업적 OK | 빌드 넉넉·Next.js 최적 | 대역폭 무제한·빠름 | GitHub 연동·완전 무료 |

:bulb: 한 줄 요약 — **빌드 시간은 Vercel(6,000분)이 Netlify(300분)의 20배로 넉넉**하지만, **Vercel은 수익 사이트 금지(비상업 전용)**라는 더 중요한 함정이 있다. 대역폭이 걱정이면 Cloudflare Pages가 유일하게 무제한이다.
{: .notice--info}

---

# [02] "개인 사용자 token 제한" — 소문의 진실

질문의 핵심을 정면으로 본다.

## 2-1. 먼저, "token"이라는 제한은 없다

Netlify·Vercel 어디에도 **"token 제한"이라는 공식 용어는 없다.** 아마 다음 중 하나를 가리키는 것이다.

| 들었던 표현 | 실제 정체 |
|---|---|
| "token 제한" | **빌드 시간(build minutes)** 또는 **크레딧(credit)** |
| "Netlify는 빡빡하다" | 무료 빌드 시간이 **월 300분**으로 적음 |
| "Vercel은 제한이 없다" | 무료 빌드 시간이 **월 6,000분**으로 넉넉 (≠ 무제한) |

:warning: 2025년 9월부터 **Netlify와 Vercel 둘 다 "크레딧(credit) 기반" 과금**으로 바뀌었다. 즉 빌드·대역폭·함수 호출 등을 크레딧으로 환산해 차감하는 방식이다. "token"은 이 크레딧을 잘못 들은 것일 가능성이 크다.
{: .notice--warning}

## 2-2. 절반은 맞다 — 빌드 시간은 Vercel이 압도적으로 넉넉

| | Netlify Free | Vercel Hobby |
|---|---|---|
| 월 빌드 시간 | **300분** | **6,000분** (약 20배) |

→ 자주 배포하는 개인 프로젝트라면 Netlify의 300분은 금방 소진될 수 있다. 이 점에서 "Vercel이 더 자유롭다"는 인상은 **맞다.**

## 2-3. 절반은 틀리다 — Vercel도 무제한이 아니고, 더 큰 제약이 있다

```
"Vercel은 제한이 없다" ❌

  ① 빌드 6,000분 한도 존재 (많을 뿐, 무제한 아님)
  ② 대역폭은 Netlify와 똑같이 100GB/월
  ③ ★결정적★ Vercel Hobby = 비상업적(non-commercial) 전용
     → 광고·수익 창출·유료 서비스 배포 금지. 위반 시 Pro($20/월) 강제.
```

:warning: **가장 중요한 차이는 빌드 시간이 아니라 "상업적 사용 가능 여부"다.** Vercel Hobby는 **개인·비상업 용도만** 허용한다(수익이 발생하는 모든 배포 금지). 반면 **Netlify 무료 플랜은 상업적 사용을 허용**한다 — 무료로 돈 버는 사이트도 가능하다. 포트폴리오·블로그면 Vercel이 편하지만, **수익 사이트라면 Netlify(또는 유료 플랜)** 여야 한다.
{: .notice--warning}

**정리:** "Netlify는 제한 있고 Vercel은 없다"는 → **"빌드 시간은 Vercel이 훨씬 넉넉하지만, Vercel은 상업적 사용이 금지된다"**가 정확한 표현이다.

---

# [03] 간단 사용 가이드

세 서비스 모두 **① Git 연동 자동 배포**(권장)와 **② CLI 배포** 두 방식을 지원한다. 정적 사이트(React/Vue 빌드물, Jekyll, Hugo 등) 기준이다.

## 3-1. Netlify

**방법 A — Git 연동 (권장):**

1. [app.netlify.com](https://app.netlify.com) 로그인 → **Add new site → Import an existing project**
2. GitHub/GitLab 저장소 연결
3. 빌드 설정 입력:
   - Build command: `npm run build` (Jekyll이면 `jekyll build`)
   - Publish directory: `dist` (또는 `_site`, `build`)
4. **Deploy** → 이후 `git push`마다 자동 재배포

**방법 B — CLI:**

```bash
npm install -g netlify-cli
netlify login
netlify deploy            # 미리보기(draft) 배포
netlify deploy --prod     # 운영(production) 배포
```

## 3-2. Vercel

**방법 A — Git 연동 (권장):**

1. [vercel.com](https://vercel.com) 로그인 → **Add New → Project**
2. 저장소 Import → **프레임워크 자동 감지**(Next.js, Vite, Astro 등)
3. 대부분 설정 그대로 **Deploy** → `git push`마다 자동 배포 + PR마다 미리보기 URL 생성

**방법 B — CLI:**

```bash
npm install -g vercel
vercel login
vercel            # 미리보기 배포
vercel --prod     # 운영 배포
```

## 3-3. Cloudflare Pages

1. Cloudflare 대시보드 → **Workers & Pages → Create → Pages**
2. Git 저장소 연결 → 빌드 명령/출력 디렉토리 설정 → 배포
3. 장점: **대역폭 무제한**, 글로벌 CDN 기본, Workers로 동적 기능 확장

## 3-4. GitHub Pages

가장 단순하고 완전 무료. **이 블로그도 GitHub Pages로 운영된다.**

1. 저장소 **Settings → Pages**
2. Source를 `main` 브랜치(또는 GitHub Actions)로 지정
3. `https://<사용자명>.github.io/<저장소>` 로 공개
4. 정적 파일만 호스팅 (서버리스 함수 ❌). Jekyll은 GitHub가 자동 빌드해 준다.

:bulb: 셋 다 핵심 흐름은 동일하다 — **저장소 연결 → 빌드 명령/출력 폴더 지정 → push 시 자동 배포.** 한 번 연결하면 그 뒤로는 `git push`만 하면 끝이다.
{: .notice--info}

---

# [04] 그래서 무엇을 고를까

| 상황 | 추천 |
|---|---|
| Next.js/프론트엔드 + 자주 배포, **비상업** 개인 프로젝트 | **Vercel** (빌드 6,000분, Next.js 최적) |
| 수익 발생 사이트(광고·유료·SaaS)인데 무료로 시작 | **Netlify** (무료 상업 사용 허용) |
| 트래픽(대역폭)이 많고 비용이 걱정 | **Cloudflare Pages** (대역폭 무제한) |
| 블로그·문서·포트폴리오, 그냥 완전 무료면 됨 | **GitHub Pages** |

:warning: "Vercel이 빌드 시간 넉넉하니까 무조건 Vercel"은 함정이다. **돈을 버는 사이트라면 Vercel Hobby는 약관 위반**이 된다. 수익 모델이 있다면 처음부터 Netlify 무료 또는 유료 플랜을 고르는 게 안전하다.
{: .notice--warning}

---

# [05] 핵심 요약

| # | 요약 |
|---|------|
| 1 | "token 제한"이라는 공식 용어는 없다 — 실제로는 **빌드 시간(build minutes)/크레딧** 이야기다 |
| 2 | 2025년 9월부터 Netlify·Vercel 모두 **크레딧 기반 과금**으로 전환 |
| 3 | 빌드 시간: **Netlify 300분 vs Vercel 6,000분** → 이 점에선 Vercel이 20배 넉넉 (맞음) |
| 4 | 그러나 **Vercel도 무제한 아님**(대역폭 100GB 동일) + **Vercel Hobby는 비상업 전용**(틀린 부분) |
| 5 | **수익 사이트는 Netlify 무료 가능, Vercel Hobby는 금지** — 이게 가장 중요한 실무 차이 |
| 6 | 대역폭 무제한은 **Cloudflare Pages**, 가장 단순·완전 무료는 **GitHub Pages** |

:bulb: 한 줄 결론 — **개인 비상업 프로젝트는 Vercel(빌드 넉넉), 수익 사이트는 Netlify(상업 OK), 트래픽 폭탄은 Cloudflare Pages(대역폭 무제한), 블로그는 GitHub Pages.**
{: .notice--info}

---

> 출처: [Netlify Pricing](https://www.netlify.com/pricing/) · [Vercel Pricing](https://vercel.com/pricing) · [Vercel Hobby Plan](https://vercel.com/docs/plans/hobby) · [Cloudflare Pages Limits](https://developers.cloudflare.com/pages/platform/limits/) · [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
