---
title: "Multipass — Ubuntu VM을 명령어 몇 개로 만드는 가장 쉬운 방법"
description: "Canonical의 Multipass로 Ubuntu VM을 빠르게 생성·접속·삭제하는 방법 총정리. 설치, launch/list/shell/exec/delete 사용법, CPU·메모리·디스크 지정, cloud-init, 파일 전송, libvirt/KVM과의 비교"
excerpt: "multipass launch 한 줄로 Ubuntu VM 생성. 설치부터 리소스 지정, cloud-init, libvirt/KVM 비교까지 개발·테스트용 VM 환경을 정리"
date: 2026-05-29
categories: VM
tags: [Multipass, Ubuntu, VM, KVM, QEMU, libvirt, cloud-init, Kubernetes, 가상머신, 개발환경, snap]
ref: multipass-ubuntu-vm
---

:bulb: Multipass는 Canonical에서 만든 경량 VM 관리 도구로, **명령어 몇 개만으로 Ubuntu VM을 만들고 접속·삭제**할 수 있다. Kubernetes 실습 노드, OpenStack 테스트, 임시 개발 환경을 빠르게 띄울 때 특히 편리하다.
{: .notice--info}

**환경**: Ubuntu / Linux (snap 지원 배포판), macOS·Windows도 지원

---

# [01] Multipass란?

Multipass는 **Ubuntu VM을 빠르게 생성·실행하는 데 특화된 경량 VM 도구**다. Linux에서는 내부적으로 KVM/QEMU를 백엔드로 사용할 수 있어 성능은 거의 KVM 수준이지만, 사용성이 훨씬 단순하다.

| 도구 | 역할 |
|------|------|
| VirtualBox / VMware | 범용 GUI 중심 가상머신 관리 |
| libvirt / KVM | 리눅스 서버용 강력한 가상화 관리 |
| **Multipass** | Ubuntu VM을 명령어 몇 개로 빠르게 생성/삭제 |

:memo: "성능이 더 좋다"기보다는 **Ubuntu VM을 빠르게 만들고 쓰는 사용성**이 강점이다. 이미지 준비, cloud-init, 네트워크 설정 등을 자동으로 처리해 준다.
{: .notice--warning}

---

# [02] 설치

Ubuntu에서는 snap으로 한 줄에 설치할 수 있다.

```bash
sudo snap install multipass
```

설치 후 버전을 확인한다.

```bash
multipass version
```

---

# [03] 기본 사용법

## 3-1. VM 생성 (launch)

이름만 지정하면 기본 사양의 Ubuntu VM이 만들어진다.

```bash
multipass launch --name test-vm
```

## 3-2. VM 목록 확인 (list)

```bash
multipass list
```

```text
Name        State       IPv4            Image
test-vm     Running     10.x.x.x        Ubuntu 24.04 LTS
```

## 3-3. VM 접속 (shell)

```bash
multipass shell test-vm
```

## 3-4. 명령만 실행 (exec)

접속하지 않고 호스트에서 바로 명령을 실행할 수도 있다.

```bash
multipass exec test-vm -- lsb_release -a
```

## 3-5. 정지 / 시작 / 삭제

```bash
multipass stop test-vm      # 정지
multipass start test-vm     # 시작
multipass delete test-vm    # 삭제 (휴지통으로 이동, 복구 가능)
multipass purge             # 삭제된 VM을 디스크에서 완전 제거
```

:warning: `delete`는 VM을 "삭제 예정" 상태로만 만든다. 디스크 공간까지 확보하려면 반드시 `purge`까지 실행해야 한다.
{: .notice--warning}

---

# [04] 리소스를 지정해서 VM 만들기

CPU, 메모리, 디스크를 직접 지정할 수 있다.

```bash
multipass launch --cpus 2 --memory 4G --disk 20G --name k8s-node
```

| 옵션 | 의미 |
|------|------|
| `--cpus` | 할당할 vCPU 개수 |
| `--memory` | 메모리 크기 (예: `4G`) |
| `--disk` | 디스크 크기 (예: `20G`) |
| `--name` | VM 이름 |

