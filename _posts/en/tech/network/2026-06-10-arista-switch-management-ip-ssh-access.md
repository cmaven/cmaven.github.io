---
title: "Assign a Management IP to an Arista Switch and Access It via SSH"
description: "Step-by-step guide to assigning an IP to an Arista EOS switch's Management interface and reaching it over SSH from a PC on the same subnet, illustrated with real device output"
excerpt: "From first console login to Management1 IP assignment, VRF check, admin account creation, confirming SSH is enabled, saving config, and testing SSH access from a PC — a full step-by-step walkthrough with real device output"
date: 2026-06-10
categories: Network
tags: [Arista, EOS, switch, ManagementIP, SSH, VRF, network, console, CLI]
ref: arista-switch-management-ip-ssh-access
---

:bulb: How to assign a management IP to an Arista EOS switch and connect to it over SSH from a PC on the same network, explained step by step with real device output.  
Environment: Arista switch (EOS) + console cable + a PC on the same subnet
{: .notice--info}

> The CLI output in this post is drawn from real work on an actual device (`DCS-7050SX3-48YC8C-F`, hostname `sw-core-01`), where `10.254.202.110/24` was assigned to `Management1` so the switch could be reached over SSH from the `10.254.202.0/24` management network. Sensitive details such as passwords are masked.

# [00] Overall Architecture

```
Management PC (10.254.202.20/24)
  │
  └── SSH   ssh admin@10.254.202.110
        │
        ▼
  Same L2 switch / same subnet (10.254.202.0/24)
        │
        ▼
Arista switch (sw-core-01)
  └── interface Management1 : 10.254.202.110/24
        └── management ssh   (SSH daemon, Default VRF)
```

:warning: **Management1 is a dedicated out-of-band management port, separate from the data ports (Ethernet1~).** Initially, connect your PC to the same subnet as the Management1 port directly, or attach it to the same L2 switch.
{: .notice--warning}

# [01] Prerequisites

| Item | Description |
|------|-------------|
| Console cable | RJ45-to-USB or serial (DB9) console cable |
| Terminal program | PuTTY, Tera Term, `screen`, `tio`, etc. |
| Management PC | A PC with an IP on the **same subnet** as the switch |
| IPs to assign | e.g. switch `10.254.202.110/24`, PC `10.254.202.20/24` |

# [02] First Login via the Console Port

Connect the console cable to the **Console port** on the switch, then connect from your terminal with these serial settings.

```
Baud rate : 9600
Data bits : 8
Parity    : None
Stop bits : 1
Flow ctrl : None
```

> That's 9600 8N1. On Windows use PuTTY/Tera Term; on Linux (Ubuntu)/macOS, use `screen` or `tio` as shown below.

## [02-1] Identify the USB Serial Device on Ubuntu

When you plug a USB-to-serial (console) cable into the PC, it usually appears as `/dev/ttyUSB0` (FTDI/PL2303 family) or `/dev/ttyACM0` (CDC-ACM family). Find out which name it got first.

```bash
# Right after plugging in the cable, check the newly created serial device
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null

# Confirm the device name from kernel messages at plug-in time (most reliable)
dmesg | grep -iE 'ttyUSB|ttyACM|usb' | tail -n 20

# Check the serial chip (FTDI, Prolific, etc.) in the USB device list
lsusb
```

> If `dmesg` shows a line like `FTDI USB Serial Device converter now attached to ttyUSB0`, that device is your console cable. Comparing `ls` before and after plugging in immediately reveals the new device.

:warning: A regular user account may lack serial-port access and hit `Permission denied`. Add your user to the `dialout` group to connect without sudo (re-login required).
{: .notice--warning}

```bash
# Add the current user to the dialout group, then log out → log in (or reboot)
sudo usermod -aG dialout $USER

# As a temporary workaround you can also just run with sudo
```

## [02-2] Connect with screen

The lightest-weight option.

```bash
# Install (Ubuntu/Debian)
sudo apt update
sudo apt install -y screen

# Connect: screen <device> <baud>
screen /dev/ttyUSB0 9600
```

