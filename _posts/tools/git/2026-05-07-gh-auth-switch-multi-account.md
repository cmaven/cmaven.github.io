---
title: "GitHub 멀티 계정 전환 — gh auth switch 활용 가이드"
description: "한 머신에서 여러 GitHub 계정을 충돌 없이 운영하는 방법. credential helper의 동작 원리부터 gh CLI 활성 계정 전환, 검증 명령어, 실전 함정 5가지까지 정리"
excerpt: "gh auth switch 한 줄로 git push의 인증 주체가 바뀐다. credential helper 동작 원리·PAT 발급·계정 전환·실전 함정까지 한 번에 정리"
date: 2026-05-07
categories: Git
tags: [GitHub, gh-cli, gh-auth-switch, gh-auth-login, Git, Authentication, credential-helper, PAT, Personal-Access-Token, multi-account, OAuth, HTTPS, GCM, osxkeychain, libsecret]
ref: gh-auth-switch-multi-account
---

:bulb: 직장 계정과 개인 계정, organization별 봇 계정 — 한 머신에서 여러 GitHub 계정을 다뤄야 하는 상황은 의외로 흔하다. 문제는 `git push` 가 일어날 때 git이 **누구의 자격증명**을 보내느냐다. **`gh` CLI를 credential helper로 쓰면 `gh auth switch` 한 줄로 push 주체가 바뀐다.** 이 글은 그 원리와 함정을 정리한다.
{: .notice--info}

:memo: 본 포스트는 macOS/Linux 기준이다. Windows는 Git Credential Manager(GCM)가 기본이라 helper 이름은 다르지만 개념은 동일하다.
{: .notice--warning}

---

# [01] 왜 멀티 계정 운영이 필요한가

git 자체는 자격증명을 저장하지 않는다. **credential helper** 라는 외부 프로그램에 위임한다. helper는 OS keyring, 평문 파일, 또는 GitHub CLI(`gh`) 같은 외부 도구일 수 있다.

`gh` 를 helper로 쓰면 멀티 계정 관리가 단 한 줄로 끝난다. 그 한 줄이 **`gh auth switch`** 다.

---

# [02] credential helper의 동작 원리

`git push` 가 일어날 때의 흐름:

<pre class="mermaid">
flowchart LR
    A["git push"] --> B{"remote URL이<br/>HTTPS인가?"}
    B -->|Yes| C["helper에게<br/>자격증명 요청"]
    C --> D["helper 응답<br/>username + PAT"]
    D --> E["Basic Auth 헤더로<br/>HTTPS 전송"]
    E --> F{"GitHub<br/>권한 검증"}
    F -->|OK| G["push 성공"]
    F -->|NG| H["403 denied"]

    style G fill:#e8f5e9,stroke:#2e7d32
    style H fill:#ffcccc,stroke:#c62828
</pre>

대표 helper:

| Helper | 저장 위치 | 특징 |
|--------|-----------|------|
| `store` | `~/.git-credentials` 평문 | 가장 단순, 보안 약함 |
| `cache` | 메모리 (TTL 15분 기본) | 일시적, 비휘발성 X |
| `manager` (GCM) | OS keyring | Windows 표준 |
| `osxkeychain` | macOS Keychain | macOS 기본 |
| `libsecret` | GNOME keyring | Linux 데스크톱 |
| `!gh auth git-credential` | `gh` 가 동적으로 제공 | **멀티 계정 native** |

`gh` helper의 특별한 점은, 자격증명을 자체 보관하지 않고 **활성 계정(active account)** 의 OAuth 토큰을 그때그때 넘겨준다는 것이다. 즉 `gh auth switch` 한 줄이면 git push의 인증 주체가 바뀐다.

---

# [03] 내 시스템 helper 확인

```bash
git config --get credential.https://github.com.helper
```

출력 예:

```
!/usr/bin/gh auth git-credential
```

이 출력이 보이면 `gh` 가 git 자격증명을 관장하고 있다. 이제부터 `gh` 의 활성 계정 = git push 계정이다.

:bulb: 출력이 비어 있거나 `store`, `osxkeychain` 등이 보이면 아직 `gh` 가 helper로 등록되지 않은 상태다. 아래 절차에서 `gh auth setup-git` 으로 등록할 수 있다.
{: .notice--info}

---

# [04] 두 번째 계정 추가하기

## 4-1. PAT 발급 (Fine-grained 권장)

새로 추가할 계정으로 GitHub 로그인 → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate**.

권장 권한:

- **Repository access**: 사용할 저장소만 선택 (전체 X)
- **Permissions**: Contents = R/W, Workflows = R/W

:warning: 토큰은 발급 직후 **단 한 번만 노출**된다. 즉시 안전한 곳(비밀번호 관리자)에 복사.
{: .notice--warning}

## 4-2. `gh auth login`

```bash
gh auth login
```

대화형 흐름:

| 질문 | 선택 |
|------|------|
| Where do you use GitHub? | **GitHub.com** |
| Preferred protocol for Git operations? | **HTTPS** |
| Authenticate Git with your GitHub credentials? | **Yes** |
| How would you like to authenticate? | **Paste an authentication token** |
| Paste your authentication token | 발급한 PAT 붙여넣기 |

