---
title: "GitHub 다중 계정 환경 구축 완전 가이드 — 4가지 방법 비교"
description: "한 머신에서 여러 GitHub 계정을 충돌 없이 운영하는 4가지 방법을 단계별로 정리. includeIf 기반 commit 신원 분리, gh helper, HTTPS+username, PAT 임베드, SSH 별칭까지 장단점 비교와 상황별 추천 포함"
excerpt: "includeIf로 author를 분리하고 SSH 별칭으로 인증을 분리하면 cd만으로 계정이 자동 전환된다. 4가지 방법 단계별 가이드와 비교표"
date: 2026-05-27
categories: Git
tags: [GitHub, Git, multi-account, includeIf, gitconfig, SSH, ssh-config, credential-helper, PAT, Personal-Access-Token, gh-cli, gh-auth-setup-git, HTTPS, identity, commit-author, WSL]
ref: github-multi-account-setup-guide
---

:bulb: 개인 계정과 회사 계정, 혹은 두 개 이상의 GitHub 계정을 같은 머신에서 사용하는 상황은 흔하다. git은 기본적으로 호스트(`github.com`) 단위로 자격증명을 저장하기 때문에, 설정 없이 두 계정을 오가면 contribution이 엉뚱하게 잡히거나 무작위 `Permission denied` 가 발생한다. 이 글은 **commit 신원(author)** 과 **인증(authentication)** 을 분리해서 다중 계정 환경을 안정적으로 구축하는 4가지 방법을 정리한다.
{: .notice--info}

:memo: 본 포스트는 macOS/Linux/WSL 기준이다. 사전 작업(`includeIf`)은 모든 방법과 호환되며, 인증 방법(A~D)은 상황에 따라 한 가지만 선택하면 된다.
{: .notice--warning}

---

# [01] 문제의 본질 — author와 auth는 다르다

다중 계정 운영에서 두 가지 축을 분리해서 봐야 한다.

| 축 | 의미 | 어디서 결정되는가 |
|----|------|------------------|
| **commit author** | 커밋에 박히는 이름/이메일 | `git config user.name`, `user.email` |
| **인증(auth)** | push 시 어떤 자격증명을 보내는가 | credential helper, SSH key, URL |

이 둘은 **완전히 독립적**이다. author가 personal인데 auth가 company일 수도 있고, 그 반대도 가능하다. 다중 계정의 혼란은 보통 이 둘을 한 덩어리로 생각하는 데서 시작된다.

---

# [02] 사전 작업 — 폴더별 commit author 자동 분리

인증 방법과 무관하게, **commit author는 폴더 단위로 자동 분리**해두는 것이 가장 깔끔하다. git 2.13+의 `includeIf` 기능을 쓴다.

## 2-1. 폴더 구조 정의

```bash
~/work/
├── personal/   # 개인 계정용 저장소
└── company/    # 회사 계정용 저장소
```

## 2-2. 전역 `~/.gitconfig` 설정

```ini
[includeIf "gitdir:~/work/personal/"]
  path = ~/.gitconfig-personal

[includeIf "gitdir:~/work/company/"]
  path = ~/.gitconfig-company
```

:warning: `gitdir:` 경로 끝에 슬래시(`/`)를 반드시 붙여야 한다. 안 붙이면 매칭이 동작하지 않는다.
{: .notice--warning}

## 2-3. 계정별 gitconfig 파일

```ini
# ~/.gitconfig-personal
[user]
  name = personal-username
  email = personal@users.noreply.github.com
```

```ini
# ~/.gitconfig-company
[user]
  name = company-username
  email = company@users.noreply.github.com
```

## 2-4. 동작 확인

```bash
cd ~/work/personal/some-repo
git config user.email
# → personal@users.noreply.github.com

cd ~/work/company/some-repo
git config user.email
# → company@users.noreply.github.com
```

이 설정만으로 commit author는 폴더 위치에 따라 자동 전환된다. 이제 남은 건 인증 분리다.

---

# [03] 인증 분리 4가지 방법 — 의사결정 흐름

<pre class="mermaid">
flowchart TD
    A["다중 계정 인증 분리"] --> B{"gh CLI를<br/>매일 쓰는가?"}
    B -->|Yes| C["방법 A<br/>gh helper"]
    B -->|No| D{"장기 운영 머신인가?"}
    D -->|Yes| E["방법 D<br/>SSH 별칭"]
    D -->|No| F{"PAT 평문 저장 OK?"}
    F -->|No| G["방법 B<br/>HTTPS+username"]
    F -->|Yes / CI 일회성| H["방법 C<br/>URL+토큰"]

    style C fill:#fff3e0,stroke:#ef6c00
    style E fill:#e8f5e9,stroke:#2e7d32
    style G fill:#e3f2fd,stroke:#1565c0
    style H fill:#ffcccc,stroke:#c62828
</pre>

---

# [04] 방법 A — `gh` CLI를 credential helper로 사용

