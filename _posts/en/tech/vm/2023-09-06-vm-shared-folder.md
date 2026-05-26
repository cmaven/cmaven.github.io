---
title: "Creating a Shared Folder Between Host and VM"
description: "How to set up a shared folder between Host and VM using virtiofs in a KVM/QEMU virt-manager environment"
excerpt: "Create and mount a Host-VM shared folder via virtiofs in virt-manager"
date: 2023-09-06
last_modified_at: 2026-05-26
categories: VM
tags: [VM, KVM, QEMU, virt-manager, shared-folder, virtiofs, Shared-Folder, Ubuntu]
ref: vm-shared-folder
---

:bulb: How to create a shared folder between a VM and the Host using virtiofs in a KVM/QEMU environment.
{: .notice--info}

# [01] Environment

| Component | Version / Notes |
|---|---|
| Host OS | Ubuntu 24.04 |
| Hypervisor | KVM + QEMU |
| Manager | virt-manager, virsh, libvirt |
| Filesystem | virtiofs |

**Why virtiofs?** virtiofs is a shared filesystem protocol designed specifically for virtual machines. Compared to older approaches like VirtIO-9P, it offers better performance (closer to native I/O), proper POSIX semantics, and active upstream support in modern Linux kernels.

# [02] Host-Side Setup

Create the directory that will be shared with the VM and set its permissions:

```shell
# Create the directory
sudo mkdir vm-shared

# Set permissions (read/write for all users)
sudo chmod 777 vm-shared
```

:warning: `chmod 777` is convenient for a local lab environment, but in production or multi-user systems, restrict permissions to only the users who need access.
{: .notice--warning}

# [03] virt-manager Setup

## 3-1. Open Virtual Machine Details

Two ways to open the VM details panel:

- virt-manager menu → **Edit** → **Virtual Machine Details**
- VM window menu → **View** → **Details**

## 3-2. Enable Shared Memory

Navigate to **Memory** → **Details** → check **Enable shared memory**.

:bulb: Shared memory must be enabled before virtiofs will work. This allows the host and guest to share a memory region used for fast data transfer.
{: .notice--info}

## 3-3. Add Filesystem Hardware

1. Click **Add Hardware** at the bottom of the details panel
2. Select **Filesystem**
3. Under **Details**, fill in:

| Field | Value |
|---|---|
| **Source path** | Host directory to expose (use Browse → Local Directory) |
| **Target path** | Mount tag name used inside the VM (e.g., `vm-shared`) |

4. Click **Apply**

The target path is not a real directory path inside the VM — it is a **tag name** that you reference when running the `mount` command.

# [04] VM-Side Setup

## 4-1. Create the Mount Point

Inside the VM, create the directory where the shared folder will be mounted:

```shell
# Create the mount point directory
sudo mkdir /root/vm-shared

# Set permissions
sudo chmod 777 /root/vm-shared
```

## 4-2. Mount the Shared Folder

```shell
# mount -t virtiofs <target_tag> <mount_point>
sudo mount -t virtiofs vm-shared /root/vm-shared
```

Replace `vm-shared` with the **Target path** (tag) you set in virt-manager Step 3-3.

## 4-3. Make the Mount Persistent (Optional)

To automatically mount the shared folder on every VM boot, add an entry to `/etc/fstab`:

```shell
# /etc/fstab entry
vm-shared  /root/vm-shared  virtiofs  defaults  0  0
```

Then verify:

```shell
# Test the fstab entry without rebooting
sudo mount -a

# Confirm it is mounted
df -h | grep vm-shared
```

# [05] Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `mount: unknown filesystem type 'virtiofs'` | Guest kernel too old | Upgrade kernel to 5.4+ or install `linux-modules-extra` |
| Mount succeeds but files don't appear | Wrong target tag | Verify tag in virt-manager matches `mount` command |
| Permission denied on files | UID mismatch between host and guest | Align UID/GID or use ACLs |
| Shared memory checkbox greyed out | VM is running | Shut down the VM first, then enable shared memory |
