---
title: "Batch-Converting Mermaid Diagrams to Images — mermaid2img.sh"
description: "Usage and internals of a shell script that extracts Mermaid diagrams from Markdown files and saves them as JPG/PNG in one shot"
excerpt: "A guide to mermaid2img.sh — a single script that handles environment setup, mermaid block extraction, mmdc rendering, and format conversion"
date: 2026-03-26
categories: Github_Blog
tags: [Mermaid, mermaid-cli, mmdc, image-conversion, shell-script, WSL, Puppeteer, Chrome, Node.js, Pillow]
ref: mermaid2img-script-guide
---

:bulb: This post explains the usage and internals of `mermaid2img.sh`, a shell script that extracts Mermaid diagrams embedded in Markdown (`.md`) files and saves them as JPG or PNG in one shot.
{: .notice--info}

# [01] Why It's Needed

Mermaid lets you draw diagrams as text inside Markdown. Platforms like GitHub, Notion, and Obsidian render it automatically, but image files are still required in cases like:

- Embedding diagrams in Office documents such as PowerPoint or Word
- Posting to blog platforms that don't support Mermaid rendering
- Converting documents to PDF while including the diagrams
- Registering with image-based document management systems

For 1 or 2 diagrams per document, manual conversion is fine. Once it's 10 or more, automation pays off.

---

# [02] Features and Usage

## 2-1. Main features

| Feature | Description |
|---------|-------------|
| **Automatic environment setup** | Installs Node.js, mermaid-cli, Chrome, Pillow, and Korean fonts if missing |
| **WSL compatibility** | Automatically detects and resolves Windows PATH priority issues |
| **Format selection** | JPG or PNG, chosen interactively or via flag |
| **High resolution** | 2x scale by default for Retina-grade sharpness |
| **Single file** | One script, no extra config files needed |

## 2-2. Usage

```bash
chmod +x mermaid2img.sh

# Interactive — prompts for format
./mermaid2img.sh document.md

# Specify format via flag — no prompt, runs immediately
./mermaid2img.sh -f png document.md

# JPG quality + output directory
./mermaid2img.sh -f jpg -q 80 document.md ./output/

# Help
./mermaid2img.sh -h
```

Without any flag, the script prompts for the format.

```
  Choose output format:

    1) jpg  — small files, good for embedding in documents
    2) png  — lossless, supports transparent backgrounds

  Select [1/2] (default: 1):
```

## 2-3. Error messages

**Run without arguments:**

```bash
./mermaid2img.sh
```

```
./mermaid2img.sh: line XX: 1: usage: ./mermaid2img.sh <input.md> [output_dir]
```

The script uses the `${1:?usage}` pattern internally, so if no input file is given it prints usage and exits.

**Non-existent file:**

```bash
./mermaid2img.sh not-exist.md
```

```
[✗] Input file not found: not-exist.md
```

**File with no mermaid blocks:**

```bash
./mermaid2img.sh no-mermaid.md
```

```
No mermaid blocks found.
```

## 2-4. Example run output

Converting a document with 16 mermaid blocks produces output like this:

```
[✓] Chrome: /home/kcloud/.cache/puppeteer/chrome/linux-.../chrome
[✓] Output format: JPG
  BLOCK 1: ./mermaid_images/document_1.mmd
  BLOCK 2: ./mermaid_images/document_2.mmd
  ...
  BLOCK 16: ./mermaid_images/document_16.mmd

  Found 16 blocks total

[1] Converting: document_1.mmd → document_1.jpg (848x1200, 150KB)
[2] Converting: document_2.mmd → document_2.jpg (848x600, 85KB)
...
[16] Converting: document_16.mmd → document_16.jpg (848x900, 120KB)

[✓] Conversion complete! Output: ./mermaid_images/
```

Output filenames follow the form `{markdown_filename}_{index}.jpg` (or `.png`) and are numbered in the order the blocks appear in the document.

