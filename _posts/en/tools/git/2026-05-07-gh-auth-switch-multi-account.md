---
title: "GitHub Multi-Account Switching — Using gh auth switch"
description: "How to manage multiple GitHub accounts on one machine without conflicts. Covers credential helper basics, switching active accounts with gh CLI, verification commands, and 5 real-world pitfalls"
excerpt: "One gh auth switch line changes who your git push goes as. Credential helper internals, PAT issuance, account switching, and real-world pitfalls in one guide"
date: 2026-05-07
categories: Git
tags: [GitHub, gh-cli, gh-auth-switch, gh-auth-login, Git, Authentication, credential-helper, PAT, Personal-Access-Token, multi-account, OAuth, HTTPS, GCM, osxkeychain, libsecret]
ref: gh-auth-switch-multi-account
---

:bulb: Work account, personal account, organization bot account — handling multiple GitHub accounts on one machine is surprisingly common. The question is **whose credentials git sends** when you `git push`. **Using `gh` CLI as your credential helper means one `gh auth switch` line changes the push subject.** This guide covers the principles and pitfalls.
{: .notice--info}

:memo: This post targets macOS/Linux. On Windows, Git Credential Manager (GCM) is the default — helper names differ, but the concept is the same.
{: .notice--warning}

---

# [01] Why Multi-Account Operations Matter

Git itself doesn't store credentials. It delegates to an external program called a **credential helper**. Helpers can be the OS keyring, a plaintext file, or an external tool like GitHub CLI (`gh`).

Using `gh` as a helper makes multi-account management a one-liner. That one line is **`gh auth switch`**.

---

# [02] How Credential Helpers Work

What happens during `git push`:

<pre class="mermaid">
flowchart LR
    A["git push"] --> B{"remote URL<br/>is HTTPS?"}
    B -->|Yes| C["Ask helper for<br/>credentials"]
    C --> D["Helper responds<br/>username + PAT"]
    D --> E["Send via<br/>Basic Auth header"]
    E --> F{"GitHub<br/>permission check"}
    F -->|OK| G["push succeeds"]
    F -->|NG| H["403 denied"]

    style G fill:#e8f5e9,stroke:#2e7d32
    style H fill:#ffcccc,stroke:#c62828
</pre>

Common helpers:

| Helper | Storage | Notes |
|--------|---------|-------|
| `store` | `~/.git-credentials` plaintext | Simplest, weakest security |
| `cache` | Memory (15min TTL default) | Temporary, non-persistent |
| `manager` (GCM) | OS keyring | Windows standard |
| `osxkeychain` | macOS Keychain | macOS default |
| `libsecret` | GNOME keyring | Linux desktop |
| `!gh auth git-credential` | `gh` provides dynamically | **Multi-account native** |

What makes `gh` helper special: instead of storing credentials itself, it **dynamically provides the OAuth token of the active account**. So `gh auth switch` changes who your git push goes as.

---

# [03] Check Your System's Helper

```bash
git config --get credential.https://github.com.helper
```

Sample output:

```
!/usr/bin/gh auth git-credential
```

If you see this, `gh` is managing your git credentials. From here on, `gh`'s active account = your git push account.

:bulb: If empty or shows `store`, `osxkeychain`, etc., `gh` isn't registered as the helper yet. Register it below with `gh auth setup-git`.
{: .notice--info}

---

# [04] Adding a Second Account

## 4-1. Issue a PAT (Fine-grained Recommended)

Log in as the new account → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate**.

Recommended permissions:

- **Repository access**: Only repos you'll use (not all)
- **Permissions**: Contents = R/W, Workflows = R/W

:warning: The token is shown **only once** right after generation. Copy it immediately to a safe location (password manager).
{: .notice--warning}

## 4-2. `gh auth login`

```bash
gh auth login
```

Interactive flow:

