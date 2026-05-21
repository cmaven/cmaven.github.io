---
title: "Configuring Time and Date on Ubuntu"
description: "How to change the timezone and synchronize time on Ubuntu using timedatectl, ln, and NTP"
excerpt: "How to change the Ubuntu timezone to Asia/Seoul and synchronize time via NTP"
date: 2023-02-20
categories: Linux
tags: [Ubuntu, timezone, timedatectl, NTP, time-config, time-sync, Asia-Seoul]
ref: ubuntu-time-and-date
---

:bulb: This guide covers how to change the timezone on Ubuntu and synchronize time using NTP.
{: .notice--info}

# [01] Check the Current Time and Date

```shell
date

#ex)
root@worker:~# date
Mon Feb 20 08:32:53 AM UTC 2023
```

# [02] Change the Timezone

This guide uses `Asia/Seoul` as the example timezone.

## 2-1. Change with the `ln` Command

```shell
sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime
```

## 2-2. Change with the `timedatectl` Command

```shell
sudo timedatectl set-timezone 'Asia/Seoul'

# ex)
root@worker:~# date
Mon Feb 20 08:32:53 AM UTC 2023
root@worker:~# sudo timedatectl set-timezone 'Asia/Seoul'
root@worker:~# date
Mon Feb 20 05:36:03 PM KST 2023
```

# [03] Time Synchronization with NTP

Even after changing the timezone, the exact time may still not be accurate.

```shell
# ex) The current time shows as Mon Feb 20 05:36:03 PM KST 2023
# There is about a 2-minute time drift
root@worker:~# date
Mon Feb 20 05:36:03 PM KST 2023
```

## 3-1. Install and Start NTP

> NTP (Network Time Protocol): a protocol for synchronizing system time over a network.

```shell
sudo apt-get install -y ntp

# After installation, verify it is running
systemctl status ntp

# ex) Exact numbers may vary
root@worker:/etc/apt# sudo systemctl status ntp
● ntp.service - Network Time Service
     Loaded: loaded (/lib/systemd/system/ntp.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2009-01-01 10:25:15 KST; 6s ago
       Docs: man:ntpd(8)
    Process: 781120 ExecStart=/usr/lib/ntp/ntp-systemd-wrapper (code=exited, status=0/SUCCESS)
   Main PID: 781126 (ntpd)
      Tasks: 2 (limit: 57601)
     Memory: 1.4M
        CPU: 16ms
     CGroup: /system.slice/ntp.service
             └─781126 /usr/sbin/ntpd -p /var/run/ntpd.pid -g -u 133:138

Jan 01 10:25:15 worker ntpd[781126]: kernel reports TIME_ERROR: 0x41: Clock Unsynchronized
Jan 01 10:25:15 worker systemd[1]: Started Network Time Service.
Jan 01 10:25:16 worker ntpd[781126]: Soliciting pool server 211.233.40.78
Jan 01 10:25:17 worker ntpd[781126]: Soliciting pool server 121.162.54.1
Jan 01 10:25:17 worker ntpd[781126]: Soliciting pool server 106.247.248.106
```

## 3-2. Verify Time Synchronization

After installing and starting NTP, reapply the timezone setting to see the synchronized time.