---

# [03] Script Structure

The script has two major sections: **PART 1 (environment setup)** and **PART 2 (conversion)**.

```
PART 1: Environment check and auto-setup
  ├── 1-1. Fix WSL Windows PATH priority issue
  ├── 1-2. Install Node.js v20+ (NodeSource)
  ├── 1-3. Configure npm global path
  ├── 1-4. Install mermaid-cli (mmdc)
  ├── 1-5. Install Chrome + system libraries
  ├── 1-6. Install Python3 & Pillow
  └── 1-7. Install Korean fonts

PART 2: Mermaid → image conversion
  ├── 2-1. Parse options and pick format
  ├── 2-2. Locate Chrome binary → configure Puppeteer
  ├── 2-3. Extract Mermaid blocks from Markdown
  ├── 2-4. Convert each block (mermaid → PNG → JPG/PNG)
  └── 2-5. Cleanup and result output
```

If the environment is already prepared, PART 1 prints nothing and moves directly to PART 2. If something is missing, it emits `[!] [Environment setup]` messages and auto-installs.

---

# [04] PART 1: Automatic Environment Setup

## 4-1. WSL Windows PATH priority

WSL inherits Windows' PATH by default. If Windows has Node.js (e.g., nvm4w) installed, it takes precedence over Linux's `node`, and `mmdc` stops working.

```bash
which node
# /mnt/c/nvm4w/nodejs/node  ← if this shows up, that's the problem
```

The script detects WSL via `/proc/version`, and if the `node` path contains `/mnt/c`, it adjusts PATH so Linux paths take priority.

## 4-2. Node.js v20+

The latest mermaid-cli requires Node.js v20 or higher. `apt install nodejs` on Ubuntu 24.04 installs v18, which is insufficient.

The script checks the current Node.js version, and if it's below v20, installs v22 LTS via the NodeSource repository.

```
[!] [Environment setup] Node.js v18.19.1 is too low. (v20+ required)
[!] [Environment setup] Installing Node.js v22 LTS...
[✓] [Environment setup] Node.js installation complete: v22.x.x
```

## 4-3. npm global path

Configures npm global packages to install under `~/.npm-global`. This avoids `sudo npm install -g` and the script automatically adds it to PATH.

## 4-4. mermaid-cli (mmdc)

If `mmdc` isn't found, or only exists at a Windows path (`/mnt/c/...`), the script installs a fresh Linux build.

## 4-5. Chrome + system libraries

`mmdc` runs headless Chrome internally via Puppeteer. If the Chrome binary is missing, the script installs it via Puppeteer and verifies the system libraries Chrome needs (libnss3, libgbm1, etc.).

On WSL or minimal Ubuntu installs, it's common for the Chrome binary to be present while the shared libraries are missing, causing failures.

```
Error: libnss3.so: cannot open shared object file
```

The script uses `ldconfig` to check for `libnss3` and, if absent, installs all required libraries at once.

## 4-6. Python3 & Pillow

JPG conversion requires Pillow. If `pip3` is available, install via pip; otherwise via `apt install python3-pil`.

## 4-7. Korean fonts

If a diagram contains Korean text and the font is missing, characters render as boxes. The script uses `dpkg` to check whether `fonts-nanum` or `fonts-noto-cjk` is installed.

:bulb: `fc-list` behaves unreliably under WSL, so the script uses `dpkg` instead.
{: .notice--info}

---

# [05] PART 2: Mermaid → Image Conversion

## 5-1. Argument validation and option parsing

The script validates the input file at startup.

```bash
INPUT="${1:?usage: $0 <input.md> [output_dir]}"
```

With no argument, it prints usage and exits immediately. It also prints an error if the file doesn't exist.

`getopts` parses `-f` (format), `-q` (JPG quality), and `-h` (help) options. `-h` is detected before PART 1 environment setup, so requesting help doesn't trigger unnecessary installations.

