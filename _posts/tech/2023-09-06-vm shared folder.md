---
title: "가상머신(VM)과 Host간 공유폴더 만들기"
date: 2023-09-06
categories: VM
tags: [VM, Shared Folder]
---

가상머신(VM)에 Host와 공유폴더 생성
------  

### 환경

- ubuntu 22.04
- virt-manager
- kvm
- qemu
- virsh
- libivrt


### Host에서 설정
- shared folder 생성  

```shell
# 디렉토리 생성
sudo mkdir vm-shared

# 권한 설정(모든 사용자 쓰기, 읽기 모두 가능)
sudo chmod 777 vm-shared
```  


### virt-manager 설정

- virt-manager의 메뉴 → Edit → Virtual Machine Details  

![2023-09-06 13 59 49](https://github.com/cmaven/cmaven.github.io/assets/76153041/0249583e-21b8-42d7-a26b-bf9c4d533548)

- vm 창의 메뉴 → View → Details  

![2023-09-06 14 00 04](https://github.com/cmaven/cmaven.github.io/assets/76153041/53dcb2e7-91ad-476e-ba96-ca9d85a6f6c6)

- Memory → Details 의 Enable shared memory 체크

![2023-09-06 13 31 09](https://github.com/cmaven/cmaven.github.io/assets/76153041/19abe96e-59fc-4212-a0f6-4ccb2c248397)

- 하단 Add Hardware → Filesystem → Details 의 Source path / Target path 작성
  - Source path : Host에 shared folder로 지정할 디렉토리 선택 (Browse 로 Local Directory 선택)
  - Target path : VM에서 shared folder를 마운트할 때, 사용할 이름

![2023-09-06 13 32 06](https://github.com/cmaven/cmaven.github.io/assets/76153041/b4a01499-fbea-4346-bdcb-d039afa86333)  

![2023-09-06 13 32 18](https://github.com/cmaven/cmaven.github.io/assets/76153041/a10725c9-829f-4471-bc89-cf94e57e54e5)  

- Apply


### VM에서 설정
- shared folder 생성

```shell
# 디렉토리 생성
sudo mkdir vm-shared

# 권한 설정(모든 사용자 쓰기, 읽기 모두 가능)
sudo chmod 777 vm-shared
```  

- 마운트  
  
```shell
# mount -t 타입 target_path vm_shared_folder_path
sudo mount -t virtiofs vm-shared /root/vm-shared
```   