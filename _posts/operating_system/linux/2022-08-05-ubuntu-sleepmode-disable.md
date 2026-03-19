---
title: "Ubuntu Suspend/Sleep Mode 비활성화"
description: "Ubuntu Server/Desktop에서 Suspend, Sleep Mode를 비활성화하여 SSH 접속 끊김을 방지하는 방법"
excerpt: "systemctl mask 명령으로 Ubuntu의 절전모드(Suspend/Sleep/Hibernate)를 비활성화하는 방법"
categories: Linux
tags: [Ubuntu, Suspend, Sleep, 절전모드, SSH, systemctl, Power-Management]
date: 2022-08-05
---

:bulb: Ubuntu Server/Desktop 사용 시, Suspend, Sleep Mode로 진입하는 현상을 방지하는 방법을 작성한다.
{: .notice--info}

# [01] 환경 및 상황

- Ubuntu 24.04 Server / Desktop
- 원격에서 SSH를 통해 Ubuntu 사용 중 접속 끊김 및 재접속 불가 현상 발생
- 일정 시간 작업을 수행하지 않을 때, Suspend/Sleep Mode로 전환되어 세션이 끊기는 것으로 파악
- 일부 Desktop 환경의 경우 재부팅이 필요하기도 함

# [02] 원인

Ubuntu 24.04는 기본적으로 Suspend/Sleep Mode(일시중단, 절전모드)가 활성화되어 있다.

```shell
sudo systemctl status sleep.target suspend.target hibernate.target hybrid-sleep.target
```

![power management-sleep enable 상태](https://user-images.githubusercontent.com/76153041/183005465-418ea20e-4229-4e70-9838-447938d540d5.png)

# [03] 해결방안

관련 Service를 모두 중단시킨다.

```shell
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

![power management-sleep disable 로 변경하기](https://user-images.githubusercontent.com/76153041/183005473-63e6011d-c292-4269-b30c-492421716a7f.png)

# [04] 기타

해당 기능을 다시 활성화(재시작)하려면:

```shell
sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

![power management-sleep enable 로 변경하기](https://user-images.githubusercontent.com/76153041/183005471-63c1ffe9-ee7d-47fd-bcd6-f57c585722f8.png)
