---
title: "Changing the Hostname on Ubuntu (Linux)"
description: "How to change the hostname on Ubuntu using the hostnamectl command"
excerpt: "How to change an Ubuntu hostname with the hostnamectl set-hostname command"
date: 2022-11-02
categories: Linux
tags: [Ubuntu, hostname, hostnamectl, change-hostname]
ref: ubuntu-hostname
---

:bulb: This guide describes how to change the hostname on Ubuntu.
{: .notice--info}

# [01] Check the Current Hostname

```shell
hostname

# ex
root@gmaster:~# hostname
gmaster
```

# [02] Change the Hostname

```shell
hostnamectl set-hostname ${hostname}

# ex
root@gmaster:~# hostnamectl set-hostname gworker01
root@gmaster:~# hostname
gworker01
```

After that, the change takes effect once you close and reopen the terminal, or reboot the system.

:small_blue_diamond:Reference: [How to do it without rebooting (askubuntu)](https://askubuntu.com/questions/87665/how-do-i-change-the-hostname-without-a-restart){:target="_blank"}