| Question | Choice |
|----------|--------|
| Where do you use GitHub? | **GitHub.com** |
| Preferred protocol for Git operations? | **HTTPS** |
| Authenticate Git with your GitHub credentials? | **Yes** |
| How would you like to authenticate? | **Paste an authentication token** |
| Paste your authentication token | (paste the PAT) |

Success shows `Logged in as <username>`.

## 4-3. Verify Registration

```bash
gh auth status
```

```
github.com
  ✓ Logged in to github.com account work-bot
    Active account: true
  ✓ Logged in to github.com account personal-acct
```

The one with `Active account: true` is used for git push.

---

# [05] Switching Active Account — `gh auth switch`

```bash
# Switch to second account
gh auth switch -u personal-acct

# Verify
gh auth status | grep -A1 "Active account"

# All subsequent git push goes as personal-acct
git push
```

:warning: `gh auth switch` applies **machine-wide**. It's not per-repo or per-directory. Other working directories are affected too — get into the habit of running `gh auth status` to check the active account before starting work.
{: .notice--warning}

---

# [06] Real Scenario — Pushing as Wrong Account

```
remote: Permission to org-a/repo.git denied to personal-acct.
fatal: unable to access 'https://github.com/org-a/repo.git/': 403
```

A clear signal — the active account doesn't match the target repo's owner.

Recovery:

```bash
# 1. Check current active account
gh auth status | grep "Active account"

# 2. Switch to the correct account
gh auth switch -u <correct-account>

# 3. Retry push
git push
```

---

# [07] Verification Commands

When in doubt, diagnose with these three lines:

```bash
# Check helper
git config --list | grep credential

# gh registered accounts + active
gh auth status

# Simulate the credentials git actually receives (most powerful)
echo -e "protocol=https\nhost=github.com\n" | gh auth git-credential get
```

The last command prints the username/password git would receive at push time. Extremely useful for debugging — verifies in one shot whether the account switch took effect.

---

# [08] Five Pitfalls

## 8-1. Switched, but Still Pushes as Old Account

Usually because **username is baked into the remote URL**:

```bash
git remote -v
# origin  https://old-user@github.com/...
```

URL username takes precedence over the helper. Clean it up:

```bash
git remote set-url origin https://github.com/<owner>/<repo>.git
```

## 8-2. PAT Expired

PATs have expiration dates. If push returns 401, suspect this first.

```bash
# Refresh
gh auth refresh -h github.com

# Or re-login
gh auth login
```

## 8-3. Need to Use **Both** Accounts Simultaneously

`gh` has only one active. For per-repo accounts:

| Method | Description | Rating |
|--------|-------------|--------|
| **A. Per-repo helper override** | `git config --local credential.helper` for a different helper | ★★ |
| **B. SSH + `~/.ssh/config` Host alias** | Map different SSH keys per host | **★★★** |
| **C. PAT directly in remote URL** | Convenient but exposed in plaintext | ★ (avoid) |

SSH alias is usually cleanest.

## 8-4. macOS Keychain Conflicts with `gh`

macOS may auto-register `osxkeychain`. With both active, priority is unclear.

```bash
# Resolve conflict
git config --global --unset credential.helper
gh auth setup-git
```

## 8-5. Can't Push to Private Fork

PAT scope insufficient, or Fine-grained PAT's Repository access doesn't include the fork. Add the fork to the access list in PAT settings.

---

# [09] One-Page Summary

```
git push auth essence
  └─ which credentials does the helper return?

Use gh as helper
  └─ 99% ends with gh commands
       ├─ add:      gh auth login
       ├─ switch:   gh auth switch -u <user>
       ├─ check:    gh auth status
       └─ refresh:  gh auth refresh

Top pitfall
  └─ Username in remote URL > helper
       → fix with git remote set-url

Machine-wide vs per-repo
  ├─ Machine-wide:  gh auth switch
  └─ Per-repo:      SSH alias / local helper override
```

:star: `gh auth switch` essentially reduces the cognitive load of GitHub multi-account operations to zero. The 30-second habit of running `gh auth status` before starting work removes 90% of 403 errors.
{: .notice--info}
