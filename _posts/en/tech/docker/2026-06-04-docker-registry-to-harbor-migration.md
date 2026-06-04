---
title: "Migrating Docker Registry (registry:2) to Harbor with Near-Zero Downtime"
description: "A field log of replacing a running registry:2 with Harbor on the same host and same port — temporary-port coexistence, skopeo image migration, a short cutover, and the three pitfalls: container name clash, the project segment, and public projects"
excerpt: "Bring up Harbor on a temporary port first, move the images, then take over the original port in a short cutover — switching registry:2 to Harbor with no node config changes"
date: 2026-06-04
categories: Docker
tags: [Docker, Harbor, Registry, registry2, skopeo, Kubernetes, containerd, Migration, OCI, ContainerRegistry, DevOps]
ref: docker-registry-to-harbor-migration
---

:bulb: A field log of replacing a running `registry:2` (Docker Distribution) with **Harbor** on the **same host and same port** (`:5100`). We bring up Harbor on a temporary port (`:5101`) first, move the images, then take over `:5100` in a short cutover. With a Kubernetes cluster actively pulling from this registry, the goal is to switch **without changing any node config**.
{: .notice--info}

---

# [01] TL;DR

<pre class="mermaid">
graph LR
    A["1. Install Harbor<br/>on :5101"] --> B["2. Migrate images<br/>with skopeo"]
    B --> C["3. Verify"]
    C --> D["4. Stop registry,<br/>move Harbor to :5100"]
    D --> E["5. Update image paths<br/>(project segment)"]

    style A fill:#e3f2fd,stroke:#1565c0
    style D fill:#fff3e0,stroke:#e65100
    style E fill:#e8f5e9,stroke:#2e7d32
</pre>

**The three key pitfalls**

| # | Pitfall | Avoidance |
|---|---------|-----------|
| ① | Harbor's internal container is also named `registry` → clash | `rename` the existing container (no downtime) |
| ② | Harbor forces a **project segment** in the path | Centralize the prefix in one variable |
| ③ | Keep the project **public** → no node / secret changes | Public project + same host:port over HTTP |

---

# [02] Why Harbor

`registry:2` is lightweight and serves OCI artifacts (including Helm charts) well, but you have to **list images with `curl`**, deletion/GC is clunky, and there's no RBAC, vulnerability scanning, or proxy-cache. Harbor (CNCF, Apache-2.0, free) provides a **web GUI, retention/GC, RBAC, Trivy scanning, and an upstream proxy-cache**.

:warning: **If you only need Helm chart hosting, Harbor is not required.** `registry:2` serves OCI artifacts (Helm charts) too. Harbor is the choice when you need "governance / visibility."
{: .notice--warning}

---

# [03] Assumptions / Environment

- Registry host: Ubuntu 22.04, `docker` + `docker compose v2` installed, ample disk and memory.
- The existing `registry:2` runs over **HTTP (plaintext, insecure)**. (No TLS → nodes are already configured to trust it as insecure.)
- The cluster nodes (containerd) have this registry registered as **insecure/HTTP**.
- This post keeps HTTP + a **public project** (anonymous pull). (If you have an internal CA/TLS, switch to distributing the node CA instead.)

## 3-1. Variables (substitute for your environment)

```bash
REG_HOST=192.0.2.10            # Registry host IP (documentation/example IP)
PORT_FINAL=5100               # Final service port (same as the old registry)
PORT_TEMP=5101                # Temporary port for migration
HARBOR_VER=v2.14.4            # Harbor version (check the latest release)
PROJECT=myproject            # Harbor project name
ADMIN_PW='<admin-password>'   # Harbor admin password
```

---

# [04] Step 1. Install Harbor (temporary port `:5101`)

:bulb: The old registry keeps serving on `:5100`, so Harbor must come up on a **different port** first to coexist without conflict.
{: .notice--info}

## 4-1. Download the installer

```bash
mkdir -p /opt/harbor-install && cd /opt/harbor-install
curl -fSL -o harbor-offline-installer-$HARBOR_VER.tgz \
  https://github.com/goharbor/harbor/releases/download/$HARBOR_VER/harbor-offline-installer-$HARBOR_VER.tgz
tar xzf harbor-offline-installer-$HARBOR_VER.tgz
cd harbor
cp harbor.yml.tmpl harbor.yml
```

> For an air-gapped host, download externally and `scp` it over. (The offline installer bundles all Harbor images.)

## 4-2. Edit `harbor.yml` (temporary 5101 + HTTP)

