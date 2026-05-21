---
title: "tmux Basics"
description: "Basic usage of the tmux terminal multiplexer — session management, screen splitting, window switching, and key bindings"
excerpt: "A guide to tmux basics: creating/detaching/attaching sessions, splitting screens (panes), and switching windows"
date: 2026-03-06
categories: Linux
tags: [tmux, terminal, session, pane, window, screen-split, terminal-multiplexer, scroll, copy-mode]
ref: tmux-basic
---

:bulb: This post covers the basics of the tmux terminal multiplexer — session management, screen splitting, and key bindings.
{: .notice--info}

# [01] What Is tmux?

tmux (terminal multiplexer) is a tool that lets you **run multiple sessions, windows, and panes simultaneously** within a single terminal.
Sessions persist even if your SSH connection drops, making it especially useful for long-running work on remote servers.

| Concept | Description |
|---|---|
| **Session** | tmux's top-level unit. An independent workspace. Can be named for easy management |
| **Window** | A tab within a session. You can create multiple and switch between them |
| **Pane** | An individual terminal region created by splitting a window |

All tmux shortcuts are entered by first pressing the **Prefix key** (`Ctrl + b`), then the next key.

:bulb: Press `Ctrl + b`, release, then press the next key. They are not pressed simultaneously.
{: .notice--info}

---

# [02] Installation

```shell
# Ubuntu / Debian
sudo apt install tmux

# macOS (Homebrew)
brew install tmux
```

Check version:

```shell
tmux -V
```

**Example output:**

```
tmux 3.3a
```

---

# [03] Creating and Managing Sessions

## 3-1. Creating a New Session

### (A) Without a name

```shell
tmux
```

### (B) With a name (recommended)

```shell
tmux new -s mywork
```

**Example output** (status bar at the bottom):

```
[mywork] 0:bash*                                         "hostname" 10:00 06-Mar-26
```

The session name `[mywork]` is shown on the left side of the status bar.

**Option details:**

| Command | Description |
|---|---|
| `tmux new` | Create a new session (short for `new-session`) |
| `-s mywork` | Set the session name to `mywork` |

---

## 3-2. Detaching from a Session

This sends the session to the background **without terminating it**.
Even if the SSH connection drops, the session keeps running on the server.

```
Ctrl + b → d
```

**Example output:**

```
[detached (from session mywork)]
```

---

## 3-3. Listing Sessions

```shell
tmux ls
```

**Example output:**

```
mywork: 1 windows (created Thu Mar  6 10:00:00 2026)
deploy: 2 windows (created Thu Mar  6 09:30:00 2026)
```

---

## 3-4. Reattaching to a Session

```shell
# Attach by name
tmux attach -t mywork

# Short form
tmux a -t mywork

# If there's only one session, you can omit the name
tmux a
```

**Example output** (status bar after attaching):

```
[mywork] 0:bash*                                         "hostname" 10:05 06-Mar-26
```

**Option details:**

| Command | Description |
|---|---|
| `tmux attach` | Reattach to a session (short for `attach-session`) |
| `-t mywork` | Specify the session name to attach to |

---

## 3-5. Terminating a Session

```shell
# Exit from within the session
exit

# Kill a specific session from outside
tmux kill-session -t mywork

# Kill all sessions
tmux kill-server
```

---

## 3-6. Session Shortcut Summary

| Shortcut | Description |
|---|---|
| `Ctrl + b → d` | Detach from current session (session remains) |
| `Ctrl + b → s` | View and switch session list |
| `Ctrl + b → $` | Rename the current session |

---

# [04] Screen Splitting (Pane)

## 4-1. Splitting the Screen

```
# Vertical split (left/right)
Ctrl + b → %

# Horizontal split (top/bottom)
Ctrl + b → "
```

**Split examples:**

```
┌─────────────┬─────────────┐
│             │             │  ← Ctrl+b % (left/right split)
│   pane 0    │   pane 1    │
│             │             │
└─────────────┴─────────────┘

┌─────────────────────────────┐
│          pane 0             │  ← Ctrl+b " (top/bottom split)
├─────────────────────────────┤
│          pane 1             │
└─────────────────────────────┘
```

---

## 4-2. Moving Between Panes

### Using arrow keys

```
Ctrl + b → ↑ / ↓ / ← / →
```

### Sequential navigation (next/previous pane)

```
Ctrl + b → o       # Move to the next pane
Ctrl + b → ;       # Move to the previously used pane
```

### Jump by pane number

```
Ctrl + b → q       # Display pane numbers
```

**Example output** (numbers briefly appear on screen):

```
┌─────────────┬─────────────┐
│             │             │
│      0      │      1      │
│             │             │
└─────────────┴─────────────┘
```

While the numbers are visible, press the corresponding number key to jump to that pane.

```
Ctrl + b → q → 1   # Jump to pane 1
```

---

## 4-3. Resizing Panes

