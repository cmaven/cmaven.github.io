---
title: "kebab-case, snake_case, camelCase — Naming Convention Guide"
description: "Differences between common case styles in programming, language-specific recommendations, and selection criteria"
excerpt: "Differences and language-specific usage of kebab-case, snake_case, camelCase, and PascalCase"
date: 2026-04-14
categories: Etc
tags: [naming-convention, kebab-case, snake_case, camelCase, PascalCase, coding-style, clean-code]
ref: naming-convention-case-styles
---

:bulb: Differences and usage criteria for the common case styles used when naming variables, functions, files, and URLs in programming.
{: .notice--info}

---

# [01] Case Styles at a Glance

| Style | Example | Rule | Aliases |
|-------|---------|------|---------|
| **camelCase** | `getUserName` | First word lowercase, subsequent words capitalized | lower camelCase |
| **PascalCase** | `GetUserName` | Every word capitalized | upper camelCase |
| **snake_case** | `get_user_name` | All lowercase, words joined by underscore `_` | |
| **SCREAMING_SNAKE_CASE** | `GET_USER_NAME` | All uppercase, words joined by underscore `_` | UPPER_SNAKE_CASE |
| **kebab-case** | `get-user-name` | All lowercase, words joined by hyphen `-` | dash-case, lisp-case |

Same meaning, five ways:

```
camelCase:              myVariableName
PascalCase:             MyVariableName
snake_case:             my_variable_name
SCREAMING_SNAKE_CASE:   MY_VARIABLE_NAME
kebab-case:             my-variable-name
```

---

# [02] Each Style In Detail

## 2-1. camelCase

First word lowercase, subsequent words capitalized at the first letter. The "humps" resemble a camel's, hence camelCase.

```javascript
// JavaScript — variables, functions
let userName = "admin";
function getUserProfile() { ... }
const maxRetryCount = 3;
```

**Main uses:**
- JavaScript / TypeScript — variables, functions
- Java — variables, methods
- Swift, Kotlin — variables, functions

## 2-2. PascalCase

Every word capitalized at the first letter. A variant of camelCase, originating from Pascal.

```python
# Python — classes
class UserProfile:
    pass

class HttpRequestHandler:
    pass
```

```typescript
// TypeScript — classes, interfaces, types
class UserService { ... }
interface ApiResponse { ... }
type UserRole = "admin" | "user";
```

**Main uses:**
- Almost every language — **class names**
- TypeScript — interfaces, types
- React — component names
- C# — methods, properties

## 2-3. snake_case

All lowercase, joined by underscore `_`.

```python
# Python — variables, functions
user_name = "admin"
def get_user_profile():
    pass
max_retry_count = 3
```

```ruby
# Ruby — variables, methods
user_name = "admin"
def get_user_profile
end
```

**Main uses:**
- Python — variables, functions, modules
- Ruby — variables, methods
- Rust — variables, functions
- SQL — tables, columns
- C — variables, functions

## 2-4. SCREAMING_SNAKE_CASE

All uppercase, joined by underscore. As the name "screaming snake" suggests, used for **constants**.

```python
# Python — constants
MAX_RETRY_COUNT = 3
DATABASE_URL = "postgresql://localhost/mydb"
DEFAULT_TIMEOUT_SECONDS = 30
```

```java
// Java — constants
public static final int MAX_RETRY_COUNT = 3;
public static final String API_BASE_URL = "https://api.example.com";
```

**Main uses:**
- Almost every language — **constants**
- Environment variables — `DATABASE_URL`, `API_KEY`

## 2-5. kebab-case

All lowercase, joined by hyphen `-`. The hyphens pierce words like a kebab skewer, hence kebab-case.

```html
<!-- HTML — attributes, CSS classes -->
<div class="user-profile" data-user-id="123">
  <span class="user-name">admin</span>
</div>
```

