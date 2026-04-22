---
title: "Kubespray로 기존 Kubernetes 클러스터에 워커 노드 추가하기"
description: "Kubespray scale.yml을 사용하여 운영 중인 K8s 클러스터에 워커 노드를 추가하는 방법과 APT fact cache 트러블슈팅"
excerpt: "인벤토리 등록, SSH/sudo 설정, scale.yml --limit 실행, fact cache 404 에러 해결까지 실전 가이드"
date: 2026-04-22
categories: K8s
tags: [Kubernetes, Kubespray, scale.yml, 워커노드, 클러스터확장, Ansible, fact-cache, APT, containerd, Calico]
---

:bulb: 운영 중인 Kubernetes 클러스터에 노드가 부족할 때, Kubespray의 `scale.yml` 플레이북으로 워커 노드를 추가하는 표준 절차와 실전 트러블슈팅을 정리한다.
{: .notice--info}

---

# [01] 환경

| 항목 | 값 |
|------|---|
| Kubespray | `inventory/mycluster/` 기반 |
| Kubernetes | v1.28.0 |
| CRI | containerd 1.7.22 |
| CNI | Calico |
| OS | Ubuntu 22.04 (Jammy) |
| Ansible | Python venv 환경 |

## 1-1. 기존 클러스터 구성

| Role | Hostname | IP |
|------|----------|----|
| control-plane + etcd | k8s-master | 192.168.1.91 |
| worker | k8s-worker1 | 192.168.1.92 |
| worker | k8s-worker2 | 192.168.1.93 |
| worker (special HW) | node-a | 192.168.1.111 |
| worker (special HW) | node-b | 192.168.1.113 |

여기에 **`k8s-worker3` (192.168.1.94)**를 추가한다.

---

# [02] 전체 흐름

```
[1] 인벤토리에 노드 추가
  ↓
[2] SSH 공개키 + NOPASSWD sudo 설정
  ↓
[3] Ansible 연결 테스트 (ping)
  ↓
[4] scale.yml 실행
  ↓
[5] kubectl get nodes로 검증
```

---

# [03] Step 1 — 인벤토리에 노드 추가

`inventory/mycluster/inventory.yaml`의 **`all.hosts`와 `children.kube_node.hosts`** 두 곳 모두에 추가한다.

```yaml
all:
  hosts:
    k8s-master:
      ansible_host: 192.168.1.91
    k8s-worker1:
      ansible_host: 192.168.1.92
    k8s-worker2:
      ansible_host: 192.168.1.93
    k8s-worker3:                 # ← 추가
      ansible_host: 192.168.1.94 # ← 추가

  children:
    kube_node:
      hosts:
        k8s-worker1:
        k8s-worker2:
        k8s-worker3:              # ← 추가
```

:warning: `hosts`에만 추가하고 `kube_node.hosts`에 빠뜨리면, 호스트 정의는 있지만 그룹에 소속되지 않아 **scale.yml 대상에서 제외**된다.
{: .notice--warning}

---

# [04] Step 2 — SSH 공개키 + NOPASSWD sudo

Kubespray는 `become: yes`로 sudo를 사용하므로, **두 가지 모두** 설정해야 한다.

## 4-1. SSH 공개키 등록

```bash
ssh-copy-id user@192.168.1.94
```

확인:

```bash
ssh 192.168.1.94 'hostname'
# 패스워드 묻지 않고 hostname 출력되면 OK
```

## 4-2. NOPASSWD sudo 등록

새 서버에서:

```bash
ssh 192.168.1.94 \
  "echo 'user ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/user && \
   sudo chmod 440 /etc/sudoers.d/user"
```

확인:

```bash
ssh 192.168.1.94 'sudo -n whoami'
# → root 출력되면 OK
```

:bulb: `sudo -n`은 패스워드 프롬프트를 띄우지 않는 옵션이다. `a password is required` 메시지가 뜨면 NOPASSWD 설정이 안 된 것이다.
{: .notice--info}

---

# [05] Step 3 — Ansible 연결 테스트

플레이북 실행 전에 반드시 `ping`으로 기본 연결성을 확인한다.

```bash
cd ~/kubespray/kubespray
../venv/bin/ansible -i inventory/mycluster/inventory.yaml k8s-worker3 -m ping
```

정상 응답:

```
k8s-worker3 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false,
    "ping": "pong"
}
```

---

# [06] Step 4 — scale.yml 실행

```bash
LOG=~/kubespray/logs/scale-$(date +%Y%m%d-%H%M%S).log
../venv/bin/ansible-playbook \
  -i inventory/mycluster/inventory.yaml \
  scale.yml \
  -b \
  --limit=k8s-worker3 \
  > "$LOG" 2>&1 &
```

| 옵션 | 설명 |
|------|------|
| `-b` | become (sudo) |
| `--limit=k8s-worker3` | 새 노드에만 플레이북 적용 → 기존 워커에 부하/변경 없음 |
| `> "$LOG" 2>&1 &` | 백그라운드 실행, 로그 파일 저장 |