After pressing the prefix, hold an arrow key to move pane boundaries.

```
Ctrl + b → Alt + ↑ / ↓ / ← / →
```

Alternatively, you can use the following after the prefix:

```
Ctrl + b → :resize-pane -D 5   # Shrink down by 5 cells
Ctrl + b → :resize-pane -U 5   # Expand up by 5 cells
Ctrl + b → :resize-pane -L 5   # Shrink left by 5 cells
Ctrl + b → :resize-pane -R 5   # Expand right by 5 cells
```

---

## 4-4. Closing a Pane

```shell
# Exit the shell inside the pane
exit

# Or use the shortcut
Ctrl + b → x    # Close current pane (confirmation prompt appears)
```

**Example output** (confirmation prompt):

```
kill pane mywork:0.1? (y/n)
```

Press `y` to close the pane.

---

## 4-5. Cycling Through Pane Layouts

```
Ctrl + b → Space    # Cycle layouts (even-horizontal → even-vertical → main-horizontal → ...)
```

---

## 4-6. Pane Shortcut Summary

| Shortcut | Description |
|---|---|
| `Ctrl + b → %` | Vertical (left/right) split |
| `Ctrl + b → "` | Horizontal (top/bottom) split |
| `Ctrl + b → arrow key` | Move to adjacent pane |
| `Ctrl + b → o` | Cycle to the next pane |
| `Ctrl + b → ;` | Move to the previous pane |
| `Ctrl + b → q` | Display pane numbers |
| `Ctrl + b → q → number` | Move to pane by number |
| `Ctrl + b → x` | Close the current pane |
| `Ctrl + b → Space` | Cycle layouts |
| `Ctrl + b → z` | Toggle full-screen for the current pane |

---

# [05] Window Management

If panes are screen splits, windows are the equivalent of browser **tabs**.

## 5-1. Window Shortcut Summary

| Shortcut | Description |
|---|---|
| `Ctrl + b → c` | Create a new window |
| `Ctrl + b → w` | View and switch window list |
| `Ctrl + b → n` | Move to the next window |
| `Ctrl + b → p` | Move to the previous window |
| `Ctrl + b → number` | Move to the window with that number (0~9) |
| `Ctrl + b → ,` | Rename the current window |
| `Ctrl + b → &` | Close the current window |

---

# [06] Scrolling (Copy Mode)

tmux does not scroll with the mouse wheel by default. You need to enter **Copy Mode** to scroll up and down.

## 6-1. Entering/Exiting Copy Mode

```
Ctrl + b → [     # Enter Copy Mode (scrolling enabled)
q                # Exit Copy Mode (scrolling disabled)
```

:bulb: Once in Copy Mode, a scroll position indicator like `[0/100]` appears at the bottom of the terminal.
{: .notice--info}

## 6-2. Navigation Shortcuts in Copy Mode

| Shortcut | Description |
|---|---|
| `↑ / ↓` | Move one line up/down |
| `Page Up / Page Down` | Move one screen up/down |
| `Ctrl + u / Ctrl + d` | Move half a screen up/down |
| `g` | Jump to the top of the buffer |
| `G` | Jump to the bottom of the buffer |
| `q` | Exit Copy Mode |

## 6-3. Enabling Mouse Scrolling (Optional)

To scroll with the mouse wheel without pressing `Ctrl+b [` each time, add the following to `~/.tmux.conf`:

```shell
set -g mouse on
```

Apply the change:

```shell
tmux source-file ~/.tmux.conf
```

:bulb: With mouse mode on, you can also switch panes by clicking with the mouse.
{: .notice--info}

---

# [07] Full Shortcut Summary

| Category | Shortcut | Description |
|---|---|---|
| **Session** | `Ctrl+b d` | Detach session |
| | `Ctrl+b s` | Session list and switch |
| | `Ctrl+b $` | Rename session |
| **Window** | `Ctrl+b c` | Create a new window |
| | `Ctrl+b w` | Window list |
| | `Ctrl+b n / p` | Next / previous window |
| | `Ctrl+b number` | Move to window by number |
| | `Ctrl+b ,` | Rename window |
| **Pane** | `Ctrl+b %` | Vertical split |
| | `Ctrl+b "` | Horizontal split |
| | `Ctrl+b arrow keys` | Move between panes |
| | `Ctrl+b o` | Cycle next pane |
| | `Ctrl+b q` | Display pane numbers |
| | `Ctrl+b z` | Toggle pane full-screen |
| | `Ctrl+b x` | Close current pane |
| | `Ctrl+b Space` | Cycle layouts |
| **Scroll** | `Ctrl+b [` | Enter Copy Mode (scrolling enabled) |
| | `q` | Exit Copy Mode (scrolling disabled) |
| | `Page Up / Down` | Move one screen at a time |
| **Other** | `Ctrl+b ?` | View full shortcut list |
| | `Ctrl+b :` | Enter tmux command mode |