:bulb: 특정 Ubuntu 버전이 필요하면 `multipass find`로 사용 가능한 이미지를 확인한 뒤, `multipass launch 22.04` 처럼 버전을 지정하면 된다.
{: .notice--info}

---

# [05] Kubernetes 실습 노드 만들기

Multipass의 가장 흔한 용도 중 하나가 **물리 서버 없이 로컬에서 여러 Ubuntu 노드를 띄워 클러스터를 테스트**하는 것이다.

```bash
multipass launch --name k8s-master  --cpus 2 --memory 4G --disk 30G
multipass launch --name k8s-worker1 --cpus 2 --memory 4G --disk 30G
multipass launch --name k8s-worker2 --cpus 2 --memory 4G --disk 30G
```

이렇게 노드 3개를 만든 뒤 각 VM에 접속해 kubeadm 등으로 클러스터를 구성하면 된다.

---

# [06] cloud-init 으로 초기 설정 자동화

VM이 처음 부팅될 때 실행할 설정을 `cloud-init` YAML로 미리 정의할 수 있다. 패키지 설치, 사용자 추가 등을 자동화할 때 유용하다.

```yaml
# init.yaml
packages:
  - docker.io
  - git
runcmd:
  - systemctl enable --now docker
```

```bash
multipass launch --name dev-vm --cloud-init init.yaml
```

:bulb: libvirt/KVM에서도 cloud-init은 가능하지만 직접 구성해야 한다. Multipass는 `--cloud-init` 한 옵션으로 처리해 준다.
{: .notice--info}

---

# [07] 호스트와 파일 공유

## 7-1. 디렉토리 마운트 (mount)

호스트 디렉토리를 VM 안에 마운트한다.

```bash
multipass mount ~/project test-vm:/home/ubuntu/project
multipass umount test-vm        # 마운트 해제
```

## 7-2. 파일 전송 (transfer)

```bash
multipass transfer file.txt test-vm:/home/ubuntu/
```

---

# [08] Multipass vs libvirt/KVM

| 항목 | Multipass | libvirt/KVM |
|------|-----------|-------------|
| 목적 | Ubuntu VM 빠른 생성·개발/테스트 | 범용 서버 가상화 |
| 난이도 | 낮음 | 중간~높음 |
| VM 생성 | 매우 간단 | 직접 설정 필요 |
| Ubuntu cloud image | 자동 처리 | 보통 수동 준비 |
| cloud-init | 쉽게 사용 | 가능하지만 직접 구성 |
| 네트워크 세부 제어 | 제한적 | 매우 강력 |
| 스토리지 세부 제어 | 제한적 | 강력 |
| 운영 환경 적합성 | 개발/테스트에 적합 | 운영/고급 가상화에 적합 |
| 성능 | 백엔드에 따라 거의 KVM 수준 | KVM 직접 사용 |

libvirt/KVM에서 세밀하게 제어하려면 보통 다음과 같은 명령을 직접 다룬다.

```bash
virsh list --all
virt-install ...
virsh edit <vm>
```

---

# [09] 정리 — 언제 무엇을 쓸까

| 상황 | 추천 |
|------|------|
| Kubernetes 실습 노드 몇 개 | **Multipass** |
| OpenStack-Helm 테스트용 Ubuntu VM | **Multipass** |
| 임시 개발 환경 빠르게 띄우기 | **Multipass** |
| SR-IOV / PCI passthrough / NUMA / hugepage | libvirt/KVM |
| OVS bridge, provider network 실험 | libvirt/KVM |
| OpenStack Nova/libvirt 구조 검증 | libvirt/KVM |

:bulb: 핵심만 기억하자. **빠르게 Ubuntu VM이 필요하면 Multipass**, **네트워크·스토리지·하드웨어 가상화를 깊게 제어해야 하면 libvirt/KVM**. 개발·테스트는 Multipass, 운영·고급 가상화는 libvirt/KVM 쪽이 낫다.
{: .notice--info}
