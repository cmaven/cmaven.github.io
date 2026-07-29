---
title: "Building Remote Hardware Monitoring over an Isolated BMC/IPMI Network — Bastion, VLANs, Channels, Read-Only Accounts"
description: "Standardizing the BMC/IPMI addresses of an on-prem bare-metal cluster into one management network and exposing hardware state (temperature, fans, power, SEL) to an external partner as read-only via a bastion leg — solving duplicate BMC IPs, an unreachable isolated network, silent switch VLAN isolation, LAN channel/cipher-suite mismatches, and a hung BMC firmware along the way"
excerpt: "What looked like 'create an account and hand over an IP' turned into a stack of problems — duplicate/unset BMC IPs, no host with a foot in the isolated network, switch VLAN isolation, a cable plugged into a different LAN channel, and a hung BMC — solved with in-band configuration, a bastion leg, LLDP diagnostics, USER-privilege accounts, and an AC power drain"
date: 2026-07-29
categories: Network
tags: [BMC, IPMI, ipmitool, OOB, bastion, VLAN, LLDP, tcpdump, hardware-monitoring, read-only, CipherSuite, SEL, Prometheus, ipmi-exporter]
ref: bmc-ipmi-remote-hardware-monitoring
---

:bulb: This post walks through the concepts, problems, and fixes from a project that exposed the hardware state (power, temperature, fans, energy) of an on-prem bare-metal cluster to an external partner organization as **read-only**. All identifying details — IPs, MACs, organization names — have been replaced with documentation ranges/pseudonyms: IPMI management network `10.20.0.0/24`, node internal network `10.10.0.0/24`, external partner network `203.0.113.0/29`, monitoring account `hwmon`, partner "PartnerOrg".  
Audience: server/infra engineers opening up out-of-band (OOB) management on bare-metal servers for the first time
{: .notice--info}

# [00] Background Concepts — BMC, IPMI, in-band/OOB, bastion

Four terms are all you need to follow this story.

## [00-1] BMC (Baseboard Management Controller)

A **separate tiny management computer** attached to the server motherboard. It runs independently of the host OS and is **always on as long as standby power is present**. Vendor brand names differ — iDRAC (Dell), iLO (HPE), BMC (Intel/Supermicro) — but the job is the same: power on/off/reset, reading temperature/fan/voltage/power sensors, the hardware event log (SEL), and remote console. All of it works **even when the OS is dead**.

## [00-2] IPMI (Intelligent Platform Management Interface)

The **standard protocol** for talking to a BMC. `ipmitool` is the de facto standard client.

## [00-3] in-band vs out-of-band (OOB) — the two ways to reach a BMC

| Method | Path | Characteristics |
|---|---|---|
| in-band | From **inside that server's OS**, over the motherboard's internal bus (KCS) to its own BMC (`/dev/ipmi0`) | No IP or credentials needed. But the OS must be up |
| out-of-band | **Over the network** to the BMC's IP (RMCP+, UDP 623) | Needs a BMC IP, credentials, and a network path. Works even when the node's OS is down |

One key property: **the BMC lives outside the OS, so it never shows up in Linux `ip addr`.** It is reachable only at its own IP, through a dedicated management NIC (a physically separate port from the data NICs).

## [00-4] bastion (gateway host)

BMCs are usually attached only to a **dedicated network isolated from everything else** (the IPMI network). It is isolated on purpose — security and stability — so you cannot reach it directly from outside. A bastion is the **single gateway server** into that isolated network: one foot in the network users connect to, the other foot in the isolated IPMI network. Users only ever reach the bastion, and run `ipmitool` on the bastion to talk to the BMCs.

> For where IPMI/BMC sits in the bigger infrastructure picture (management-path redundancy), see the IPMI/BMC section of the [switch redundancy concepts post](/en/Network/switch-redundancy-network-concepts/).

---

# [01] Why — the Case for BMC Monitoring

An external partner (PartnerOrg) wanted to **check the hardware state of our physical nodes themselves**. VM/container metrics (k8s, OpenStack) were already visible through Prometheus, but that's the **software level**. What they actually needed was the layer below — **physical server temperature, fans, power draw, power state, and hardware events**.

