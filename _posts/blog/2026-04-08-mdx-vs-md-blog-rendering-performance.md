---
title: "MDX vs MD 기반 블로그: 렌더링 성능 차이와 선택 기준"
description: "MDX 기반 문서 포털의 느린 렌더링 원인을 분석하고, MD 기반 솔루션과의 성능 차이, VitePress 등 대안을 비교 정리"
excerpt: "MDX 빌드 파이프라인 15~30초 vs MD 렌더링 수백ms — 왜 이렇게 차이가 나는지, 어떤 상황에 무엇을 선택해야 하는지"
date: 2026-04-08
categories: Blog
tags: [MDX, Markdown, VitePress, Fumadocs, Next.js, 렌더링성능, SSG, Docker, MkDocs, Hugo]
---

:bulb: MDX 기반 문서 포털(Fumadocs + Next.js)을 Docker Compose로 운영하면서 겪은 렌더링 성능 문제를 분석하고, MD 기반 대안과 비교한다. 결론적으로 VitePress로의 전환을 결정한 과정을 정리한다.
{: .notice--info}

---

# [01] 문제 상황

Fumadocs(Next.js + MDX) 기반 문서 포털을 Docker Compose로 실행한 뒤, `.md` 파일 하나를 수정하고 브라우저에서 반영을 확인하려고 했다.

**기대**: 파일 저장 → 1~2초 내 브라우저 반영

**현실**: 파일 저장 → **30초 이상** 대기

<pre class="mermaid">
graph LR
    EDIT[".md 파일 수정"] -->|기대: 1~2초| BROWSER["브라우저 반영"]
    EDIT -->|현실: 30초+| WAIT["⏳ 대기..."]
    WAIT --> BROWSER

    style EDIT fill:#e3f2fd,stroke:#1565c0
    style WAIT fill:#ffcccc,stroke:#c62828
    style BROWSER fill:#e8f5e9,stroke:#2e7d32
</pre>

문서 한 줄 수정하고 30초를 기다리는 것은 개발 생산성을 심각하게 저하시킨다. 왜 이렇게 느린지 원인을 분석했다.

---

# [02] MDX 렌더링이 느린 이유

## 2-1. MDX 빌드 파이프라인의 복잡성

MDX는 Markdown + React의 하이브리드다. 단순히 마크다운을 HTML로 변환하는 것이 아니라, **6단계 파이프라인**을 거쳐야 한다.

<pre class="mermaid">
graph TD
    A[".mdx 파일 변경"] --> B["[1] Fumadocs-mdx 스캔<br/>.mdx 파싱, frontmatter 추출<br/>.source/ 재생성 (84+ imports)"]
    B --> C["[2] Remark/Rehype<br/>플러그인 체인 처리"]
    C --> D["[3] TypeScript 컴파일<br/>JSX 변환, 타입 체크"]
    D --> E["[4] Webpack/Turbopack<br/>번들링, 코드 스플리팅"]
    E --> F["[5] Next.js SSG<br/>페이지별 HTML 생성"]
    F --> G["[6] 브라우저 반영 (HMR)<br/>약 15~30초 소요"]

    style A fill:#e3f2fd,stroke:#1565c0
    style G fill:#ffcccc,stroke:#c62828
</pre>

반면 순수 Markdown(`.md`)은:

<pre class="mermaid">
graph LR
    A[".md 파일 변경"] --> B["Markdown → HTML 변환"]
    B --> C["브라우저 반영<br/>~100~300ms"]

    style A fill:#e3f2fd,stroke:#1565c0
    style C fill:#e8f5e9,stroke:#2e7d32
</pre>

**핵심 차이**: MDX는 React 컴포넌트 변환, TypeScript 컴파일, 번들링이 필수다. MD는 텍스트 → HTML 변환만 하면 끝이다.

## 2-2. Next.js Dev 모드의 JIT 오버헤드

Next.js 개발 모드에서는 페이지 요청마다 **on-the-fly 컴파일**을 수행한다.

<pre class="mermaid">
sequenceDiagram
    participant User as 브라우저
    participant Next as Next.js Dev Server
    participant MDX as MDX 컴파일러
    participant TS as TypeScript
    participant WP as Webpack

    User->>Next: 페이지 요청
    Next->>MDX: .mdx 파일 로드
    MDX->>MDX: frontmatter 추출
    MDX->>TS: JSX → JS 변환
    TS->>WP: 번들링 요청
    WP->>WP: 코드 스플리팅
    WP-->>Next: 번들 완료
    Next-->>User: HTML 응답
    Note over User,WP: 이 전체 과정이 매 요청마다 반복
</pre>