GitHub CLI를 이미 쓰는 사용자에게 가장 간단한 방법이다.

## 4-1. 두 계정 모두 로그인

```bash
gh auth login    # personal 계정 로그인
gh auth login    # company 계정 로그인 (다시 실행)
```

```bash
gh auth status
# github.com
#   ✓ Logged in to github.com account personal-username
#   ✓ Logged in to github.com account company-username
```

## 4-2. `gh`를 git credential helper로 등록

```bash
gh auth setup-git
```

`~/.gitconfig` 에 다음이 추가된다:

```ini
[credential "https://github.com"]
  helper = !/usr/bin/gh auth git-credential
```

## 4-3. 계정 전환

```bash
gh auth switch --user personal-username
# 이후 모든 git push는 personal 계정으로

gh auth switch --user company-username
# 이후 모든 git push는 company 계정으로
```

:warning: `gh auth switch` 는 **머신 전역**에 적용된다. 저장소·디렉토리별 분리가 아니다.
{: .notice--warning}

---

# [05] 방법 B — HTTPS URL에 username 박기 + credential helper

`gh` CLI 없이 순수 git만으로 분리하는 방법.

## 5-1. credential helper 활성화

```bash
# Linux/WSL — 평문 저장
git config --global credential.helper store

# macOS — Keychain 사용
git config --global credential.helper osxkeychain

# Linux — libsecret (gnome-keyring 기반, 더 안전)
git config --global credential.helper libsecret
```

## 5-2. 각 계정의 PAT 발급

GitHub 웹 → `Settings → Developer settings → Personal access tokens → Tokens (classic)` 에서 각 계정마다 `repo`, `workflow` 권한으로 토큰을 발급.

## 5-3. remote URL에 username 박기

```bash
# personal 계정 저장소
git remote set-url origin https://personal-username@github.com/personal-username/repo.git

# company 계정 저장소
git remote set-url origin https://company-username@github.com/company-username/repo.git
```

## 5-4. 최초 push 시 PAT 입력

```bash
git push
# Username: (자동 입력됨)
# Password: <PAT 붙여넣기>
```

이후 credential helper가 **username별로 분리 저장**해주기 때문에 두 계정의 토큰이 충돌하지 않는다.

:warning: WSL에서 `wincred`(Windows credential manager)가 활성화돼 있으면 username 분리가 동작하지 않을 수 있다. `git config --global --unset credential.helper` 후 위 helper 중 하나를 명시적으로 지정하자.
{: .notice--warning}

---

# [06] 방법 C — PAT를 URL에 직접 삽입

helper조차 쓰기 싫을 때의 최후 수단.

## 6-1. PAT 발급

방법 B의 5-2와 동일.

## 6-2. remote URL에 토큰 박기

```bash
git remote set-url origin https://personal-username:ghp_xxxxxxxxxxxxxxxxxxxx@github.com/personal-username/repo.git
```

## 6-3. 사용

이후 `git push` / `pull` 은 별도 인증 없이 동작한다.

:warning: **`.git/config` 에 토큰이 평문으로 저장된다.** 디스크 암호화가 없는 환경, 백업 대상에 포함되는 경로, 공유 머신에서는 절대 사용하지 말 것. CI 환경변수로 주입하는 경우가 아니라면 권장하지 않는다.
{: .notice--danger}

---

# [07] 방법 D — SSH 키 + 호스트 별칭 (장기 운영 추천)

장기 운영에 가장 안정적인 방법.

## 7-1. 계정별 SSH 키 생성

```bash
ssh-keygen -t ed25519 -C "personal@github" -f ~/.ssh/id_ed25519_personal
ssh-keygen -t ed25519 -C "company@github"  -f ~/.ssh/id_ed25519_company
```

## 7-2. 공개키를 각 GitHub 계정에 등록

```bash
gh auth switch --user personal-username
gh ssh-key add ~/.ssh/id_ed25519_personal.pub --title "$(hostname)-personal"

gh auth switch --user company-username
gh ssh-key add ~/.ssh/id_ed25519_company.pub --title "$(hostname)-company"
```

수동 등록은 `Settings → SSH and GPG keys → New SSH key`.

## 7-3. `~/.ssh/config`에 호스트 별칭 정의

```ssh-config
Host github.com-personal
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_personal
  IdentitiesOnly yes

Host github.com-company
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_company
  IdentitiesOnly yes
```

:warning: `IdentitiesOnly yes` 는 반드시 포함. 빠뜨리면 ssh-agent의 첫 키로 시도해 잘못된 계정으로 인증된다.
{: .notice--warning}

## 7-4. 권한 설정

```bash
chmod 600 ~/.ssh/config ~/.ssh/id_ed25519_personal ~/.ssh/id_ed25519_company
chmod 644 ~/.ssh/id_ed25519_personal.pub ~/.ssh/id_ed25519_company.pub
```

## 7-5. 연결 테스트

```bash
ssh -T git@github.com-personal
# → Hi personal-username! You've successfully authenticated...

ssh -T git@github.com-company
# → Hi company-username! ...
```