진행 모니터링:

```bash
tail -f $LOG
```

---

# [07] 트러블슈팅 — APT 버전 404 에러

## 7-1. 에러 메시지

```
TASK [kubernetes/preinstall : Install packages requirements] ***
fatal: [k8s-worker3]: FAILED! =>
  "msg": "'/usr/bin/apt-get -y ...
    install 'apt-transport-https=2.4.13' ...' failed:
    E: Failed to fetch .../apt-transport-https_2.4.13_all.deb
    404 Not Found"
```

## 7-2. 원인

**Ansible fact cache가 오래된 패키지 버전을 기억**하고 있었다.

`ansible.cfg`에 fact caching 설정이 있다:

```ini
[defaults]
fact_caching = jsonfile
fact_caching_connection = /tmp
fact_caching_timeout = 86400
```

이전에 수집된 `apt-transport-https=2.4.13` 버전 정보가 캐시에 남아 있었지만, Ubuntu 저장소에서는 이미 `2.4.14`로 교체되어 **404 Not Found**가 발생했다.

```bash
# 새 서버에서 확인하면 2.4.14만 존재
apt-cache madison apt-transport-https | head -3
# apt-transport-https | 2.4.14 | ... jammy-updates
# apt-transport-https |  2.4.5 | ... jammy
```

## 7-3. 해결

```bash
# 제어 노드에서 — fact cache 삭제
rm -rf /tmp/k8s-worker3

# 새 서버에서 — APT 메타데이터 강제 갱신
ssh 192.168.1.94 'sudo apt-get update'
```

이후 동일한 `scale.yml` 명령을 재실행하면 **한 번에 완료**된다.

:bulb: **핵심 교훈**: "한 번 성공한 절차가 왜 갑자기 실패하지?"의 답은 대부분 **캐시가 본 세상이 지금 세상과 다르기 때문**이다. Ansible fact cache, APT metadata, Docker image digest 모두 마찬가지다.
{: .notice--info}

---

# [08] Step 5 — 결과 검증

## 8-1. Ansible PLAY RECAP

```
PLAY RECAP ************************************************************
k8s-worker3 : ok=490  changed=77  unreachable=0  failed=0  skipped=772
```

`failed=0` 확인.

## 8-2. Kubernetes 노드 상태

```bash
kubectl get nodes -o wide
```

```
NAME          STATUS   ROLES           AGE    VERSION   INTERNAL-IP
k8s-master    Ready    control-plane   132d   v1.28.0   192.168.1.91
k8s-worker1   Ready    <none>          132d   v1.28.0   192.168.1.92
k8s-worker2   Ready    <none>          132d   v1.28.0   192.168.1.93
k8s-worker3   Ready    <none>          42s    v1.28.0   192.168.1.94  ← 신규
node-a        Ready    <none>          23h    v1.28.0   192.168.1.111
node-b        Ready    <none>          23h    v1.28.0   192.168.1.113
```

새 노드가 `Ready`로 정상 조인되었다. Calico CNI도 배포되어 Pod 스케줄링이 가능하다.

## 8-3. (선택) 테스트 Pod 스케줄링

```bash
kubectl run test-nginx --image=nginx:alpine \
  --overrides='{"spec":{"nodeSelector":{"kubernetes.io/hostname":"k8s-worker3"}}}'

kubectl get pod test-nginx -o wide
# NODE가 k8s-worker3인지 확인

# 테스트 후 정리
kubectl delete pod test-nginx
```

---

# [09] 참고 명령어 모음

```bash
# 제어 노드에서
../venv/bin/ansible -i inventory/mycluster/inventory.yaml <node> -m ping
../venv/bin/ansible-playbook -i inventory/mycluster/inventory.yaml scale.yml -b --limit=<node>
rm -rf /tmp/<node>                  # fact cache 삭제

# 대상 서버에서
sudo apt-get update                 # APT 메타데이터 갱신
sudo -n whoami                      # NOPASSWD sudo 확인

# 마스터에서
kubectl get nodes -o wide
kubectl describe node <node>
kubectl get pods -A -o wide --field-selector spec.nodeName=<node>
```

---

# [10] 정리

| 단계 | 작업 | 핵심 포인트 |
|------|------|-------------|
| 1 | 인벤토리 등록 | `hosts` + `kube_node.hosts` **두 곳 모두** |
| 2 | SSH / sudo | `ssh-copy-id` + `NOPASSWD` 필수 |
| 3 | 연결 테스트 | `ansible -m ping`으로 사전 확인 |
| 4 | scale.yml | `--limit=<node>`로 새 노드에만 적용 |
| 5 | 검증 | `PLAY RECAP` + `kubectl get nodes` 2단 확인 |
| (트러블) | APT 404 | fact cache 삭제 + `apt-get update` |
