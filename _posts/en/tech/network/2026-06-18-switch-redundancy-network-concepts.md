---
title: "Core Network Concepts for Switch Redundancy — VLAN, SVI, LACP, MLAG/VLT, VRRP/VIP, IPMI, PXE"
description: "The foundational concepts behind the Arista/25G build-and-verify posts, plus everything used for switch redundancy (high availability): VLAN, SVI, LACP, Port-Channel, MLAG/VLT, STP, VRRP, VIP, FHRP, server bonding, IPMI, and PXE — organized by layer"
excerpt: "The terms that show up when you make a switch pair redundant — VLAN/SVI (L2·L3), LACP/Port-Channel/MLAG·VLT (link & chassis redundancy), VRRP/VIP·FHRP (gateway redundancy), server bonding, IPMI/BMC, PXE — explained by why they matter and how they fit together"
date: 2026-06-18
categories: Network
tags: [network, switch-redundancy, high-availability, VLAN, SVI, LACP, PortChannel, MLAG, VLT, STP, VRRP, VIP, FHRP, bonding, IPMI, BMC, PXE, ECMP, VXLAN, Arista]
ref: switch-redundancy-network-concepts
---

:bulb: Reading the Arista/25G build-and-verify series (management IP, 25G links, transceivers, netplan), terms like **VLAN, SVI, LACP, MLAG/VLT, VRRP, VIP, IPMI, PXE** keep appearing. This post organizes those concepts by layer, with a focus on **switch redundancy (high availability)**.  
Audience: server/infra engineers organizing network and redundancy terms for the first time
{: .notice--info}

# [00] Why "Redundancy" — Removing the Single Point of Failure

If a server attaches to a single switch over a single cable, then **any one of the switch, cable, or port failing breaks connectivity.** Redundancy (high availability / HA) removes that **single point of failure (SPOF)** by making paths, devices, and gateways exist in twos.

Redundancy is designed **per layer**.

| Layer | What's made redundant | Key technology |
|------|-----------------------|----------------|
| Physical/Link (L1–L2) | Cable, port, switch chassis | LACP, Port-Channel, **MLAG/VLT**, STP |
| Network (L2/L3 edge) | Broadcast domain, gateway | VLAN, **SVI**, **VRRP/VIP**, FHRP |
| L3 routing (core/spine) | Upstream path | ECMP, OSPF/BGP |
| Server side | NIC, uplink | **bonding** |
| Ops/Management | Device access path, boot | **IPMI/BMC**, **PXE** |

Let's go through them one by one.

---

# [01] L2 Foundation — VLAN and SVI

## [01-1] VLAN — Splitting One Switch into Many

A **VLAN (Virtual LAN)** logically divides one physical switch into **separate broadcast domains**. VLAN 10 (server network) and VLAN 20 (management network) can't talk directly even on the same switch (they must be routed).

| Port mode | Meaning |
|-----------|---------|
| **Access** | Belongs to one VLAN (usually server/PC). Untagged |
| **Trunk** | Carries multiple VLANs over one link (switch-to-switch). VLANs distinguished by 802.1Q tags |

```text
! Arista EOS example
vlan 10
   name SERVER
vlan 20
   name MGMT
interface Ethernet1
   switchport mode access
   switchport access vlan 10
interface Ethernet48
   switchport mode trunk
   switchport trunk allowed vlan 10,20
```

> Redundancy note: VLAN itself is a **segmentation** technology, not a redundancy one. But SVI, VRRP, and MLAG all run on top of VLANs, so it's the starting point.

## [01-2] SVI — Giving a VLAN an IP (an L3 Interface)

A switch port does L2 (switching) by default. To **route between VLANs**, each VLAN needs a **gateway IP**. The virtual interface that holds that IP is the **SVI (Switched Virtual Interface)**. On Arista/Cisco you create it as `interface Vlan10`.

```text
interface Vlan10
   ip address 10.0.10.1/24      ! gateway for VLAN 10 servers
interface Vlan20
   ip address 10.0.20.1/24      ! gateway for VLAN 20 management
```

- A server in VLAN 10 sets its gateway to `10.0.10.1` (the SVI).
- An SVI is a **logical L3 interface bound to a VLAN, not a physical port**. It's up as long as at least one member port of that VLAN is up.

> Note: the `Management1` from the earlier [management IP post](/en/Network/arista-switch-management-ip-ssh-access/) is a **dedicated management port**, not an SVI. An SVI is a data-VLAN gateway; the Management interface is for out-of-band (OOB) management — different roles.

---