The source of that information is the BMC. And the requirement was **read-only**: no dangerous privileges like power control or console — sensor values only.

Two approaches were possible:

- **in-band exporter**: each node reads its own BMC locally and publishes to Prometheus. No BMC network or credentials needed. But when a node's OS goes down, the data stops.
- **out-of-band (remote)**: a collector connects to BMC IPs and reads them. Collection continues even when nodes are off. But it requires the BMC network and credentials.

Because the partner wanted to **run `ipmitool` with their own hands**, we chose the OOB path plus read-only accounts. That decision caused most of the problems that followed — OOB means you must **actually reach the isolated BMC network**.

---

# [02] Current State — the Problems We Dug Up

I assumed it would be "create an account, hand over an IP, done." In reality the problems were stacked in layers.

**(1) BMC IPs were inconsistent and duplicated.**
Surveying the BMC IPs of 15 nodes, many were set to the **same (duplicate) IP** or not set at all. Different subnets (`10.20.0.x` and `10.30.0.x`) were mixed together. In that state they couldn't be tied into one management network.

**(2) There was no host that could reach the isolated IPMI network.**
Every BMC hung off the isolated switch via a **dedicated management NIC**. Critically, **not a single server OS had a foot in that isolated network.** Nodes couldn't even ping their own BMCs (dedicated NIC — separate from the OS). So no matter how correctly the BMC IPs were set, they were **reachable from nowhere**.

**(3) The switch was silently splitting things with VLANs.**
We plugged a spare NIC of the bastion candidate node into the isolated switch and gave it an IP — still no BMC responded. The link LED was on. The cause was **VLAN isolation on the switch**: the bastion port and the BMC ports sat in different VLANs.

**(4) One server's BMC was cabled to a different channel.**
Most nodes had their BMC LAN on channel 1, but one server (an Intel board) had **its cable plugged into channel 3 (the dedicated management port)**. Setting an IP on channel 1 got no response. On top of that, the channel's **standard cipher suite (suite 3) was disabled**, so even with the right IP, no authenticated session would open.

**(5) One BMC's firmware was frozen solid.**
On one node, even in-band `ipmitool mc info` timed out. `/dev/ipmi0` existed and the kernel modules were fine, but the BMC chip wasn't answering. **The BMC firmware itself had hung.** Because the BMC runs on standby power, rebooting the server does not clear it.

---

# [03] Fix 1 — Standardizing BMC IPs (in-band)

We unified every node's BMC IP into a single subnet, `10.20.0.0/24`. The important property here: **BMC IP configuration works in-band, with no network at all.** On each node:

```bash
sudo ipmitool lan set 1 ipsrc static
sudo ipmitool lan set 1 ipaddr 10.20.0.1X       # per node
sudo ipmitool lan set 1 netmask 255.255.255.0
sudo ipmitool lan set 1 access on
```

The key was that even while the BMC network was still unreachable, we could reconfigure the BMCs from inside each server (over KCS).

---

# [04] Fix 2 — Giving the Bastion a Leg into the Isolated Network

The "no host in the isolated network" problem is solved by **plugging one spare NIC of the gateway node into the IPMI switch** and putting an IP (`10.20.0.254`) on it. That leg becomes the single entry point.

```bash
sudo ip addr add 10.20.0.254/24 dev <spare NIC> && sudo ip link set <spare NIC> up
# persist across reboots via netplan/systemd
```

> Caution: if the gateway is a Kubernetes node, do not force `ip_forward=0` (it breaks pod routing). Block direct external↔BMC routing with the firewall instead.

---

# [05] Diagnostics — "Link Is Up but Nothing Answers"

This is where I learned the most. When the leg is plugged in but no BMC shows up, **ask the switch directly**:

## [05-1] Who is on this L2 — passive capture

```bash
sudo tcpdump -i <leg> -ne not stp
```

If all you see is the switch's STP and zero BMC frames, the BMCs are not in the same broadcast domain.

## [05-2] What VLAN is this port in — LLDP

