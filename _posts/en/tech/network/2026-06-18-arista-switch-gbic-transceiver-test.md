---
title: "Testing Arista Switch GBIC (SFP28) Modules — Diagnosing xcvr-unsupported"
description: "How to test 25G SFP28 transceivers (GBICs) on an Arista EOS switch with CLI commands to diagnose why a link won't come up: optical Tx/Rx power, errdisabled reason, inventory module identification, and server-side ethtool cross-check leading to an xcvr-unsupported conclusion"
excerpt: "When a 25G link won't come up, how do you test the switch's GBIC modules and reach a conclusion? Cross-analyze Tx/Rx optical power and Bias Current, the errdisabled reason, show inventory, and server ethtool to diagnose OEM/third-party transceivers blocked as unsupported, step by step"
date: 2026-06-18
categories: Network
tags: [Arista, EOS, SFP28, GBIC, transceiver, 25G, errdisabled, xcvr-unsupported, optics, compatibility, link-diagnosis, FEC]
ref: arista-switch-gbic-transceiver-test
---

:bulb: When a 25G link won't come up, this is how to **test the GBIC (SFP28 transceiver) modules in the switch, diagnose the cause, and reach a conclusion**.  
Topology: `Server (25G NIC) ── fiber ── Arista switch (SFP28 port)`  
Key diagnostic points: **Tx/Rx optical power**, **Bias Current**, **errdisabled reason**, **inventory module identification**, **server-side ethtool cross-check**
{: .notice--info}

> The CLI output in this post is drawn from real work testing 25G SFP28 transceivers on an actual device (`DCS-7050SX3-48YC8C-F` / EOS 4.30.4M, hostname `sw-core-01`). Device identifiers such as serial numbers and MAC addresses are masked (`xxxx`), and IPs use documentation example values. Substitute your own values when diagnosing in practice.

# [00] Goal and Setup

A new 25G NIC is connected to an Arista switch but the link won't come up. The goal is to determine **whether the cause lies in the transceiver (GBIC)**. The test subjects are 25G SFP28 optics across several ports.

| Item | Value |
|------|-------|
| Switch | `sw-core-01` (DCS-7050SX3-48YC8C-F / EOS 4.30.4M) |
| Test ports | `Ethernet21`, `Ethernet23`, `Ethernet35`, `Ethernet37` |
| Transceivers | OEM `25GBASE-SR`, MikroTik `XS+31LC10D` (`25GBASE-LR`) |
| Server NIC | `ens801f0np0` (25G SFP28) |

> Looking at one or two ports invites the wrong conclusion ("just that module is bad"). **Cross-test several ports with different modules** to separate an individual-module fault from a policy issue.

# [01] Test Method — What to Check, With Which Commands

GBIC diagnosis checks four things in order.

| Step | What | Command |
|---:|------|---------|
| 1 | Port status / transceiver type | `show interfaces EthernetN status` |
| 2 | Optical power (Tx/Rx) and Bias | `show interfaces EthernetN transceiver` |
| 3 | errdisabled reason | `show interfaces status errdisabled` |
| 4 | Module vendor/model/serial | `show inventory` |

The crux is the **three optical-power values**.

- **Bias Current (mA)** — transmit laser drive current. `0.00 mA` means the transmitter is off.
- **Tx Power (dBm)** — optical output the switch emits. `-30.00 dBm` means effectively no transmission.
- **Rx Power (dBm)** — incoming optical signal from the far end (server). A normal range means the cable and the far-end transmitter are alive.

# [02] Collecting Per-Port Transceiver State

## [02-1] Ethernet21 — Port Status

```text
sw-core-01#show interfaces Ethernet21 status
Port       Name   Status       Vlan     Duplex Speed  Type         Flags Encapsulation
Et21              errdisabled  1        full   25G    25GBASE-SR
```

The transceiver type is **correctly detected** as `25GBASE-SR` at `25G`. But the status is `errdisabled` — not a cable-out `notconnect`, but the switch forcibly disabling the port after detecting a specific error condition.

## [02-2] Ethernet21 — Optical Power

```text
sw-core-01#show interfaces Ethernet21 transceiver
                               Bias      Optical   Optical
          Temp       Voltage   Current   Tx Power  Rx Power
Port      (Celsius)  (Volts)   (mA)      (dBm)     (dBm)     Last Update
-----     ---------  --------  --------  --------  --------  -------------------
Et21       31.11      3.31      0.00     -30.00    -0.28     0:00:01 ago
```

| Item | Value | Meaning |
|---|---:|---|
| Bias Current | `0.00 mA` | No transmit-laser drive current |
| Tx Power | `-30.00 dBm` | Switch optical output is effectively nil |
| Rx Power | `-0.28 dBm` | Optical signal from the server is detected |

So the **switch receives but does not transmit**. This asymmetry is the key clue.

## [02-3] Ethernet21 — Detailed Counters