# [02] Link & Chassis Redundancy — LACP, Port-Channel, MLAG/VLT

## [02-1] LACP and Port-Channel — Bundling Links into One

A **Port-Channel (= LAG, Link Aggregation Group)** bundles several physical links into **one logical link**. Two benefits:

1. **Bandwidth aggregation** — 25G × 2 ≈ 50G
2. **Redundancy** — if one link dies, the rest keep carrying traffic

**LACP (Link Aggregation Control Protocol, 802.3ad)** is the protocol that **negotiates and manages** the bundle automatically. Both ends exchange LACP packets (LACPDUs) to form the bundle and drop dead links automatically.

| Mode | Behavior |
|------|----------|
| `active` | Initiates LACP negotiation |
| `passive` | Responds if the peer initiates |
| `static` (on) | Force-bundles without negotiation (not recommended — weak failure detection) |

```text
! Arista: bundle Et1, Et2 into Port-Channel 1 via LACP
interface Ethernet1-2
   channel-group 1 mode active
interface Port-Channel1
   switchport mode trunk
```

## [02-2] MLAG / VLT — "Two Switches Acting as One"

An LACP bundle normally terminates on **one switch**. If that switch dies entirely, you're done. **MLAG/VLT** solves this — it makes **two separate physical switches** look like one logically, so a server connects **one cable to each switch** yet operates as a single LACP bundle.

| Vendor | Name |
|--------|------|
| **Arista** | **MLAG** (Multi-chassis Link Aggregation) |
| **Dell** | **VLT** (Virtual Link Trunking) |
| Cisco | vPC (virtual Port Channel) |

> So **VLT is Dell's term and MLAG is Arista's for the same concept** — different names, same goal: *chassis-level redundancy*.

<pre class="mermaid">
graph TD
    SRV["Server A<br/>bond0 (802.3ad LACP)"]
    SW1["Switch1<br/>MLAG peer"]
    SW2["Switch2<br/>MLAG peer"]
    SRV -->|eth0| SW1
    SRV -->|eth1| SW2
    SW1 <-->|"Peer-Link + Keepalive"| SW2
    style SRV fill:#e8f5e9,stroke:#2e7d32
    style SW1 fill:#e3f2fd,stroke:#1565c0
    style SW2 fill:#e3f2fd,stroke:#1565c0
</pre>

The server connects one cable to each switch but operates as **a single LACP bond (bond0)**, while Switch1·2 are MLAG peers that appear as one. If Switch1 dies, the server keeps communicating over eth1 (Switch2) without interruption.

**Inside MLAG — the two channels that bind the switches**

For MLAG to make two switches look like one, two kinds of channels are needed between them.

- **Peer-Link**: syncs data and state (MAC table, ARP). Usually a high-bandwidth Port-Channel.
- **Peer-Keepalive**: a separate path to confirm the peer is alive. Usually over the management network.
- **Split-brain**: a dangerous state where the Peer-Link drops and both switches think the other is dead, so **both act as Master**. The keepalive path detects and prevents this.

## [02-3] STP — Loop Prevention (supporting concept)

