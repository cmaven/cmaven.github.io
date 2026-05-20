---
title: "SSD Secure Erase on Windows 11 — Unrecoverable Deletion"
description: "Concept of Secure Erase for completely (unrecoverably) wiping an SSD, how to run it via Samsung Magician/Rufus, and comparison with DiskPart clean all"
excerpt: "Regular formatting leaves SSD data recoverable — compare Secure Erase, Rufus+ISO, and DiskPart clean all"
date: 2026-04-20
categories: Storage
tags: [SSD, Secure-Erase, Windows11, Samsung-Magician, Rufus, DiskPart, data-erase, Frozen, UEFI, secure-deletion]
ref: ssd-secure-erase-windows11
---

:bulb: How to completely (unrecoverably) wipe an SSD on Windows 11 using Secure Erase.
{: .notice--info}

**Environment**: Windows 11 + 2 SSDs (C: OS / H: target for deletion)

---

# [01] Why Regular Formatting Isn't Enough

Standard Windows formatting (quick or full) **only removes the file system index** — actual data remains on the disk.

| Method | Data actually removed? | Recoverable? |
|--------|:---:|:---:|
| Quick format | X | Yes, with recovery tools |
| Full format | X | Yes, with recovery tools |
| **Secure Erase** | **O** | **Practically impossible** |

---

# [02] What Is Secure Erase?

Secure Erase is an initialization performed by the **SSD's internal controller**.

| Trait | Description |
|-------|-------------|
| Scope | Erases data on every cell |
| Recoverability | Practically impossible |
| Speed | 1–10 minutes (independent of capacity) |
| SSD performance | Restored to factory-fresh state |

---

# [03] Frozen State — Why a Reboot Is Required

When Windows is running, the OS puts SSDs in a **Frozen (security lock) state**. Secure Erase cannot run in this state.

```
Windows running
  → SSD state: Frozen (security)
  → Secure Erase: cannot run

USB boot (pre-boot environment)
  → SSD state: Not Frozen
  → Secure Erase: can run
```

:warning: Secure Erase must be run in a **pre-boot environment** (before Windows starts).
{: .notice--warning}

**Resolving Frozen state:**

| Environment | Resolution |
|-------------|------------|
| Laptop | Enter Sleep mode → wake again |
| Desktop | Re-seat SATA cable (rarely needed) |
| Common | Boot from USB to enter pre-boot |

---

# [04] Overall Flow

```
[1] Create Secure Erase USB
  ↓
[2] Reboot PC
  ↓
[3] Boot from USB via BIOS
  ↓
[4] Run Secure Erase
  ↓
[5] Select target SSD (⚠ critical)
  ↓
[6] Done — SSD restored to factory state
```

---

# [05] Method 1: Samsung Magician (Samsung SSDs)

## 5-1. Requirement
- Using a Samsung SSD (860 EVO, 970 EVO, 980 PRO, etc.)

## 5-2. Procedure

```
1. Run Samsung Magician (as Administrator)
2. Left menu → Secure Erase
3. Create bootable USB (USB required)
4. Reboot → boot from USB
5. Select target SSD → execute
```

## 5-3. If USB Creation Fails

Common error from Samsung Magician:

```
"Failed to create bootable USB drive"
```

In that case, use **Method 2 (Rufus)**.

---

# [06] Method 2: Rufus + ISO (Recommended)

Use when Magician's USB creation fails, or when you have a non-Samsung SSD.

## 6-1. Requirements

| Item | Description |
|------|-------------|
| USB | 8GB+ |
| Rufus | Download from [rufus.ie](https://rufus.ie) |
| ISO | Samsung Secure Erase ISO or Parted Magic |

## 6-2. Rufus USB Settings

```
Boot selection:   ISO file
Partition scheme: GPT (for UEFI)
File system:      FAT32
```

## 6-3. Boot from USB

```
1. Restart PC
2. Enter BIOS (F2, F12, DEL — varies by vendor)
3. Boot menu → select USB
4. Run Secure Erase tool from USB
```

## 6-4. Run Secure Erase

```
1. Identify target in the SSD list
2. Select the SSD to wipe
3. Execute Secure Erase
4. Complete in 1–10 minutes
```

---

# [07] Avoiding Wrong SSD Selection

:warning: Selecting the OS-installed SSD will **wipe your system**. Triple-check the target.
{: .notice--warning}

| Check | Description |
|-------|-------------|
| **Capacity** | Compare sizes (C: vs H:) |
| **Model name** | Check via Samsung Magician or BIOS |
| **Disk number** | `diskpart` → `list disk` to see number + size |

```bash
# Pre-check in Windows
diskpart
list disk
```

```
  Disk ###  Status         Size     Free
  --------  -------------  -------  -------
  Disk 0    Online          476 GB    0 B     ← C: drive (OS)
  Disk 1    Online          931 GB    0 B     ← H: drive (target)
```

**Note capacity and disk number** before running Secure Erase.

---

# [08] Alternative: DiskPart clean all

When Secure Erase isn't available, use the Windows command alternative.

```bash
diskpart
list disk
select disk 1          # target disk number
clean all              # overwrite entire area with zeros
```

| Trait | Description |
|-------|-------------|
| Operation | Overwrites entire area with zeros |
| Recoverability | Very low |
| Time | 1–3 hours per TB |
| Pros | No USB boot needed, runs from Windows |
| Cons | Slower than Secure Erase; no SSD performance restoration |

---

# [09] Method Comparison

| Method | Time | Recoverability | SSD performance restore | Recommended |
|--------|------|----------------|:---:|:---:|
| **Secure Erase** | 1–10 min | Practically impossible | Yes | ★★★★★ |
| **DiskPart clean all** | 1–3 hr | Very low | No | ★★★ |
| **Regular format** | Seconds | High | No | Not recommended |

---

# [10] Summary

```
SSD complete deletion = Secure Erase (NOT format)
```

| Tier | Task |
|------|------|
| 1st | Samsung Magician Secure Erase |
| Fallback | Rufus + ISO USB boot |
| Alternative | `diskpart` → `clean all` (slower but works from Windows) |

:warning: **Back up important data first**. After Secure Erase, recovery is practically impossible.
{: .notice--warning}
