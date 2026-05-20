---
title: "Creating a Shared Folder Between Host and VM"
description: "How to set up a shared folder between Host and VM using virtiofs in a KVM/QEMU virt-manager environment"
excerpt: "Create and mount a Host-VM shared folder via virtiofs in virt-manager"
date: 2023-09-06
categories: VM
tags: [VM, KVM, QEMU, virt-manager, shared-folder, virtiofs, Shared-Folder, Ubuntu]
ref: vm-shared-folder
---

:bulb: How to create a shared folder between a VM and the Host.
{: .notice--info}

# [01] Environment

- Ubuntu 24.04
- virt-manager, KVM, QEMU, virsh, libvirt

# [02] Host-Side Setup

```shell
# Create the directory
sudo mkdir vm-shared

# Set permissions (read/write for all users)
sudo chmod 777 vm-shared
```

# [03] virt-manager Setup

## 3-1. Open Virtual Machine Details
- virt-manager menu → Edit → Virtual Machine Details
- VM window menu → View → Details

## 3-2. Enable Shared Memory
- Memory → Details → check `Enable shared memory`

## 3-3. Add Filesystem
- Bottom `Add Hardware` → Filesystem → Details → fill Source path / Target path
  - Source path: Host directory to expose as the shared folder (use Browse → Local Directory)
  - Target path: name to use when mounting the shared folder inside the VM
- Apply

# [04] VM-Side Setup

## 4-1. Create Shared Folder

```shell
# Create the directory
sudo mkdir vm-shared

# Set permissions (read/write for all users)
sudo chmod 777 vm-shared
```

## 4-2. Mount

```shell
# mount -t type target_path vm_shared_folder_path
sudo mount -t virtiofs vm-shared /root/vm-shared
```
