---
title: "Resolving IP Conflicts Between Cloned VMs"
description: "How to resolve the IP conflict caused by identical machine-ids when cloning a VM in a KVM/QEMU environment"
excerpt: "After VM clone, DHCP fails because of duplicate machine-id — fix by regenerating /etc/machine-id"
date: 2024-02-29
categories: VM
tags: [VM, KVM, QEMU, Clone, DHCP, machine-id, IP-conflict, virt-manager]
ref: vm-clone-ip-share
---

:bulb: In Ubuntu / KVM / virt-manager environments, cloning a VM often causes a DHCP IP assignment failure where the new VM behaves like it shares the original's IP. This post covers how to make both VMs receive distinct IPs.
{: .notice--info}

# [01] Environment and Symptom

## Environment
- Ubuntu 24.04
- virt-manager
- KVM
- QEMU
- virsh
- libvirt

## Symptom
- Clone VM A into VM B
- VM A receives `10.10.10.10` from the DHCP server
- VM B brings its link UP but never receives an IP
- `virsh net-dhcp-leases default` shows only VM A's IP

## Root Cause

On Linux, DHCP IP assignment is **not** based on MAC address by default — it's based on `machine-id`. When you clone a VM, **both VMs end up with the same `machine-id`**.

# [02] Change the VM's machine-id

```bash
# Remove the existing machine-id
sudo rm -f /etc/machine-id

# Generate a new machine-id
dbus-uuidgen --ensure=/etc/machine-id

# Verify
cat /etc/machine-id
```

# [03] Verify After Change

Both the original and cloned VMs should now receive distinct IPs from DHCP.
