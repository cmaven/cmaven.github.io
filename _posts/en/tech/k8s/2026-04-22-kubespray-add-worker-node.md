---
title: "Adding a Worker Node to an Existing Kubernetes Cluster with Kubespray"
description: "How to add a worker node to a running K8s cluster using Kubespray scale.yml, plus APT fact cache troubleshooting"
excerpt: "Inventory registration, SSH/sudo setup, scale.yml --limit execution, and solving the fact cache 404 error — a real-world walkthrough"
date: 2026-04-22
categories: K8s
tags: [Kubernetes, Kubespray, scale.yml, worker-node, cluster-expansion, Ansible, fact-cache, APT, containerd, Calico]
ref: kubespray-add-worker-node
---

:bulb: When your Kubernetes cluster needs more capacity, use Kubespray's `scale.yml` playbook to add a worker node. This guide covers the standard procedure plus real-world troubleshooting.
{: .notice--info}

---

# [01] Environment

| Item | Value |
|------|-------|
| Kubespray | `inventory/mycluster/` based |
| Kubernetes | v1.28.0 |
| CRI | containerd 1.7.22 |
| CNI | Calico |
| OS | Ubuntu 22.04 (Jammy) |
| Ansible | Python venv environment |

## 1-1. Existing Cluster

| Role | Hostname | IP |
|------|----------|----|
| control-plane + etcd | k8s-master | 192.168.1.91 |
| worker | k8s-worker1 | 192.168.1.92 |
| worker | k8s-worker2 | 192.168.1.93 |
| worker (special HW) | node-a | 192.168.1.111 |
| worker (special HW) | node-b | 192.168.1.113 |

We're adding **`k8s-worker3` (192.168.1.94)**.

---

# [02] Overall Flow

```
[1] Add the node to inventory
  ↓
[2] SSH public key + NOPASSWD sudo
  ↓
[3] Ansible connectivity test (ping)
  ↓
[4] Run scale.yml
  ↓
[5] Verify with kubectl get nodes
```

---

# [03] Step 1 — Add the Node to Inventory

Edit `inventory/mycluster/inventory.yaml` and add the entry in **both `all.hosts` and `children.kube_node.hosts`**.

```yaml
all:
  hosts:
    k8s-master:
      ansible_host: 192.168.1.91
    k8s-worker1:
      ansible_host: 192.168.1.92
    k8s-worker2:
      ansible_host: 192.168.1.93
    k8s-worker3:                 # ← add
      ansible_host: 192.168.1.94 # ← add

  children:
    kube_node:
      hosts:
        k8s-worker1:
        k8s-worker2:
        k8s-worker3:              # ← add
```

:warning: If you add to `hosts` but forget `kube_node.hosts`, the host definition exists but isn't part of the group — **scale.yml will skip it**.
{: .notice--warning}

---

# [04] Step 2 — SSH Public Key + NOPASSWD sudo

Kubespray uses `become: yes` for sudo, so **both** must be configured.

## 4-1. Register SSH Public Key

```bash
ssh-copy-id user@192.168.1.94
```

Verify:

```bash
ssh 192.168.1.94 'hostname'
# Should print hostname without password prompt
```

## 4-2. Configure NOPASSWD sudo

On the new server:

```bash
ssh 192.168.1.94 \
  "echo 'user ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/user && \
   sudo chmod 440 /etc/sudoers.d/user"
```

Verify:

```bash
ssh 192.168.1.94 'sudo -n whoami'
# → should print 'root'
```

:bulb: `sudo -n` suppresses the password prompt. If you see `a password is required`, NOPASSWD is not configured.
{: .notice--info}

---

# [05] Step 3 — Ansible Connectivity Test

Before running the playbook, always confirm connectivity with `ping`.

```bash
cd ~/kubespray/kubespray
../venv/bin/ansible -i inventory/mycluster/inventory.yaml k8s-worker3 -m ping
```

Expected response:

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

# [06] Step 4 — Run scale.yml

```bash
LOG=~/kubespray/logs/scale-$(date +%Y%m%d-%H%M%S).log
../venv/bin/ansible-playbook \
  -i inventory/mycluster/inventory.yaml \
  scale.yml \
  -b \
  --limit=k8s-worker3 \
  > "$LOG" 2>&1 &
```

