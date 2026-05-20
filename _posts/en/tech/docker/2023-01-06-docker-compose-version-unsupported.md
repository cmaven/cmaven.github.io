---
title: "Fix: docker-compose.yml is unsupported error"
description: "Cause and resolution of 'Version is unsupported' error when running docker-compose up, fixed by reinstalling the latest version"
excerpt: "Reinstall docker-compose to the latest version to fix the 'version is unsupported' error"
date: 2023-01-06
categories: Docker
tags: [Docker, Docker-compose, version-error, Ubuntu, reinstall, troubleshooting]
ref: docker-compose-version-unsupported
---

:bulb: How to resolve the `version ... is unsupported` error when running docker-compose.
{: .notice--info}

# [01] Situation

- Running `docker-compose up -d`
  - Error: `Version in "./docker-compose.yml" is unsupported`

```shell
$ sudo docker-compose up -d
ERROR: Version in "./docker-compose.yml" is unsupported. You might be seeing this error because you're using the wrong Compose file version. Either specify a supported version (e.g "2.2" or "3.3") and place your service definitions under the `services` key, or omit the `version` key and place your service definitions at the root of the file to use version 1.
For more on the Compose file format versions, see https://docs.docker.com/compose/compose-file/
```

# [02] Root Cause

- The installed docker-compose version doesn't support the current OS (Ubuntu 24.04)
  - [Ref: Version in docker-compose.yml is unsupported](https://github.com/datahub-project/datahub/issues/2020){:target="_blank"}

- Current system's docker-compose version: `1.25.0`

```shell
$ docker-compose version
docker-compose version 1.25.0, build unknown
docker-py version: 4.1.0
CPython version: 3.8.10
OpenSSL version: OpenSSL 1.1.1f  31 Mar 2020
```

# [03] Fix

- Reinstall `docker-compose`
  - As of 2023-01-06, version `2.14.2` installs on Ubuntu 24.04

```shell
# Install jq to fetch the latest version metadata
sudo apt-get install jq

# Store the latest version and install destination
VERSION=$(curl --silent https://api.github.com/repos/docker/compose/releases/latest | jq .name -r)
DESTINATION=/usr/bin/docker-compose

# Download the docker-compose binary to the destination
sudo curl -L https://github.com/docker/compose/releases/download/${VERSION}/docker-compose-$(uname -s)-$(uname -m) -o $DESTINATION

# Grant execute permission (so non-root users can run it)
sudo chmod 755 $DESTINATION

# Verify the install path
which docker-compose

# Check the installed version
docker-compose version
```