```text
sw-core-01#show interfaces Ethernet21
Ethernet21 is down, line protocol is down (errdisabled)
  Hardware is Ethernet, address is xxxx.xxxx.5f06 (bia xxxx.xxxx.5f06)
  Ethernet MTU 9214 bytes, BW 25000000 kbit
  Full-duplex, 25Gb/s, auto negotiation: off, uni-link: n/a
  ...
     0 input errors, 0 CRC, 0 alignment, 0 symbol, 0 input discards
     0 output errors, 0 collisions
```

CRC, symbol, and alignment errors are **all 0**. This is not errors accumulating after a link came up — the port was **blocked before reaching normal operation**.

## [02-4] Ethernet23 — Same Pattern (25GBASE-SR)

```text
sw-core-01#show interfaces Ethernet23 transceiver
Port      ...  Current(mA)  Tx Power(dBm)  Rx Power(dBm)  Last Update
Et23      ...  0.00         -30.00         -0.38          0:00:01 ago
```

`Et23` matches `Et21` exactly: `Bias 0.00 mA / Tx -30.00 dBm / Rx -0.38 dBm`. Two ports with identical symptoms point away from an individual port fault and toward a **module/policy issue**.

# [03] Cross-Test — Does It Reproduce on Other Modules?

To reach a sound conclusion, check whether **different transceivers** show the same symptom.

## [03-1] Ethernet35 — A Different OEM SR Module

```text
sw-core-01#show interfaces Ethernet35 transceiver
Et35      ...  0.00(mA)   -30.00(Tx dBm)   -0.74(Rx dBm)
```

`transceiver detail` makes it clearer against the thresholds.

```text
sw-core-01#show interfaces Ethernet35 transceiver detail
           Tx Power      Low Alarm   Low Warn
Port       (dBm)         (dBm)       (dBm)
-------    ------------  ----------  ----------
Et35       -30.00        -11.40      -8.40
           Rx Power
Et35       -0.75         (normal range)
```

The current `Tx Power -30.00 dBm` is far below the `-11.40 dBm` Low Alarm, while `Rx Power` is in normal range → the **switch is not driving the transmit laser**.

## [03-2] Ethernet37 — A MikroTik 25GBASE-LR Module

Test an **LR module**, not just the SR family.

```text
sw-core-01#show interfaces Ethernet37 status
Et37              errdisabled  1        full   25G    25GBASE-LR

sw-core-01#show interfaces Ethernet37 transceiver detail
           Current   Low Alarm
Et37       0.00 mA   1.00 mA
           Tx Power  Low Alarm
Et37       -30.00    -7.00 dBm
           Rx Power  Low Alarm
Et37       1.05      -19.00 dBm   (normal range)
```

The `25GBASE-LR` MikroTik `XS+31LC10D` also shows `Bias 0.00 mA / Tx -30.00 dBm` with only `Rx` normal. The fact that **SR and LR alike show the same symptom** is decisive.

# [04] Confirming the errdisabled Reason — The Clinching Evidence

```text
sw-core-01#show interfaces status errdisabled
   Port       Name             Status         Reason
---------- ---------------- ----------------- ----------------
   Et21                        errdisabled    xcvr-unsupported
   Et23                        errdisabled    xcvr-unsupported
   Et35                        errdisabled    xcvr-unsupported
   Et37                        errdisabled    xcvr-unsupported
   ... (Et1, Et3, ... many more ports the same)
```

All four ports — and many others — show the reason `xcvr-unsupported`. The **switch classifies the installed transceivers as "unsupported" and blocks the ports**.

`xcvr-unsupported` typically arises from:

- An SFP28 module not on Arista's certified/compatible list
- Optics coded exclusively for another vendor
- A module whose EEPROM data doesn't match Arista equipment
- An EOS policy that blocks unsupported transceivers

# [05] Identifying the Modules via inventory

Use `show inventory` to see exactly what's blocked.

```text
sw-core-01#show inventory
System has 56 switched transceiver slots
  Port Manufacturer     Model            Serial Number    Rev
  ---- ---------------- ---------------- ---------------- ----
  21   OEM              25GBASE-SR       PS3Hxxxxxx       0002
  23   OEM              25GBASE-SR       PS3Hxxxxxx       0002
  35   OEM              25GBASE-SR       PS3Hxxxxxx       0002
  37   MikroTik         XS+31LC10D       OLxxxxxxxxxx     1.0
```

The key point: the **switch reads the vendor/model/serial/revision correctly**.

```text
37   MikroTik   XS+31LC10D   OLxxxxxxxxxx   1.0
```

So it's not a case of **failing to read** the EEPROM. It reads the data but **does not recognize the module as Arista-compatible**, and blocks it as `xcvr-unsupported`.

# [06] Server-Side Cross-Check (ethtool)

Confirm the switch-side diagnosis once more from the server.

```text
root@server-a:~# ethtool ens801f0np0
        Supported link modes:   25000baseSR/Full ...
        Supported FEC modes: None        RS      BASER
        Speed: Unknown!
        Duplex: Unknown! (255)
        Link detected: no (No cable)
```

The server NIC **supports** 25G SR (`25000baseSR/Full`) and RS-FEC, yet reports `Link detected: no (No cable)`.

