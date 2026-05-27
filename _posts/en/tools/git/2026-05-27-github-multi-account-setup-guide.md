---
title: "Complete Guide to GitHub Multi-Account Setup — 4 Methods Compared"
description: "Step-by-step guide for running multiple GitHub accounts on one machine without conflicts. Covers includeIf-based commit identity separation, gh helper, HTTPS+username, PAT embedding, and SSH host aliases — with comparison and recommendations per scenario"
excerpt: "Separate author with includeIf, separate auth with SSH host aliases — and accounts switch automatically with cd. Four methods compared step by step"
date: 2026-05-27
categories: Git
tags: [GitHub, Git, multi-account, includeIf, gitconfig, SSH, ssh-config, credential-helper, PAT, Personal-Access-Token, gh-cli, gh-auth-setup-git, HTTPS, identity, commit-author, WSL]
ref: github-multi-account-setup-guide
---

:bulb: Running personal and work accounts (or two or more GitHub accounts) on the same machine is common. Since git stores credentials per host (`github.com`) by default, switching accounts without configuration causes contributions to land on the wrong account or triggers random `Permission denied` errors. This guide covers 4 methods to build a stable multi-account environment by **separating commit identity (author)** from **authentication (auth)**.
{: .notice--info}

:memo: This post targets macOS/Linux/WSL. The prerequisite step (`includeIf`) is compatible with all methods. For authentication, pick just one of methods A through D depending on your situation.
{: .notice--warning}

---

# [01] The Core Problem — Author ≠ Auth

Multi-account operations require thinking of two independent axes.

| Axis | Meaning | Where it's decided |
|------|---------|-------------------|
| **commit author** | Name/email stamped onto commits | `git config user.name`, `user.email` |
| **authentication** | Which credentials are sent at push | credential helper, SSH key, URL |

These are **completely independent**. The author can be personal while auth is company — or vice versa. Most multi-account confusion comes from conflating them.

---

# [02] Prerequisite — Folder-Based Auto Author Separation

Regardless of which auth method you pick, the cleanest baseline is **auto-switching commit author by folder**. Use git 2.13+'s `includeIf` feature.

## 2-1. Define Folder Structure

```bash
~/work/
├── personal/   # personal account repos
└── company/    # company account repos
```

## 2-2. Configure Global `~/.gitconfig`

```ini
[includeIf "gitdir:~/work/personal/"]
  path = ~/.gitconfig-personal

[includeIf "gitdir:~/work/company/"]
  path = ~/.gitconfig-company
```

:warning: The `gitdir:` path **must** end with a trailing slash (`/`). Without it, the match silently fails.
{: .notice--warning}

## 2-3. Per-Account gitconfig Files

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

## 2-4. Verify

```bash
cd ~/work/personal/some-repo
git config user.email
# → personal@users.noreply.github.com

cd ~/work/company/some-repo
git config user.email
# → company@users.noreply.github.com
```

With this alone, commit author auto-switches based on folder location. Now we just need to handle auth.

---

# [03] Four Auth Separation Methods — Decision Flow

<pre class="mermaid">
flowchart TD
    A["Multi-account auth"] --> B{"Use gh CLI<br/>daily?"}
    B -->|Yes| C["Method A<br/>gh helper"]
    B -->|No| D{"Long-term machine?"}
    D -->|Yes| E["Method D<br/>SSH alias"]
    D -->|No| F{"OK with plaintext PAT?"}
    F -->|No| G["Method B<br/>HTTPS+username"]
    F -->|Yes / one-shot CI| H["Method C<br/>URL+token"]

    style C fill:#fff3e0,stroke:#ef6c00
    style E fill:#e8f5e9,stroke:#2e7d32
    style G fill:#e3f2fd,stroke:#1565c0
    style H fill:#ffcccc,stroke:#c62828
</pre>

---

# [04] Method A — Use `gh` CLI as Credential Helper

The simplest approach if you already have GitHub CLI installed.

## 4-1. Log In to Both Accounts

