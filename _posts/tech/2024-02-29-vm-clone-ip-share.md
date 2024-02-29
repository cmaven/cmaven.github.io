---
title: "복제(Clone)한 가상머신(VM)의 IP 충돌문제 해결"
date: 2024-02-29
categories: VM
tags: [VM, DHCP, IP]
---

:bulb: Ubuntu, KVM, Virt-manager를 사용하는 환경에서, 기존의 가상머신을 복제(Clone)할 경우, DHCP 서버에서 IP를 할당 받지 못하는 문제가 발생한다.  
기존의 가상머신과 복제한 가상머신이 동일한 IP를 가진 것처럼 동작한다.  
기존의 가상머신과, 복제한 가상머신이 서로 다른 IP를 정상적으로 할당 받을 수 있는 방법을 작성한다.
{: .notice--info}


# [01]  환경 및 상황  

## 환경
- ubuntu 22.04
- virt-manager
- kvm
- qemu
- virsh
- libvirt  

## 상황
- A 가상머신을 Clone하여 B 가상머신 생성
- A의 가상머신이 10.10.10.10의 IP를 DHCP 서버에서 할당 받음
- B의 가상머신은 Link를 UP하여도 IP를 할당 받지 못함
- virsh으로 IP 할당 상태를 확인할 경우 A의 가상머신이 할당 받은 IP만 확인할 수 있음  

- :triangular_flag_on_post: 예) 실행 중인 VM  
  ![2024-02-29 13 59 55](https://github.com/cmaven/cmaven.github.io/assets/76153041/ae1b40b3-cba6-4464-b264-bff4263ad300)     
- 실행 중인 VM이 2개인데, IP 할당은 하나로 표시됨 (`virsh net-dhcp-leases default`)
  ![2024-02-26 18 18 33](https://github.com/cmaven/cmaven.github.io/assets/76153041/512b0ce6-a064-4584-a49e-96fd38cbd580)

## 원인  
기본적으로 리눅스에서 IP 주소는 DHCP 서버로부터 MAC 주소를 기반으로 할당 받지 않는다.  
대신 `machine-id`를 기준으로 IP 주소를 할당 받는다.  
가상머신을 복제할 경우, *두 가상머신은 서로 같은 `machine-id`를 갇는다.*  

![2024-02-26 18 12 17](https://github.com/cmaven/cmaven.github.io/assets/76153041/cbdc464b-a340-47ed-a00a-3266e86245c9)

# [02]  가상머신의 machine-id 변경 및 적용 방법  

```bash
# 기존 machine-id 삭제
sudo rm -f /etc/machine-id

# 신규 machine-id 생성
dbus-uuidgen --ensure=/etc/machine-id  

# machine-id 확인
cat /etc/machine-id  
```  

# [03]  변경 후, 기존 가상머신과 복제한 가상머신의 IP 할당 확인  

![2024-02-29 14 15 14](https://github.com/cmaven/cmaven.github.io/assets/76153041/4d3cc8a6-54ac-4c78-ad67-4f779eb5144c)  