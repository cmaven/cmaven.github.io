---
title: "BAD PASSWORD: contains the user name 우회하기"
category: Linux
tags: [Ubuntu]
date: 2023-09-21
---

BAD PASSWORD: the password contains the user name in some form  
기능 끄기  

------  

### 상황
Linux(Ubuntu)에서 Password를 입력하는데, 
`BAD PASSWORD: The password contains the user name in some form`
오류로, 원하는 Password로 입력이 불가능 할 때
- ex) Test용 서버
  - username: testuser
  - passowrd: testuser

### 검증 기능 끄기
🛑 보안이 중요한 환경에서는 수정을 권장하지 않음

- Password 관련 설정 파일 확인
  - Debian(Ubuntu)의 경우, /etc/pam.d/common-password
    - 아래의 경우, pam_pwquality.so 에서 설정을 참조
- Password 검증 설정 변경
  - /etc/security/pwquality.conf
    - `usercheck = 0`으로 변경

```shell
# root 권한 
# /etc/pam.d/common-password
# here are the per-package modules (the "Primary" block)
password        requisite                       pam_pwquality.so retry=3
password        [success=2 default=ignore]      pam_unix.so obscure use_authtok try_first_pass yescrypt
```  

```shell
# root 권한 
# /etc/security/pwquality.conf
# Whether to check if it contains the user name in some form.
# The check is enabled if the value is not 0.
usercheck = 0
#
```  


[참조][Password 검증 설정 참조](https://www.networkworld.com/article/2726217/how-to-enforce-password-complexity-on-linux.html){: target="_blank"}  
