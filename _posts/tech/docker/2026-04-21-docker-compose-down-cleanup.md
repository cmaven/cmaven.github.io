---
title: "docker compose down 완전 삭제 가이드 — 컨테이너, 볼륨, 이미지 단계별 정리"
description: "docker compose up -d로 띄운 환경을 단계별로 깨끗하게 삭제하는 방법과 각 옵션(-v, --rmi all, --remove-orphans)의 차이 정리"
excerpt: "docker compose down만으로는 볼륨과 이미지가 남는다 — 상황별 삭제 옵션과 완전 초기화 방법"
date: 2026-04-21
categories: Docker
tags: [Docker, docker-compose, down, volume, 삭제, cleanup, prune, orphan, 초기화]
---

:bulb: `docker compose up -d`로 띄운 환경을 완전히 깨끗하게 삭제하려면 단계별로 정리해야 한다. 상황별 삭제 방법과 각 옵션의 차이를 정리한다.
{: .notice--info}

---

# [01] 삭제 단계별 비교

| 명령어 | 컨테이너 | 네트워크 | 볼륨 | 이미지 | 용도 |
|--------|:---:|:---:|:---:|:---:|------|
| `docker compose down` | O | O | X | X | 기본 삭제 |
| `docker compose down -v` | O | O | O | X | DB 데이터 포함 삭제 |
| `docker compose down --rmi all -v` | O | O | O | O | 거의 처음 상태로 |
| `docker compose down -v --remove-orphans` | O | O | O | X | + 찌꺼기 컨테이너 |
| `docker system prune -a --volumes` | 전체 | 전체 | 전체 | 전체 | Docker 전체 초기화 |

---

# [02] 기본 삭제 — 컨테이너 + 네트워크

```bash
docker compose down
```

| 삭제 대상 | 삭제 여부 |
|----------|:---:|
| 컨테이너 | O |
| 네트워크 | O |
| 볼륨 | X |
| 이미지 | X |

가장 기본적인 삭제 명령이다. 컨테이너와 네트워크만 제거하고, **볼륨(DB 데이터 등)과 이미지는 그대로 남는다.** 다시 `docker compose up -d`를 실행하면 기존 데이터가 유지된 채 빠르게 재시작된다.

---

# [03] 볼륨까지 삭제 — DB 데이터 포함

```bash
docker compose down -v
```

| 옵션 | 설명 |
|------|------|
| `-v` | `docker-compose.yml`에 정의된 named volume 삭제 |

:warning: 볼륨을 삭제하면 **DB 데이터, 설정 파일, 캐시 등이 전부 삭제**된다. 필요한 데이터는 미리 백업한다.
{: .notice--warning}

```yaml
# docker-compose.yml 예시
volumes:
  postgres_data:    # ← -v 옵션으로 이 볼륨이 삭제됨
  redis_data:       # ← 이것도 삭제됨
```

---

# [04] 이미지까지 삭제 — 거의 처음 상태

```bash
docker compose down --rmi all -v
```

| 옵션 | 설명 |
|------|------|
| `--rmi all` | compose에서 사용한 모든 이미지 삭제 |
| `-v` | 볼륨 삭제 |

이 명령 후에는 다음 `docker compose up -d` 시 **이미지를 다시 pull/build**해야 하므로 시간이 걸린다.

`--rmi` 옵션 종류:

| 값 | 설명 |
|----|------|
| `all` | 모든 이미지 삭제 |
| `local` | 커스텀 빌드한 이미지만 삭제 (pull한 이미지는 유지) |

---

# [05] orphan 컨테이너 정리 — 찌꺼기 삭제

```bash
docker compose down -v --remove-orphans
```

| 옵션 | 설명 |
|------|------|
| `--remove-orphans` | 현재 `docker-compose.yml`에 정의되지 않은 이전 서비스의 컨테이너 삭제 |

**orphan 컨테이너란?**

`docker-compose.yml`에서 서비스를 삭제하거나 이름을 변경한 후 `down`을 실행하면, 이전 서비스의 컨테이너가 남을 수 있다. `--remove-orphans`는 이런 찌꺼기를 정리한다.

```yaml
# 이전 docker-compose.yml
services:
  web:
  db:
  redis:     # ← 이후 삭제했지만 컨테이너는 남아있음

# 현재 docker-compose.yml
services:
  web:
  db:
  # redis 없음 → orphan 컨테이너
```

---

# [06] Docker 전체 초기화

```bash
docker system prune -a --volumes
```

:warning: **다른 프로젝트의 컨테이너, 이미지, 볼륨까지 전부 삭제된다.** 현재 실행 중인 컨테이너만 제외하고 모든 것을 정리한다.
{: .notice--warning}

| 삭제 대상 | 설명 |
|----------|------|
| 중지된 컨테이너 | 전부 |
| 사용하지 않는 네트워크 | 전부 |
| dangling 이미지 | 태그 없는 이미지 |
| `-a` 옵션 시 | 사용하지 않는 **모든** 이미지 |
| `--volumes` 옵션 시 | 사용하지 않는 볼륨 |

삭제 전 확인:

```bash
# 삭제될 대상 미리 확인
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

# [07] 특정 프로젝트만 삭제

여러 compose 프로젝트가 있을 때, 특정 프로젝트만 정확히 지정하여 삭제할 수 있다.

```bash
docker compose -p my-project down -v
```

| 옵션 | 설명 |
|------|------|
| `-p my-project` | 프로젝트 이름 지정 (기본값: 디렉토리명) |

프로젝트 이름 확인:

```bash
docker compose ls
```

```
NAME            STATUS          CONFIG FILES
my-app          running(3)      /home/user/my-app/docker-compose.yml
docs-portal     running(2)      /home/user/docs/docker-compose.yml
```

---

# [08] 볼륨이 남아서 문제되는 경우

## 8-1. 증상

`docker compose down` 후 다시 `up`하면 **이전 DB 데이터가 그대로 남아있는** 경우:

```bash
docker compose down
docker compose up -d
# → DB에 이전 데이터가 여전히 존재
```

## 8-2. 원인

`down`은 기본적으로 볼륨을 삭제하지 않는다. named volume에 저장된 데이터는 유지된다.

## 8-3. 해결

```bash
# 볼륨 포함 삭제
docker compose down -v

# 또는 특정 볼륨만 수동 삭제
docker volume ls
docker volume rm my-app_postgres_data
```

---

# [09] 정리

**일반적인 상황별 권장 명령어:**

| 상황 | 명령어 |
|------|--------|
| 잠시 중지 후 재시작 예정 | `docker compose down` |
| 데이터 포함 깨끗하게 삭제 | `docker compose down -v --remove-orphans` |
| 완전히 처음부터 다시 시작 | `docker compose down --rmi all -v --remove-orphans` |
| Docker 전체 정리 | `docker system prune -a --volumes` |

:bulb: 대부분의 경우 `docker compose down -v --remove-orphans`이면 충분하다.
{: .notice--info}