Comment out the entire `https:` block and use HTTP only.

```bash
awk 'BEGIN{h=0} /^https:/{h=1} h&&/^[a-zA-Z]/&&!/^https:/{h=0} {if(h) print "# "$0; else print}' harbor.yml.tmpl \
 | sed "s/^hostname: .*/hostname: $REG_HOST/" \
 | sed "s/^  port: 80\$/  port: $PORT_TEMP/" \
 | sed "s/^harbor_admin_password: .*/harbor_admin_password: $ADMIN_PW/" \
 | sed "s#^data_volume: .*#data_volume: /data/harbor#" > harbor.yml

# Verify
grep -E "^hostname:|^  port:|^# https:|^harbor_admin_password:|^data_volume:" harbor.yml
```

## 4-3. Install

```bash
sudo ./prepare
sudo ./install.sh        # (optional) --with-trivy to enable vulnerability scanning
```

## :warning: Pitfall ① — container name `registry` clash

Harbor's **internal registry container is also named `registry`**, so it clashes with the existing `registry:2` container.

```
Error response from daemon: Conflict. The container name "/registry" is already in use ...
```

**Fix**: `rename` the existing container (a rename while running causes no interruption — `:5100` keeps serving), then bring Harbor up.

```bash
docker rename registry registry-legacy     # existing registry:2, rename only, no downtime
curl -s -o /dev/null -w "5100 still up -> %{http_code}\n" http://localhost:$PORT_FINAL/v2/   # expect 200
cd /opt/harbor-install/harbor && docker compose up -d
```

## 4-4. Health check + create the project (public)

```bash
# Health
curl -s http://localhost:$PORT_TEMP/api/v2.0/health | grep -o '"status":"healthy"' | head -1

# Create project myproject as public (anonymous pull → no node/secret changes)
curl -s -u admin:$ADMIN_PW -X POST http://localhost:$PORT_TEMP/api/v2.0/projects \
  -H "Content-Type: application/json" \
  -d "{\"project_name\":\"$PROJECT\",\"public\":true}" -w "\nHTTP %{http_code}\n"
```

---

# [05] Step 2. Migrate images (`:5100` → `:5101/myproject/...`)

