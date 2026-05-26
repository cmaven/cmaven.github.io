---
title: "Changing the Hostname on Ubuntu (Linux)"
description: "How to permanently change the hostname on Ubuntu using hostnamectl, with verification steps, /etc/hosts update, and tips for multi-node environments."
excerpt: "Use hostnamectl set-hostname to rename an Ubuntu machine — takes effect immediately without a reboot."
date: 2022-11-02
last_modified_at: 2026-05-26
categories: Linux
tags: [Ubuntu, hostname, hostnamectl, change-hostname, /etc/hosts, multi-node, networking]
ref: ubuntu-hostname
---

:bulb: This guide explains how to change the hostname on Ubuntu using `hostnamectl`, verify the result, update `/etc/hosts`, and avoid common pitfalls in multi-node environments.
{: .notice--info}

**Environment**: Ubuntu 20.04 / 22.04 / 24.04 (Server or Desktop)

---

# [01] Check the Current Hostname

Before making any change, confirm the active hostname so you have a baseline to compare against.

```shell
hostname
```

Sample output:

```text
root@gmaster:~# hostname
gmaster
```

You can also use `hostnamectl` for a richer status view:

```shell
hostnamectl status
```

```text
 Static hostname: gmaster
       Icon name: computer-server
         Chassis: server
      Machine ID: e2f4a1...
         Boot ID: 7d9bc3...
Operating System: Ubuntu 22.04.4 LTS
          Kernel: Linux 5.15.0-107-generic
    Architecture: x86-64
```

| Field | Meaning |
|---|---|
| **Static hostname** | The persistent name stored in `/etc/hostname` |
| **Transient hostname** | The kernel's current name (usually matches static) |
| **Pretty hostname** | A free-form display label (optional) |

---

# [02] Change the Hostname

`hostnamectl set-hostname` writes to `/etc/hostname` and updates the running kernel name atomically — no reboot required.

```shell
sudo hostnamectl set-hostname <new-hostname>
```

Example — renaming `gmaster` to `gworker01`:

```shell
sudo hostnamectl set-hostname gworker01
```

Verify immediately without logging out:

```shell
hostname
# gworker01

hostnamectl status | grep "Static hostname"
# Static hostname: gworker01
```

:bulb: The prompt still shows the old name until you open a new shell session. Close and reopen the terminal (or run `exec bash`) to see the updated prompt.
{: .notice--info}

---

# [03] Update /etc/hosts

`hostnamectl` updates `/etc/hostname` but does **not** touch `/etc/hosts`. If the old hostname appears in `/etc/hosts` (which is common), update it to avoid DNS resolution warnings and to keep `sudo` from printing `unable to resolve host`.

```shell
sudo nano /etc/hosts
```

Change the line that maps `127.0.1.1` (or `127.0.0.1`) to the old hostname:

```text
# Before
127.0.1.1   gmaster

# After
127.0.1.1   gworker01
```

Test resolution:

```shell
ping -c 1 gworker01
# PING gworker01 (127.0.1.1): 56 data bytes
```

---

# [04] Hostname Naming Rules

Not all strings are valid hostnames. Follow these rules to avoid subtle networking issues.

| Rule | Good example | Bad example |
|---|---|---|
| Letters, digits, hyphens only | `web-node-01` | `web_node_01` (underscore not valid) |
| Must not start or end with a hyphen | `node-01` | `-node01` |
| Maximum 63 characters per label | `gworker01` | 64+ chars |
| Case-insensitive (use lowercase) | `gworker01` | `GWorker01` |

:warning: Hostnames with underscores can cause issues with some SSL/TLS libraries and Kubernetes node naming. Stick to hyphens.
{: .notice--warning}

---

# [05] Multi-Node Tip — Scripted Rename

When setting up a cluster (e.g., Kubernetes, Hadoop), you often rename several machines in sequence. A small loop on the orchestrator makes this safe and repeatable:

```shell
# Run on each worker node via SSH
for i in 01 02 03; do
  ssh root@192.168.1.1${i} "hostnamectl set-hostname gworker${i}"
done
```

Also update `/etc/hosts` on every node (or use a DNS server) so all nodes can resolve each other by hostname:

```text
# /etc/hosts on every node
192.168.1.100  gmaster
192.168.1.101  gworker01
192.168.1.102  gworker02
192.168.1.103  gworker03
```

---

# [06] Reference

:small_blue_diamond: [How to change hostname without a restart (askubuntu)](https://askubuntu.com/questions/87665/how-do-i-change-the-hostname-without-a-restart){:target="_blank"}

:small_blue_diamond: [Ubuntu `hostnamectl` man page](https://manpages.ubuntu.com/manpages/jammy/man1/hostnamectl.1.html){:target="_blank"}