## 7-6. remote URL에 별칭 사용

```bash
git clone git@github.com-personal:personal-username/repo.git
git clone git@github.com-company:company-username/repo.git

# 기존 저장소라면
git remote set-url origin git@github.com-personal:personal-username/repo.git
```

---

# [08] 4가지 방법 비교표

| 항목 | 방법 A (`gh` helper) | 방법 B (URL+username) | 방법 C (URL+토큰) | 방법 D (SSH 별칭) |
|------|---------------------|----------------------|-------------------|-------------------|
| **초기 설정 난이도** | ★☆☆☆☆ (명령 1개) | ★★☆☆☆ | ★☆☆☆☆ | ★★★☆☆ |
| **장기 유지 비용** | 중 (토큰 갱신 필요) | 중 (PAT 만료마다 재입력) | 높음 (PAT 만료 시 URL 수정) | **낮음 (영구)** |
| **계정 전환 방식** | `gh auth switch` | remote URL 자동 | remote URL 자동 | remote URL 자동 |
| **저장소별 자동 분리** | ✗ (활성 계정 따라감) | ✓ | ✓ | ✓ |
| **자격증명 노출 위험** | 낮음 (OAuth 토큰) | 중 (helper 저장 위치 의존) | **높음 (평문)** | **매우 낮음 (private key 미전송)** |
| **`gh` CLI 의존성** | 필수 | 없음 | 없음 | 등록 시에만 |
| **WSL helper 충돌** | 없음 | 발생 가능 | 없음 | 없음 |
| **CI/서버 이식성** | `gh` 필요 | helper 재설정 필요 | URL만 복사 | 키 파일 복사 |
| **공개키 등록 필요** | ✗ | ✗ | ✗ | ✓ (한 번) |
| **토큰/키 만료** | ~1년 (OAuth) | 최대 1년 (PAT) | 최대 1년 (PAT) | **무기한** |
| **2FA/SSO 호환성** | ✓ | ✓ (PAT 인가 필요) | ✓ (PAT 인가 필요) | ✓ |
| **권장 사용처** | gh 주력 사용자 | 가벼운 다중 계정 | CI 일회성 | **장기 운영 머신** |

---

# [09] 상황별 최종 추천

## 🥇 메인 개발 머신 — 방법 D (SSH) + 사전 작업(`includeIf`)

장기적으로 가장 마찰이 적다. 초기 등록 비용을 한 번 지불하면 이후 **토큰 갱신·인증 재설정·credential helper 충돌**에서 자유롭다. 폴더별 `includeIf` 까지 함께 적용하면 commit author와 인증이 모두 자동으로 분리된다.

## 🥈 `gh` CLI를 매일 쓰는 사용자 — 방법 A

이미 `gh pr create`, `gh issue list` 등이 손에 익었다면, `gh auth setup-git` 하나로 git push까지 통합된다. 단, **활성 계정 전환을 의식해야 한다는 정신적 부담**은 감안하자. 저장소별로 어떤 계정을 써야 하는지 헷갈리기 시작하면 D로 이전하는 게 답이다.

## 🥉 가볍게 가끔 사용 — 방법 B

다중 계정 사용 빈도가 낮고 SSH 등록조차 번거롭다면 B가 합리적이다. WSL에서는 credential helper 종류를 명시적으로 지정해 wincred와의 충돌을 먼저 차단하자.

## 🚫 피해야 할 조합

- **방법 C를 일상 머신에서 사용** — 토큰이 평문으로 디스크에 남는다. 백업·실수로 push될 위험이 너무 크다.
- **`.netrc` 사용** — 호스트당 자격증명 1개만 인식해 다중 계정에 부적합.
- **A + D 혼용** — 같은 머신에서 credential helper(A)와 SSH(D)를 동시에 켜두면 어떤 인증이 적용됐는지 추적이 어렵다. 하나의 방식으로 통일하자.

---

# [10] 정리 한 장

```
다중 계정 = author 분리 + auth 분리

author 분리
  └─ ~/.gitconfig + includeIf
       └─ 폴더 단위 자동 전환 (모든 방법과 호환)

auth 분리 4가지
  ├─ A. gh helper            → gh 주력 사용자 단기 운영
  ├─ B. HTTPS + username     → 가벼운 다중 계정
  ├─ C. URL + 토큰 평문      → CI 일회성, 일상 비추
  └─ D. SSH + Host alias     → 장기 메인 머신 ⭐

최종 공식
  includeIf (author) + 방법 D (auth) = cd 만으로 계정 자동 전환
```

:star: 다중 계정 설정은 한 번 제대로 해두면 이후 몇 년간 신경 쓸 일이 없다. **"지금 한 번 등록하기 귀찮다"의 비용은 항상 "분기마다 토큰 갱신·인증 디버깅"의 누적 비용보다 작다.** 메인 머신이라면 30분 투자해서 방법 D로 가는 것을 권한다.
{: .notice--info}
