---
title: "Jekyll 블로그에 Mermaid 다이어그램 추가하기"
date: 2026-03-13
categories: Github_Blog
tags: [Jekyll, Mermaid, diagram]
---

:bulb: Jekyll(Minimal Mistakes) 블로그에서 코드 기반 다이어그램을 그릴 수 있도록 Mermaid를 설정하는 방법을 작성한다.
{: .notice--info}

# [01] Mermaid란?

Mermaid는 **텍스트 기반으로 다이어그램을 생성**하는 JavaScript 라이브러리다.
마크다운 안에서 간단한 문법으로 플로우차트, 시퀀스 다이어그램, 클래스 다이어그램 등을 그릴 수 있다.

| 특징 | 설명 |
|---|---|
| 코드 기반 | 이미지 파일 없이 텍스트로 다이어그램 작성 |
| 실시간 렌더링 | 브라우저에서 JavaScript로 SVG 변환 |
| Git 친화적 | 텍스트이므로 변경 이력 추적 가능 |
| 다양한 다이어그램 | 플로우차트, 시퀀스, 간트, 파이, 클래스 등 지원 |

---

# [02] 설정 방법

## 2-1. `_includes/head/custom.html` 수정

Minimal Mistakes 테마에서는 `_includes/head/custom.html` 파일에 커스텀 스크립트를 추가할 수 있다.
이 파일 하단에 Mermaid CDN 스크립트를 추가한다.

```html
<!-- ======= mermaid diagram ======= -->
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true, theme: 'default' });
</script>
```

**설명:**

| 항목 | 설명 |
|---|---|
| `type="module"` | ES Module 방식으로 로드 |
| `mermaid@11` | Mermaid v11 사용 (최신 안정 버전) |
| `startOnLoad: true` | 페이지 로드 시 자동으로 다이어그램 렌더링 |
| `theme: 'default'` | 기본 테마 적용 (`dark`, `forest`, `neutral` 등 변경 가능) |

:bulb: `_includes/head/custom.html`은 모든 페이지의 `<head>` 태그에 포함되므로, 한 번만 설정하면 모든 포스트에서 mermaid를 사용할 수 있다.
{: .notice--info}

---

## 2-2. 설정 확인

별도의 플러그인 설치나 `_config.yml` 수정은 필요 없다. CDN으로 직접 로드하기 때문에 GitHub Pages에서도 바로 동작한다.

---

# [03] 사용 방법

포스트(.md) 본문에서 아래와 같이 `<pre class="mermaid">` 태그 안에 mermaid 문법을 작성한다.

## 3-1. 플로우차트

**작성 예:**

```html
<pre class="mermaid">
graph LR
    A[시작] --> B{조건 확인}
    B -->|Yes| C[실행]
    B -->|No| D[종료]
    C --> D
</pre>
```

**결과:**

<pre class="mermaid">
graph LR
    A[시작] --> B{조건 확인}
    B -->|Yes| C[실행]
    B -->|No| D[종료]
    C --> D
</pre>

---

## 3-2. 시퀀스 다이어그램

**작성 예:**

```html
<pre class="mermaid">
sequenceDiagram
    participant Client
    participant Server
    participant DB
    Client->>Server: 요청
    Server->>DB: 쿼리
    DB-->>Server: 결과
    Server-->>Client: 응답
</pre>
```

**결과:**

<pre class="mermaid">
sequenceDiagram
    participant Client
    participant Server
    participant DB
    Client->>Server: 요청
    Server->>DB: 쿼리
    DB-->>Server: 결과
    Server-->>Client: 응답
</pre>

---

## 3-3. 간트 차트

**작성 예:**

```html
<pre class="mermaid">
gantt
    title 프로젝트 일정
    dateFormat  YYYY-MM-DD
    section 설계
    요구사항 분석    :a1, 2026-01-01, 7d
    시스템 설계      :a2, after a1, 5d
    section 개발
    구현             :b1, after a2, 14d
    테스트           :b2, after b1, 7d
</pre>
```

**결과:**

<pre class="mermaid">
gantt
    title 프로젝트 일정
    dateFormat  YYYY-MM-DD
    section 설계
    요구사항 분석    :a1, 2026-01-01, 7d
    시스템 설계      :a2, after a1, 5d
    section 개발
    구현             :b1, after a2, 14d
    테스트           :b2, after b1, 7d
</pre>

---

# [04] 지원 다이어그램 종류

| 다이어그램 | 키워드 | 용도 |
|---|---|---|
| 플로우차트 | `graph` / `flowchart` | 프로세스 흐름 |
| 시퀀스 | `sequenceDiagram` | API 호출 흐름, 통신 순서 |
| 클래스 | `classDiagram` | 클래스 구조, 상속 관계 |
| 상태 | `stateDiagram-v2` | 상태 전이 |
| ER | `erDiagram` | 데이터베이스 관계 |
| 간트 | `gantt` | 일정 관리 |
| 파이 | `pie` | 비율 표시 |
| 마인드맵 | `mindmap` | 아이디어 구조화 |

:bulb: 전체 문법은 [Mermaid 공식 문서](https://mermaid.js.org/intro/)에서 확인할 수 있다.
{: .notice--info}

---

# [05] 테마 변경

`mermaid.initialize`의 `theme` 옵션으로 다이어그램 스타일을 변경할 수 있다.

| 테마 | 설명 |
|---|---|
| `default` | 기본 (밝은 배경, 파란 계열) |
| `dark` | 다크 모드 |
| `forest` | 초록 계열 |
| `neutral` | 흑백 계열 |

```javascript
mermaid.initialize({ startOnLoad: true, theme: 'neutral' });
```

---

# [06] 주의사항

:warning: 마크다운의 코드 블록(````mermaid`)이 아닌, **`<pre class="mermaid">`** 태그를 사용해야 한다. Jekyll의 kramdown은 코드 블록 안의 내용을 코드로 취급하여 mermaid가 파싱하지 못한다.
{: .notice--warning}

| 항목 | 설명 |
|---|---|
| 태그 사용 | ````mermaid` 대신 `<pre class="mermaid">` 사용 |
| 들여쓰기 | `<pre>` 태그 안의 내용은 들여쓰기에 주의 (불필요한 공백이 파싱 오류 유발) |
| CDN 의존 | 인터넷 연결 필요 (오프라인 환경에서는 렌더링 불가) |