```bash
gh auth login    # personal account
gh auth login    # company account (run again)
```

```bash
gh auth status
# github.com
#   ✓ Logged in to github.com account personal-username
#   ✓ Logged in to github.com account company-username
```

## 4-2. Register `gh` as Git Credential Helper

```bash
gh auth setup-git
```

This adds the following to `~/.gitconfig`:

```ini
[credential "https://github.com"]
  helper = !/usr/bin/gh auth git-credential
```

## 4-3. Switch Accounts

```bash
gh auth switch --user personal-username
# All subsequent git push goes as personal

gh auth switch --user company-username
# All subsequent git push goes as company
```

:warning: `gh auth switch` applies **machine-wide**, not per-repo or per-directory.
{: .notice--warning}

---

# [05] Method B — Embed Username in HTTPS URL + Credential Helper

Pure git, no `gh` CLI.

## 5-1. Enable a Credential Helper

```bash
# Linux/WSL — plaintext store
git config --global credential.helper store

# macOS — Keychain
git config --global credential.helper osxkeychain

# Linux — libsecret (gnome-keyring backed, more secure)
git config --global credential.helper libsecret
```

## 5-2. Issue a PAT per Account

GitHub web → `Settings → Developer settings → Personal access tokens → Tokens (classic)` → issue a token with `repo`, `workflow` scope for each account.

## 5-3. Bake Username into the Remote URL

```bash
# personal account repo
git remote set-url origin https://personal-username@github.com/personal-username/repo.git

# company account repo
git remote set-url origin https://company-username@github.com/company-username/repo.git
```

## 5-4. Enter PAT on First Push

```bash
git push
# Username: (auto-filled)
# Password: <paste PAT>
```

After this, the credential helper **stores credentials per-username**, so the two accounts' tokens don't collide.

:warning: In WSL with `wincred` (Windows credential manager) active, per-username separation may not work. Run `git config --global --unset credential.helper` first, then explicitly pick one of the helpers above.
{: .notice--warning}

---

# [06] Method C — Embed PAT Directly in URL

A last resort when you refuse to use any helper.

## 6-1. Issue PAT

Same as 5-2.

## 6-2. Bake the Token into the Remote URL

```bash
git remote set-url origin https://personal-username:ghp_xxxxxxxxxxxxxxxxxxxx@github.com/personal-username/repo.git
```

## 6-3. Use

`git push` / `pull` works without any further authentication.

:warning: **The token is stored in plaintext in `.git/config`.** Never use this on machines without disk encryption, in paths included in backups, or on shared machines. Not recommended unless the PAT is injected via CI env vars.
{: .notice--danger}

---

# [07] Method D — SSH Keys + Host Aliases (Recommended for Long-Term)

The most stable for long-term operations.

## 7-1. Generate One SSH Key per Account

```bash
ssh-keygen -t ed25519 -C "personal@github" -f ~/.ssh/id_ed25519_personal
ssh-keygen -t ed25519 -C "company@github"  -f ~/.ssh/id_ed25519_company
```

## 7-2. Register Public Keys with Each GitHub Account

```bash
gh auth switch --user personal-username
gh ssh-key add ~/.ssh/id_ed25519_personal.pub --title "$(hostname)-personal"

gh auth switch --user company-username
gh ssh-key add ~/.ssh/id_ed25519_company.pub --title "$(hostname)-company"
```

Manual registration: `Settings → SSH and GPG keys → New SSH key`.

## 7-3. Define Host Aliases in `~/.ssh/config`

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

:warning: `IdentitiesOnly yes` is **required**. Without it, SSH tries the first key from `ssh-agent` and authenticates as the wrong account.
{: .notice--warning}

## 7-4. Set Permissions

```bash
chmod 600 ~/.ssh/config ~/.ssh/id_ed25519_personal ~/.ssh/id_ed25519_company
chmod 644 ~/.ssh/id_ed25519_personal.pub ~/.ssh/id_ed25519_company.pub
```

## 7-5. Test Connections

