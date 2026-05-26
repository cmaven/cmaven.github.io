---
title: "Changing Git Account (User) in a Local Shell Environment"
description: "How to view and change the Git user name and email globally or per-repository, manage multiple accounts with includeIf, and set up SSH config for account switching."
excerpt: "How to change your Git account (user.name, user.email) with git config, manage multiple accounts with includeIf, and use SSH config for seamless account switching."
date: 2022-02-16
last_modified_at: 2026-05-26
categories: Git
tags: [Git, git-config, User, account-switch, user.name, user.email, multi-account, SSH, includeIf]
ref: git-account
---

:bulb: When you use two or more Git accounts on a single machine — for example, a personal GitHub account and a work GitHub/GitLab account — and need to push or pull as a specific identity, this guide covers every approach from a quick one-off override to a fully automated per-directory setup.
{: .notice--info}

# [01] Check Current Git Settings

Before making changes, confirm the active identity.

### Check all config entries

```shell
git config -l
```

*Figure 1. Sample output — `git config -l`*
![git-config check-01](https://user-images.githubusercontent.com/76153041/154203932-08c2ccee-1154-47e5-9de2-c4a89ed00e18.png)

*Figure 1. `git config -l` lists every config key from system, global, and local scopes. Look for `user.name` and `user.email` lines.*

### Check only user name and email

```shell
git config user.name
git config user.email
```

![git-config check-02](https://user-images.githubusercontent.com/76153041/154203935-2d0f7c70-01ff-46df-b9df-a7a8a2c06080.png)

*Figure 2. Querying individual keys returns just the effective value — useful for a quick sanity check before committing.*

Git resolves config in priority order: **local** (`repo/.git/config`) overrides **global** (`~/.gitconfig`) overrides **system** (`/etc/gitconfig`). The `git config -l` output shows which file each value comes from when you add `--show-origin`.

```shell
git config -l --show-origin
```

# [02] Change Git Identity

### Global change — applies to all repositories

Use `--global` to update `~/.gitconfig`. This becomes the default identity for every repo that does not have a local override.

```shell
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

![git-config update](https://user-images.githubusercontent.com/76153041/154203940-6bce8ce9-827d-449a-9b02-7c781b3ce793.png)

*Figure 3. After running the two `--global` commands, `git config user.name` returns the new value immediately.*

### Local change — applies only to the current repository

Run the same commands without `--global` inside the repo directory:

```shell
git config user.name "Work Name"
git config user.email "work@company.com"
```

This writes to `.git/config` in the current repo and overrides the global value for that repo only. Useful when a single machine hosts both personal and work repositories.

### One-off override for a single commit

If you only need to use a different identity once, set the environment variables inline:

```shell
GIT_AUTHOR_NAME="Other Name" GIT_AUTHOR_EMAIL="other@example.com" \
GIT_COMMITTER_NAME="Other Name" GIT_COMMITTER_EMAIL="other@example.com" \
git commit -m "feat: one-off commit as other identity"
```

# [03] Automatic Per-Directory Account Switching with includeIf

When you have all personal repos under `~/personal/` and all work repos under `~/work/`, Git's **`includeIf`** directive can apply the correct identity automatically based on the repository path — no manual switching needed.

### Step 1 — Create separate config files

```shell
# ~/.gitconfig-personal
[user]
    name = Personal Name
    email = personal@gmail.com

# ~/.gitconfig-work
[user]
    name = Work Name
    email = work@company.com
```

### Step 2 — Add includeIf blocks to ~/.gitconfig

```ini
[user]
    name = Personal Name
    email = personal@gmail.com

[includeIf "gitdir:~/work/"]
    path = ~/.gitconfig-work

[includeIf "gitdir:~/personal/"]
    path = ~/.gitconfig-personal
```

When Git detects that the current repository lives under `~/work/`, it loads `~/.gitconfig-work` and its `[user]` section overrides the global default. The match is based on the `.git` directory path, so subdirectories are covered automatically.

| Condition | Config applied |
|---|---|
| Repo is anywhere under `~/work/` | `~/.gitconfig-work` |
| Repo is anywhere under `~/personal/` | `~/.gitconfig-personal` |
| Repo is anywhere else | Global `~/.gitconfig` default |

# [04] SSH Config for Multi-Account Authentication

Changing `user.name` and `user.email` only affects commit authorship — it does not change which SSH key is used to authenticate with the remote. For full account isolation (so pushes go to the correct GitHub/GitLab account), configure SSH aliases.

### Step 1 — Generate separate SSH keys

```shell
ssh-keygen -t ed25519 -C "personal@gmail.com" -f ~/.ssh/id_ed25519_personal
ssh-keygen -t ed25519 -C "work@company.com"   -f ~/.ssh/id_ed25519_work
```

### Step 2 — Add public keys to each Git host account

Copy each `.pub` file content and add it under **Settings → SSH Keys** on GitHub/GitLab for the respective account.

### Step 3 — Configure ~/.ssh/config

```text
Host github-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal

Host github-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_work
```

### Step 4 — Use the alias in remote URLs

```shell
# Personal repo
git remote set-url origin git@github-personal:username/repo.git

# Work repo
git remote set-url origin git@github-work:org/repo.git
```

Git will now use the correct SSH key automatically when pushing or pulling, regardless of the global identity settings.

# [05] Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Commits still show old name/email after `--global` change | Local repo config overrides global | Run `git config user.name` inside the repo — if it shows the old value, remove the local override with `git config --unset user.name` |
| `includeIf` not applying the expected identity | Path condition does not match — trailing slash required | Ensure the path ends with `/`: `gitdir:~/work/` not `gitdir:~/work` |
| Push rejected with "Permission denied (publickey)" | SSH key for target account not loaded | Run `ssh -T git@github-personal` to test the alias; add the key with `ssh-add ~/.ssh/id_ed25519_personal` |
| Author of past commits is wrong | Identity was misconfigured when commits were made | For local branches not yet pushed, use `git rebase` to rewrite; for public commits, coordinate with repo maintainers before rewriting history |
| `git config -l` shows duplicate user.name | Both global and local scopes have a value | The local value wins; decide which scope should own the setting and remove the other with `--unset` |
