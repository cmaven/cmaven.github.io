---
title: "로컬 환경(Shell)에서 Git 계정(사용자) 변경 하기"
date: 2022-02-16
categories: Git
tags: [User, Config]
---

:bulb: 두 개의 Git 계정을 하나의 시스템에서 사용 시, 원하는 계정으로 Remote Repository에 작업을 수행하고자 할 때
{: .notice--info}

# [01]  설정 확인

전체 설정 확인

``` shell
git config -l
```
- 출력예시  
![git-confing 확인-01](https://user-images.githubusercontent.com/76153041/154203932-08c2ccee-1154-47e5-9de2-c4a89ed00e18.png)


특정 설정 확인(사용자 이름, 사용자 이메일)
``` shell
git config user.name
git config user.email
```
- 출력예시  
![git-confing 확인-02](https://user-images.githubusercontent.com/76153041/154203935-2d0f7c70-01ff-46df-b9df-a7a8a2c06080.png)

# [02]  설정 변경

사용자 계정 및 이메일 변경

``` shell
git config --global user.name $(username)
git config --global user.email $(useremail)
```

- 출력예시  
![git-config 수정](https://user-images.githubusercontent.com/76153041/154203940-6bce8ce9-827d-449a-9b02-7c781b3ce793.png)





