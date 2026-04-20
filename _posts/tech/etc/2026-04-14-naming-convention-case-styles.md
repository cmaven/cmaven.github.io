---
title: "kebab-case, snake_case, camelCase — 네이밍 컨벤션 정리"
description: "프로그래밍에서 자주 사용하는 케이스 스타일의 차이점, 각 언어/환경별 권장 컨벤션, 선택 기준을 정리"
excerpt: "kebab-case, snake_case, camelCase, PascalCase 등 네이밍 컨벤션의 차이와 언어별 사용 기준"
date: 2026-04-14
categories: Etc
tags: [네이밍컨벤션, kebab-case, snake_case, camelCase, PascalCase, 코딩스타일, 클린코드]
---

:bulb: 프로그래밍에서 변수, 함수, 파일, URL 등의 이름을 짓는 대표적인 케이스 스타일의 차이와 사용 기준을 정리한다.
{: .notice--info}

---

# [01] 케이스 스타일 한눈에 보기

| 스타일 | 표기 예시 | 규칙 | 별칭 |
|--------|-----------|------|------|
| **camelCase** | `getUserName` | 첫 단어 소문자, 이후 단어 첫 글자 대문자 | lower camelCase |
| **PascalCase** | `GetUserName` | 모든 단어 첫 글자 대문자 | upper camelCase |
| **snake_case** | `get_user_name` | 모든 소문자, 단어 사이 언더스코어 `_` | |
| **SCREAMING_SNAKE_CASE** | `GET_USER_NAME` | 모든 대문자, 단어 사이 언더스코어 `_` | UPPER_SNAKE_CASE |
| **kebab-case** | `get-user-name` | 모든 소문자, 단어 사이 하이픈 `-` | dash-case, lisp-case |

같은 의미를 표현하는 5가지 방식:

```
camelCase:              myVariableName
PascalCase:             MyVariableName
snake_case:             my_variable_name
SCREAMING_SNAKE_CASE:   MY_VARIABLE_NAME
kebab-case:             my-variable-name
```

---

# [02] 각 스타일 상세

## 2-1. camelCase

첫 단어는 소문자, 이후 단어의 첫 글자만 대문자로 표기한다. 대문자 부분이 낙타(camel)의 혹처럼 보여서 camelCase라 부른다.

```javascript
// JavaScript — 변수, 함수
let userName = "admin";
function getUserProfile() { ... }
const maxRetryCount = 3;
```

**주 사용처:**
- JavaScript / TypeScript — 변수, 함수
- Java — 변수, 메서드
- Swift, Kotlin — 변수, 함수

## 2-2. PascalCase

모든 단어의 첫 글자를 대문자로 표기한다. camelCase의 변형으로, Pascal 언어에서 유래했다.

```python
# Python — 클래스
class UserProfile:
    pass

class HttpRequestHandler:
    pass
```

```typescript
// TypeScript — 클래스, 인터페이스, 타입
class UserService { ... }
interface ApiResponse { ... }
type UserRole = "admin" | "user";
```

**주 사용처:**
- 거의 모든 언어 — **클래스명**
- TypeScript — 인터페이스, 타입
- React — 컴포넌트명
- C# — 메서드, 프로퍼티

## 2-3. snake_case

모든 글자를 소문자로, 단어 사이를 언더스코어 `_`로 연결한다.

```python
# Python — 변수, 함수
user_name = "admin"
def get_user_profile():
    pass
max_retry_count = 3
```

```ruby
# Ruby — 변수, 메서드
user_name = "admin"
def get_user_profile
end
```

**주 사용처:**
- Python — 변수, 함수, 모듈
- Ruby — 변수, 메서드
- Rust — 변수, 함수
- SQL — 테이블, 컬럼
- C — 변수, 함수

## 2-4. SCREAMING_SNAKE_CASE

모든 글자를 대문자로, 단어 사이를 언더스코어 `_`로 연결한다. "소리 지르는 뱀"이라는 이름답게, **상수(constant)**를 나타낼 때 사용한다.

```python
# Python — 상수
MAX_RETRY_COUNT = 3
DATABASE_URL = "postgresql://localhost/mydb"
DEFAULT_TIMEOUT_SECONDS = 30
```

```java
// Java — 상수
public static final int MAX_RETRY_COUNT = 3;
public static final String API_BASE_URL = "https://api.example.com";
```

**주 사용처:**
- 거의 모든 언어 — **상수**
- 환경변수 — `DATABASE_URL`, `API_KEY`

## 2-5. kebab-case

모든 글자를 소문자로, 단어 사이를 하이픈 `-`으로 연결한다. 하이픈이 케밥 꼬치처럼 단어를 꿰뚫고 있어서 kebab-case라 부른다.

```html
<!-- HTML — 속성, CSS 클래스 -->
<div class="user-profile" data-user-id="123">
  <span class="user-name">admin</span>
</div>
```

```css
/* CSS — 프로퍼티, 클래스 */
.user-profile {
  font-size: 14px;
  background-color: #fff;
  max-width: 1200px;
}
```

```
# URL 경로
https://example.com/api/user-profile
https://example.com/blog/my-first-post
```

**주 사용처:**
- HTML — 속성, 커스텀 태그
- CSS — 클래스명, 프로퍼티
- URL — 경로
- 파일명 — `user-profile.js`, `api-handler.ts`
- CLI 옵션 — `--max-retry`, `--output-dir`

