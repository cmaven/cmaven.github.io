---
title: "Disabling Suspend/Sleep Mode on Ubuntu"
description: "How to disable Suspend and Sleep on Ubuntu Server/Desktop to prevent SSH session drops"
excerpt: "Use systemctl mask to disable Ubuntu's power-saving modes (Suspend/Sleep/Hibernate)"
categories: Linux
tags: [Ubuntu, Suspend, Sleep, power-saving, SSH, systemctl, Power-Management]
date: 2022-08-05
ref: ubuntu-sleepmode-disable
---

:bulb: This post describes how to prevent Ubuntu Server/Desktop from entering Suspend or Sleep mode.
{: .notice--info}

# [01] Environment and Situation

- Ubuntu 24.04 Server / Desktop
- While using Ubuntu remotely over SSH, the connection drops and cannot be re-established
- After a period of inactivity, the system transitions into Suspend/Sleep mode, dropping the session
- Some desktop environments require a reboot to recover

# [02] Cause

By default, Ubuntu 24.04 has Suspend/Sleep mode enabled.

```shell
sudo systemctl status sleep.target suspend.target hibernate.target hybrid-sleep.target
```

![power management-sleep enabled](https://user-images.githubusercontent.com/76153041/183005465-418ea20e-4229-4e70-9838-447938d540d5.png)

# [03] Solution

Mask the related services so they cannot start.

```shell
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

![power management-sleep disabled](https://user-images.githubusercontent.com/76153041/183005473-63e6011d-c292-4269-b30c-492421716a7f.png)

# [04] Additional Notes

To re-enable these features:

```shell
sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

![power management-sleep re-enabled](https://user-images.githubusercontent.com/76153041/183005471-63c1ffe9-ee7d-47fd-bcd6-f57c585722f8.png)