프로덕션 최적화(Minification, Code Splitting, Tree Shaking)도 Dev 모드에서는 비활성화 상태라 더 느리다.

## 2-3. Docker 환경의 추가 오버헤드

Docker Compose로 실행하면 성능이 더 악화된다.

<pre class="mermaid">
graph TD
    subgraph "로컬 개발 (~5ms)"
        L1["호스트 SSD"] -->|직접 접근| L2["Node.js"]
    end

    subgraph "Docker 개발 (~50~100ms+)"
        D1["호스트 SSD"] -->|FUSE/VPKit| D2["Docker 데몬"]
        D2 -->|가상화 계층| D3["컨테이너 Node.js"]
    end

    style L2 fill:#e8f5e9,stroke:#2e7d32
    style D3 fill:#ffcccc,stroke:#c62828
</pre>

| 병목 지점 | 로컬 | Docker |
|-----------|------|--------|
| 파일 I/O | ~5ms (SSD 직접) | ~50~100ms+ (볼륨 마운트) |
| 파일 변경 감지 | OS 이벤트 (즉시) | 폴링 방식 (+1초) |
| 네트워크 | 직접 | 컨테이너 포트 변환 (+10~20ms) |
| node_modules 접근 | 로컬 | 호스트 마운트 시 10배 느림 |

**특히 볼륨 마운트 I/O**가 치명적이다. node_modules의 수천 개 파일을 매번 가상화 계층을 통해 접근하면, 체감 성능이 크게 떨어진다.

---

# [03] MD vs MDX 성능 비교

같은 문서를 MD 기반과 MDX 기반으로 처리할 때의 성능 차이다.

<pre class="mermaid">
graph LR
    subgraph MD["MD 기반 서버 (~120ms)"]
        direction LR
        M1["파일 감지<br/>100ms"] --> M2["MD→HTML<br/>10ms"]
        M2 --> M3["템플릿<br/>5ms"]
        M3 --> M4["파일 쓰기<br/>5ms"]
    end

    subgraph MDX["MDX 기반 Docker (~21.7초)"]
        direction LR
        X1["파일 감지<br/>500ms"] --> X2["mdx 스캔<br/>200ms"]
        X2 --> X3[".source/<br/>2초"]
        X3 --> X4["TS 컴파일<br/>5초"]
        X4 --> X5["번들링<br/>8초"]
        X5 --> X6["SSG<br/>5초"]
        X6 --> X7["Docker I/O<br/>500ms"]
    end

    style MD fill:#e8f5e9,stroke:#2e7d32
    style MDX fill:#ffcccc,stroke:#c62828
</pre>

| 구분 | MD 기반 | MDX 기반 (Docker) |
|------|---------|-------------------|
| 파일 감지 | 100ms | 500ms |
| 변환 처리 | 15ms | 15,200ms |
| 기타 오버헤드 | 5ms | 6,000ms |
| **총 소요** | **~120ms** | **~21.7초 (실제 30초+)** |

**~180배 차이**. 문서 한 줄 수정에 30초는, 생산성이 아니라 인내심 테스트다.

---

# [04] 대안 솔루션 비교

## 4-1. 카테고리별 분류

<pre class="mermaid">
graph TD
    ROOT["문서 사이트 도구"] --> RT["런타임 렌더링<br/>(빌드 제로)"]
    ROOT --> FAST["빠른 SSG<br/>(1초 이내)"]
    ROOT --> SLOW["MDX 기반 SSG<br/>(15초 이상)"]

    RT --> Docsify["Docsify<br/>0초"]
    RT --> Wiki["Wiki.js<br/>실시간"]

    FAST --> Hugo["Hugo (Go)<br/>~50ms"]
    FAST --> mdBook["mdBook (Rust)<br/>~100ms"]
    FAST --> VP["VitePress (Vite)<br/>~200ms"]
    FAST --> MK["MkDocs (Python)<br/>~300ms"]

    SLOW --> Fuma["Fumadocs<br/>15~30초"]
    SLOW --> Docu["Docusaurus<br/>20~40초"]
    SLOW --> Nextra["Nextra<br/>10~20초"]

    style RT fill:#e8f5e9,stroke:#2e7d32
    style FAST fill:#e3f2fd,stroke:#1565c0
    style SLOW fill:#ffcccc,stroke:#c62828
    style VP fill:#ffffcc,stroke:#f9a825,stroke-width:3px
</pre>

## 4-2. 성능 비교 테이블