Dual paths risk **L2 loops (broadcast storms)**. **STP (Spanning Tree Protocol)** logically blocks one of the redundant paths to prevent loops. In MLAG, though, both uplinks are used **active/active** (STP doesn't block them), so you get full bandwidth — one of MLAG's advantages.

---

# [03] Gateway Redundancy — VRRP and VIP

Even with redundant switches/links, if the **gateway IP lives on only one device**, external connectivity breaks when that device dies. **VRRP** makes the gateway itself redundant.

## [03-1] VIP — A Floating Virtual IP

A **VIP (Virtual IP)** is a virtual IP address not pinned to one physical device — **whichever device is currently active (Master) holds it**. Servers point their gateway at this VIP, not at a real switch IP.

## [03-2] VRRP — Electing Who Holds the VIP

**VRRP (Virtual Router Redundancy Protocol)** lets several routers/L3 switches **share one VIP and one virtual MAC**, with only the **Master answering for the VIP**. If the Master dies, a Backup takes over the VIP instantly (failover), and servers keep communicating, unaware the gateway changed.

```text
! Switch1 (preferred Master)
interface Vlan10
   ip address 10.0.10.2/24
   vrrp 10 ip 10.0.10.1          ! ← VIP (the server's gateway)
   vrrp 10 priority 200          ! higher = Master

! Switch2 (Backup)
interface Vlan10
   ip address 10.0.10.3/24
   vrrp 10 ip 10.0.10.1          ! ← shares the same VIP
   vrrp 10 priority 100
```

| Item | Value | Meaning |
|------|-------|---------|
| VIP | `10.0.10.1` | gateway the server sees (floats) |
| Switch1 real IP | `10.0.10.2` | priority 200 → Master |
| Switch2 real IP | `10.0.10.3` | priority 100 → Backup |

{% raw %}
<pre class="mermaid">
graph TD
    SRV["Server<br/>gateway = 10.0.10.1 (VIP)"]
    VIP{{"VIP 10.0.10.1<br/>virtual IP/MAC"}}
    M["Switch1 (Master)<br/>10.0.10.2 · priority 200"]
    B["Switch2 (Backup)<br/>10.0.10.3 · priority 100"]
    SRV --> VIP
    VIP -->|"answers normally"| M
    VIP -.->|"takes over on Master failure (failover)"| B
    M <-->|"VRRP advertisement"| B
    style SRV fill:#e8f5e9,stroke:#2e7d32
    style VIP fill:#f3e5f5,stroke:#6a1b9a
    style M fill:#e3f2fd,stroke:#1565c0
    style B fill:#fff3e0,stroke:#e65100
</pre>
{% endraw %}

> Using **MLAG (L2 chassis redundancy) + VRRP (L3 gateway redundancy) together** makes links, switches, and the gateway all redundant. That's the standard redundant topology.

## [03-3] The FHRP Family — VRRP Isn't the Only One

Gateway-redundancy protocols are collectively called **FHRP (First Hop Redundancy Protocol)**. VRRP is one of them.

| Protocol | Vendor | Trait |
|---|---|---|
| **VRRP** | Open standard | Most universal. 1 Master + N Backup |
| **HSRP** | Cisco only | Similar to VRRP, uses Active/Standby terms |
| **GLBP** | Cisco only | Multiple gateways carry traffic **simultaneously** (load balancing) |

> Arista uses standard **VRRP**. In multi-vendor environments, standard VRRP is the safe choice.

---

# [04] Server-Side Redundancy — Bonding

To match the switch-side MLAG, **the server must bundle two NICs into one** as well. On Linux this is **bonding / teaming**. To pair with switch MLAG, use **802.3ad (LACP) mode**.

```yaml
# netplan example (LACP bond) — two NICs into bond0
network:
  version: 2
  ethernets:
    ens801f0np0: {}
    ens801f1np1: {}
  bonds:
    bond0:
      interfaces: [ens801f0np0, ens801f1np1]
      parameters:
        mode: 802.3ad          # LACP
        lacp-rate: fast
        mii-monitor-interval: 100
      addresses: [10.0.10.50/24]
      routes:
        - to: default
          via: 10.0.10.1       # ← VRRP VIP
```

> For configuring NICs directly with netplan, see the [netplan manual config post](/en/Network/netplan-manual-config-cloud-init/). The bonding mode **must match the switch-side LACP/MLAG config** for the link to bundle properly.

| bonding mode | Trait | Switch requirement |
|---|---|---|
| `802.3ad` (LACP) | Standard LACP, bandwidth + redundancy | Switch Port-Channel/MLAG required |
| `active-backup` | One NIC active, fails over | No switch config (simplest redundancy) |
| `balance-xor`, etc. | Static hash distribution | Static LAG |

---

# [05] Ops/Management Redundancy — IPMI/BMC and PXE

## [05-1] IPMI / BMC — A Separate Path Independent of the OS

**IPMI (Intelligent Platform Management Interface)** is the **out-of-band management** standard provided by a server's **BMC (Baseboard Management Controller)** chip. The key point: it's **completely separate from the OS and the main NIC**.

- It has a dedicated management LAN port and **its own IP** (works even when the server OS is off).
- Remote power on/off/reset, hardware sensors (temperature, fans, voltage), and a **remote console (SOL/KVM)**.
- Vendor implementations: Dell **iDRAC**, HPE **iLO**, Supermicro **IPMI**, Lenovo **XCC**.

> Redundancy note: even if the data network/OS is down, you can diagnose and recover the server over the IPMI path — **management-path redundancy**. The "management network" in the earlier [management IP/SSH post](/en/Network/arista-switch-management-ip-ssh-access/) is exactly where this OOB traffic flows.

```text
Management network (VLAN 20 / OOB)
  ├── Switch Management1   (device management SSH)
  ├── Server1 IPMI/BMC     (power & console, IP separate from OS)
  └── Server2 IPMI/BMC
```

## [05-2] PXE — Booting an OS Over the Network

**PXE (Preboot eXecution Environment)** lets a server **boot a boot image from the network** instead of a local disk. Used for mass provisioning, diskless nodes, and automated OS installs.

Flow:

```text
1. NIC boots via PXE → DHCP request (gets IP + next-server + boot filename)
2. Downloads a bootloader (e.g. iPXE, GRUB) over TFTP/HTTP
3. The bootloader fetches kernel/initrd/kickstart-preseed to install/boot the OS
```

**DHCP Relay for PXE**

If the PXE client and DHCP server are in **different VLANs**, broadcast DHCP can't cross the router. Add a **DHCP relay (`ip helper-address`)** on the SVI to forward DHCP requests to the server.

```text
interface Vlan30
   ip address 10.0.30.1/24
   ip helper-address 10.0.99.10   ! DHCP/PXE server address
```

> Redundancy note: making the PXE infrastructure (DHCP/TFTP) itself redundant removes that SPOF in the provisioning path. PXE runs on top of **VLAN/SVI (gateway)**, so a boot VLAN and DHCP relay design go hand in hand.

---

# [06] The Whole Picture — How the Concepts Wire into One Topology

{% raw %}
<pre class="mermaid">
graph TD
    CORE["external / core"]
    VIP{{"VRRP VIP 10.0.10.1<br/>gateway redundancy"}}
    SW1["Switch1<br/>SVI Vlan10 · MLAG"]
    SW2["Switch2<br/>SVI Vlan10 · MLAG"]
    S1["Server1<br/>bond0 (802.3ad)"]
    S2["Server2<br/>bond0 (802.3ad)"]
    MGMT["mgmt network VLAN 20 (OOB)<br/>IPMI/BMC · Management1"]
    CORE --> VIP
    VIP --> SW1
    VIP --> SW2
    SW1 <-->|"Peer-Link"| SW2
    SW1 ---|LACP| S1
    SW2 ---|LACP| S1
    SW1 ---|LACP| S2
    SW2 ---|LACP| S2
    S1 -.->|OOB| MGMT
    S2 -.->|OOB| MGMT
    style CORE fill:#eceff1,stroke:#455a64
    style VIP fill:#f3e5f5,stroke:#6a1b9a
    style SW1 fill:#e3f2fd,stroke:#1565c0
    style SW2 fill:#e3f2fd,stroke:#1565c0
    style S1 fill:#e8f5e9,stroke:#2e7d32
    style S2 fill:#e8f5e9,stroke:#2e7d32
    style MGMT fill:#fff3e0,stroke:#e65100
</pre>
{% endraw %}

| Redundancy target | Responsible concept |
|-------------------|---------------------|
| Cable/port | LACP / Port-Channel |
| Switch chassis | **MLAG (Arista) / VLT (Dell)** |
| L2 loop prevention | STP (supporting in MLAG) |
| Gateway (L3) | **VRRP + VIP** (FHRP) |
| Server uplink | bonding (802.3ad) |
| Management path | IPMI/BMC + management VLAN |
| Provisioning | PXE (redundant DHCP/TFTP) |

---

# [07] L3 Routing Redundancy — ECMP and BGP/OSPF

If the gateway is made redundant with VRRP, the path **above it (core/spine) is made redundant with dynamic routing**. Where VRRP covers "the one gateway hop," this covers "the path beyond it."

- **ECMP (Equal-Cost Multi-Path)**: spreads traffic over multiple equal-cost paths and auto-reroutes if one dies — bandwidth and redundancy at once.
- **OSPF / BGP**: dynamically learn paths and reconverge on failure. Modern data centers (leaf-spine fabric) trend toward **L3 + BGP/EVPN** instead of L2 MLAG.

<pre class="mermaid">
graph TD
    LEAF["Leaf switch"]
    SP1["Spine 1"]
    SP2["Spine 2"]
    DST["destination prefix"]
    LEAF -->|"path A · cost 10"| SP1
    LEAF -->|"path B · cost 10"| SP2
    SP1 --> DST
    SP2 --> DST
    style LEAF fill:#e8f5e9,stroke:#2e7d32
    style SP1 fill:#e3f2fd,stroke:#1565c0
    style SP2 fill:#e3f2fd,stroke:#1565c0
    style DST fill:#eceff1,stroke:#455a64
</pre>

Both equal-cost paths are used **simultaneously** (ECMP load balancing); if one path (Spine) dies, routing reconverges and auto-reroutes over the remaining path.

> Small designs center on MLAG+VRRP (L2-centric); large ones center on L3 routing (ECMP+BGP).

---

# [08] Physical-Layer Values You Must Align — MTU/Jumbo, FEC, Transceivers

Not redundancy per se, but for a 25G link to **work at all**, both ends must agree on these physical/link-layer values. Mismatches break link quality or the connection itself — before redundancy is even relevant.

- **Jumbo Frames (MTU 9000+)**: improve large-transfer efficiency. The **entire path** (server NIC, bond, switch port, SVI) must share the same MTU; one mismatch causes fragmentation or blackholing.
- **FEC (RS-FEC)**: corrects bit errors on 25G+ links. **Both ends must use the same FEC mode** for a stable link → see the [25G verification post](/en/Network/25g-nic-arista-switch-link-verification/).
- **Transceiver compatibility**: if the switch blocks a module as `xcvr-unsupported`, the link never comes up → see the [GBIC test post](/en/Network/arista-switch-gbic-transceiver-test/).

---

# [09] Modern Alternatives at Scale — VXLAN/EVPN and Anycast Gateway

At scale, to get past VLAN limits (4094 IDs, hard L2 extension), people use **VXLAN** (tunneling L2 over L3) and **EVPN** (its control plane).

The gateway is then made redundant with an **Anycast Gateway** — every leaf switch holds the **same gateway IP/MAC simultaneously**, so wherever a server attaches, the nearest switch is its gateway.

> For this post's scope (small-to-mid switch redundancy), MLAG+VRRP is enough. VXLAN/EVPN is the "bigger picture" — knowing the concept is enough.

---

# [10] Quick Glossary

| Term | One-line definition | Layer | Redundancy role |
|------|--------------------|-------|-----------------|
| **VLAN** | A logically partitioned broadcast domain on a switch | L2 | Segmentation (foundation) |
| **SVI** | Virtual L3 interface giving a VLAN an IP (gateway) | L3 | Basis for VRRP |
| **LACP** | Protocol that auto-bundles links into one (802.3ad) | L2 | Link redundancy |
| **Port-Channel/LAG** | The logical link formed by LACP | L2 | Bandwidth + redundancy |
| **MLAG / VLT** | Two switches as one — chassis redundancy (Arista/Dell) | L2 | Switch redundancy |
| **Peer-Link/Keepalive** | MLAG state-sync and liveness paths between the two switches | L2 | MLAG stability |
| **STP** | Blocks L2 loops | L2 | Loop prevention |
| **VRRP** | Master/Backup auto-handoff of a VIP | L3 | Gateway redundancy |
| **VIP** | Virtual gateway IP held by the active device | L3 | Gateway redundancy |
| **FHRP (HSRP/GLBP)** | Umbrella term for gateway-redundancy protocols (incl. VRRP) | L3 | Gateway redundancy |
| **bonding** | Bundling server NICs (LACP/active-backup) | Server | Server uplink redundancy |
| **ECMP** | Equal-cost multipath distribution/reroute | L3 | Path redundancy |
| **OSPF/BGP** | Dynamic routing learning/reconvergence | L3 | Path redundancy |
| **IPMI/BMC** | OOB hardware management separate from the OS | Mgmt | Management-path redundancy |
| **PXE** | Network boot (DHCP+TFTP) | Boot | Provisioning |
| **DHCP relay** | Relays to a DHCP server in another VLAN (`ip helper-address`) | L3 | Enables PXE |
| **Jumbo/MTU** | Large frames; must match across the path | L2/L3 | (performance) |
| **FEC (RS-FEC)** | Bit-error correction on fast links, both ends matched | L1 | (link stability) |
| **VXLAN/EVPN** | L2 over L3 + Anycast Gateway | overlay | Large-scale redundancy |

---

# [11] Wrap-up

Switch redundancy is **not a single technology but a combination of per-layer techniques**.

1. **VLAN/SVI** segment the network and create gateways.
2. **LACP/Port-Channel** make links redundant; **MLAG/VLT** makes the switch chassis redundant (synced via Peer-Link/Keepalive, with split-brain prevented).
3. **VRRP/VIP** (FHRP) make the gateway redundant; **ECMP/BGP** make the upstream path redundant.
4. The server attaches to both switches at once via **bonding (802.3ad)**.
5. **IPMI/BMC** provides an OS-independent management path; **PXE** provides the provisioning path.

At the physical layer you must align **MTU, FEC, and transceiver compatibility** on both ends for the link to work, and at scale **VXLAN/EVPN + Anycast Gateway** becomes the alternative. With these in mind, terms like `Management1`, `Port-Channel`, `VLAN`, `gateway`, and `bonding` from the Arista management-IP, 25G-link, transceiver, and netplan posts fall into place — you can see **where each one sits in a single redundancy picture**.