- If the screen is blank, press **Enter** once to wake the prompt.
- Quit: `Ctrl + a` then `k` → `y` (or `Ctrl + a`, `\`).
- Detach (keep session): `Ctrl + a` then `d`; reattach with `screen -r`.

## [02-3] Connect with tio

A modern serial terminal with clean command-line options that **auto-reconnects when the device is unplugged and plugged back in**. Handy when you attach to device consoles often.

```bash
# Install (in the default repos on Ubuntu 22.04+)
sudo apt update
sudo apt install -y tio

# Connect: tio defaults to 115200, so specify 9600 explicitly
tio -b 9600 /dev/ttyUSB0
```

- If the screen is blank, press **Enter** once to wake the prompt.
- Every shortcut uses `Ctrl + t` as the prefix key. Quit: `Ctrl + t` then `q`.
- List shortcuts: `Ctrl + t` then `?`.
- Frequently used settings can be saved as a profile (`/etc/tio/config` or `~/.config/tio/config`).

```ini
# e.g. ~/.config/tio/config — connect instantly with "tio arista"
[arista]
device = /dev/ttyUSB0
baudrate = 9600
```

Once connected, log in with the default `admin` account (no initial password). The prompt appears as `switch>` or `switch login:`.

```
switch login: admin
switch>
```

# [03] Enter Enable Mode and Set the Hostname

```
switch> enable
switch# configure terminal
switch(config)# hostname sw-core-01
sw-core-01(config)#
```

- `enable` : enter privileged (EXEC) mode
- `configure terminal` : enter global configuration mode

# [04] Check the VRF (Important)

On recent EOS versions, the Management1 interface often belongs to a separate VRF (usually named `MGMT`). **The location of routes and service enablement depends on whether a VRF is used, so check first.**

```
sw-core-01# show ip route vrf MGMT
% IP Routing table for VRF MGMT does not exist.
```

On this device, the `MGMT` VRF routing table **did not exist**, as shown above. That means `Management1` operates in the **Default VRF**, not a separate management VRF. When accessing from the same `10.254.202.0/24` range, it communicates via the connected route without any extra routes.

> Conversely, if `show vrf` lists a VRF like `MGMT` and Management1 belongs to it, follow the **VRF path**; if there is no VRF, follow the **default path**. Both cases are shown in the steps below.

# [05] Assign the Management IP (Management1)

First, checking `Management1` before the work shows the physical link is up but no IP is assigned.

```
sw-core-01# show ip interface Management1
Management1 is up, line protocol is up (connected)
  No Internet protocol address assigned
  IPv6 Interface Forwarding : None
  IP MTU 1500 bytes
```

> The key line is `No Internet protocol address assigned`. The physical link (`up, line protocol is up (connected)`) is fine, so you only need to assign an IP.

Now assign the IP and bring up the interface.

```
sw-core-01# configure terminal
sw-core-01(config)# interface Management1
sw-core-01(config-if-Ma1)# ip address 10.254.202.110/24
sw-core-01(config-if-Ma1)# no shutdown
sw-core-01(config-if-Ma1)# exit
```

:bulb: Arista takes the subnet mask in **CIDR notation (`/24`)**, not `255.255.255.0`.
{: .notice--info}

Checking again after the change confirms the IP is applied.

```
sw-core-01# show ip interface Management1
Management1 is up, line protocol is up (connected)
  Internet address is 10.254.202.110/24
  Broadcast address is 255.255.255.255
  IPv6 Interface Forwarding : None
  Proxy-ARP is disabled
  Local Proxy-ARP is disabled
  Gratuitous ARP is ignored
  IP MTU 1500 bytes

sw-core-01# show running-config interfaces Management1
interface Management1
   ip address 10.254.202.110/24
```

# [06] Set the Default Gateway

If you only access from a PC on the same subnet, it works without a gateway (that was the case in this work). To reach it from another network, set a default route.

**Without VRF (default):**

```
sw-core-01(config)# ip route 0.0.0.0/0 10.254.202.1
```

**When Management1 is in the MGMT VRF:**

```
sw-core-01(config)# ip route vrf MGMT 0.0.0.0/0 10.254.202.1
```

:warning: The gateway address above (`10.254.202.1`) is an example. **Confirm your actual management gateway address** before applying it.
{: .notice--warning}

# [07] Create an Admin Account and Password

You need an account with a password for SSH login.

```
sw-core-01# configure terminal
sw-core-01(config)# username admin privilege 15 role network-admin secret ********
sw-core-01(config)# end
sw-core-01# write memory
Copy completed successfully.
```

- `privilege 15` : highest privilege
- `role network-admin` : role that can run all commands
- `secret` : password stored encrypted (masked as `********` above for security)

# [08] Confirm SSH Is Enabled

EOS usually has SSH enabled by default. In fact, on this device the SSHD was already on in the Default VRF with no extra configuration.

```
sw-core-01# show management ssh
SSHD status for Default VRF is enabled
SSH connection limit is 50
SSH per host connection limit is 20
FIPS status: disabled
```

> The key line is `SSHD status for Default VRF is enabled`. In this state, once the `Management1` IP and a local account are ready, you can test SSH access right away.

If SSH is off, or you want to enable it explicitly, or you need to account for a VRF, configure it as below.

**default VRF:**

```
sw-core-01(config)# management ssh
sw-core-01(config-mgmt-ssh)# no shutdown
sw-core-01(config-mgmt-ssh)# exit
```

**MGMT VRF (when management traffic arrives over the MGMT VRF):**

```
sw-core-01(config)# management ssh
sw-core-01(config-mgmt-ssh)# no shutdown
sw-core-01(config-mgmt-ssh)# vrf MGMT
sw-core-01(config-mgmt-ssh-vrf-MGMT)# no shutdown
sw-core-01(config-mgmt-ssh-vrf-MGMT)# exit
```

# [09] Save the Configuration

```
sw-core-01(config)# end
sw-core-01# write memory
Copy completed successfully.
```

- `write memory` = `copy running-config startup-config`
- If you don't save, the config is lost on reboot.

# [10] Test Access from the PC (Same Network)

First set your management PC's IP to the same range as the switch (e.g. `10.254.202.20/24`).

**Check connectivity (ping):**

```bash
ping 10.254.202.110
```

**SSH access:**

```bash
ssh admin@10.254.202.110
```

→ After entering the `admin` account password, you log in at the `sw-core-01>` prompt. With a privilege 15 account, elevated rights may apply right after login.

# [11] Status Check Commands on the Switch

```
# Check the management IP
show ip interface brief
show ip interface Management1

# Interface physical/link status
show interfaces Management1

# SSH service status
show management ssh

# Check VRF configuration
show vrf
show ip route vrf MGMT
```

# [12] Troubleshooting

| Symptom | What to check |
|---------|---------------|
| ping fails | Are the PC and switch on the **same subnet**? Did you `no shutdown` Management1? Is the cable in the Management port? Any IP conflict? |
| SSH refused | Did you set a password with `username ... secret`? Is it active in `show management ssh`? In a VRF, did you `no shutdown` under that VRF? Is an SSH access ACL blocking it? |
| Unreachable from another network | Did you set the default gateway (`ip route ...`) in the correct VRF? Check the real routing with `show ip route` / `show vrf`. |
| Config lost after reboot | Did you save startup-config with `write memory`? |

# [13] Summary

| Step | Where | What |
|------|-------|------|
| STEP 02 | Console | First login at 9600 8N1, log in as `admin` |
| STEP 04 | Switch CLI | `show ip route vrf MGMT` / `show vrf` to check whether the MGMT VRF is used (this device uses the Default VRF) |
| STEP 05 | Switch CLI | `ip address 10.254.202.110/24` + `no shutdown` on Management1 |
| STEP 06 | Switch CLI | Set the default gateway (`ip route`) for cross-network access, with VRF if needed |
| STEP 07 | Switch CLI | Create a password account with `username admin ... secret` |
| STEP 08 | Switch CLI | Confirm SSHD is active with `show management ssh` (enable `management ssh` if needed) |
| STEP 09 | Switch CLI | Save config with `write memory` |
| STEP 10 | Management PC | Test `ssh admin@10.254.202.110` |
