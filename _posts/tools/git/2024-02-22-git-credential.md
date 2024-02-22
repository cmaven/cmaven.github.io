---
title: "Git Pull, Commit, Push 시, 인증 없이 수행하기(SSH,Credential)"
date: 2024-02-22
categories: Git
tags: [Git, Credential]
---

:bulb: 본 문서는 Git 작업 수행에 필요한 credential(인증)에 대해 정리한다.  
일반적으로 pull, commit, push 수행 시에 사용자 ID, PW(Token) 값을 요구하는데, 이를 간편하게 수행하는 방법을 알아본다.
{: .notice--info}

# [01]  사용자 인증 정보를 로컬(Local) Git에 저장하는 방법

1. SSH Key 사용 방법
   - 개발을 수행하는 시스템에서 SSH Key 생성 후, Git에 등록
   - SSH 활용 Repository 
2. Git Config(Credential) 사용 방법
   - 시스템 영구 저장
   - Cache 활용 일정 시간 저장


# [02]  SSH Key 등록, 활용  

## SSH Key 생성

```bash
# 수행 시, 입력 요구사항은 default (Enter)
ssh-keygen -t rsa -C "Git" -b 4096

# 출력된 내용을 gitlab 의 SSH Key 값에 복사&붙여넣기
cat ~/.ssh/id_rsa.pub

# 출역 예
root@cmaven:~# cat ~/.ssh/id_rsa.pub
ssh-rsa AAAA124123QABAAACAQCbKx1YXw8bUIWUb39eLkm7+AMVT92PhMCo...
```  

## SSH Key를 Git에 등록  

프로필 :arrow_right: Settings :arrow_right: SSH and GPG Keys  :arrow_right:  New SSH Key  :arrow_right:  Key 값 입력  :arrow_right:  Add SSH Key  

![그림1](https://github.com/cmaven/cmaven.github.io/assets/76153041/cb7654b1-1c4e-4522-8144-2f1d2905902a)  

![그림2](https://github.com/cmaven/cmaven.github.io/assets/76153041/bf6d3bc7-4b6f-4de3-ad09-1289cd56f9d1)  



## 활용할 Repository를 Clone with SSH로 다운로드  

![2024-02-22 13 52 04](https://github.com/cmaven/cmaven.github.io/assets/76153041/8fdfd3d3-5f26-4a44-8258-ec53188b365e)  

이 후에는 인증 없이 Pull, Commit, Push 수행 가능


# [03]  Git Config(Credential) 사용  

- 개발 시스템의 Git Repository에서 실행  
- 아래 방법 중 하나를 적용하고 최초 IP,PW(Token)으로 인증하면 이 후에는 인증 없이 Pull, Commit, Push 수행 가능

## 영구 저장  

```bash
git config credential.helper store

# 변경내역 확인
git config --list
```  

## Cache 저장  

```bash
# default 15분
git config credential.helper cache

# 시간 지정 (timeout 3600초 = 1시간)
git config credential.helper `cache --timeout=3600`
```  


## 모든 프로젝트에 적용  

```bash
git config credential.helper store --global
```  