Since the switch has its transmitter off (`Tx Power -30.00 dBm` / `Bias 0.00 mA`), the server seeing "No cable" is the **natural consequence** — not a server NIC capability problem.

```text
root@server-a:~# ethtool --show-fec ens801f0np0
Configured FEC encodings: Auto
Active FEC encoding: None
```

`Active FEC: None` is merely a result of the link being down, not evidence of an FEC mismatch.

# [07] Interpreting the Physical Link State

Putting the data together, the optical path looks like this:

```text
Server NIC Tx  ─────────────▶  Switch Rx detected (Rx Power normal)
Server NIC Rx  ◀────────────X  Switch Tx disabled (Bias 0mA, Tx -30dBm)
```

| Evidence | Value |
|----------|-------|
| Switch Rx Power | Et21 -0.28 / Et23 -0.38 / Et35 -0.74 / Et37 1.05 dBm (detected) |
| Switch Tx Power | all four ports `-30.00 dBm` (no transmit) |
| Switch Bias | all four ports `0.00 mA` (laser not driven) |
| errdisabled reason | all four ports `xcvr-unsupported` |
| Server | `Link detected: no (No cable)` |

# [08] Root-Cause Conclusion

| Priority | Candidate cause | Assessment |
|---:|------|------------|
| 1 | Arista transceiver compatibility/support policy | **Very high** |
| 2 | OEM/third-party 25G SR·LR modules classified unsupported by EOS | **Very high** |
| 3 | unsupported-transceiver unlock/license not applied | High |
| 4 | Fiber cable problem | Low (Rx signal detected) |
| 5 | Server NIC configuration | Low (25G·RS-FEC supported) |
| 6 | FEC mismatch | Secondary (link block precedes it) |
| 7 | MTU/IP settings | Post-link-up check |

**Conclusion**: before cable type (SR/LR) or server settings, the issue is that the **Arista switch blocks the installed third-party/OEM 25G SFP28 transceivers as unsupported**. It's not a single bad module (different SR and LR modules all show the same symptom).

# [09] Recommended Actions

## [09-1] Replace with Arista-Compatible 25G SFP28 Modules (recommended)

The most stable fix. Capture module info beforehand to match against the compatibility list.

```text
show interfaces Ethernet21 transceiver detail
show interfaces transceiver detail
```

Check: `Vendor name`, `Vendor PN`, `Vendor SN`, `Identifier`, `Connector`, `Nominal bitrate`.

## [09-2] Allow Unsupported Transceivers for Testing

If this is a test environment and policy permits, consider:

```text
configure terminal
service unsupported-transceiver
end
```

Then re-enable the port:

```text
configure terminal
interface Ethernet21
   shutdown
   no shutdown
end
```

:warning: On this device (EOS 4.30.4M / 7050SX3), `service unsupported-transceiver` once returned `% Incomplete command`, so an additional argument or an unlock/license key may be required. Rather than guessing, **confirm with your vendor/Arista**. In production this may void vendor support, so use it only for validation/temporary purposes.
{: .notice--warning}

## [09-3] Set FEC Explicitly After the Link Recovers

Once the transceiver issue is resolved, align RS-FEC on both sides for 25G stability.

```text
# Switch
interface Ethernet21
   speed forced 25gfull
   error-correction encoding reed-solomon
   no shutdown
```

```bash
# Server
sudo ethtool --set-fec ens801f0np0 encoding rs
```

# [10] Post-Recovery Verification

| Step | What | Command | Expected |
|---:|------|---------|----------|
| 1 | errdisabled cleared | `show interfaces status errdisabled` | Port no longer listed |
| 2 | Tx optical output restored | `show interfaces Ethernet21 transceiver` | `Tx Power` not `-30 dBm`, `Bias` not `0 mA` |
| 3 | Server link | `ethtool ens801f0np0` | `Speed: 25000Mb/s`, `Link detected: yes` |
| 4 | FEC | `ethtool --show-fec ens801f0np0` | `Active FEC encoding: RS` |
| 5 | IP connectivity | `ping -c 5 10.0.0.2` | 0% packet loss |
| 6 | Throughput | `iperf3 -c 10.0.0.2 -P 8 -t 30` | ~23 Gbps or more |

# [11] Conclusion

Following `Et21`·`Et23` (OEM 25GBASE-SR), the cross-tests on `Et35` (OEM SR) and `Et37` (MikroTik XS+31LC10D 25GBASE-LR) all showed `errdisabled / xcvr-unsupported`.

```text
On Arista DCS-7050SX3-48YC8C-F / EOS 4.30.4M,
the installed OEM 25GBASE-SR and MikroTik 25GBASE-LR transceivers
are all classified as unsupported, leaving the ports errdisabled.
```

Because the switch ports emit no transmit light (`Bias 0 mA / Tx -30 dBm / Rx detected`), the server sees "No cable" — but the **actual cause is the switch blocking unsupported transceivers**. The first action is either (1) replacing with Arista-compatible 25G SFP28 (SR/LR) modules, or (2) obtaining the `unsupported-transceiver` unlock/license via your vendor/Arista — after which you validate FEC, cabling, MTU, IP, and iperf3 throughput.
