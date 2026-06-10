---
title: "Verifying a 25G Network — Server-to-Arista-to-Server Link Compatibility Test"
description: "Step-by-step test guide for verifying compatibility between newly purchased 25G NICs and an Arista switch: link/speed, transceiver detection, FEC match, error counters, and iperf3 throughput, with commands, sample output, and result interpretation"
excerpt: "How to verify, step by step, link negotiation, transceiver detection, FEC mode match, error counters, and throughput/latency in a Server A 25G NIC ↔ Arista 25G port ↔ Server B 25G NIC setup. The goal is confirming compatibility between new 25G cards and the switch"
date: 2026-06-10
categories: Network
tags: [25G, SFP28, Arista, EOS, NIC, FEC, ethtool, iperf3, transceiver, compatibility, link-verification, DAC, RS-FEC, Mellanox, Intel]
ref: 25g-nic-arista-switch-link-verification
---

:bulb: A step-by-step test for verifying that **newly purchased 25G NICs are compatible with an Arista switch**.  
Topology: `Server A (25G NIC) ── Arista switch (25G port) ── Server B (25G NIC)`  
Key checks: link speed (25G), transceiver detection, **FEC mode match**, error counters, measured throughput
{: .notice--info}

# [00] Overall Architecture

```
Server A                       Arista switch                       Server B
┌──────────────┐              ┌──────────────────┐              ┌──────────────┐
│ 25G NIC      │  SFP28 DAC   │ Ethernet1 (25G)  │  SFP28 DAC   │ 25G NIC      │
│ ens1f0       ├──────────────┤                  ├──────────────┤ ens1f0       │
│ 10.0.0.1/24  │              │ Ethernet2 (25G)  │              │ 10.0.0.2/24  │
└──────────────┘              └──────────────────┘              └──────────────┘
       │                              │                                │
   ethtool / iperf3            show interfaces             ethtool / iperf3
```

:warning: Most 25G link compatibility problems come from one of three things: **① transceiver/cable not detected, ② FEC mode mismatch, ③ speed auto-negotiation failure.** This guide focuses on those three.
{: .notice--warning}

# [01] Test Goals and Pass Criteria

| Item | Pass criteria |
|------|---------------|
| Link speed | **25 Gbps** on both ends, `up` |
| Transceiver detection | Switch/server identify the SFP28 transceiver; vendor/serial shown |
| FEC mode | **Same mode on both** switch and server (RS-FEC recommended), uncorrected = 0 |
| Error counters | No increase in CRC/symbol/FEC-uncorrected errors |
| Throughput | **≥ 23 Gbps** with multiple streams (accounting for overhead) |
| Latency | Tens of µs RTT through the same switch, 0% loss |

# [02] Prerequisites and Information Gathering

| Item | Details |
|------|---------|
| Server A/B | OS (e.g. Ubuntu 22.04 / RHEL 9), 25G NIC model, slot (PCIe Gen3 x8+) |
| 25G NIC | e.g. Mellanox ConnectX-4 Lx / ConnectX-5, Intel E810/XXV710, Broadcom |
| Cable | **SFP28** DAC (≤3m) or AOC/optical — confirm it's 25G (not 10G SFP+) |
| Switch | Arista EOS with 25G-capable ports (e.g. 7050X3/7060X) |
| Tools | `ethtool`, `iperf3`, `ping`, (optional) `sockperf`, `lspci` |

```bash
# Install tools on the servers (Ubuntu)
sudo apt-get install -y ethtool iperf3 pciutils
# RHEL/Rocky
sudo dnf install -y ethtool iperf3 pciutils
```

# [03] Physical Cabling and Interface Identification

Connect Server A's NIC to switch `Ethernet1` and Server B's NIC to `Ethernet2` with SFP28 cables. First identify the 25G interface name on each server.

```bash
# Interface list with state
ip -br link
```

Sample output:

```
lo               UNKNOWN        00:00:00:00:00:00
eno1             UP             a0:36:9f:xx:xx:xx
ens1f0           UP             b8:ce:f6:xx:xx:xx
```

```bash
# NIC model and PCIe location
lspci | grep -i ethernet
```

