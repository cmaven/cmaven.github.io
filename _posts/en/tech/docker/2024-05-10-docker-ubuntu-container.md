---
title: "Create an Ubuntu Container in Docker and Access an Nginx Server"
description: "How to build an Ubuntu 24.04 container with a Dockerfile, run Nginx, and access it externally"
excerpt: "Walk through writing a Dockerfile, building the image, running the container, and forwarding the Nginx port"
date: 2024-05-10
last_modified_at: 2026-05-26
categories: Docker
tags: [Docker, Dockerfile, Ubuntu, Nginx, container, port-forwarding, docker-build, docker-run]
ref: docker-ubuntu-container
---

:bulb: How to create and run an Ubuntu container with a Dockerfile, then run Nginx inside it and access it externally.
{: .notice--info}

# [01] Dockerfile, Image Build, and Container Run

## Dockerfile

```shell
# Dockerfile.ubuntu.24.04
vim Dockerfile.ubuntu.24.04

FROM ubuntu:24.04
ARG VERSION=latest
WORKDIR /root
RUN apt-get update ; apt-get install -y nginx net-tools vim iperf3

CMD service nginx start && tail -f /dev/null
```

- After `apt-get install` on the `RUN` line, list the packages you want.
- `tail -f /dev/null` in `CMD` keeps the container from exiting immediately.

## Build the Image

```shell
# Run from the same directory as the Dockerfile
sudo docker build -f Dockerfile.ubuntu.24.04 -t test/ubuntu24.04 .
```

## Run a Container with the Image

- `-p`: port forwarding
  - Below maps host port 8800 to container port 80
- `--restart`: behavior when Docker service restarts
  - `always` — always restart, keep the container running

```shell
docker run -d -p 8800:80 --name medge_ubuntu --restart always test/ubuntu24.04
```

# [02] (Optional) Configure Nginx Inside the Container

## Access the Container

- Open a bash shell inside the running container.

```shell
# test_ubuntu is the container name set above
docker exec -it test_ubuntu /bin/bash
```

## Edit Nginx index.html

- Modify to confirm the access goes inside the container.
- File: `/var/www/html/index.nginx-debian.html`

```html
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
<!-- Edited: -Con(8800) -->
<h1>Welcome to nginx!-Con(8800)</h1>
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

# [03] Verify Access

- ServerIP + Docker Port
  - e.g., `111.111.111.111:8800`
  - Uses port 8800 set in [01]
  - Confirm `<h1>Welcome to nginx!-Con(8800)</h1>` from [02] is displayed