| 솔루션 | 엔진 | 재빌드 시간 | 컴포넌트 | SEO | 특징 |
|--------|------|------------|---------|-----|------|
| **Hugo** | Go | ~50ms | 제한적 | O | 가장 빠른 SSG |
| **mdBook** | Rust | ~100ms | 제한적 | O | Rust 공식 문서 사용 |
| **VitePress** | Vue/Vite | ~200ms | Vue | O | HMR 즉시 반영 |
| **MkDocs Material** | Python | ~300ms | 제한적 | O | 기술문서 인기 1위 |
| **Docsify** | JS (브라우저) | 0초 | X | X | 빌드 불필요 |
| **Nextra** | Next.js | 10~20초 | React | O | MDX 중 상대적 빠름 |
| **Fumadocs** | React | 15~30초 | React | O | 현재 사용 중 |
| **Docusaurus** | React | 20~40초 | React | O | Meta 주도 |

---

# [05] 왜 VitePress인가

## 5-1. 선택 기준

<pre class="mermaid">
graph TD
    Q1{"파일 수정 후<br/>즉시 반영 필요?"}
    Q1 -->|Yes| Q2{"React 컴포넌트<br/>반드시 필요?"}
    Q1 -->|No| KEEP["현재 스택 유지<br/>(최적화 필수)"]

    Q2 -->|Yes| NEXTRA["Nextra 검토<br/>(MDX 중 가장 빠름)"]
    Q2 -->|No| Q3{"모던 개발 경험<br/>(TS, HMR) 필요?"}

    Q3 -->|Yes| VITEPRESS["✅ VitePress"]
    Q3 -->|No| MKDOCS["MkDocs / Hugo"]

    style Q1 fill:#fff3e0,stroke:#e65100
    style VITEPRESS fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
    style KEEP fill:#ffcccc,stroke:#c62828
</pre>

| 질문 | 답 | 결과 |
|------|---|------|
| 파일 수정 후 즉시 반영(1초 이내)이 필요한가? | **Yes** | MDX 계열 탈락 |
| React 커스텀 컴포넌트가 반드시 필요한가? | **No** | Vue 컴포넌트로 대체 가능 |
| 모던 개발 경험(TypeScript, HMR)이 필요한가? | **Yes** | Hugo, MkDocs 대비 우위 |

## 5-2. Fumadocs vs VitePress 비교

| 항목 | Fumadocs (현재) | VitePress (전환 대상) |
|------|----------------|----------------------|
| 재빌드 시간 | 15~30초 (Docker: 30초+) | ~200ms |
| HMR | 느림 (전체 빌드 경유) | 즉시 (Vite 네이티브) |
| 컴포넌트 | React (MDX 필수) | Vue 3 (선택적) |
| 프로덕션 빌드 | 수 분 | 1초 미만 |
| 설정 복잡도 | 높음 (Next.js + Fumadocs) | 낮음 |
| Docker 호환성 | 볼륨 마운트 병목 | 가벼워서 영향 적음 |

## 5-3. VitePress 기본 구조

```bash
npm create vitepress
npm run docs:dev
```

```
docs/
├── .vitepress/
│   └── config.ts          # 사이트 설정
├── index.md               # 메인 페이지
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

# [06] 핵심 교훈

## 6-1. MDX가 필요한 경우

- 문서 안에 **인터랙티브 React 컴포넌트**가 필수일 때
- 디자인 시스템 문서처럼 **라이브 코드 프리뷰**가 필요할 때
- React 기반 프로젝트의 **스토리북 대체 용도**로 사용할 때

## 6-2. MD 기반이 더 나은 경우 (대부분)

- 기술 문서, API 레퍼런스, 가이드 등 **텍스트 중심 콘텐츠**
- 파일 수정 후 **즉시 확인**이 중요한 워크플로우
- Docker 환경에서 개발/배포하는 경우
- 팀원 중 프론트엔드 전문가가 아닌 사람이 문서를 작성하는 경우

## 6-3. 판단 기준

<pre class="mermaid">
graph TD
    Q{"문서에 React<br/>인터랙션이<br/>꼭 필요한가?"}
    Q -->|Yes| MDX["MDX 기반<br/>(Fumadocs, Docusaurus)<br/>⚠️ 30초+ 빌드 감수"]
    Q -->|No| MD["MD 기반<br/>(VitePress, MkDocs, Hugo)<br/>✅ 200~300ms 즉시 반영"]

    style Q fill:#fff3e0,stroke:#e65100
    style MDX fill:#ffcccc,stroke:#c62828
    style MD fill:#e8f5e9,stroke:#2e7d32,stroke-width:3px
</pre>

:bulb: 대부분의 기술 문서는 **텍스트 + 코드 블록 + 이미지**로 충분하다. "혹시 나중에 React 컴포넌트가 필요할지도" 라는 이유로 MDX를 선택하면, 매일 30초씩 대기하는 비용을 치르게 된다.
{: .notice--info}