```css
/* CSS — properties, classes */
.user-profile {
  font-size: 14px;
  background-color: #fff;
  max-width: 1200px;
}
```

```
# URL path
https://example.com/api/user-profile
https://example.com/blog/my-first-post
```

**Main uses:**
- HTML — attributes, custom tags
- CSS — class names, properties
- URL — paths
- File names — `user-profile.js`, `api-handler.ts`
- CLI options — `--max-retry`, `--output-dir`

:warning: kebab-case **cannot be used as a variable name** in most programming languages — hyphen `-` is interpreted as the subtraction operator.
{: .notice--warning}

```javascript
// X impossible — interpreted as subtraction
let user-name = "admin";  // SyntaxError

// O variables use camelCase
let userName = "admin";
```

---

# [03] Language-Specific Conventions

| Language/Env | Variables/Functions | Classes/Types | Constants | File names |
|--------------|---------------------|----------------|-----------|------------|
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
| **Env variables** | - | - | SCREAMING_SNAKE | - |

:bulb: Within a single project, the case style varies by target. In JavaScript: variables `camelCase`, classes `PascalCase`, constants `SCREAMING_SNAKE_CASE`, file names `kebab-case`.
{: .notice--info}

---

# [04] Real Example — One Project Using Multiple Styles

A React + TypeScript project uses 4 styles in one project:

```
src/
├── components/
│   └── user-profile/              ← directory: kebab-case
│       ├── UserProfile.tsx        ← component file: PascalCase
│       └── user-profile.css       ← style file: kebab-case
├── utils/
│   └── api-handler.ts             ← util file: kebab-case
└── constants/
    └── config.ts
```

```typescript
// config.ts
export const API_BASE_URL = "https://api.example.com";   // constant: SCREAMING_SNAKE
export const MAX_RETRY_COUNT = 3;

// UserProfile.tsx
import React from 'react';

interface UserProfileProps {    // interface: PascalCase
  userName: string;            // property: camelCase
  isActive: boolean;
}

class UserService {            // class: PascalCase
  getUserById(userId: number) {  // method, parameter: camelCase
    const requestUrl = `${API_BASE_URL}/users/${userId}`;
    return fetch(requestUrl);
  }
}
```

```css
/* user-profile.css */
.user-profile {               /* class: kebab-case */
  max-width: 600px;           /* CSS property: kebab-case */
  background-color: #f5f5f5;
}

.user-profile__header {       /* BEM notation also kebab-based */
  font-size: 18px;
}
```

---

# [05] Selection Criteria

## 5-1. Default Rule

```
Follow the language/framework's official style guide.
```

| Where to look | Examples |
|---------------|----------|
| Python | PEP 8 |
| JavaScript | Airbnb Style Guide, Google Style Guide |
| Go | Effective Go |
| Rust | Rust API Guidelines |
| Java | Google Java Style Guide |

## 5-2. When No Official Guide

| Context | Recommendation |
|---------|----------------|
| URL, file names | kebab-case (SEO, readability) |
| Env variables | SCREAMING_SNAKE_CASE |
| DB tables/columns | snake_case |
| API JSON fields | camelCase (frontend) or snake_case (backend) |
| Config file keys | kebab-case (YAML, CLI) or camelCase (JSON) |

## 5-3. Most Important

:bulb: Whatever style you pick, **consistency within a project matters most**. Mixing `userName` and `user_name` for the same thing causes confusion.
{: .notice--info}

---

# [06] Summary

| Style | Form | Typical use |
|-------|------|-------------|
| **camelCase** | `myVariable` | JS/Java variables, functions |
| **PascalCase** | `MyClass` | classes, components, types |
| **snake_case** | `my_variable` | Python/Rust/Ruby variables, DB |
| **SCREAMING_SNAKE** | `MY_CONSTANT` | constants, env variables |
| **kebab-case** | `my-component` | URL, CSS, HTML, file names |

```
Naming rule = language convention + target type + project consistency
```
