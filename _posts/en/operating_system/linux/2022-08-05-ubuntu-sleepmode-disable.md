---
title: "Disabling Suspend/Sleep Mode on Ubuntu"
description: "How to permanently disable Suspend, Sleep, Hibernate, and Hybrid-Sleep on Ubuntu Server and Desktop using systemctl mask, with verification steps and revert instructions."
excerpt: "Use systemctl mask to disable Ubuntu's power-saving modes (Suspend/Sleep/Hibernate) and prevent SSH session drops on headless servers."
categories: Linux
tags: [Ubuntu, Suspend, Sleep, power-saving, SSH, systemctl, Power-Management, Hibernate, server]
date: 2022-08-05
last_modified_at: 2026-05-26
ref: ubuntu-sleepmode-disable
---

:bulb: This post describes how to prevent Ubuntu Server or Desktop from entering Suspend, Sleep, Hibernate, or Hybrid-Sleep mode — and how to verify the change and revert it if needed. The fix is essential for any machine accessed remotely over SSH.
{: .notice--info}

# [01] Environment and Situation

- **OS**: Ubuntu 22.04 / 24.04 (Server or Desktop)
- **Symptom**: SSH connection drops after a period of inactivity and cannot be re-established without physical access or a reboot
- **Cause**: The system enters Suspend or Sleep mode, suspending all network interfaces and terminating active sessions

This problem is most common on:

| Use case | Why it hurts |
|---|---|
| Headless home or office server | No monitor or keyboard — impossible to wake remotely |
| Ubuntu Desktop used as a dev server | Desktop power settings are active even when logged out |
| CI / build runner on bare metal | Long builds trigger inactivity timeout mid-job |
| Remote NAS or media server | Sleep drops NFS/Samba shares for all clients |

# [02] Understanding the Sleep Targets

Ubuntu's power-saving behaviour is managed by **systemd** through four sleep targets. Understanding each target helps you decide which ones to disable.

| Target | Triggered by | What it does |
|---|---|---|
| `sleep.target` | Any sleep operation | Parent target — reached before the specific sleep type |
| `suspend.target` | Lid close, inactivity timeout | RAM stays powered (S3 state); wake is fast |
| `hibernate.target` | Manual command or critical battery | RAM written to swap, then power cut; wake is slow |
| `hybrid-sleep.target` | Manual command | RAM stays powered AND written to swap; tolerates power loss |
| `suspend-then-hibernate.target` | Long inactivity | Suspends first, then hibernates after a delay |

By default, Ubuntu 22.04/24.04 enables all of these. You can check their current status with:

```shell
sudo systemctl status sleep.target suspend.target hibernate.target hybrid-sleep.target
```

![power management-sleep enabled](https://user-images.githubusercontent.com/76153041/183005465-418ea20e-4229-4e70-9838-447938d540d5.png)

*Figure 1. Default status — all four sleep targets are **active** and will respond to sleep requests from the system or desktop environment.*

The output shows each target as `active` with `Loaded: loaded` and no masking. Any power event (inactivity timer, lid close, `systemctl suspend`) can start these targets.

# [03] Disabling Sleep — systemctl mask

The recommended way to permanently disable the sleep targets is **masking**. Masking symlinks the unit file to `/dev/null`, which prevents systemd from starting the target under any circumstance — including requests from desktop environments, power daemons (UPower, logind), or `systemctl suspend`.

```shell
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

![power management-sleep disabled](https://user-images.githubusercontent.com/76153041/183005473-63e6011d-c292-4269-b30c-492421716a7f.png)

*Figure 2. After masking — each target reports `Loaded: masked` and `Unit sleep.target is masked`, meaning no process can start it.*

### Why mask instead of disable?

| Method | Effect | Can be overridden by? |
|---|---|---|
| `systemctl disable` | Removes the start symlinks from `multi-user.target` | A service that `Wants=suspend.target` can still start it |
| `systemctl mask` | Symlinks the unit to `/dev/null` — the unit cannot start at all | Nothing — masking is absolute |

For a server that must never sleep, `mask` is the correct choice.

# [04] Verifying the Change

After masking, confirm that the targets are truly inactive:

```shell
sudo systemctl status sleep.target suspend.target hibernate.target hybrid-sleep.target
```

Each target should now show:

```text
Loaded: masked (/dev/null; bad)
Active: inactive (dead)
```

You can also verify that `logind` (the daemon that triggers sleep on lid close or inactivity) will no longer act:

```shell
cat /etc/systemd/logind.conf | grep -i sleep
# Should show HandleSuspendKey=ignore or similar if you set it,
# but masking the targets is sufficient — logind cannot start a masked unit.
```

To test without rebooting, try issuing a manual suspend request and confirm it is blocked:

```shell
sudo systemctl suspend
# Expected: Failed to suspend system via logind: Sleep verb "suspend" is not supported
```

# [05] Re-enabling Sleep (Revert)

If you later need to restore the default sleep behaviour — for example, when repurposing the machine as a laptop or desktop — unmask all four targets:

```shell
sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

![power management-sleep re-enabled](https://user-images.githubusercontent.com/76153041/183005471-63c1ffe9-ee7d-47fd-bcd6-f57c585722f8.png)

*Figure 3. After unmasking — the targets return to their default `active` state and the system will respond to sleep requests again.*

The change takes effect immediately; no reboot is required.

# [06] Notes and Troubleshooting

| Topic | Detail |
|---|---|
| **Persistence** | `mask` / `unmask` writes to `/etc/systemd/system/` and survives reboots and OS minor updates |
| **Desktop environment override** | GNOME Power Settings and similar GUIs call `logind`, which calls systemd — masking the targets blocks this path too |
| **Screen blanking is separate** | Masking sleep targets does not prevent the display from turning off. Disable screen blanking via DPMS: `xset -dpms && xset s off` |
| **Swap/hibernation dependency** | If you unmask `hibernate.target` but have no swap space (common on cloud VMs), hibernation will fail — ensure swap exists first |
| **Ubuntu Server minimal** | On a server install without a desktop environment, only `suspend.target` is typically triggered; masking all four is still recommended for completeness |
| **SSH still drops after fix** | If sessions drop even after masking, check `ClientAliveInterval` / `ServerAliveInterval` in `/etc/ssh/sshd_config` — the issue may be a TCP keepalive timeout, not sleep |