Sample output:

```
01:00.0 Ethernet controller: Mellanox Technologies MT27710 Family [ConnectX-4 Lx]
```

> `ens1f0` is the 25G interface under test. Confirm the same on both servers.

# [04] Switch Side — Link/Speed Check

From the Arista console (or SSH), check port status.

```
sw-core-01# show interfaces Ethernet1 status
```

Sample output:

```
Port       Name   Status       Vlan     Duplex Speed  Type            Flags
Et1               connected    1        full   25G    25GBASE-CR
```

| Field | Meaning |
|-------|---------|
| `Status: connected` | Physical link up (`notconnect` = not connected / negotiation failed) |
| `Speed: 25G` | Negotiated at 25 Gbps (dropping to `10G` = cable/port config issue) |
| `Type: 25GBASE-CR` | DAC copper. Optical would be `25GBASE-SR`, etc. |

To see multiple ports at once:

```
sw-core-01# show interfaces status | include 25G
```

# [05] Switch Side — Transceiver Detection (Compatibility Core)

Check that the switch correctly identifies the new transceiver/cable. Arista may flag unsupported/third-party transceivers.

```
sw-core-01# show interfaces Ethernet1 transceiver
```

Sample output:

```
Port    Vendor          Part Number    Serial Number    Type
Et1     Arista Networks CAB-D-D-25G-3M  XYZ123456789    25GBASE-CR
```

Detailed diagnostics (optical power for optics):

```
sw-core-01# show interfaces Ethernet1 transceiver detail
```

| Check | Meaning |
|-------|---------|
| Vendor/Part/Serial shown | Transceiver EEPROM read correctly |
| `Type` is 25GBASE-* | 25G-specific cable (10G shown = wrong cable) |
| Rx Power in range (optical) | Optical signal level healthy |

:warning: On Arista, third-party transceivers may be blocked by default policy. If needed, check rejection logs with `show logging | include transceiver` and confirm the model is policy-allowed.
{: .notice--warning}

# [06] FEC Mode Check and Match (Most Important)

At 25G, **if the FEC (Forward Error Correction) mode differs between the two ends, the link may not come up — or come up but accumulate errors.** This is the core step of new-card compatibility verification.

- **RS-FEC (CL91, Reed-Solomon)**: generally required for 25GBASE-CR (DAC > 3m) and SR optics
- **FC-FEC (CL74, Fire-code / BASE-R)**: usable on short DACs
- **None (disabled)**: very short passive cables only

**Switch-side FEC check:**

```
sw-core-01# show interfaces Ethernet1 phy detail | include -i fec
```

Or from the interface config:

```
sw-core-01# show running-config interfaces Ethernet1
```

Sample output:

```
interface Ethernet1
   error-correction encoding reed-solomon
```

**Switch-side FEC config (if needed):**

```
sw-core-01(config)# interface Ethernet1
sw-core-01(config-if-Et1)# error-correction encoding reed-solomon
```

> Options: `reed-solomon` (RS-FEC), `fire-code` (FC-FEC), `disabled`. Match the server side **exactly**.

**Server-side FEC check:**

```bash
ethtool --show-fec ens1f0
```

Sample output:

```
FEC parameters for ens1f0:
Configured FEC encodings: Auto
Active FEC encoding: RS
```

| Field | Meaning |
|-------|---------|
| `Active FEC encoding: RS` | RS-FEC active now (must match the switch) |
| `Auto` | Auto-negotiated. If one side is fixed, fix both |

**Force server-side FEC (on mismatch):**

```bash
# Fix to RS-FEC
sudo ethtool --set-fec ens1f0 encoding rs
# Options: rs | baser (= FC-FEC) | off | auto
```

:bulb: **Fixing both ends to the same mode** is the most stable. Mixing one `auto` and one `rs` can cause intermittent link flaps.
{: .notice--info}

# [07] Server Side — Link/Speed Check

```bash
ethtool ens1f0
```

Sample output (excerpt):

```
Settings for ens1f0:
        Supported link modes:   25000baseCR/Full
        Speed: 25000Mb/s
        Duplex: Full
        Auto-negotiation: on
        Link detected: yes
```

