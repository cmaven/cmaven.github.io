<!-- 2026-06-11-linux-serial-terminal-programs.md: Linux serial terminal programs — overview/install/usage/comparison/removal | created: 2026-06-11 -->
---
title: "Linux Serial Terminal Programs — Install, Use, and Compare screen/minicom/picocom/tio"
description: "A one-stop guide to the serial terminal programs (screen, minicom, picocom, tio, cu) used to reach network-device and embedded consoles on Ubuntu: overview, install, start/stop, pros/cons, and removal"
excerpt: "From install to exit shortcuts, pros and cons, and clean removal — comparing screen, minicom, picocom, and tio for USB-serial console access"
date: 2026-06-11
categories: Etc
tags: [serial, console, screen, minicom, picocom, tio, cu, Ubuntu, Linux, ttyUSB, console-cable, network-device]
ref: linux-serial-terminal-programs
---

:bulb: A single roundup of the Linux serial terminal programs you use to reach the **console port** of network devices (switches/routers) or embedded boards over a USB-serial cable — overview, install, usage (start/stop), pros/cons, and removal.
{: .notice--info}

**Environment**: Ubuntu 22.04+ / USB-to-Serial console cable (FTDI, PL2303, etc.)

---

# [01] Overview — What Is a Serial Terminal

A network device's **Console port** is a path to the CLI that works even without an IP. When you connect a USB-serial cable to the PC, Linux usually exposes it as:

- `/dev/ttyUSB0` — USB-Serial converter chips like FTDI, PL2303
- `/dev/ttyACM0` — CDC-ACM family (USB built into some boards)

A "serial terminal" is a program that opens this device and communicates using serial parameters such as **baud rate** (e.g. 9600). The main ones are `screen`, `minicom`, `picocom`, and `tio`.

:warning: A regular user may lack serial-port access and hit `Permission denied`. Add your user to the `dialout` group to connect without sudo (re-login required).
{: .notice--warning}

```bash
# Identify the device
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
dmesg | grep -iE 'ttyUSB|ttyACM' | tail   # device name at plug-in time
lsusb                                       # check the serial chip (FTDI/Prolific)

# Grant access (once, then log out → log in)
sudo usermod -aG dialout $USER
```

> All examples below assume **9600 8N1, no flow control** (the default for Arista and similar network devices). Just change the baud to match your device.

---

# [02] screen

The most widely preinstalled, all-purpose "just connect" tool. Not serial-specific, but supports serial.

```bash
# Install
sudo apt update && sudo apt install -y screen

# Start: screen <device> <baud>
screen /dev/ttyUSB0 9600
```

- **After starting**: if the screen is blank, press `Enter` to wake the prompt.
- **Quit**: `Ctrl + a` then `k` → `y` (force-kill the session).
- **Detach (keep in background)**: `Ctrl + a` then `d`; reattach with `screen -r`.

---

# [03] minicom

A serial-dedicated program. Saves settings via menus and provides **file transfer (X/Y/Zmodem)** and logging.

```bash
# Install
sudo apt install -y minicom

# Start: specify device/baud directly
sudo minicom -D /dev/ttyUSB0 -b 9600

# Settings menu (persistent)
sudo minicom -s
```

- In `Serial port setup`, set **Serial Device** (`/dev/ttyUSB0`), **Bps/Par/Bits** (`9600 8N1`), **Hardware/Software Flow Control** (`No`) → `Save setup as dfl`.
- **Quit**: `Ctrl + a` then `x` → `Yes`.

---

# [04] picocom

As the name suggests, lightweight with clear command-line options — great for **scripts/automation**. Almost no UI features.

```bash
# Install
sudo apt install -y picocom

# Start
picocom -b 9600 /dev/ttyUSB0
```

- **Quit**: `Ctrl + a` then `Ctrl + x`.
- All other shortcuts use the `Ctrl + a` prefix.

---

# [05] tio (Recommended)

A modern serial terminal. Clean command line and **auto-reconnect when the device is unplugged and plugged back in** — the most convenient option when you attach to device consoles often.

```bash
# Install (default repos on Ubuntu 22.04+)
sudo apt install -y tio

# Start: tio defaults to 115200, so specify 9600
tio -b 9600 /dev/ttyUSB0
```

- **Quit**: `Ctrl + t` then `q` (all shortcuts use the `Ctrl + t` prefix).
- **List shortcuts**: `Ctrl + t` then `?`.
- **Save a profile**: register it in `~/.config/tio/config` to connect by name.

```ini
# ~/.config/tio/config — connect with "tio arista"
[arista]
device = /dev/ttyUSB0
baudrate = 9600
```

---

# [06] (Reference) cu / putty

- **cu**: `sudo apt install -y cu` → `cu -l /dev/ttyUSB0 -s 9600`, quit with `~.`. An old UUCP-era tool for simple uses.
- **putty**: has GUI/CLI versions on Linux too. `putty -serial /dev/ttyUSB0 -sercfg 9600`. The tools above are nicer in a console environment, though.

---

# [07] Pros and Cons

| Program | Pros | Cons | Best for |
|---------|------|------|----------|
| **screen** | Preinstalled almost everywhere, simple | Lacks serial-specific features, confusing exit keys, awkward logging | Quick, ad-hoc console access on someone else's server |
| **minicom** | Serial-dedicated, saves settings, logging/file transfer | Fiddly initial setup UI | When you need features like file transfer |
| **picocom** | Lightweight, clear options, good for automation | Almost no UI features | Cleanly viewing a console from a script |
| **tio** | Modern, auto-reconnect, profiles | Sometimes not preinstalled | **Attaching to your own device consoles often (personal pick)** |
| **putty** | Familiar in GUI | Awkward in a server CLI | GUI access on Ubuntu Desktop |

## Recommended Order

For attaching to network-device consoles from your own PC: **tio → picocom → screen → minicom**.

- **Your device / used often** → `tio` (auto-reconnect and profiles are decisive)
- **Ad-hoc / on-site / someone else's server (install rights unclear)** → `screen` (already everywhere)
- **Need file transfer** → `minicom`

> In short: *"tio for your own setup, screen for ad-hoc"* — those two axes are enough.

---

# [08] Removal

```bash
# Remove individually
sudo apt remove -y screen
sudo apt remove -y minicom
sudo apt remove -y picocom
sudo apt remove -y tio

# Fully remove including config files (purge)
sudo apt purge -y minicom

# Clean up dependencies
sudo apt autoremove -y
```

- `remove` deletes the package only; `purge` also removes config files under `/etc`.
- User settings (`~/.config/tio/`, `~/.minirc.dfl`, etc.) must be deleted manually.

```bash
rm -f ~/.minirc.dfl              # minicom user settings
rm -rf ~/.config/tio             # tio profiles
```

---

# [09] Summary

| Step | Command |
|------|---------|
| Identify device | `ls /dev/ttyUSB*`, `dmesg \| grep ttyUSB`, `lsusb` |
| Permission | `sudo usermod -aG dialout $USER` (re-login) |
| screen | `screen /dev/ttyUSB0 9600` / quit `Ctrl+a` `k` |
| minicom | `minicom -D /dev/ttyUSB0 -b 9600` / quit `Ctrl+a` `x` |
| picocom | `picocom -b 9600 /dev/ttyUSB0` / quit `Ctrl+a` `Ctrl+x` |
| tio | `tio -b 9600 /dev/ttyUSB0` / quit `Ctrl+t` `q` |
| Removal | `sudo apt remove/purge <pkg>` + `autoremove` |
