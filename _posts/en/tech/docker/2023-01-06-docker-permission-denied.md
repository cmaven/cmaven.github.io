---
title: "Fix: 'permission denied' when running Docker commands"
description: "Cause of permission denied error when running Docker as a non-root user, and how to fix it by adding the user to the docker group"
excerpt: "Resolve the docker.sock permission denied error by adding your user to the docker group with usermod"
date: 2023-01-06
last_modified_at: 2026-05-26
categories: Docker
tags: [Docker, Permission, docker.sock, usermod, permission-error, Ubuntu, troubleshooting]
ref: docker-permission-denied
---

:bulb: How to resolve `permission denied` errors when running Docker commands as a non-root user.
{: .notice--info}

# [01] Situation

Running any Docker command as a non-root user produces the following error:

```shell
$ docker version
Client: Docker Engine - Community
 Version:           20.10.22
...
Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/version": dial unix /var/run/docker.sock: connect: permission denied
```

This error appears even though Docker is installed and the daemon is running. Common trigger points:

- Fresh Docker installation on Ubuntu
- A new user account that was not set up alongside Docker
- A VM or container environment where the user context differs from the installer

# [02] Root Cause

Docker communicates through a Unix socket at `/var/run/docker.sock`. By default, that socket is owned by the `docker` group, and **only root or members of the `docker` group** can access it.

When a non-root user runs `docker`, they are denied access to the socket.

```shell
# Check current user and groups
$ id
uid=1001(myuser) gid=1001(myuser) groups=1001(myuser),27(sudo)
```

The user above is in `sudo` but **not** in `docker` — so Docker commands fail.

```shell
# Confirm socket ownership
$ ls -la /var/run/docker.sock
srw-rw---- 1 root docker 0 Jan  6 10:00 /var/run/docker.sock
```

The socket is readable/writable only by `root` and the `docker` group.

# [03] Fix

Add the current user to the `docker` group, then apply the change:

```shell
# Add the current user to the docker group
sudo usermod -aG docker $USER

# Restart the Docker daemon
systemctl restart docker

# Apply the new group membership to the current shell session
newgrp docker
```

**What each command does:**

| Command | Purpose |
|---|---|
| `usermod -aG docker $USER` | Appends the `docker` group to the user's group list |
| `systemctl restart docker` | Restarts the daemon to pick up permission changes |
| `newgrp docker` | Activates the new group in the current terminal without logging out |

:warning: `newgrp docker` only applies to the current shell session. For a permanent effect across all sessions, **log out and log back in**, or reboot.
{: .notice--warning}

# [04] Verify

After applying the fix, confirm the group membership and test Docker:

```shell
# Confirm docker group is listed
$ id
uid=1001(myuser) gid=1001(myuser) groups=1001(myuser),27(sudo),998(docker)

# Run docker without sudo
$ docker version
Client: Docker Engine - Community
 Version:           20.10.22
 ...
Server: Docker Engine - Community
 ...
```

The `permission denied` error should no longer appear.

# [05] Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| Error persists after `usermod` | Group change not applied to session | Run `newgrp docker` or log out/in |
| `newgrp docker` exits immediately | Shell restart behavior | Open a new terminal instead |
| Error on a different socket path | Custom Docker socket location | Check `DOCKER_HOST` env variable |
| Error inside a CI/CD container | No `docker` group in container | Mount the socket and set group or use `--privileged` |

:warning: Adding a user to the `docker` group grants effective root-equivalent access to the host system via Docker. Only add trusted users.
{: .notice--warning}