| Field | Meaning |
|-------|---------|
| `Speed: 25000Mb/s` | 25 Gbps link OK |
| `Link detected: yes` | Physical link up |
| `Auto-negotiation: on` | Auto-neg in use (policy must match both ends) |

Both servers (A/B) must show `25000Mb/s`, `Link detected: yes`.

# [08] Server Side — Driver/Firmware Check

For a new card, driver/firmware versions directly affect compatibility.

```bash
ethtool -i ens1f0
```

Sample output:

```
driver: mlx5_core
version: 5.15.0-xx
firmware-version: 14.32.1010 (MT_0000000080)
bus-info: 0000:01:00.0
```

| Field | Meaning |
|-------|---------|
| `driver` | Kernel NIC driver (e.g. `mlx5_core`, `ice`, `i40e`, `bnxt_en`) |
| `firmware-version` | NIC firmware — confirm it's the vendor-recommended latest |

> Old firmware can carry 25G/FEC negotiation bugs, so cross-check vendor release notes.

# [09] PCIe Bandwidth Check (Bottleneck)

To push 25G (≈3.125 GB/s) you need at least PCIe Gen3 x8.

```bash
sudo lspci -vv -s 01:00.0 | grep -i -E 'LnkCap|LnkSta'
```

Sample output:

```
LnkCap: ... Speed 8GT/s, Width x8
LnkSta: ... Speed 8GT/s, Width x8
```

| Check | Meaning |
|-------|---------|
| `LnkSta` Width `x8` | Slot operating at x8 (dropping to x4 throttles throughput) |
| Speed `8GT/s` (Gen3)+ | Can carry 25G line rate |

# [10] IP Setup and Basic Connectivity

```bash
# Server A
sudo ip addr add 10.0.0.1/24 dev ens1f0
sudo ip link set ens1f0 up
# Server B
sudo ip addr add 10.0.0.2/24 dev ens1f0
sudo ip link set ens1f0 up
```

Connectivity check:

```bash
# From A to B
ping -c 4 10.0.0.2
```

Sample output:

```
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=0.045 ms
...
4 packets transmitted, 4 received, 0% packet loss
```

> `0% packet loss` with µs-level RTT means the L2/L3 path is healthy.

# [11] MTU / Jumbo Frame Setup and Verification

Before high-throughput tests, set Jumbo Frames (9000) to lower CPU load and raise throughput. **Both servers and the switch port/VLAN must use the same MTU.**

```bash
# Both servers
sudo ip link set ens1f0 mtu 9000
```

```
# Switch (Arista) — port L2 MTU
sw-core-01(config)# interface Ethernet1
sw-core-01(config-if-Et1)# l2 mtu 9214
```

Verify the jumbo path (9000B without fragmentation):

```bash
ping -M do -s 8972 -c 4 10.0.0.2
```

| Result | Meaning |
|--------|---------|
| Success (0% loss) | 9000 MTU path OK |
| `Message too long` / 100% loss | MTU mismatch somewhere → recheck switch/server MTU |

# [12] Throughput Test — iperf3

A single TCP stream may not saturate 25G due to single-core limits. Use **multiple streams (`-P`)** to approach line rate.

**Server B (receiver / server role):**

```bash
iperf3 -s
```

**Server A (sender / client):**

```bash
# 8 parallel streams, 30 seconds
iperf3 -c 10.0.0.2 -P 8 -t 30
```

Sample output (excerpt):

```
[SUM]   0.00-30.00  sec  82.1 GBytes  23.5 Gbits/sec   0   sender
[SUM]   0.00-30.00  sec  82.0 GBytes  23.5 Gbits/sec       receiver
```

| Field | Meaning |
|-------|---------|
| `23.5 Gbits/sec` | Measured throughput — ~94% of 25G, normal given TCP/header overhead |
| `Retr` (retransmits) 0 or small | Closer to 0 is better. A spike suggests FEC/congestion/buffer issues |

**Test the reverse direction (B→A) too:**

```bash
iperf3 -c 10.0.0.2 -P 8 -t 30 -R
```

