---
title: "Fix Arista ZTP Error: cannot copy to startup-config when ZeroTouch is enabled"
description: "Fix the 'cannot copy to startup-config when ZeroTouch is enabled' error and %ZTP-6-RETRY logs on an Arista EOS switch by disabling ZTP with zerotouch cancel"
excerpt: "The cause of the 'cannot copy to startup-config when ZeroTouch is enabled' error and the repeating ZTP retry logs on a factory-default Arista switch, how to fix it with zerotouch cancel, and the follow-up admin account / Management IP / SSH setup, save, and verification — a step-by-step guide"
date: 2026-06-19
categories: Network
tags: [Arista, EOS, switch, ZTP, ZeroTouch, startup-config, provisioning, network, console, CLI]
ref: arista-ztp-zerotouch-troubleshooting
---

:bulb: A step-by-step guide to resolving the `cannot copy to startup-config when ZeroTouch is enabled` error and the repeating `%ZTP-6-RETRY` logs you hit when manually configuring a factory-default Arista EOS switch — by using `zerotouch cancel`.  
Environment: a factory-default (or no-startup-config) Arista switch (EOS) + console cable
{: .notice--info}

> The hostname (`sw-core-01`), management IP (`192.0.2.110/24`), and gateway (`192.0.2.1`) in this post have been replaced with documentation example ranges (RFC 5737), and sensitive details such as passwords are masked. Substitute your own values when applying this in practice.

# [00] Overview

While doing the initial setup of an Arista switch — creating an admin account, assigning a management IP, enabling SSH — you may hit the following error when you try to save the config.

```text
cannot copy to startup-config when ZeroTouch is enabled
```

You may also see this log printed continuously on the console/terminal.

```text
%ZTP-6-RETRY: Retrying Zero Touch Provisioning from the beginning
```

For example, this is what happens when you create an account and try to save.

```
sw-core-01# configure terminal
sw-core-01(config)# username admin privilege 15 role network-admin secret ********
sw-core-01(config)# end
sw-core-01# write memory
```

But if the switch is still in Zero Touch Provisioning (ZTP) mode, it cannot save the config to `startup-config`, and the ZTP retry log keeps appearing.

:warning: In ZTP mode you **cannot save** the configuration you entered to `startup-config`. Because saving is blocked, every setting you typed is lost on reboot.
{: .notice--warning}

# [01] Cause

An Arista EOS switch boots into Zero Touch Provisioning mode when it is in a **factory-default state or has no `startup-config`**.

ZTP automatically pulls the switch configuration via DHCP, HTTP, TFTP, CloudVision, and so on to perform initial provisioning. In other words, the switch is stuck in this loop.

```text
Switch boots
   │
   ▼
No startup-config
   │
   ▼
ZeroTouch Provisioning enabled
   │
   ▼
Tries to fetch config automatically via DHCP / TFTP / HTTP / CloudVision
   │
   ▼
Fetch fails → retries from the beginning (%ZTP-6-RETRY)
```

In this state the switch has not fully switched to manual configuration mode. So even if you enter settings by hand, `write memory` or `copy running-config startup-config` fails with this error.

```text
cannot copy to startup-config when ZeroTouch is enabled
```

# [02] Fix at a Glance

To configure an Arista switch manually, you must first cancel ZTP. There is just one key command.

```
zerotouch cancel
```

The typical resolution order is as follows.

```text
1. Log in to the console as admin
2. Enter enable mode
3. Run zerotouch cancel
4. Reboot the switch (may happen automatically)
5. After reboot, do the manual configuration
6. Run write memory or copy running-config startup-config
```

:bulb: `zerotouch cancel` disables ZTP mode and creates an empty `startup-config`, so you can save your configuration normally afterward.
{: .notice--info}

# [03] Canceling ZTP

Connect to the factory-default Arista switch over the console, then run the following (the initial account is usually `admin`, with no password).

```
localhost login: admin

localhost> enable
localhost# zerotouch cancel
```

Running `zerotouch cancel` may reboot the switch. Log back in after the reboot.

```
localhost login: admin

localhost> enable
localhost#
```

From here you can proceed with normal manual configuration.

# [04] Admin Account / Management IP / SSH Setup Example

This is an example of applying basic management settings after canceling ZTP. Replace `<password>`, `<mgmt-IP>`, `<prefix>`, and `<gateway>` to match your environment.

```
localhost# configure terminal

localhost(config)# hostname sw-core-01

sw-core-01(config)# username admin privilege 15 role network-admin secret <password>

sw-core-01(config)# interface Management1
sw-core-01(config-if-Ma1)# ip address <mgmt-IP>/<prefix>
sw-core-01(config-if-Ma1)# no shutdown
sw-core-01(config-if-Ma1)# exit

sw-core-01(config)# ip route 0.0.0.0/0 <gateway>

sw-core-01(config)# management ssh
sw-core-01(config-mgmt-ssh)# no shutdown
sw-core-01(config-mgmt-ssh)# exit

sw-core-01(config)# end
```

