---
title: "nvidia-smi 실행 시, Driver/library version mismatch 오류"
description: "Ubuntu에서 nvidia-smi 실행 시 Driver/library version mismatch 오류 원인 분석 및 해결 방법"
excerpt: "unattended-upgrade로 인한 NVIDIA 드라이버 버전 불일치 오류 해결법 (모듈 재로드, 자동업데이트 방지)"
categories: Linux
tags: [Ubuntu, NVIDIA, nvidia-smi, GPU, 드라이버오류, unattended-upgrade, 버전불일치]
date: 2022-03-24
---

:bulb: nvidia-driver 설치된 상태에서 `nvidia-smi` 실행 시, Failed to initialize NVML: Driver/library version mismatch 오류가 발생할 때의 해결 방법을 작성한다.
{: .notice--info}

# [01] 상황

- nvidia gpu가 장착된 ubuntu 서버
- nvidia-driver 설치 후, gpu 사용
- nvidia-smi 명령어 수행 시, Failed to initialize NVML: Driver/library version mismatch 오류 발생하며 동작하지 않음

  ![nvidia-error-01](https://user-images.githubusercontent.com/76153041/159899223-2e10ca48-c076-4384-8162-d07eccd9c06d.png)

# [02] 원인

## 2-1. 문제 확인

```shell
dmesg
```

![nvidia-error-02](https://user-images.githubusercontent.com/76153041/159899571-6bd84838-cc76-4ae3-9f9e-391564d4c4a1.png)

- NVRM: API mismatch ... 오류 메시지
- 클라이언트의 버전은 470.103.01인데, 커널 모듈 버전은 470.86
- 리눅스의 unattended-upgrade가 보안 관련 패키지를 자동으로 업데이트하여 버전 간 차이가 발생

## 2-2. unattended-upgrade 수행 목록 확인

```shell
cat /var/log/apt/history.log
```

![nvidia-error-03](https://user-images.githubusercontent.com/76153041/159901192-57d1870e-d0ce-4870-8dd8-35b597c89f91.png)

```shell
view /var/log/unattended-upgrades/unattended-upgrades.log.1.gz
```

![nvidia-error-04](https://user-images.githubusercontent.com/76153041/159901243-4a9784c3-69ad-485e-be1d-15e1ece17b76.png)

![nvidia-error-05](https://user-images.githubusercontent.com/76153041/159901195-00637157-36e7-4bc4-b490-278201990596.png)

- log 파일의 내용을 보면 2022-02-08에 libnvidia-* 관련 패키지들이 자동으로 업데이트 되었다.

:bulb: unattended-upgrades.log 에서 관련 내용을 찾을 수 없으면, 이전 log 파일(ex, log.1.gz 등)을 확인해본다.
{: .notice--info}

# [03] 해결방안 1: unattended-upgrade 방지

unattended-upgrade의 대상 패키지에서 nvidia 관련 패키지를 제외한다.

`/etc/apt/apt.conf.d/50unattended-upgrades` 파일 수정:

```shell
# ubuntu 24.04 기준
# /etc/apt/apt.conf.d/50unattended-upgrades 파일에 아래 내용 추가

Unattended-Upgrade::Package-Blacklist {
  "nvidia-*.";
}
```

![이미지 41](https://user-images.githubusercontent.com/76153041/183000202-374ce1b1-ae1e-46d2-8374-63c91c2ddae4.png)

:small_blue_diamond:참조: [해당링크참조](https://blog.ggaman.com/1029){:target="_blank"}

# [04] 해결방안 2: nvidia module 삭제(재시작)

이미 자동으로 업데이트 되어, 설치가 된 경우, 기존 모듈을 삭제하면 문제를 해결할 수 있다.

## 4-1. nvidia 커널 모듈 확인

```shell
lsmod |grep nvidia
```

![nvidia-error-06](https://user-images.githubusercontent.com/76153041/159901287-a51e2c73-38ea-490d-9638-9cbc9e92ad61.png)

## 4-2. 모듈 제거

```shell
# 출력된 모듈 제거
rmmod $모듈명

# ex)
rmmod nvidia_uvm
```

:warning: 아래와 같이 ERROR: Module nvidia_drm is in use 오류가 발생하면 관련 프로세스를 종료한다.
{: .notice--warning}

![nvidia-error-07](https://user-images.githubusercontent.com/76153041/159902947-16947caf-9940-42f2-8f37-34aad3c1d7ab.png)

```shell
# nvidia 사용 프로세스 확인 및 종료
lsof /dev/nvidia*
kill -9 $PID

# ex)
kill -9 449143
```

![nvidia-error-08](https://user-images.githubusercontent.com/76153041/159903271-b8e198b2-077b-4bd5-8499-046846713f0d.png)

## 4-3. 결과 확인

모듈이 자동으로 재업로드되어 `nvidia-smi` 명령어가 정상 작동함

![nvidia-error-09](https://user-images.githubusercontent.com/76153041/159903143-af2f7b1e-3098-4322-b79d-8ae6808b0dc0.png)