```bash
ssh -T git@github.com-personal
# → Hi personal-username! You've successfully authenticated...

ssh -T git@github.com-company
# → Hi company-username! ...
```

## 7-6. Use the Alias in Remote URLs

```bash
git clone git@github.com-personal:personal-username/repo.git
git clone git@github.com-company:company-username/repo.git

# For an existing repo
git remote set-url origin git@github.com-personal:personal-username/repo.git
```

---

# [08] Comparison Table

| Item | A (`gh` helper) | B (URL+username) | C (URL+token) | D (SSH alias) |
|------|----------------|------------------|---------------|---------------|
| **Initial setup difficulty** | ★☆☆☆☆ (1 command) | ★★☆☆☆ | ★☆☆☆☆ | ★★★☆☆ |
| **Long-term maintenance** | Medium (token renewal) | Medium (PAT re-entry at expiry) | High (URL edit on expiry) | **Low (permanent)** |
| **Account switching** | `gh auth switch` | Auto via remote URL | Auto via remote URL | Auto via remote URL |
| **Per-repo auto-separation** | ✗ (follows active) | ✓ | ✓ | ✓ |
| **Credential exposure risk** | Low (OAuth token) | Medium (helper store) | **High (plaintext)** | **Very low (private key never leaves)** |
| **`gh` CLI dependency** | Required | None | None | Only at setup |
| **WSL helper conflict** | None | Possible | None | None |
| **CI/server portability** | Needs `gh` | Helper reconfig | URL copy only | Copy key files |
| **Public key registration** | ✗ | ✗ | ✗ | ✓ (once) |
| **Token/key expiry** | ~1 year (OAuth) | Up to 1 year (PAT) | Up to 1 year (PAT) | **Indefinite** |
| **2FA/SSO compatibility** | ✓ | ✓ (PAT must be authorized) | ✓ (PAT must be authorized) | ✓ |
| **Recommended use** | `gh`-centric users | Light multi-account | One-shot CI | **Long-term primary machine** |

---

# [09] Recommendations by Scenario

## 🥇 Primary Development Machine — Method D (SSH) + Prerequisite (`includeIf`)

The least friction long-term. Pay the setup cost once and you're free from **token renewals, auth re-configuration, and credential helper conflicts**. Combine with folder-based `includeIf` and both commit author *and* auth separate automatically.

## 🥈 Daily `gh` CLI Users — Method A

If `gh pr create`, `gh issue list` are already in your muscle memory, `gh auth setup-git` unifies git push with that flow. The cost: **mental overhead of remembering which account is active**. Once you start confusing which account a repo needs, migrate to D.

## 🥉 Occasional Light Use — Method B

If multi-account usage is infrequent and SSH setup feels heavy, B is reasonable. On WSL, explicitly pin the credential helper first to block wincred conflicts.

## 🚫 Combinations to Avoid

- **Method C on a daily machine** — tokens sit in plaintext on disk. Risk of leaks via backups or accidental pushes is too high.
- **Using `.netrc`** — only recognizes one credential per host, unsuitable for multi-account.
- **A + D simultaneously** — running credential helper (A) and SSH (D) together on the same machine makes it hard to trace which auth path was used. Standardize on one.

---

# [10] One-Page Summary

```
Multi-account = author separation + auth separation

Author separation
  └─ ~/.gitconfig + includeIf
       └─ Auto-switch per folder (compatible with all methods)

Auth separation — 4 options
  ├─ A. gh helper            → gh-centric users, short-term
  ├─ B. HTTPS + username     → light multi-account
  ├─ C. URL + plaintext PAT  → one-shot CI; avoid daily
  └─ D. SSH + Host alias     → long-term primary machine ⭐

Final formula
  includeIf (author) + Method D (auth)
     = cd alone switches everything
```

:star: Multi-account configuration is a one-time investment that lasts years. **The cost of "I don't feel like registering this once" is always smaller than the accumulated cost of "token renewal and auth debugging every quarter."** For your primary machine, spend 30 minutes and go with Method D.
{: .notice--info}
