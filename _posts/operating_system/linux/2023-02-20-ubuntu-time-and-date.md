---
title: "Ubuntu 시간 설정(time, date)"
category: Linux
tags: [Ubuntu, date, time]
date: 2023-02-20
---

Ubuntu 시간 설정(time, date)
------  

### 현재 시간 및 날짜 확인

```shell
date

#ex)
root@worker:~# date
Mon Feb 20 08:32:53 AM UTC 2023
```  

### 시간 (Timezone) 변경

- 시간은 `Asia/Seoul`을 기준으로 한다.

#### `ln` 명령어를 활용하여 변경

```shell
sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime
```  

#### `timedatectl` 명령어를 활용하여 변경

```shell
sudo timedatectl set-timezone 'Asia/Seoul'

# ex)
root@worker:~# date
Mon Feb 20 08:32:53 AM UTC 2023
root@worker:~# sudo timedatectl set-timezone 'Asia/Seoul'
root@worker:~# date
Mon Feb 20 05:36:03 PM KST 2023
```  


### `ln`, `timedatectl` 활용 방법으로 정확한 시간을 맞출 수 없을 때

- Timezone을 변경하였지만 정확한 시간이 반영되지 않을 수 있음

```shell
# ex) 현재 시각은 Mon Feb 20 05:36:03 PM KST 2023
# 약 2분 정도의 시간 차이가 있음
root@worker:~# date
Mon Feb 20 05:36:03 PM KST 2023
```  

- NTP(Network Time Protocol)을 사용하여 시간 동기화
  - 네트워크를 통해 시스템의 시간을 동기화 하는 프로토콜
  - 설치

  ```shell
  sudo apt-get install -y ntp

  # 설치 후, 실행 확인
  systemctl status ntp

  # ex) 정확한 숫자는 다소 차이가 있을 수 있음
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

- 설치 및 실행 후, 다시 Timezone 설정을 해주면 동기화된 시간을 확인할 수 있다.  



