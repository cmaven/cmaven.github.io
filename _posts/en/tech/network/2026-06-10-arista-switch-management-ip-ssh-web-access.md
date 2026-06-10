---
title: "Assign a Management IP to an Arista Switch and Access It via SSH and Web"
description: "Step-by-step guide to assigning an IP to an Arista EOS switch's Management interface and reaching it over SSH and the web (eAPI) from a PC on the same subnet"
excerpt: "From first console login to Management1 IP assignment, VRF check, admin account creation, SSH and eAPI (HTTPS) enablement, saving config, and testing SSH/web access from a PC — a full step-by-step walkthrough"
date: 2026-06-10
categories: Network
tags: [Arista, EOS, switch, ManagementIP, SSH, eAPI, HTTPS, VRF, network, console, CLI]
ref: arista-switch-management-ip-ssh-web-access
---

:bulb: How to assign a management IP to an Arista EOS switch and connect to it over SSH and the web (eAPI) from a PC on the same network, explained step by step.  
Environment: Arista switch (EOS) + console cable + a PC on the same subnet
{: .notice--info}

# [00] Overall Architecture

```
Management PC (192.168.1.20/24)
  │
  ├── SSH   ssh admin@192.168.1.10
  └── HTTPS https://192.168.1.10   (eAPI Explorer)
        │
        ▼
  Same L2 switch / same subnet (192.168.1.0/24)
        │
        ▼
Arista switch
  └── interface Management1 : 192.168.1.10/24
        ├── management ssh                (SSH daemon)
        └── management api http-commands  (eAPI / web UI, HTTPS)
```

:warning: **Management1 is a dedicated out-of-band management port, separate from the data ports (Ethernet1~).** Initially, connect your PC to the same subnet as the Management1 port directly, or attach it to the same L2 switch.
{: .notice--warning}

# [01] Prerequisites

| Item | Description |
|------|-------------|
| Console cable | RJ45-to-USB or serial (DB9) console cable |
| Terminal program | PuTTY, Tera Term, `screen`, `minicom`, etc. |
| Management PC | A PC with an IP on the **same subnet** as the switch |
| IPs to assign | e.g. switch `192.168.1.10/24`, PC `192.168.1.20/24` |

# [02] First Login via the Console Port

Connect the console cable to the **Console port** on the switch, then connect from your terminal with these serial settings.

```
Baud rate : 9600
Data bits : 8
Parity    : None
Stop bits : 1
Flow ctrl : None
```

> That's 9600 8N1. On Linux/macOS you can connect like this:

```bash
# Device name varies (e.g. /dev/ttyUSB0, /dev/tty.usbserial-XXXX)
screen /dev/ttyUSB0 9600
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
sw-core-01# show vrf
```

If you see a VRF like `MGMT` and Management1 belongs to it, follow the **VRF path**; if there is no VRF, follow the **default path**. Both cases are shown in the steps below.

# [05] Assign the Management IP (Management1)

```
sw-core-01# configure terminal
sw-core-01(config)# interface Management1
sw-core-01(config-if-Ma1)# ip address 192.168.1.10/24
sw-core-01(config-if-Ma1)# no shutdown
sw-core-01(config-if-Ma1)# exit
```

:bulb: Arista takes the subnet mask in **CIDR notation (`/24`)**, not `255.255.255.0`.
{: .notice--info}

# [06] Set the Default Gateway

If you only access from a PC on the same subnet, it works without a gateway, but to reach it from another network you need a default route.

**Without VRF (default):**

```
sw-core-01(config)# ip route 0.0.0.0/0 192.168.1.1
```

**When Management1 is in the MGMT VRF:**

```
sw-core-01(config)# ip route vrf MGMT 0.0.0.0/0 192.168.1.1
```

# [07] Create an Admin Account and Password

You need an account with a password for SSH/web login.

```
sw-core-01(config)# username admin privilege 15 role network-admin secret <your-password>
```

- `privilege 15` : highest privilege
- `role network-admin` : role that can run all commands
- `secret` : password stored encrypted

# [08] Enable SSH

EOS usually has SSH enabled by default, but enable it explicitly and account for the VRF.

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

# [09] Enable the Web (eAPI / HTTPS)

Arista's web UI is based on **eAPI (Command API)**, and enabling it over HTTPS is recommended.

**default VRF:**

```
sw-core-01(config)# management api http-commands
sw-core-01(config-mgmt-api-http-cmds)# protocol https
sw-core-01(config-mgmt-api-http-cmds)# no shutdown
sw-core-01(config-mgmt-api-http-cmds)# exit
```

**MGMT VRF:**

```
sw-core-01(config)# management api http-commands
sw-core-01(config-mgmt-api-http-cmds)# protocol https
sw-core-01(config-mgmt-api-http-cmds)# no shutdown
sw-core-01(config-mgmt-api-http-cmds)# vrf MGMT
sw-core-01(config-mgmt-api-http-cmds-vrf-MGMT)# no shutdown
sw-core-01(config-mgmt-api-http-cmds-vrf-MGMT)# exit
```

:warning: HTTPS uses a self-signed certificate by default, so the browser shows a security warning. On an internal management network, add an exception and proceed.
{: .notice--warning}

# [10] Save the Configuration

```
sw-core-01(config)# end
sw-core-01# write memory
```

- `write memory` = `copy running-config startup-config`
- If you don't save, the config is lost on reboot.

# [11] Test Access from the PC (Same Network)

First set your management PC's IP to the same range as the switch (e.g. `192.168.1.20/24`).

**Check connectivity (ping):**

```bash
ping 192.168.1.10
```

**SSH access:**

```bash
ssh admin@192.168.1.10
```

**Web (eAPI Explorer) access:**

Open the following address in a browser.

```
https://192.168.1.10
```

→ After getting past the self-signed certificate warning and logging in with the `admin` account, the **eAPI Explorer** opens, where you can run commands directly and inspect the JSON responses.

# [12] Status Check Commands on the Switch

```
# Check the management IP
show ip interface brief

# SSH service status
show management ssh

# eAPI (web) service status — active protocol/port/VRF
show management api http-commands

# Check VRF configuration
show vrf
```

# [13] Troubleshooting

| Symptom | What to check |
|---------|---------------|
| ping fails | Are the PC and switch on the **same subnet**? Did you `no shutdown` Management1? Is the cable in the Management port? |
| SSH refused | Did you set a password with `username ... secret`? Is it active in `show management ssh`? In a VRF, did you `no shutdown` under that VRF? |
| Web unreachable | In `show management api http-commands`, is `protocol https` active and on the right port? In a VRF, did you `no shutdown` under the VRF? |
| Unreachable from another network | Did you set the default gateway (`ip route ...`) in the correct VRF? |
| Config lost after reboot | Did you save startup-config with `write memory`? |

# [14] Summary

| Step | Where | What |
|------|-------|------|
| STEP 02 | Console | First login at 9600 8N1, log in as `admin` |
| STEP 04 | Switch CLI | `show vrf` to check whether the MGMT VRF is used |
| STEP 05 | Switch CLI | `ip address <IP>/24` + `no shutdown` on Management1 |
| STEP 06 | Switch CLI | Set the default gateway (`ip route`), with VRF if needed |
| STEP 07 | Switch CLI | Create a password account with `username admin ... secret` |
| STEP 08 | Switch CLI | Enable `management ssh` |
| STEP 09 | Switch CLI | Enable `management api http-commands` + HTTPS |
| STEP 10 | Switch CLI | Save config with `write memory` |
| STEP 11 | Management PC | Test `ssh admin@IP` / `https://IP` |