## 5-2. Locating the Chrome binary

The Chrome binary lives in different places across environments, so the script searches multiple candidate paths.

| Environment | Chrome path |
|-------------|-------------|
| Installed via apt (chromium) | `/usr/bin/chromium-browser` or `/usr/bin/chromium` |
| Direct Google Chrome install | `/usr/bin/google-chrome-stable` |
| Auto-installed by Puppeteer | `~/.cache/puppeteer/chrome/linux-*/chrome-linux64/chrome` |

The found path is written into a temporary JSON file and passed to `mmdc` via the `-p` option.

## 5-3. Extracting Mermaid blocks

An inline Python script extracts mermaid blocks from the Markdown.

```python
blocks = re.findall(r'```mermaid\s*\n(.*?)```', content, re.DOTALL)
```

| Pattern | Matches |
|---------|---------|
| ` ```mermaid ` | Opening tag |
| `\s*\n` | Whitespace and newline after opening tag |
| `(.*?)` | Mermaid code body (non-greedy capture) |
| ` ``` ` | Closing tag |

The `re.DOTALL` flag makes `.` also match newlines, so multi-line mermaid bodies are captured correctly. Each block is saved to a `{filename}_{index}.mmd` file.

## 5-4. Rendering (Mermaid → PNG → JPG/PNG)

Each `.mmd` file is converted as follows.

```bash
mmdc -i "$mmd_file" -o "$png_file" -b "$BG" -w "$WIDTH" -s "$SCALE" -p "$PUPPETEER_CONFIG" -q
```

| Option | Description |
|--------|-------------|
| `-i` | Input `.mmd` file |
| `-o` | Output file (format determined by extension) |
| `-b white` | White background |
| `-w 1200` | Rendering canvas width |
| `-s 2` | 2x scale (high resolution) |
| `-p` | Puppeteer config (Chrome path, sandbox flags) |
| `-q` | Quiet mode (suppress noisy logs) |

`mmdc` internally launches headless Chrome, renders the diagram with mermaid.js, and screenshots it to produce a PNG.

**Format branching:**
- **JPG selected**: convert PNG → JPG with Pillow (`.convert('RGB')` then save)
- **PNG selected**: keep the PNG that `mmdc` produced as-is

---

# [06] End-to-End Flow

```
./mermaid2img.sh document.md
  │
  ├─ -h detected → print help and exit (skip environment setup)
  │
  ├─ PART 1: Environment check and auto-setup
  │    ├─ 1-1. WSL PATH issue → prioritize Linux
  │    ├─ 1-2. Node.js < v20 → install v22 via NodeSource
  │    ├─ 1-3. npm global path → ~/.npm-global
  │    ├─ 1-4. mmdc missing → npm install -g mermaid-cli
  │    ├─ 1-5. Chrome missing → install via Puppeteer + system libs
  │    ├─ 1-6. Pillow missing → install via pip3 or apt
  │    └─ 1-7. Korean fonts missing → install fonts-nanum
  │
  ├─ PART 2: Conversion
  │    ├─ 2-1. Parse options + choose format (interactive or -f)
  │    ├─ 2-2. Locate Chrome binary → generate puppeteer.json
  │    ├─ 2-3. Extract mermaid blocks via Python regex
  │    ├─ 2-4. Each .mmd → PNG → JPG/PNG
  │    └─ 2-5. Clean up temp files
  │
  └─ Result: document_1.jpg, document_2.jpg, ... (or .png)
```

---

# [07] Dependency Map

The role of each tool the script installs automatically:

| Tool | Role | Install method |
|------|------|----------------|
| Node.js v22 | Runtime for mmdc | NodeSource repo → apt |
| `mmdc` (mermaid-cli) | Render Mermaid code to PNG | npm install -g |
| Puppeteer + Chrome | Headless browser used internally by mmdc | npx puppeteer browsers install |
| Chrome system libraries | libnss3, libgbm1, etc. — Chrome dependencies | apt |
| Python3 | Extract mermaid blocks from Markdown (regex) | apt |
| Pillow | PNG → JPG format conversion | pip3 or apt (python3-pil) |
| fonts-nanum | Korean rendering | apt |

