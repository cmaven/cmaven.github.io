---
title: "Complete docker compose down — Cleaning Up Containers, Volumes, and Images"
description: "How to fully clean up an environment created by docker compose up -d, with each option (-v, --rmi all, --remove-orphans) explained"
excerpt: "docker compose down alone leaves volumes and images behind — situational delete options and full reset methods"
date: 2026-04-21
categories: Docker
tags: [Docker, docker-compose, down, volume, cleanup, prune, orphan, reset]
ref: docker-compose-down-cleanup
---

:bulb: To completely clean up an environment created with `docker compose up -d`, you need a step-by-step approach. This guide summarizes situational delete methods and the difference between each option.
{: .notice--info}

---

# [01] Deletion Levels Compared

| Command | Containers | Networks | Volumes | Images | Use case |
|---------|:---:|:---:|:---:|:---:|----------|
| `docker compose down` | O | O | X | X | Basic cleanup |
| `docker compose down -v` | O | O | O | X | Including DB data |
| `docker compose down --rmi all -v` | O | O | O | O | Near factory reset |
| `docker compose down -v --remove-orphans` | O | O | O | X | + leftover containers |
| `docker system prune -a --volumes` | All | All | All | All | Full Docker cleanup |

---

# [02] Basic Cleanup — Containers + Networks

```bash
docker compose down
```

| Target | Removed? |
|--------|:---:|
| Containers | O |
| Networks | O |
| Volumes | X |
| Images | X |

The most basic delete. Removes containers and networks only — **volumes (DB data, etc.) and images remain**. Running `docker compose up -d` again will restart quickly with existing data intact.

---

# [03] Including Volumes — Removes DB Data

```bash
docker compose down -v
```

| Option | Description |
|--------|-------------|
| `-v` | Removes named volumes defined in `docker-compose.yml` |

:warning: Removing volumes deletes **DB data, configuration files, caches, and more**. Back up anything important first.
{: .notice--warning}

```yaml
# docker-compose.yml example
volumes:
  postgres_data:    # ← removed by -v
  redis_data:       # ← also removed
```

---

# [04] Including Images — Near Factory Reset

```bash
docker compose down --rmi all -v
```

| Option | Description |
|--------|-------------|
| `--rmi all` | Removes all images used by compose |
| `-v` | Removes volumes |

After this command, the next `docker compose up -d` must **re-pull/build images**, which takes time.

`--rmi` option values:

| Value | Description |
|-------|-------------|
| `all` | Remove all images |
| `local` | Remove only locally built images (keep pulled images) |

---

# [05] Cleaning Up Orphan Containers

```bash
docker compose down -v --remove-orphans
```

| Option | Description |
|--------|-------------|
| `--remove-orphans` | Removes containers from services no longer defined in the current `docker-compose.yml` |

**What's an orphan container?**

If you delete or rename a service in `docker-compose.yml` and then run `down`, the old service's container may remain. `--remove-orphans` cleans these up.

```yaml
# Previous docker-compose.yml
services:
  web:
  db:
  redis:     # ← removed later, but container remains

# Current docker-compose.yml
services:
  web:
  db:
  # no redis → orphan container
```

---

# [06] Full Docker Reset

```bash
docker system prune -a --volumes
```

:warning: This removes **containers, images, and volumes from other projects too**. Everything not actively used will be cleaned up.
{: .notice--warning}

| Target | Description |
|--------|-------------|
| Stopped containers | All |
| Unused networks | All |
| Dangling images | Untagged images |
| With `-a` | All unused images |
| With `--volumes` | All unused volumes |

Check what will be removed first:

```bash
# Preview deletion candidates
docker system df
```

```
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          15        3         4.2GB     3.1GB (73%)
Containers      5         2         120MB     80MB (66%)
Local Volumes   8         2         2.1GB     1.5GB (71%)
Build Cache     20        0         500MB     500MB
```

---

# [07] Deleting Only a Specific Project

When multiple compose projects exist, target a specific one:

```bash
docker compose -p my-project down -v
```

| Option | Description |
|--------|-------------|
| `-p my-project` | Specify project name (default: directory name) |

Check project names:

```bash
docker compose ls
```

```
NAME            STATUS          CONFIG FILES
my-app          running(3)      /home/user/my-app/docker-compose.yml
docs-portal     running(2)      /home/user/docs/docker-compose.yml
```

---

# [08] When Volumes Remain and Cause Issues

## 8-1. Symptom

After `docker compose down` and `up` again, **old DB data is still there**:

```bash
docker compose down
docker compose up -d
# → DB still has old data
```

## 8-2. Cause

`down` does not remove volumes by default. Data in named volumes persists.

## 8-3. Resolution

```bash
# Delete with volumes
docker compose down -v

# Or manually delete specific volumes
docker volume ls
docker volume rm my-app_postgres_data
```

---

# [09] Summary

**Recommended commands by situation:**

| Situation | Command |
|-----------|---------|
| Temporarily stopping, will restart | `docker compose down` |
| Clean delete including data | `docker compose down -v --remove-orphans` |
| Complete restart from scratch | `docker compose down --rmi all -v --remove-orphans` |
| Full Docker cleanup | `docker system prune -a --volumes` |

:bulb: In most cases, `docker compose down -v --remove-orphans` is sufficient.
{: .notice--info}