Here is the same example with real values filled in.

```
sw-core-01# configure terminal

sw-core-01(config)# username admin privilege 15 role network-admin secret ********

sw-core-01(config)# interface Management1
sw-core-01(config-if-Ma1)# ip address 192.0.2.110/24
sw-core-01(config-if-Ma1)# no shutdown
sw-core-01(config-if-Ma1)# exit

sw-core-01(config)# ip route 0.0.0.0/0 192.0.2.1

sw-core-01(config)# management ssh
sw-core-01(config-mgmt-ssh)# no shutdown
sw-core-01(config-mgmt-ssh)# exit

sw-core-01(config)# end
```

:bulb: The full procedure for assigning a management IP and connecting over SSH (including the VRF check and connection test) is covered in more detail in the separate post "Assign a Management IP to an Arista Switch and Access It via SSH."
{: .notice--info}

# [05] Saving the Configuration

After canceling ZTP, saving the config should work normally.

```
sw-core-01# write memory
```

Or you can spell out the equivalent command.

```
sw-core-01# copy running-config startup-config
```

On a successful save you see the following message.

```text
Copy completed successfully.
```

- `write memory` = `copy running-config startup-config`
- If you don't save, the config is lost on reboot.

# [06] Verification Commands

## [06-1] Check startup-config

```
sw-core-01# show startup-config
```

If the config has been saved, you'll see the hostname, username, Management1 IP, SSH settings, and so on. Before ZTP is canceled, this output is empty.

## [06-2] Check running-config

```
sw-core-01# show running-config
```

Shows the currently active configuration.

## [06-3] Check ZTP status

The supported command may differ by EOS version, but you can check ZTP status with the following.

```
sw-core-01# show zerotouch
```

Or check for ZTP-related messages in the log.

```
sw-core-01# show logging | include ZTP|ZeroTouch
```

If ZTP was canceled properly, the following repeating log no longer appears.

```text
%ZTP-6-RETRY: Retrying Zero Touch Provisioning from the beginning
```

# [07] Troubleshooting Checklist

If the problem persists even after running `zerotouch cancel`, check the items below.

| Symptom | What to check |
|---------|---------------|
| Still the ZTP error on save | Run `show startup-config` to confirm a startup-config was created. If empty, re-run `zerotouch cancel` and reboot |
| `%ZTP-6-RETRY` keeps repeating | Check with `show logging \| include ZTP` → if it still occurs, re-run `zerotouch cancel` |
| Config gone after reboot | Confirm you saved with `write memory` and that it ended with `Copy completed successfully.` |
| Re-enters ZTP after reboot | If startup-config is empty or missing, the switch can re-enter ZTP mode on reboot → always save after entering config |

The corresponding check commands are as follows.

```
# Does a startup-config exist?
sw-core-01# show startup-config

# Retry saving the config
sw-core-01# copy running-config startup-config

# Is ZTP active again?
sw-core-01# show logging | include ZTP|ZeroTouch

# Cancel again if it recurs
sw-core-01# zerotouch cancel

# Confirm config persists after reboot
sw-core-01# reload
sw-core-01# show running-config
sw-core-01# show startup-config
```

# [08] Summary

| Step | Where | What |
|------|-------|------|
| STEP 03 | Console | Log in as `admin` → `enable` → `zerotouch cancel` |
| - | Switch | (automatic) reboot, empty startup-config created |
| STEP 04 | Switch CLI | Set hostname / username / Management1 IP / SSH |
| STEP 05 | Switch CLI | Save with `write memory` (`Copy completed successfully.`) |
| STEP 06 | Switch CLI | Verify ZTP cancel and save with `show startup-config` / `show zerotouch` |

The point is simple. If you hit the following error or log, the switch is still in ZTP mode.

```text
cannot copy to startup-config when ZeroTouch is enabled
%ZTP-6-RETRY: Retrying Zero Touch Provisioning from the beginning
```

The fix is a single line, `zerotouch cancel`. After the reboot, configure the admin account, Management IP, and SSH, then save with `write memory`. If you plan to manage an Arista switch manually, the most important thing is to **cancel ZTP first, during the initial setup**.

# [09] Command Reference

```
enable
zerotouch cancel
configure terminal
hostname sw-core-01
username admin privilege 15 role network-admin secret <password>
interface Management1
ip address <mgmt-IP>/<prefix>
no shutdown
exit
ip route 0.0.0.0/0 <gateway>
management ssh
no shutdown
exit
end
write memory
show startup-config
show running-config
show zerotouch
show logging | include ZTP|ZeroTouch
```
