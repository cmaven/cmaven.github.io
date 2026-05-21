---
title: "WSL Terminal Color Settings - Fixing the Black Background"
description: "Why Windows Terminal shows a black background when opening WSL Ubuntu, and how to apply the purple Ubuntu theme"
excerpt: "Understand the color scheme difference between the WSL profile and the Ubuntu profile, and learn how to set the background color you want"
date: 2026-03-26
categories: Windows
tags: [WSL, Windows-Terminal, color-settings, Ubuntu, Color-Scheme, settings.json, terminal]
ref: wsl-terminal-color-settings
---

:bulb: This guide explains why Windows Terminal shows a black background when opening WSL, and how to apply the familiar purple Ubuntu theme.
{: .notice--info}

# [01] The Problem

After installing WSL on Windows, searching for it in the Start menu and launching it opens Windows Terminal.

The dropdown menu shows multiple profiles, including Windows PowerShell, Command Prompt, and Ubuntu.

- **Opening the Ubuntu tab directly** -> the familiar **purple background** terminal appears
- **Opening WSL by default** -> a **black background** appears

Even after changing the default profile to Ubuntu, the black background sometimes persists.

---

# [02] Cause: Per-Profile Color Schemes

Windows Terminal **maintains an independent color scheme for each profile**.

| Profile | Default color scheme | Background color |
|--------|---------------|--------|
| WSL profile | Default (Campbell) | Black |
| Ubuntu profile | Ubuntu-specific | Purple (`#300A24`) |

Even if you change the default profile to Ubuntu, the WSL profile's colors may still apply, resulting in a black screen.

---

# [03] Solutions

## 3-1. Change the default profile to Ubuntu

Open Windows Terminal settings (`Ctrl + ,`), and on the **Startup** tab change the **Default profile** to `Ubuntu`.

This way the Ubuntu profile is selected automatically whenever you open the terminal.

## 3-2. Check and change the color scheme

If you still see a black screen after changing the default profile, you need to set the Ubuntu profile's color scheme directly.

### (A) Change via GUI

1. Open Settings (`Ctrl + ,`)
2. Click **Ubuntu** in the profile list on the left
3. Select the **Appearance** tab
4. Change **Color scheme** to `One Half Dark` or whichever you prefer
5. Manually set the background color to `#300A24` (the default Ubuntu purple)

### (B) Change via settings.json

Click `Open JSON file` at the bottom-left of the settings screen and add the following inside the Ubuntu profile entry.

```json
{
    "name": "Ubuntu",
    "background": "#300A24",
    "colorScheme": "One Half Dark"
}
```

## 3-3. Save and verify

Settings apply immediately on save. Open a new tab and confirm the purple background appears.

---

# [04] Creating Your Own Color Scheme

If the built-in color schemes don't suit you, add a custom scheme to the `schemes` array in `settings.json`.

```json
{
    "name": "Ubuntu Custom",
    "background": "#300A24",
    "foreground": "#EEEEEC",
    "cursorColor": "#FFFFFF",
    "black": "#2E3436",
    "red": "#CC0000",
    "green": "#4E9A06",
    "yellow": "#C4A000",
    "blue": "#3465A4",
    "purple": "#75507B",
    "cyan": "#06989A",
    "white": "#D3D7CF",
    "brightBlack": "#555753",
    "brightRed": "#EF2929",
    "brightGreen": "#8AE234",
    "brightYellow": "#FCE94F",
    "brightBlue": "#729FCF",
    "brightPurple": "#AD7FA8",
    "brightCyan": "#34E2E2",
    "brightWhite": "#EEEEEC"
}
```

Then set the Ubuntu profile's `colorScheme` to `"Ubuntu Custom"`.

---

# [05] Summary

| Setting | Location | Effect |
|------|------|------|
| Change default profile | Settings -> Startup -> Default profile | Ubuntu opens immediately on launch |
| Change color scheme | Settings -> Ubuntu -> Appearance | Apply background, text colors, and more |
| Set background color directly | settings.json -> background | Fine-grained control over the exact color |

The key takeaway is that **the "default profile" and the "color scheme" are independent settings**. Check both - changing the default profile to Ubuntu AND adjusting the color scheme - to get the terminal environment you want.