Use `skopeo` to copy directly between registries (it skips the local docker store, so it's fast).

```bash
sudo apt-get install -y skopeo    # install if missing
```

## :warning: Pitfall ② — Harbor forces a **project segment** in the path

The flat path `…/my-operator` in `registry:2` becomes `…/<project>/my-operator` in Harbor. So set the copy destination to `$PROJECT/<original-path>`.

```bash
SRC=localhost:$PORT_FINAL
DST=localhost:$PORT_TEMP

# Repos to move (only what you need!). To move everything, enumerate via /v2/_catalog.
REPOS="my-operator my-agent my-driver-ds base/kubectl vendor/device-plugin"

for repo in $REPOS; do
  # Enumerate tags for this repo
  tags=$(curl -s http://$SRC/v2/$repo/tags/list \
         | tr ',' '\n' | sed 's/[]["{}]//g;s/tags://;s/name://;s/ //g' | grep -v '^$')
  for t in $tags; do
    [ "$t" = "$(basename $repo)" ] && continue   # skip when the parser mistakes the repo name for a tag
    echo ">> $repo:$t"
    skopeo copy --quiet --all \
      --src-tls-verify=false --dest-tls-verify=false \
      --dest-creds admin:$ADMIN_PW \
      docker://$SRC/$repo:$t docker://$DST/$PROJECT/$repo:$t
  done
done
```

> Example result path: `…:5101/myproject/my-operator:v0.5.24`. Harbor allows multi-level repos under a project (`myproject/vendor/device-plugin`).
> If you prefer a GUI approach, **Harbor Replication** works too (Administration → Registries → register a "Docker Registry" endpoint → pull rule).

---

# [06] Step 3. Verify the migration

```bash
# Check repos/artifacts that landed in Harbor (GUI: Projects → myproject → Repositories)
curl -s -u admin:$ADMIN_PW "http://localhost:$PORT_TEMP/api/v2.0/projects/$PROJECT/repositories?page_size=100" \
  | tr ',' '\n' | grep '"name"'

# Anonymous pull test (public project → docker fetches an anonymous token and pulls without credentials)
docker pull localhost:$PORT_TEMP/$PROJECT/my-operator:v0.5.24
```

:warning: Hitting `/v2/.../manifests/...` directly with `curl` returns **401** (it skips the token flow). **`docker pull` is the accurate verification.**
{: .notice--warning}

---

# [07] Step 4. Cutover — stop the old registry, move Harbor to `:5100`

:warning: This is the only point with short (a few minutes) downtime. **Already-running pods are unaffected (cached)**, but a pod restart or new scheduling during this window may briefly fail to pull, so move fast.
{: .notice--warning}

```bash
# (1) Stop the old registry (keep data — for rollback)
docker update --restart=no registry-legacy
docker stop registry-legacy
ss -ltn | grep -q ":$PORT_FINAL" && echo "still bound" || echo "5100 released"

# (2) Switch Harbor port 5101 → 5100
cd /opt/harbor-install/harbor
sed -i "s/^  port: $PORT_TEMP\$/  port: $PORT_FINAL/" harbor.yml
sudo ./prepare
sudo docker compose down && sudo docker compose up -d

# (3) Confirm Harbor responds on 5100
curl -s http://localhost:$PORT_FINAL/api/v2.0/health | grep -o '"status":"healthy"' | head -1
```

---

# [08] Step 5. Update clients

## 8-1. Nodes (containerd) — **no change needed**

Same `host:port` over HTTP and a **public project**, so the existing insecure config keeps working as-is. containerd even handles Harbor's anonymous token flow automatically.

```bash
# On any node (the real k8s pull path)
sudo crictl pull $REG_HOST:$PORT_FINAL/$PROJECT/my-operator:v0.5.24
```

> If containerd 1.7+ has `server="http://…"` + `skip_verify=true` in `/etc/containerd/certs.d/<host:port>/hosts.toml`, you're good.
> (If you went with a private project instead, you'd now need node auth + a k8s `imagePullSecret`.)

## 8-2. Update application image paths (add the project segment)

The image path changed from `…/my-operator` to `…/myproject/my-operator`, so update your manifests / Helm values. If you centralize the registry prefix in a single variable, it's a one-liner (e.g. Helm `global.registry`).

```bash
# Example: when the Helm chart assembles the prefix from global.registry
helm upgrade --install <release> <chart> -n <ns> \
  --set global.registry=$REG_HOST:$PORT_FINAL/$PROJECT
```

## :warning: Pitfall ③ — quote `.env` values that contain spaces

If your deploy wrapper does `source deploy.env`, values with spaces **must be quoted**. Otherwise `source` puts only the first token into the variable and tries to run the rest as a command, which fails.

```bash
# Wrong: EXTRA_ARGS=--set a=b --set c=d        # → "c=d: No such file" style error
# Right:
EXTRA_ARGS="--set a=b --set c=d"
```

---

# [09] Final verification

```bash
kubectl get pods -A | grep -iE "ImagePull|ErrImage" || echo "No ImagePull errors"
kubectl get pod -n <ns> -o jsonpath='{..image}' | tr ' ' '\n' | grep "$PROJECT/" | sort -u   # confirm the new path is used
```

- If every app pulls from the `…/myproject/…` path and runs normally, you're done.
- **The Harbor containers are `restart: always`**, so they come back automatically on host reboot.

---

# [10] Rollback (if something breaks)

Since the original data is preserved, you can revert immediately.

```bash
cd /opt/harbor-install/harbor && sudo docker compose down       # take Harbor down
docker start registry-legacy                                    # bring registry:2 back up (:5100)
docker update --restart=always registry-legacy
# Revert the registry path in app values to the original (no project) and redeploy
```

---

# [11] Wrap-up — lessons (pitfalls recap)

1. **Container name clash**: Harbor's internal `registry` collides with the existing `registry:2` container name → avoid it with a `rename` (no downtime).
2. **Project segment**: every repo in Harbor lives under a project → image paths change. Centralize the prefix in one variable (`global.registry`, etc.) and the switch is a single line.
3. **Value of a public project**: keeping pull anonymous means **no node config or imagePullSecret changes at all** (assuming the same host:port over HTTP).
4. **TLS is the real answer**: the answer to "I don't want to touch node config" is **trusted-CA-based TLS**, not Harbor specifically — it's product-agnostic.
5. **`.env` quoting**: always quote values that contain spaces.
6. **Verify with `docker/crictl pull`**: `curl`'s 401 is because the token flow wasn't followed — it's not an error.

:bulb: Result: we kept the same address (`:5100`) while gaining a GUI, GC, scanning, and RBAC, and the running workloads moved over with zero downtime.
{: .notice--success}