:warning: kebab-case는 대부분의 프로그래밍 언어에서 **변수명으로 사용할 수 없다.** 하이픈 `-`이 뺄셈 연산자로 해석되기 때문이다.
{: .notice--warning}

```javascript
// ❌ 불가능 — 뺄셈으로 해석됨
let user-name = "admin";  // SyntaxError

// ✅ 변수명은 camelCase
let userName = "admin";
```

---

# [03] 언어별 권장 컨벤션

| 언어/환경 | 변수/함수 | 클래스/타입 | 상수 | 파일명 |
|-----------|-----------|-----------|------|--------|
| **JavaScript** | camelCase | PascalCase | SCREAMING_SNAKE | kebab-case |
| **TypeScript** | camelCase | PascalCase | SCREAMING_SNAKE | kebab-case |
| **Python** | snake_case | PascalCase | SCREAMING_SNAKE | snake_case |
| **Java** | camelCase | PascalCase | SCREAMING_SNAKE | PascalCase |
| **Go** | camelCase | PascalCase | PascalCase | snake_case |
| **Rust** | snake_case | PascalCase | SCREAMING_SNAKE | snake_case |
| **Ruby** | snake_case | PascalCase | SCREAMING_SNAKE | snake_case |
| **C / C++** | snake_case | PascalCase | SCREAMING_SNAKE | snake_case |
| **C#** | camelCase | PascalCase | PascalCase | PascalCase |
| **Swift** | camelCase | PascalCase | camelCase | PascalCase |
| **Kotlin** | camelCase | PascalCase | SCREAMING_SNAKE | PascalCase |
| **SQL** | snake_case | - | - | snake_case |
| **HTML/CSS** | kebab-case | - | - | kebab-case |
| **URL** | kebab-case | - | - | - |
| **환경변수** | - | - | SCREAMING_SNAKE | - |

:bulb: 같은 프로젝트 안에서도 대상에 따라 케이스 스타일이 달라진다. 예를 들어 JavaScript에서 변수는 `camelCase`, 클래스는 `PascalCase`, 상수는 `SCREAMING_SNAKE_CASE`, 파일명은 `kebab-case`를 사용한다.
{: .notice--info}

---

# [04] 실전 예시: 하나의 프로젝트에서

React + TypeScript 프로젝트를 예로 들면, 한 프로젝트 안에서 4가지 스타일을 모두 사용한다.

```
src/
├── components/
│   └── user-profile/              ← 디렉토리: kebab-case
│       ├── UserProfile.tsx        ← 컴포넌트 파일: PascalCase
│       └── user-profile.css       ← 스타일 파일: kebab-case
├── utils/
│   └── api-handler.ts             ← 유틸 파일: kebab-case
└── constants/
    └── config.ts
```

```typescript
// config.ts
export const API_BASE_URL = "https://api.example.com";   // 상수: SCREAMING_SNAKE
export const MAX_RETRY_COUNT = 3;

// UserProfile.tsx
import React from 'react';

interface UserProfileProps {    // 인터페이스: PascalCase
  userName: string;            // 프로퍼티: camelCase
  isActive: boolean;
}

class UserService {            // 클래스: PascalCase
  getUserById(userId: number) {  // 메서드, 매개변수: camelCase
    const requestUrl = `${API_BASE_URL}/users/${userId}`;
    return fetch(requestUrl);
  }
}
```

```css
/* user-profile.css */
.user-profile {               /* 클래스: kebab-case */
  max-width: 600px;           /* CSS 프로퍼티: kebab-case */
  background-color: #f5f5f5;
}

.user-profile__header {       /* BEM 표기법도 kebab 기반 */
  font-size: 18px;
}
```

---

# [05] 선택 기준

## 5-1. 기본 원칙

```
해당 언어/프레임워크의 공식 스타일 가이드를 따른다.
```

| 찾는 곳 | 예시 |
|---------|------|
| Python | PEP 8 |
| JavaScript | Airbnb Style Guide, Google Style Guide |
| Go | Effective Go |
| Rust | Rust API Guidelines |
| Java | Google Java Style Guide |

## 5-2. 공식 가이드가 없을 때

| 상황 | 권장 |
|------|------|
| URL, 파일명 | kebab-case (SEO, 가독성) |
| 환경변수 | SCREAMING_SNAKE_CASE |
| DB 테이블/컬럼 | snake_case |
| API JSON 필드 | camelCase (프론트엔드) 또는 snake_case (백엔드) |
| 설정 파일 키 | kebab-case (YAML, CLI) 또는 camelCase (JSON) |

## 5-3. 가장 중요한 것

:bulb: 어떤 스타일을 선택하든 **프로젝트 내에서 일관성을 유지하는 것**이 가장 중요하다. 하나의 프로젝트에서 같은 대상에 `userName`과 `user_name`이 혼재하면 혼란을 초래한다.
{: .notice--info}

---

# [06] 정리

| 스타일 | 형태 | 대표 용도 |
|--------|------|-----------|
| **camelCase** | `myVariable` | JS/Java 변수, 함수 |
| **PascalCase** | `MyClass` | 클래스, 컴포넌트, 타입 |
| **snake_case** | `my_variable` | Python/Rust/Ruby 변수, DB |
| **SCREAMING_SNAKE** | `MY_CONSTANT` | 상수, 환경변수 |
| **kebab-case** | `my-component` | URL, CSS, HTML, 파일명 |

```
이름 짓기 규칙 = 언어 컨벤션 + 대상 종류 + 프로젝트 일관성
```
