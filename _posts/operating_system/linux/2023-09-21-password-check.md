---
title: "BAD PASSWORD: contains the user name 우회하기"
description: "Ubuntu에서 BAD PASSWORD 오류를 우회하여 사용자명 포함 패스워드를 설정하는 방법 (pwquality.conf)"
excerpt: "pwquality.conf의 usercheck 설정으로 패스워드 검증 정책을 변경하는 방법"
categories: Linux
tags: [Ubuntu, password, pwquality, pam, 패스워드정책, 보안설정]
date: 2023-09-21
---

:bulb: Linux(Ubuntu)에서 Password 입력 시 `BAD PASSWORD: The password contains the user name in some form` 오류로 원하는 Password로 설정이 불가능할 때의 우회 방법을 작성한다.
{: .notice--info}

# [01] 상황

- Linux(Ubuntu)에서 Password를 입력하는데, `BAD PASSWORD: The password contains the user name in some form` 오류로 원하는 Password로 입력이 불가능
- ex) Test용 서버
  - username: testuser
  - password: testuser

# [02] 검증 기능 끄기

:warning: 보안이 중요한 환경에서는 수정을 권장하지 않는다.
{: .notice--warning}

## 2-1. Password 관련 설정 파일 확인

Debian(Ubuntu)의 경우, `/etc/pam.d/common-password` 에서 `pam_pwquality.so` 설정을 참조한다.

```shell
# root 권한
# /etc/pam.d/common-password
# here are the per-package modules (the "Primary" block)
password        requisite                       pam_pwquality.so retry=3
password        [success=2 default=ignore]      pam_unix.so obscure use_authtok try_first_pass yescrypt
```

## 2-2. Password 검증 설정 변경

`/etc/security/pwquality.conf` 에서 `usercheck = 0`으로 변경한다.

```shell
# root 권한
# /etc/security/pwquality.conf
# Whether to check if it contains the user name in some form.
# The check is enabled if the value is not 0.
usercheck = 0
#
```

:small_blue_diamond:참조: [Password 검증 설정 참조](https://www.networkworld.com/article/2726217/how-to-enforce-password-complexity-on-linux.html){:target="_blank"}