성공하면 `Logged in as <username>` 이 출력된다.

## 4-3. 등록 결과 확인

```bash
gh auth status
```

```
github.com
  ✓ Logged in to github.com account work-bot
    Active account: true
  ✓ Logged in to github.com account personal-acct
```

`Active account: true` 가 붙은 쪽이 git push 시 사용된다.

---

# [05] 활성 계정 전환 — `gh auth switch`

```bash
# 두 번째 계정으로 전환
gh auth switch -u personal-acct

# 결과 확인
gh auth status | grep -A1 "Active account"

# 이제 모든 git push가 personal-acct 로 나간다
git push
```

:warning: `gh auth switch` 는 **머신 전역**에 적용된다. 저장소·디렉토리별 분리가 아니다. 다른 작업 디렉토리에서도 영향을 받으니, 작업 시작 전에 `gh auth status` 로 활성 계정을 한 번 확인하는 습관을 들이자.
{: .notice--warning}

---

# [06] 실전 시나리오 — 잘못된 계정으로 push 하려 할 때

```
remote: Permission to org-a/repo.git denied to personal-acct.
fatal: 'https://github.com/org-a/repo.git/'에 접근할 수 없습니다: 403
```

이 에러는 명확한 신호다 — push 대상 저장소의 권한 소유자와 활성 계정이 일치하지 않는다.

복구 절차:

```bash
# 1. 현재 활성 계정 확인
gh auth status | grep "Active account"

# 2. 필요한 계정으로 전환
gh auth switch -u <correct-account>

# 3. 재push
git push
```

---

# [07] 검증 명령어 모음

작업 도중 의심스러우면 다음 세 줄로 즉시 진단할 수 있다.

```bash
# helper 확인
git config --list | grep credential

# gh 등록 계정 + 활성 계정
gh auth status

# git이 실제로 받는 자격증명 시뮬레이션 (가장 강력함)
echo -e "protocol=https\nhost=github.com\n" | gh auth git-credential get
```

마지막 명령은 git이 push 시 받게 되는 username/password를 콘솔에 출력해준다. 디버깅에 매우 유용 — 활성 계정 전환이 제대로 반영됐는지 한 번에 검증된다.

---

# [08] 함정 5가지

## 8-1. switch 했는데도 여전히 옛 계정으로 push됨

원인은 대부분 **remote URL에 username이 박혀 있는 경우**:

```bash
git remote -v
# origin  https://old-user@github.com/...
```

URL의 username은 helper보다 우선된다. 다음과 같이 정리:

```bash
git remote set-url origin https://github.com/<owner>/<repo>.git
```

## 8-2. PAT 만료

PAT는 만료기한이 있다. push 시 401이 뜨면 가장 먼저 의심해야 할 부분.

```bash
# 갱신
gh auth refresh -h github.com

# 또는 재로그인
gh auth login
```

## 8-3. 두 계정을 **동시에** 사용해야 한다

`gh` 의 active는 1개뿐이다. 저장소별로 다른 계정이 필요하면:

| 방법 | 설명 | 추천도 |
|------|------|--------|
| **A. 저장소별 helper 오버라이드** | `git config --local credential.helper` 로 다른 helper 지정 | ★★ |
| **B. SSH + `~/.ssh/config` Host alias** | 호스트별로 다른 SSH 키 매핑 | **★★★** |
| **C. PAT를 remote URL에 직접 박아두기** | 편하지만 평문 노출 | ★ (비추) |

대부분의 경우 SSH alias가 가장 깔끔하다.

## 8-4. macOS Keychain과 `gh` 가 충돌

macOS는 `osxkeychain` helper가 자동 등록될 수 있다. `gh` 와 둘 다 활성화되면 우선순위가 불명확해진다.

```bash
# 충돌 정리
git config --global --unset credential.helper
gh auth setup-git
```

## 8-5. private fork 에 push 안 됨

PAT scope이 부족하거나 Fine-grained PAT의 Repository access에 fork가 빠진 경우. PAT 설정 화면에서 해당 fork를 access list에 추가해야 한다.

---

# [09] 정리 한 장

```
git push 인증의 본질
  └─ helper가 어떤 자격증명을 반환하는가

gh를 helper로 쓰면
  └─ 99%가 gh 명령어로 끝난다
       ├─ 추가:    gh auth login
       ├─ 전환:    gh auth switch -u <user>
       ├─ 확인:    gh auth status
       └─ 재발급:  gh auth refresh

함정 1순위
  └─ remote URL의 username이 helper보다 우선
       → git remote set-url 로 정리

머신 전역 vs 저장소 단위
  ├─ 머신 전역:    gh auth switch
  └─ 저장소 단위:  SSH alias / 로컬 helper 오버라이드
```

:star: `gh auth switch` 는 한 번 익혀두면 GitHub 멀티 계정 운영의 심리적 부담을 거의 0으로 만들어준다. 작업 시작 전에 `gh auth status` 로 활성 계정을 한 번 확인하는 30초 습관 — 이것만으로 403 에러의 90%가 사라진다.
{: .notice--info}
