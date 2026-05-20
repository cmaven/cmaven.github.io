---
title: "Fix: 'permission denied' when running Docker commands"
description: "Cause of permission denied error when running Docker as a non-root user, and how to fix it by adding the user to the docker group"
excerpt: "Resolve the docker.sock permission denied error by adding your user to the docker group with usermod"
date: 2023-01-06
categories: Docker
tags: [Docker, Permission, docker.sock, usermod, permission-error, Ubuntu, troubleshooting]
ref: docker-permission-denied
---

:bulb: How to resolve `permission denied` errors when running Docker commands.
{: .notice--info}

# [01] Situation

- Running a Docker command produces `dial unix /var/run/docker.sock: connect: permission denied`

```shell
$ docker version
Client: Docker Engine - Community
 Version:           20.10.22
...
Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.24/version": dial unix /var/run/docker.sock: connect: permission denied
```

# [02] Root Cause

- The user running the command needs access permission on `/var/run/docker.sock`
- Typically occurs when running `docker` commands as a non-root user

```shell
# Check user permissions
$ id
uid=1001(myuser) gid=1001(myuser) groups=1001(myuser),27(sudo)
```

# [03] Fix

```shell
# Add the current user to the docker group
sudo usermod -aG docker $USER

# Restart docker
systemctl restart docker

# Apply the new group membership immediately
newgrp docker
```

# [04] Verify

- After applying the group change, run `docker` commands again — the permission denied error should be gone.
