---
title: "Fix: docker-compose.yml is unsupported error"
description: "Cause and resolution of 'Version is unsupported' error when running docker-compose up, fixed by reinstalling the latest version"
excerpt: "Reinstall docker-compose to the latest version to fix the 'version is unsupported' error"
date: 2023-01-06
last_modified_at: 2026-05-26
categories: Docker
tags: [Docker, Docker-compose, version-error, Ubuntu, reinstall, troubleshooting]
ref: docker-compose-version-unsupported
---

:bulb: How to resolve the `version ... is unsupported` error when running docker-compose.
{: .notice--info}

# [01] Situation

Running `docker-compose up -d` fails immediately with a version compatibility error:

```shell
$ sudo docker-compose up -d
ERROR: Version in "./docker-compose.yml" is unsupported. You might be seeing this error because you're using the wrong Compose file version. Either specify a supported version (e.g "2.2" or "3.3") and place your service definitions under the `services` key, or omit the `version` key and place your service definitions at the root of the file to use version 1.
For more on the Compose file format versions, see https://docs.docker.com/compose/compose-file/
```

This typically happens after:

- Installing Docker on a newer Ubuntu release (22.04 / 24.04)
- Copying a `docker-compose.yml` from a project that uses a newer Compose file format
- Upgrading Docker Engine without upgrading docker-compose

# [02] Root Cause

The system has an outdated version of `docker-compose` that does not support the Compose file format version declared in `docker-compose.yml`.

```shell
$ docker-compose version
docker-compose version 1.25.0, build unknown
docker-py version: 4.1.0
CPython version: 3.8.10
OpenSSL version: OpenSSL 1.1.1f  31 Mar 2020
```

Version `1.25.0` (the apt-installed binary on older Ubuntu) does not understand Compose file format versions `3.8` and above, which are common in modern projects.

| Compose CLI Version | Max Supported File Version | Notes |
|---|---|---|
| 1.25.x | 3.7 | Installed via `apt` on Ubuntu 20.04 |
| 1.29.x | 3.9 | Last of the Python-based v1 series |
| 2.x+ | 3.9 / current | Go-based rewrite, actively maintained |

:small_blue_diamond: Reference: [Version in docker-compose.yml is unsupported](https://github.com/datahub-project/datahub/issues/2020){:target="_blank"}

# [03] Fix — Reinstall docker-compose

Upgrade to the latest release directly from the Docker GitHub releases. The script below fetches the current version automatically using the GitHub API:

```shell
# Install jq (used to parse the GitHub API JSON response)
sudo apt-get install jq

# Fetch the latest version tag and set the install destination
VERSION=$(curl --silent https://api.github.com/repos/docker/compose/releases/latest | jq .name -r)
DESTINATION=/usr/bin/docker-compose

# Download the correct binary for this OS and architecture
sudo curl -L https://github.com/docker/compose/releases/download/${VERSION}/docker-compose-$(uname -s)-$(uname -m) -o $DESTINATION

# Grant execute permission
sudo chmod 755 $DESTINATION

# Confirm the binary location
which docker-compose

# Check the installed version
docker-compose version
```

As of 2023-01-06, this installs version `2.14.2` on Ubuntu 24.04.

## Alternative: Docker Compose Plugin (Recommended)

Modern Docker Engine ships with Compose as a plugin (`docker compose` instead of `docker-compose`). If you are starting fresh, use the plugin instead:

```shell
# Install Docker Compose plugin via apt
sudo apt-get install docker-compose-plugin

# Verify
docker compose version
```

The plugin is invoked as `docker compose` (space, not hyphen) and stays in sync with Docker Engine updates.

# [04] Verify

After reinstalling, confirm the version and re-run your stack:

```shell
$ docker-compose version
Docker Compose version v2.14.2

$ docker-compose up -d
[+] Running 3/3
 ✔ Container app   Started
 ✔ Container db    Started
 ✔ Container proxy Started
```

The `version is unsupported` error should be gone.

# [05] Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `curl` download fails | No internet access or GitHub rate limit | Download manually and `scp` to host |
| Wrong binary (not executable) | Architecture mismatch | Check `uname -m` output and match to release filename |
| Both `docker-compose` and `docker compose` exist | Parallel installs | Remove old binary: `sudo rm /usr/local/bin/docker-compose` |
| Error persists after upgrade | Shell cached old binary path | Run `hash -r` or open a new terminal |