> If both directions exceed 23 Gbps, compatibility/performance pass. If only one direction is low, inspect that sender's NIC/cable.

To see line-rate loss with UDP:

```bash
iperf3 -c 10.0.0.2 -u -b 25G -t 20
```

`Lost/Total Datagrams` should be near 0%.

# [13] Latency Test

```bash
# RTT distribution at a fast interval
sudo ping -i 0.2 -c 50 10.0.0.2
```

Sample output:

```
rtt min/avg/max/mdev = 0.038/0.046/0.071/0.008 ms
```

| Metric | Meaning |
|--------|---------|
| `avg` tens of µs | Normal through the same switch |
| Small `mdev` (jitter) | Stable. Large spikes suggest FEC retries/buffer issues |

# [14] Error Counter Check (Before/After Comparison)

Snapshot counters **before and after** the throughput test and look at the delta. Compatibility problems show up here.

**Server side:**

```bash
ethtool -S ens1f0 | grep -i -E 'err|drop|fec|crc'
```

Sample output:

```
     rx_crc_errors_phy: 0
     rx_corrected_bits_phy: 1024
     rx_symbol_err_phy: 0
     fec_uncorrectable_blocks: 0
```

| Counter | Meaning |
|---------|---------|
| `rx_crc_errors_phy` | CRC errors — **must not increase** (cable/FEC issue) |
| `fec_corrected_*` | Bits FEC corrected — small increase is normal (evidence FEC is working) |
| `fec_uncorrectable_*` | **Correction failures — must be 0**. Increase = link quality / FEC mismatch |
| `rx_symbol_err_phy` | Symbol errors — 0 preferred |

**Switch side:**

```
sw-core-01# show interfaces Ethernet1 counters errors
```

Sample output:

```
Port    FCS Err  Align Err  Symbol Err  Rx Err  Tx Err
Et1     0        0          0           0       0
```

```
# FEC stats (corrected/uncorrected codewords)
sw-core-01# show interfaces Ethernet1 phy detail | include -i -A2 fec
```

| Check | Meaning |
|-------|---------|
| FCS/Symbol Err stay 0 | Link quality good |
| FEC uncorrected = 0 | **Required pass condition** |

# [15] Compatibility Troubleshooting

| Symptom | Cause / action |
|---------|----------------|
| Link won't come up (`notconnect` / `Link detected: no`) | FEC mismatch → fix both switch and server to the same mode (RS-FEC). Confirm the cable is 25G SFP28 |
| Negotiates at 10G, not 25G | Cable is 10G SFP+ or a forced port speed → set `speed forced 25gfull` on the switch or align auto-neg |
| Transceiver not detected / rejection logs | Third-party block policy → check `show logging | include transceiver`, verify allowed model/policy |
| Link flaps (intermittent drops) | One side `auto`, the other fixed → fix both the same. Consider firmware update |
| Throughput stuck at ~10G | PCIe x4 downgrade (check `LnkSta`), single-stream limit → use `-P` multi-stream, tune IRQ/RSS |
| FEC corrected surges + uncorrected appears | Cable quality/length limit → replace cable, apply stronger FEC (RS) |

# [16] Summary Checklist

| Step | Where | Check |
|------|-------|-------|
| STEP 04 | Switch | `show interfaces Et1 status` → `connected`, `25G` |
| STEP 05 | Switch | `show interfaces Et1 transceiver` → transceiver detected |
| STEP 06 | Switch + server | FEC mode **identical on both** (RS recommended) |
| STEP 07 | Server | `ethtool ens1f0` → `25000Mb/s`, `Link: yes` |
| STEP 08 | Server | `ethtool -i` → latest driver/firmware |
| STEP 09 | Server | `lspci` → PCIe x8 / Gen3+ |
| STEP 11 | Both | MTU 9000 matched, `ping -M do -s 8972` succeeds |
| STEP 12 | Server | `iperf3 -P 8` → ≥ 23 Gbps both directions |
| STEP 14 | Both | CRC/FEC uncorrected **delta 0** |

> When all nine items pass, consider the **compatibility and performance between the new 25G NIC and the Arista switch verified**.
