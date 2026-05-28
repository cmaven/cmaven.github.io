---
title: "Complete Guide to File Compression on Ubuntu — zip and tar (gzip/bzip2)"
description: "A full guide to compressing and extracting files and directories on Ubuntu/Linux with zip and tar. Covers zip/unzip installation, recursive compression (-r), including hidden files, and a tar.gz vs tar.bz2 comparison with option reference"
excerpt: "Use zip -r for multiple files and tar -czvf to bundle directories. Learn the difference between gzip and bzip2 with hands-on examples"
date: 2026-05-28
categories: Linux
tags: [Ubuntu, Linux, zip, unzip, tar, gzip, bzip2, compression, extract, tar-gz, tar-bz2, command-line, terminal]
ref: ubuntu-file-compression-zip-tar
---

:bulb: The two most common ways to bundle or transfer files on Linux are `zip` and `tar`. `zip` offers great compatibility with Windows, while `tar` is the standard on Linux/Unix systems. This guide walks through the compression and extraction commands for both, with examples.
{: .notice--info}

**Environment**: Ubuntu (applies to all apt-based distributions)

---

# [01] Installing zip / unzip

`zip` and `unzip` are not always pre-installed on Ubuntu. Refresh the package list and install them.

```bash
sudo apt update
sudo apt install zip unzip -y
```

| Package | Purpose |
|---------|---------|
| `zip` | Compress files/directories into `.zip` |
| `unzip` | Extract `.zip` files |

:memo: `tar` and `gzip` ship with most distributions by default, so no separate install is needed.
{: .notice--warning}

---

# [02] Compressing with zip

## 2-1. Compress a Single File

Use the form `zip <output> <target>`.

```bash
zip archive.zip file.txt
```

## 2-2. Compress Multiple Files/Directories (-r)

To include directories you need the **`-r` option, which recursively captures subfolders**. Without `-r`, the files inside a directory are skipped.

```bash
zip -r archive.zip folder1 folder2 file1.txt
```

## 2-3. Include Hidden Files

Hidden files starting with a dot (`.`), such as `.bashrc`, are not matched by ordinary patterns. Add the `.[!.]*` pattern to include them.

```bash
zip -r archive.zip folder1 folder2 file1.txt .[!.]*
```

:bulb: `.[!.]*` means "files starting with a dot whose second character is not a dot." It safely includes hidden files while excluding `.` (current directory) and `..` (parent directory).
{: .notice--info}

| Option | Description |
|--------|-------------|
| `-r` | Recursively compress directories and their contents |
| `-e` | Encrypt the archive with a password |
| `-1` – `-9` | Compression level (1 = fast, 9 = best compression) |
| `-q` | Quiet mode (suppress progress messages) |

---

# [03] Extracting with unzip

## 3-1. Extract to the Current Directory

```bash
unzip archive.zip
```

## 3-2. Extract to a Specific Directory (-d)

Use the `-d` option to set the target path. The directory is created automatically if it does not exist.

```bash
unzip archive.zip -d /path/to/directory/
```

| Option | Description |
|--------|-------------|
| `-d <path>` | Extract into the specified directory |
| `-l` | List archive contents without extracting |
| `-o` | Overwrite existing files without prompting |
| `-n` | Never overwrite; skip existing files |

---

# [04] tar — gzip vs bzip2

`tar` bundles multiple files into one archive, and is usually combined with `gzip` (`.tar.gz`) or `bzip2` (`.tar.bz2`) to compress as well.

| Aspect | gzip (`.tar.gz`) | bzip2 (`.tar.bz2`) |
|--------|------------------|--------------------|
| Compression ratio | Medium | High |
| Speed | Fast | Slow |
| Output size | Moderate | Smaller |
| Notes | Standard format, great compatibility & speed | CPU intensive |

:bulb: In general, **`tar.gz` is preferred for its compatibility and speed**. When you need to minimize size and have time to spare, `tar.bz2` is the better choice.
{: .notice--info}

---

# [05] tar.gz Compression & Extraction

## 5-1. Compress

```bash
tar -czvf archive.tar.gz file1.txt folder1
```

## 5-2. Extract

```bash
# Extract to the current directory
tar -xzvf archive.tar.gz

# Extract to a specific path
tar -xzvf archive.tar.gz -C /path/to/target/
```

---

# [06] tar.bz2 Compression & Extraction

Just swap the `z` (gzip) for the **`j` option (bzip2)**. Everything else stays the same.

## 6-1. Compress

```bash
tar -cjvf archive.tar.bz2 file1.txt folder1
```

## 6-2. Extract

```bash
# Extract to the current directory
tar -xjvf archive.tar.bz2

# Extract to a specific path
tar -xjvf archive.tar.bz2 -C /opt/data/
```

---

# [07] tar Option Reference

| Option | Meaning | Description |
|--------|---------|-------------|
| `c` | create | Create a new archive (compress) |
| `x` | extract | Extract an archive |
| `t` | list | List contents without extracting |
| `z` | gzip | gzip compress/extract (`.tar.gz`) |
| `j` | bzip2 | bzip2 compress/extract (`.tar.bz2`) |
| `v` | verbose | Print progress to the screen |
| `f` | file | Specify the archive filename (always last) |
| `-C` | change dir | Set the target directory for extraction |

:warning: The `f` option must come right before the filename (last). While `tar -cvzf` also works with the order mixed, the conventional form is `tar -czvf <filename>`.
{: .notice--warning}

---

# [08] Summary — When to Use What

| Situation | Recommendation |
|-----------|----------------|
| Exchanging files with Windows | `zip` (best compatibility) |
| Backing up/transferring directories between Linux hosts | `tar.gz` (standard, fast) |
| Squeezing out maximum size savings | `tar.bz2` (high compression) |
| Bundling just a few files | `zip` |

:bulb: Remember the essentials: **use `zip -r` for multiple files/folders** and **`tar -czvf` for directory backups**. To extract, just change the `c` in the compression options to `x`.
{: .notice--info}