| Option | Description |
|--------|-------------|
| `-b` | become (sudo) |
| `--limit=k8s-worker3` | Apply playbook to the new node only — no impact on existing workers |
| `> "$LOG" 2>&1 &` | Background execution, save log to file |

Monitor progress:

```bash
tail -f $LOG
```

---

# [07] Troubleshooting — APT Version 404 Error

## 7-1. Error Message

```
TASK [kubernetes/preinstall : Install packages requirements] ***
fatal: [k8s-worker3]: FAILED! =>
  "msg": "'/usr/bin/apt-get -y ...
    install 'apt-transport-https=2.4.13' ...' failed:
    E: Failed to fetch .../apt-transport-https_2.4.13_all.deb
    404 Not Found"
```

## 7-2. Root Cause

**Ansible fact cache remembered an old package version.**

`ansible.cfg` had fact caching enabled:

```ini
[defaults]
fact_caching = jsonfile
fact_caching_connection = /tmp
fact_caching_timeout = 86400
```

The previously cached `apt-transport-https=2.4.13` was no longer in the Ubuntu repo — it had been replaced with `2.4.14`, causing **404 Not Found**.

```bash
# Confirmed on the new server — only 2.4.14 exists
apt-cache madison apt-transport-https | head -3
# apt-transport-https | 2.4.14 | ... jammy-updates
# apt-transport-https |  2.4.5 | ... jammy
```

## 7-3. Resolution

```bash
# On the control node — delete the fact cache
rm -rf /tmp/k8s-worker3

# On the new server — force APT metadata refresh
ssh 192.168.1.94 'sudo apt-get update'
```

Re-running the same `scale.yml` command **completes successfully in one pass**.

:bulb: **Key lesson**: When "a procedure that worked before suddenly fails", the answer is usually **the cache sees a different world than reality**. Ansible fact cache, APT metadata, and Docker image digests all suffer this.
{: .notice--info}

---

# [08] Step 5 — Verify Results

## 8-1. Ansible PLAY RECAP

```
PLAY RECAP ************************************************************
k8s-worker3 : ok=490  changed=77  unreachable=0  failed=0  skipped=772
```

Confirm `failed=0`.

## 8-2. Kubernetes Node Status

```bash
kubectl get nodes -o wide
```

```
NAME          STATUS   ROLES           AGE    VERSION   INTERNAL-IP
k8s-master    Ready    control-plane   132d   v1.28.0   192.168.1.91
k8s-worker1   Ready    <none>          132d   v1.28.0   192.168.1.92
k8s-worker2   Ready    <none>          132d   v1.28.0   192.168.1.93
k8s-worker3   Ready    <none>          42s    v1.28.0   192.168.1.94  ← new
node-a        Ready    <none>          23h    v1.28.0   192.168.1.111
node-b        Ready    <none>          23h    v1.28.0   192.168.1.113
```

The new node joined successfully as `Ready`. Calico CNI is deployed too, so pod scheduling works.

## 8-3. (Optional) Test Pod Scheduling

```bash
kubectl run test-nginx --image=nginx:alpine \
  --overrides='{"spec":{"nodeSelector":{"kubernetes.io/hostname":"k8s-worker3"}}}'

kubectl get pod test-nginx -o wide
# Confirm NODE is k8s-worker3

# Clean up after testing
kubectl delete pod test-nginx
```

---

# [09] Command Reference

```bash
# On the control node
../venv/bin/ansible -i inventory/mycluster/inventory.yaml <node> -m ping
../venv/bin/ansible-playbook -i inventory/mycluster/inventory.yaml scale.yml -b --limit=<node>
rm -rf /tmp/<node>                  # delete fact cache

# On the target server
sudo apt-get update                 # refresh APT metadata
sudo -n whoami                      # verify NOPASSWD sudo

# On the master
kubectl get nodes -o wide
kubectl describe node <node>
kubectl get pods -A -o wide --field-selector spec.nodeName=<node>
```

---

# [10] Summary

| Step | Task | Key point |
|------|------|-----------|
| 1 | Inventory registration | Add to **both** `hosts` + `kube_node.hosts` |
| 2 | SSH / sudo | `ssh-copy-id` + `NOPASSWD` required |
| 3 | Connectivity test | Pre-check with `ansible -m ping` |
| 4 | scale.yml | Use `--limit=<node>` to target only the new node |
| 5 | Verification | `PLAY RECAP` + `kubectl get nodes` double check |
| (trouble) | APT 404 | Delete fact cache + `apt-get update` |
