---
title: "Sort and Display Directories by Disk Usage (du + sort)"
description: "How to combine the du and sort commands on Ubuntu/Linux to list directories ordered by disk usage"
excerpt: "Use du -h --max-depth=1 | sort -hr to see directory sizes at a glance"
date: 2026-02-10
categories: Linux
tags: [Linux, Ubuntu, du, sort, disk-usage, directory, capacity-check]
ref: linux-disk-usage-sort
---

:bulb: When disk space runs low on a Linux server, this guide covers the `du` + `sort` combination for quickly identifying which directories are the largest.
{: .notice--info}

# [01] Check the Current Directory's Usage

## 1-1. Basic Command

Lists the subdirectories of the current directory **ordered from largest to smallest**.

```bash
du -h --max-depth=1 | sort -hr
```

| Option | Description |
|---|---|
| `du -h` | Display sizes in human-readable units (K, M, G) |
| `--max-depth=1` | Only show one level below the current directory |
| `sort -h` | Sort considering human-readable units (K < M < G) |
| `sort -r` | Descending order (largest first) |

**Example output:**

```
15G     .
8.2G    ./data
4.1G    ./logs
2.3G    ./backup
512M    ./config
```

## 1-2. Targeting a Specific Directory

Replace `/var` with any path to analyze that directory.

```bash
du -h --max-depth=1 /var | sort -hr
```

---

# [02] Filtering Directories Only

## 2-1. Exclude Files, Show Only Directories

Add `grep` to filter out files and keep only directory entries.

```bash
du -h --max-depth=1 | grep '/$' | sort -hr
```

:bulb: `grep '/$'` filters only entries ending with `/` (directories).
{: .notice--info}

## 2-2. Adjusting Depth

Increasing `--max-depth` lets you inspect deeper subdirectories.

```bash
# Check up to 2 levels deep
du -h --max-depth=2 | sort -hr | head -20
```

:bulb: Appending `head -20` displays only the top 20 entries for better readability.
{: .notice--info}

---

# [03] Practical Examples

## 3-1. Finding Large Folders from the Root Directory

The first command to run when disk space is tight.

```bash
sudo du -h --max-depth=1 / | sort -hr | head -15
```

:warning: Scanning root (`/`) requires `sudo` and may take a while.
{: .notice--warning}

## 3-2. Cleaning Up the Home Directory

```bash
du -h --max-depth=1 ~ | sort -hr
```

## 3-3. Inspecting the Log Directory

```bash
sudo du -h --max-depth=2 /var/log | sort -hr | head -10
```