Every 30 seconds the switch advertises its name, port, and PVID out of each port.

```bash
sudo tcpdump -i <leg> -v ether proto 0x88cc
```

A value like `Port VLAN Id (PVID): 40` pops right out. That's not a guess — **the switch is telling you itself.** This is how we confirmed "the bastion port is in VLAN 40, the BMCs are in a different VLAN."

## [05-3] Which channel's port is the cable actually in

BMC dedicated ports are invisible to the OS. Temporarily assign a distinguishing IP to each channel and check ARP from the bastion — **the channel whose IP answers is the port the cable is actually plugged into.**

The VLAN problem was fixed by putting the bastion port and BMC ports into the same VLAN on the switch; the channel problem by moving the IP to the channel the cable was really in (channel 3) and re-enabling the standard cipher suite on that channel.

---

# [06] Fix 3 — Read-Only Accounts and the Privilege Model

`ipmitool` is just a tool; what is actually possible is determined by the **BMC account's privilege level** and enforced by the BMC firmware.

| priv | Name | Allows |
|---|---|---|
| 2 | USER | Sensors, SDR, SEL, status — **read only** |
| 3 | OPERATOR | + power control |
| 4 | ADMIN | + account/channel configuration, remote console |

For the partner we created a **USER (2) account `hwmon`** on every BMC. It's read-only: they can connect with `ipmitool`, but control commands like `chassis power off` are rejected by the BMC — "can run the tool" and "cannot control power" coexist. We also verified the no-auth cipher suite (cipher 0) was disabled.

```bash
# create the read-only account (in-band, on each node)
sudo ipmitool user set name    <slot> hwmon
sudo ipmitool user set password <slot> '<strong-password>'   # inject from a file, never echo on screen
sudo ipmitool user priv        <slot> 2 1                    # 2 = USER
sudo ipmitool user enable      <slot>
```

Always pass `-L USER` when connecting (without it the tool requests an ADMIN session and fails).

```bash
ipmitool -I lanplus -H 10.20.0.1X -U hwmon -f <password-file> -L USER sdr type Temperature
```

---

# [07] Fix 4 — Reviving a Hung BMC: Cutting AC Power

A BMC with hung firmware does not recover from an OS reboot (the BMC keeps running on standby power). The only cure is to **cut AC power completely** — unplug the power cords (both, on dual-PSU machines) or drop the outlet at the PDU, wait for standby power to drain (30 seconds to a few minutes), then power back on. That cold-boots the BMC firmware.

> If live services run on that node, shut them down safely first. In our case the node hosted guest-cluster VMs, so we gracefully stopped the VMs and paused the orchestrator's auto-recovery before pulling power. After the AC reset, the BMC responded normally.

---

# [08] Results and Lessons

- **Every** target node's BMC IP was unified into `10.20.0.0/24`, with the read-only `hwmon` account planted on each.
- The bastion's leg into the isolated network was made persistent, so the partner can SSH into the bastion and query each BMC's temperature, fans, power, and SEL with `ipmitool`. Privileges are pinned to read-only.
- If an always-on dashboard is ever needed, run `prometheus-ipmi-exporter` (remote mode) on the host with the leg and put the BMCs in as targets. It just automates and periodizes the same data as the manual checks.

Lessons learned:

- **"IP configured successfully" ≠ "reachable."** Even with correct BMC IPs, nothing works if no host has a foot in the isolated network, the switch VLANs differ, or the cable is in a different channel.
- **Ask the switch directly.** When the link is up but nothing answers, one LLDP capture (`0x88cc`) pins down the port and VLAN. Faster than guessing by pulling cables.
- **A BMC is a computer too, and it hangs.** And because it runs on standby power, OS reboots are irrelevant — only an AC power drain resets it.
- **Read-only is enforced by account privilege, not by the tool.** Hand someone `ipmitool` and with USER privilege they still cannot touch power.

BMC/IPMI is a layer you forget exists most of the time, but when you work with physical infrastructure it gives you the most reliable information from the very bottom. Punch through to it once, and even with a node powered off you can tell whether it's running hot and whether the fans are spinning.
