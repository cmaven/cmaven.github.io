---
title: "Ubuntu Release Cycle (LTS, Interim, ESM)"
description: "A clear overview of the Ubuntu release cycle — LTS vs. interim cadence, ESM extended security support, and how to choose the right version for your workload."
excerpt: "Ubuntu LTS releases every 2 years with 5 years of standard support and up to 10 years of security maintenance via ESM. Interim releases ship every 6 months with 9 months of support."
date: 2023-01-06
last_modified_at: 2026-05-26
categories: Linux
tags: [Ubuntu, LTS, ESM, Release, release-cycle, security-patches, version-management, Ubuntu-Advantage, Canonical]
ref: ubuntu-release
---

:bulb: This post summarizes the Ubuntu release cycle, the difference between LTS and interim releases, and ESM (Extended Security Maintenance) — so you can pick the right Ubuntu version and plan upgrades confidently.
{: .notice--info}

**Reference date**: 2023-01-06 (release plan current as of that date)

---

# [01] Release Version Format

Ubuntu version numbers encode the release date directly:

```text
Ubuntu YY.MM
       ^^  ^^
       │   └─ Month (04 = April, 10 = October)
       └───── Year (last 2 digits)
```

**Examples:**

| Version | Release month |
|---|---|
| Ubuntu 20.04 | April 2020 |
| Ubuntu 20.10 | October 2020 |
| Ubuntu 22.04 | April 2022 |
| Ubuntu 23.10 | October 2023 |

---

# [02] LTS vs. Interim Releases

Ubuntu ships two distinct release tracks aimed at different audiences.

| Property | LTS | Interim |
|---|---|---|
| **Cadence** | Every 2 years (April of even years) | Every 6 months |
| **Support period** | 5 years standard + 5 years ESM = **10 years total** | **9 months** |
| **Stability** | Enterprise-grade, conservative package versions | Production-quality, newer upstream packages |
| **Typical users** | Servers, enterprise, long-lived deployments | Developers, early adopters, upstream contributors |
| **Examples** | 20.04, 22.04, 24.04 | 20.10, 21.04, 21.10, 23.10 |

:bulb: For any workload that needs predictable stability and long-term security patches — servers, CI pipelines, embedded systems — always choose an **LTS** release.
{: .notice--info}

---

# [03] ESM — Extended Security Maintenance

After the standard 5-year LTS support window closes, Canonical offers **ESM** to extend security coverage for another 5 years, bringing the total to **10 years**.

ESM covers:

- Kernel Live Patch (zero-downtime kernel security updates)
- Security updates for the main and universe package repositories
- Basic package maintenance

**ESM subscription tiers:**

| Tier | Who | Cost |
|---|---|---|
| **Personal** | Individual / home users | Free (up to 5 machines) |
| **Ubuntu Pro** | Organisations, cloud, enterprises | Paid (Ubuntu Advantage subscription) |

To attach a machine to ESM (Ubuntu Pro):

```shell
sudo pro attach <token>
sudo pro status
```

---

# [04] Release Plan

The diagram below (as of 2023-01-06) shows the LTS and ESM support windows for major Ubuntu releases.

![Ubuntu release plan — LTS and ESM windows](https://user-images.githubusercontent.com/76153041/210934649-ea8e88d0-ebf5-469e-8440-80131416b042.png)

*Figure 1. Ubuntu LTS release plan showing standard support (dark) and ESM windows (light) for each version.*

![Ubuntu LTS and ESM duration and pricing](https://user-images.githubusercontent.com/76153041/210934650-ecb1b907-a3ce-4b44-b17b-8b30b7afb789.png)

*Figure 2. LTS and ESM duration and Ubuntu Advantage pricing tiers.*

---

# [05] Choosing a Version — Quick Decision Guide

| Situation | Recommended release |
|---|---|
| Production server, multi-year lifespan | Latest LTS (e.g., 24.04) |
| CI/CD runner or build agent | Latest LTS |
| Developer workstation, want latest packages | Latest interim (e.g., 23.10) |
| Legacy system already on 20.04 | Stay on 20.04 + enable ESM when standard support ends |
| Cloud VM with auto-patching | Latest LTS |
| Raspberry Pi / IoT device | Latest LTS |

:warning: Never run an interim release in production — it reaches end-of-life after just 9 months and will stop receiving security patches.
{: .notice--warning}

---

# [06] Checking Your Current Ubuntu Version

```shell
lsb_release -a
```

```text
Distributor ID: Ubuntu
Description:    Ubuntu 22.04.4 LTS
Release:        22.04
Codename:       jammy
```

To check whether ESM is active on your machine:

```shell
sudo pro status
```

---

# [07] Reference

:small_blue_diamond: [Ubuntu release cycle — official](https://ubuntu.com/about/release-cycle){:target="_blank"}

:small_blue_diamond: [Ubuntu Pro (ESM) — Canonical](https://ubuntu.com/pro){:target="_blank"}
