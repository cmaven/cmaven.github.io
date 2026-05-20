---
title: "Run Snap Firefox via MobaXterm X11 Forwarding — Fixing 'cannot open display'"
description: "Cause and fix for 'cannot open display localhost:10.0' and 'Unsupported authorisation protocol' errors with MobaXterm X11 forwarding"
excerpt: "Error: cannot open display: localhost:10.0 — Snap Firefox's missing XAUTHORITY is the root cause; fix by setting it explicitly"
date: 2026-04-15
categories: Etc
tags: [MobaXterm, X11, Firefox, Snap, xauth, XAUTHORITY, Ubuntu, cannot-open-display, remote-desktop]
ref: mobaxterm-firefox-x11-forwarding
---

:bulb: Authentication errors and resolution when running Snap Firefox over SSH + X11 forwarding from Windows MobaXterm to an Ubuntu server.
{: .notice--info}

**Environment**: Windows + MobaXterm (X11 proxy) → Ubuntu 22.04 server + Firefox snap 149.0.2

---

# [01] The Problem

After SSH'ing into the Ubuntu server with X11 forwarding enabled in MobaXterm:

```bash
$ firefox &
libpxbackend-1.0.so: cannot open shared object file: No such file or directory
Failed to load module: /home/user/snap/firefox/common/.cache/gio-modules/libgiolibproxy.so
MobaXterm X11 proxy: Unsupported authorisation protocol
Error: cannot open display: localhost:10.0
```

What the errors say:

| Error | Meaning |
|-------|---------|
| `libpxbackend-1.0.so` missing | Snap sandbox library loading issue |
| `Unsupported authorisation protocol` | X11 auth protocol mismatch |
| `cannot open display: localhost:10.0` | Final display connection failure |

---

# [02] Root Cause — DISPLAY vs xauth Mismatch

## 2-1. Check Environment

```bash
$ echo $DISPLAY
localhost:10.0

$ xauth list
myserver/unix:10  MIT-MAGIC-COOKIE-1  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**The core issue:**

| Item | Value | Format |
|------|-------|--------|
| `DISPLAY` | `localhost:10.0` | TCP form |
| `xauth` entry | `myserver/unix:10` | Unix socket form |

MobaXterm's X11 proxy connects via TCP (`localhost:10.0`), but xauth only has a Unix-socket cookie (`/unix:10`). **The two formats don't match.**

## 2-2. Other X11 Apps Work — Why Only Firefox?

```bash
$ xdpyinfo
name of display:    localhost:10.0
version number:    11.0
vendor string:    The X.Org Foundation
...
```

`xdpyinfo` works fine. The X11 server itself isn't the problem.

---

# [03] Real Cause — Snap Sandbox Blocks Environment Variables

## 3-1. Inside the Snap Environment

```bash
$ snap run firefox env | grep -i xauth
XAUTHORITY=
```

**`XAUTHORITY` is empty!** The Snap sandbox didn't inherit the parent environment variables.

More serious:

```bash
$ snap run firefox which xauth
(no output)
```

**There is no `xauth` binary inside Snap.** It can't create or verify the cookie.

## 3-2. The Problem Diagram

```
Regular X11 apps (xdpyinfo etc.)
  → use system xauth → cookie verified → O connection succeeds

Snap Firefox
  → enters Snap sandbox
  → XAUTHORITY empty
  → no xauth binary
  → cookie verification impossible
  → X "Unsupported authorisation protocol"
```

---

# [04] Attempted Fixes

## 4-1. Try 1 — `xauth add` for TCP Cookie

```bash
$ xauth add localhost:10 MIT-MAGIC-COOKIE-1 xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xauth:  unable to write authority file /home/user/.Xauthority
```

xauth refused to add the TCP-form entry.

## 4-2. Try 2 — `xauth generate`

```bash
$ xauth generate :10
xauth:  (null):0:  unable to resolve "SECURITY" extension to get random data
```

Security extension query failed too.

## 4-3. The Real Fix — Set XAUTHORITY Explicitly

Since the root cause is missing `XAUTHORITY` inside the Snap sandbox, **specify it explicitly**.

```bash
$ XAUTHORITY=$HOME/.Xauthority firefox --no-remote &
```

Firefox appears in MobaXterm.

`xhost` for extra permissions also helps:

```bash
$ xhost +local:
access control enabled, only authorized clients can connect
LOCAL:
```

---

# [05] Permanent Setup

Add to `~/.bashrc` so you don't have to type it every time.

```bash
# Append to ~/.bashrc
export XAUTHORITY="$HOME/.Xauthority"
```

```bash
$ source ~/.bashrc
$ firefox --no-remote &
# Now works normally
```

---

# [06] Bonus — Broken Korean Font

If Firefox launches but Korean text shows as boxes (□):

```bash
$ fc-list | grep -i hangul
(almost no output)
```

No Korean font installed.

**Fix:**

```bash
$ sudo apt update
$ sudo apt install fonts-noto-cjk fonts-nanum -y
$ fc-cache -fv
```

Run Firefox again — Korean renders correctly.

---

# [07] Summary

## 7-1. Final Commands

```bash
# One-shot
XAUTHORITY=$HOME/.Xauthority firefox --no-remote &

# Permanent (add to ~/.bashrc)
export XAUTHORITY="$HOME/.Xauthority"
```

## 7-2. Key Lessons

| Lesson | Description |
|--------|-------------|
| **Snap doesn't inherit env vars** | For security, doesn't pass `XAUTHORITY` from parent |
| **Check xauth format mismatch** | Unix socket (`/unix:10`) ≠ TCP (`localhost:10`) |
| **One X11 app working doesn't mean all do** | `xdpyinfo` works but Snap apps may fail due to sandbox |
| **No xauth binary inside Snap** | Provide `XAUTHORITY` path explicitly |
| **Install fonts separately** | `fonts-noto-cjk`, `fonts-nanum` for Korean rendering |

:bulb: This isn't a simple X11 auth issue — it's the **incomplete interaction between the Snap sandbox and remote X11 forwarding**. The non-Snap Firefox package wouldn't have this problem.
{: .notice--info}
