---
title: "Resolving IP Conflicts Between Cloned VMs"
description: "How to resolve the IP conflict caused by identical machine-ids when cloning a VM in a KVM/QEMU environment"
excerpt: "After VM clone, DHCP fails because of duplicate machine-id — fix by regenerating /etc/machine-id"
date: 2024-02-29
last_modified_at: 2026-05-26
categories: VM
tags: [VM, KVM, QEMU, Clone, DHCP, machine-id, IP-conflict, virt-manager]
ref: vm-clone-ip-share
---

:bulb: In Ubuntu / KVM / virt-manager environments, cloning a VM often causes a DHCP IP assignment failure where the new VM behaves like it shares the original's IP. This post covers how to make both VMs receive distinct IPs.
{: .notice--info}

# [01] Environment and Symptom

## Environment

| Component | Details |
|---|---|
| Host OS | Ubuntu 24.04 |
| Hypervisor | KVM + QEMU |
| Manager | virt-manager, virsh, libvirt |

## Symptom

1. Clone VM A into VM B
2. VM A receives `10.10.10.10` from the DHCP server
3. VM B brings its network link UP, but **never receives an IP**
4. `virsh net-dhcp-leases default` shows only VM A's entry

```shell
$ virsh net-dhcp-leases default
 Expiry Time           MAC address         Protocol   IP address        Hostname
 2024-02-29 10:00:00   52:54:00:aa:bb:cc   ipv4       10.10.10.10/24    vm-a
```

VM B does not appear in the lease table at all, even though its NIC is active.

## Root Cause

On Linux, DHCP IP assignment is **not** based on MAC address by default — it is based on `machine-id` (defined in `/etc/machine-id`).

When you clone a VM, the entire disk image is copied, including `/etc/machine-id`. Both VMs end up with the **identical machine-id**, so the DHCP server treats them as the same client and assigns only one IP.

```shell
# On VM A
$ cat /etc/machine-id
a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4

# On VM B (cloned from VM A — same ID)
$ cat /etc/machine-id
a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4
```

# [02] Fix — Regenerate machine-id on the Cloned VM

Run the following commands **inside VM B** (the clone):

```bash
# Remove the existing machine-id
sudo rm -f /etc/machine-id

# Generate a new unique machine-id
dbus-uuidgen --ensure=/etc/machine-id

# Verify the new ID was written
cat /etc/machine-id
```

After regeneration, VM B will have a different `machine-id` from VM A.

## Why dbus-uuidgen?

`dbus-uuidgen --ensure` writes a new UUID to the file only if it is missing or empty — making it safe to run without worrying about accidentally overwriting a valid ID. It uses the D-Bus UUID format, which is compatible with `systemd-machine-id-setup` expectations on modern Ubuntu.

Alternatively, you can use `systemd-machine-id-setup`:

```bash
# systemd-based alternative
sudo systemd-machine-id-setup
```

Both approaches produce a valid, unique machine-id.

# [03] Verify After Change

After regenerating the machine-id, reboot VM B and check DHCP lease assignment:

```shell
# On VM B — reboot to trigger a fresh DHCP request
sudo reboot
```

After reboot, both VMs should appear in the DHCP lease table with distinct IPs:

```shell
$ virsh net-dhcp-leases default
 Expiry Time           MAC address         Protocol   IP address        Hostname
 2024-02-29 10:05:00   52:54:00:aa:bb:cc   ipv4       10.10.10.10/24    vm-a
 2024-02-29 10:05:00   52:54:00:dd:ee:ff   ipv4       10.10.10.11/24    vm-b
```

# [04] Preventing the Problem at Clone Time

To avoid this issue entirely for future clones, clear the machine-id **before** taking a snapshot or template image:

```bash
# Run inside the template VM before cloning
sudo truncate -s 0 /etc/machine-id
sudo rm -f /var/lib/dbus/machine-id
```

When the cloned VM first boots, `systemd` will automatically generate a fresh machine-id.

# [05] Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Clone still gets no IP after fix | `/var/lib/dbus/machine-id` also duplicated | Remove it: `sudo rm -f /var/lib/dbus/machine-id` |
| DHCP works but IP is same as original | Old lease not expired | Wait for lease expiry or flush: `sudo dhclient -r && sudo dhclient` |
| `dbus-uuidgen` not found | dbus not installed | `sudo apt-get install dbus` |
| machine-id file is empty after reboot | systemd regenerated it correctly | Normal behavior — check `cat /etc/machine-id` again |