:bulb: **Why so complex?** mermaid-cli (`mmdc`) runs mermaid.js inside a headless Chrome browser to render diagrams. Since it's reproducing in the command line what a web browser does, the Node.js → Puppeteer → Chrome dependency chain is required.
{: .notice--info}

---

# [08] WSL Pitfalls Log

## 8-1. "mmdc: command not found"

`mmdc` not found even after `npm install -g`. On WSL, Windows' npm got picked up first, installed mmdc to a Windows path, and Linux couldn't execute it.

```bash
which mmdc
# /mnt/c/nvm4w/nodejs/mmdc  ← Windows path
```

**Fix:** Make Linux PATH take precedence over Windows (auto-handled by 1-1).

## 8-2. "node: not found"

mmdc is present but can't find `node`. The mmdc binary lives in a Windows path and tries to call `node` from there, missing the Linux `node`.

**Fix:** Install Linux Node.js and adjust PATH priority (auto-handled by 1-1 and 1-2).

## 8-3. "Unsupported engine: required node >= 20"

Ubuntu 24.04's default apt package installs Node.js v18. The dependencies of recent mermaid-cli require v20+, triggering a warning.

**Fix:** Install v22 LTS from the NodeSource repository (auto-handled by 1-2).

## 8-4. "libnss3.so: cannot open shared object file"

The Chrome binary exists, but required system libraries don't. Common on minimal Ubuntu and WSL.

**Fix:** Bulk install Chrome dependency libraries (auto-handled by 1-5).

## 8-5. Korean font install check runs every time

`fc-list` was used to check fonts, but in WSL fontconfig might be absent or its cache stale, so already-installed fonts go undetected.

**Fix:** Replace `fc-list` with `dpkg -l fonts-nanum` to directly query package state (fixed in 1-7).

---

# [09] Customization

| Option / variable | Default | Description |
|-------------------|---------|-------------|
| `-f` | (prompts) | `jpg` or `png`. Skip the prompt when specified |
| `-q` | `95` | JPG quality (1-100). 90 roughly halves file size |
| `SCALE` | `2` | Render scale. 1 = normal, 2 = high resolution (Retina-grade) |
| `WIDTH` | `1200` | Canvas width (px). Use 800 for narrow diagrams, 1600 for wide ones |
| `BG` | `white` | Background color. Set to `transparent` (PNG only) for transparency |

`SCALE`, `WIDTH`, and `BG` are edited directly at the top of PART 2 in the script.

---

# [10] Standalone Environment Setup Script

For users who want to do the setup ahead of time, there's a standalone script, `setup-mermaid-env.sh`, identical to PART 1 of `mermaid2img.sh`. It lets you check the state of your environment at a glance.

```bash
chmod +x setup-mermaid-env.sh
./setup-mermaid-env.sh
```

```
========================================
  mermaid2img environment setup
========================================

[✓] PATH priority OK
[✓] Node.js installed: v22.x.x
[✓] mmdc installed: OK
[✓] Chrome found: /home/kcloud/.cache/puppeteer/chrome/...
[✓] Python3 installed: Python 3.12.x
[✓] Pillow installed
[✓] Korean fonts installed

========================================
  Environment setup complete!
========================================
```

---

# [11] Summary

This script bundles a pipeline — **automatic environment setup → mermaid block extraction → mmdc rendering → format conversion** — into a single shell script. Because it auto-resolves the issues you actually hit in real environments (WSL PATH, Node.js versions, missing Chrome libraries, etc.), even a freshly installed Ubuntu can be done in a single command.

```bash
./mermaid2img.sh my-document.md
```
