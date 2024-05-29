---
title: "서버에서 구동 중인 VM에 외부에서 접근하는 방법"
date: 2024-05-13
categories: VM
tags: [VM, Ubuntu]
---

:bulb: VM 환경(Qemu, KVM) 환경에서 생성한 Ubuntu VM에 접근하는 방법을 작성한다.  
(외부접근 서버 A ↔ 호스트 서버 B ↔ 호스트 서버에서 구동 중인 VM A 환경에서 서버 A에서 VM A로의 접근 방법)  
이 때, vm은 default network 형태인 virbr0 (NAT)를 활용한다.  
{: .notice--info}

# [01]  Ubuntu VM 이미지 생성

- virt-manager 활용  
- ubuntu-22.04-server 이미지 다운로드: [(https://releases.ubuntu.com/22.04/)](https://releases.ubuntu.com/22.04/){:target="_blank"}  

# [02]  VM 내부 Nginx 패키지 설치, (선택)설정

## 패키지 설치

```shell
sudo apt-get -y install nginx net-tools vim  
```  

## VM 내부 Nginx index.html 수정

- Nginx Web Server의 Homepage로 접근했을 때, 컨테이너 내부로의 진입인지 확인하기 위함
- `/var/www/html/index.nginx-debian.html` 파일

```html
<!-- /var/html/index.nginx-debian.html <h1> 태그 부분 수정(제목) -->
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    }
</style>
</head>
<body>
<!-- 내용 추가: -VM -->
<h1>Welcome to nginx!-VM</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
```    

- 서비스 재시작  

```shell
# nginx 서비스 재시작
service nginx restart
```

# [03]  외부 접근 요청 Forwarding 설정 (iptables)  

## 호스트 서버와 VM 사이 패킷 Forwarding 설정  

- 호스트 서버 B의 네트워크 장치로 들어온 Reqeust 중, 특정 Port를 만족할 경우
- 내부에서 운영 중인 VM으로 해당 Request를 전달  
- iptables 의 `nat`, `filter` 테이블 활용
  - `-t` 옵션을 지정하지 않으면, default로 `filter` 테이블에 적용됨

```shell
iptables -t nat -A PREROUTING -i enp0s31f6 -p tcp -m tcp --dport 9999 -j DNAT --to-destination 192.168.122.131:80
iptables -I FORWARD -o virbr0 -d 192.168.122.131 -p tcp --dport 80 -j ACCEPT
```  

- (1번) 규칙
  - `enp0s31f6`은 호스트 서버 B의 네트워크 장치 명
  - `--dport 9999`는 호스트 서버 B의 네트워크 장치에 9999 포트로 요청이 들어왔음을 의미
  - `--to-destination 192.168.122.131:80` 은 위의 9999 포트로 들어온 요청을 192.168.122.131 IP가 할당된 VM의 80 포트로 전달한다는 의미
  - 즉, 외부에서 호스트 서버 B의 9999 포트로 들어오는 모든 트래픽이 192.168.122.131의 80 포트로 전달  
- (2번) 규칙
  - `-o virbr0`은 호스트 서버 B에서 virbr0으로 나가는 패킷의 경우
  - `-d 192.168.122.131 -p tcp, --dport 80`은 tcp 형태의 해당 IP, 포트일 경우
  - `-j ACCEPT` 패킷을 허용
  - 즉, 첫 번째 설정으로 전달된 패킷이 iptables의 방화벽에서 통과할 수 있도록 방화벽 오픈

## 서버 재시작 시, 설정된 값 유지

- 자동 (패키지 활용)  

```shell
# 설치 및 시작
sudo apt-get update
sudo apt-get install iptables-persistent

# 중지
sudo systemctl stop netfilter-persistent
sudo systemctl disable netfilter-persistent

# 재시작
sudo systemctl enable netfilter-persistent
sudo systemctl start netfilter-persistent
```  

- 수동 (파일 저장)  

```shell
# 저장
sudo iptables-save > /etc/iptables/rules.v4

# 변경, 백업
sudo mv /etc/iptables/rules.v4 /etc/iptables/rules.v4.backup
sudo mv /etc/iptables/rules.v6 /etc/iptables/rules.v6.backup

# 제거
sudo rm /etc/iptables/rules.v4
sudo rm /etc/iptables/rules.v6
```  

## (참조) iptables의 Table  

> 패킷을 필터링하고 조작하는데 사용되는 논리적 그룹

- Filter
  - 패킷 필터링 처리
  - 방화벽 정책 정의
  - 패킷의 허용, 거부를 결정할 때 사용
  - 관련 Chain
    - INPUT, OUTPUT, FORWARD
- NAT
  - 네트워크 주소 변환(NAT)과 포트 포워딩을 처리
  - 관련 Chain
    - PREROUTING, POSTROUTING
- Mangle
  - 특정 유형의 패킷 변경을 위해 사용됩니다. 
  - 주로, 데이터 전송 경로 변경, 우선순위 값 변경 등에 사용
- Raw
  - 구성 예외를 처리

## (참조) iptables의 Chain

> 패킷이 특정 단계에 도달했을 때 적용되는 규칙의 집합  

- INPUT
  - 패킷이 시스템의 네트워크 스택으로 들어오는 경우에 적용
  - 즉, 외부에서 시스템으로 들어오는 패킷을 처리
  - 대표적으로 포트 포워딩이나 서버로 들어오는 요청을 처리하는 데 사용

- OUTPUT
  - 시스템에서 나가는 패킷을 처리
  - 시스템에서 생성되는 모든 패킷이 이 체인을 통과하게 됩니다. 
  - 주로 시스템에서 발생한 패킷을 필터링하거나 조작하는 데 사용

- FORWARD
  - 시스템이 라우터로 동작할 때, 패킷이 하나의 인터페이스로 들어와서 다른 인터페이스로 나가는 경우에 적용
  - 즉, 시스템을 라우터로 사용할 때 패킷이 이 체인을 통과

- PREROUTING 체인: 이 체인은 
  - 패킷이 라우팅되기 전에 적용 
  - 따라서 패킷이 라우터로 전달되기 전에 처리되어야 하는 작업을 수행
  - 주로 포트 포워딩이나 패킷의 소스 주소를 변경하는 데 사용

- POSTROUTING
  - 패킷이 라우팅된 후에 적용
  - 따라서 패킷이 라우터를 통과한 후 처리되어야 하는 작업을 수행
  - 주로 NAT(Network Address Translation)을 사용하여 출발지나 목적지 주소를 변경하는 데 사용  


## (참조) iptables 관련 명령어  

```shell
# iptables 규칙 확인
sudo iptables -t nat --line-numbers -L PREROUTING
sudo iptables -t filter --line-numbers -L FORWARD

# ipaddress 형태로 조회(table마다 동일)
sudo iptables -t filter -L -n
sudo iptables -t nat -L -n
sudo iptables -t mangle -L -n
sudo iptables -t raw -L -n

# 특정 규칙 삭제
sudo iptables -t nat -D PREROUTING ${줄 번호}
sudo iptables -t filter -D FORWARD
```

## (참조) virsh 관련 명령어

```shell
# VM 확인
virsh list

# 특정 VM 주소 확인
virsh domifaddr ${id}
virsh domifaddr ${name}

# 전체 DHCP 주소 확인
virsh net-dhcp-leases ${interface_name}
#ex) virsh net-dhcp-leases default
```  


# [04]  접근확인

- ServerIP + Forwarding(iptables) Port
  - ex) 111.111.111.111:9999  
  - [03]에서 설정한 9999 포트 활용
  - [02]에서 작성한 `<h1>Welcome to nginx!-VM</h1>` 출력 확인  

  ![2024-05-13 16 51 11](https://github.com/cmaven/cmaven.github.io/assets/76153041/80cb4448-2648-407e-b0e3-5f0d39dfff5d)