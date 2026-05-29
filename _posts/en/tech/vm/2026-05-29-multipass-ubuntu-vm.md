---
title: "Multipass — The Easiest Way to Spin Up an Ubuntu VM in a Few Commands"
description: "A complete guide to creating, accessing, and deleting Ubuntu VMs quickly with Canonical's Multipass. Covers installation, launch/list/shell/exec/delete usage, CPU/memory/disk options, cloud-init, file sharing, and a comparison with libvirt/KVM"
excerpt: "Create an Ubuntu VM with a single multipass launch. From installation to resource options, cloud-init, and a libvirt/KVM comparison for dev and test environments"
date: 2026-05-29
categories: VM
tags: [Multipass, Ubuntu, VM, KVM, QEMU, libvirt, cloud-init, Kubernetes, virtual-machine, dev-environment, snap]
ref: multipass-ubuntu-vm
---

:bulb: Multipass is a lightweight VM manager from Canonical that lets you **create, access, and delete Ubuntu VMs with just a few commands**. It's especially handy for spinning up Kubernetes lab nodes, OpenStack test setups, or quick throwaway dev environments.
{: .notice--info}

**Environment**: Ubuntu / Linux (snap-enabled distributions); macOS and Windows are also supported

---

# [01] What is Multipass?

Multipass is a **lightweight VM tool focused on quickly creating and running Ubuntu VMs**. On Linux it can use KVM/QEMU as its backend, so performance is close to KVM, but it's far simpler to use.

| Tool | Role |
|------|------|
| VirtualBox / VMware | General-purpose, GUI-centric VM management |
| libvirt / KVM | Powerful virtualization management for Linux servers |
| **Multipass** | Create/delete Ubuntu VMs in just a few commands |

:memo: It's less about "better performance" and more about **the ease of quickly creating and using Ubuntu VMs**. It handles image preparation, cloud-init, and networking automatically.
{: .notice--warning}

---

# [02] Installation

On Ubuntu you can install it with a single snap command.

```bash
sudo snap install multipass
```

Check the version after installing.

```bash
multipass version
```

---

# [03] Basic Usage

## 3-1. Create a VM (launch)

Specify just a name to create an Ubuntu VM with default specs.

```bash
multipass launch --name test-vm
```

## 3-2. List VMs (list)

```bash
multipass list
```

```text
Name        State       IPv4            Image
test-vm     Running     10.x.x.x        Ubuntu 24.04 LTS
```

## 3-3. Open a shell (shell)

```bash
multipass shell test-vm
```

## 3-4. Run a command only (exec)

You can run a command directly from the host without opening a shell.

```bash
multipass exec test-vm -- lsb_release -a
```

## 3-5. Stop / Start / Delete

```bash
multipass stop test-vm      # stop
multipass start test-vm     # start
multipass delete test-vm    # delete (moves to trash, recoverable)
multipass purge             # permanently remove deleted VMs from disk
```

:warning: `delete` only marks the VM as "to be deleted." To actually reclaim disk space, you must also run `purge`.
{: .notice--warning}

---

# [04] Creating a VM with Specific Resources

You can specify CPU, memory, and disk directly.

```bash
multipass launch --cpus 2 --memory 4G --disk 20G --name k8s-node
```

| Option | Meaning |
|--------|---------|
| `--cpus` | Number of vCPUs to allocate |
| `--memory` | Memory size (e.g., `4G`) |
| `--disk` | Disk size (e.g., `20G`) |
| `--name` | VM name |

:bulb: If you need a specific Ubuntu version, run `multipass find` to see available images, then specify the version like `multipass launch 22.04`.
{: .notice--info}

---

# [05] Building Kubernetes Lab Nodes

One of the most common uses for Multipass is **spinning up several Ubuntu nodes locally to test a cluster without any physical servers**.

```bash
multipass launch --name k8s-master  --cpus 2 --memory 4G --disk 30G
multipass launch --name k8s-worker1 --cpus 2 --memory 4G --disk 30G
multipass launch --name k8s-worker2 --cpus 2 --memory 4G --disk 30G
```

After creating three nodes, shell into each VM and set up the cluster with kubeadm or similar.

---

# [06] Automating Initial Setup with cloud-init

You can predefine what runs on the VM's first boot using a `cloud-init` YAML file. This is useful for automating package installation, adding users, and so on.

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

:bulb: cloud-init also works with libvirt/KVM, but you have to configure it yourself. Multipass handles it with a single `--cloud-init` option.
{: .notice--info}

---

# [07] Sharing Files with the Host

## 7-1. Mount a directory (mount)

Mount a host directory inside the VM.

```bash
multipass mount ~/project test-vm:/home/ubuntu/project
multipass umount test-vm        # unmount
```

## 7-2. Transfer files (transfer)

```bash
multipass transfer file.txt test-vm:/home/ubuntu/
```

---

# [08] Multipass vs libvirt/KVM

| Item | Multipass | libvirt/KVM |
|------|-----------|-------------|
| Purpose | Fast Ubuntu VM creation, dev/test | General-purpose server virtualization |
| Difficulty | Low | Medium to high |
| VM creation | Very simple | Manual configuration required |
| Ubuntu cloud image | Handled automatically | Usually prepared manually |
| cloud-init | Easy to use | Possible, but configured manually |
| Fine network control | Limited | Very powerful |
| Fine storage control | Limited | Powerful |
| Production fit | Suited for dev/test | Suited for production/advanced virtualization |
| Performance | Close to KVM, depending on backend | Uses KVM directly |

For fine-grained control with libvirt/KVM, you typically work with commands like these directly.

```bash
virsh list --all
virt-install ...
virsh edit <vm>
```

---

# [09] Summary — When to Use What

| Situation | Recommendation |
|-----------|----------------|
| A few Kubernetes lab nodes | **Multipass** |
| Ubuntu VMs for OpenStack-Helm testing | **Multipass** |
| Quickly spinning up a temporary dev environment | **Multipass** |
| SR-IOV / PCI passthrough / NUMA / hugepage | libvirt/KVM |
| OVS bridge, provider network experiments | libvirt/KVM |
| Validating OpenStack Nova/libvirt internals | libvirt/KVM |

:bulb: Remember the essentials. **Need an Ubuntu VM fast? Use Multipass.** **Need deep control over networking, storage, or hardware virtualization? Use libvirt/KVM.** Multipass for dev and test, libvirt/KVM for production and advanced virtualization.
{: .notice--info}
