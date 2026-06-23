<!-- 2026-06-23-homeserver-https-dns01-country-block.md: HTTPS on a Korea-only home server via DNS-01 wildcard | created: 2026-06-23 -->
---
title: "HTTPS for a Domestic-Only Home Server — Let's Encrypt DNS-01 + DuckDNS Wildcard"
description: "When iptime country-based access restriction (Korea-only) makes HTTP-01 cert issuance fail, use port-free DNS-01 + a DuckDNS wildcard to add HTTPS without disabling the security setting"
excerpt: "When inbound from abroad is blocked (country restriction / CGNAT) and port-80 HTTP-01 fails, use certbot DNS-01 with a DuckDNS TXT hook to obtain a wildcard cert and serve multiple subdomains over HTTPS — a step-by-step guide"
date: 2026-06-23
categories: Network
tags: [iptime, DuckDNS, HTTPS, "Let's Encrypt", Certbot, DNS-01, wildcard, country-restriction, Nginx, Docker, home-server]
ref: homeserver-https-dns01-country-block
---

:bulb: A home server with iptime **"country-based access restriction (allow Korea only)"** blocks inbound traffic from abroad, so **HTTP-01 (port 80) cert issuance fails**. With port-free **DNS-01 (DuckDNS TXT)** you can obtain a **wildcard certificate** and add HTTPS while keeping the security setting on.
{: .notice--info}

This is a **follow-up** to [DuckDNS + HTTPS Setup on an iptime Router](/en/Network/iptime-duckdns-https-guide/). DuckDNS domain registration, IP auto-update, port forwarding, and the basic Docker Compose layout were covered there, so here we focus only on **diagnosing the environment where HTTP-01 fails and switching to DNS-01**.

Example environment used in this post:
- Server LAN IP `192.168.0.22`, domain prefix `mydomain` (→ `mydomain.duckdns.org`)
- Three services: `engwrite` (Django), `birthplanner` (Vite SPA), `cdocs` (VitePress) — host ports 8000/8100/8200
- Goal: expose each as a **subdomain** like `https://engwrite.mydomain.duckdns.org`

The relationship between the components (iptime · DuckDNS · Let's Encrypt · nginx · server) looks like this.

<pre class="mermaid">
graph TD
    USER["Domestic user<br/>browser"] -->|"https://*.mydomain.duckdns.org<br/>(443)"| DUCK
    LE["Let's Encrypt<br/>(overseas validation servers)"] -.->|"DNS-01: read TXT<br/>_acme-challenge"| DUCK
    OVERSEAS["Inbound from abroad<br/>(80/443)"] -.->|"blocked by country<br/>restriction"| IPTIME

    DUCK["DuckDNS<br/>(DNS + TXT record)"] -->|"domain → router public IP"| IPTIME

    IPTIME["iptime router<br/>country restriction: Korea only<br/>port-forward 443"] -->|"443 → 192.168.0.22"| NGINX

    subgraph SERVER["Linux server (192.168.0.22)"]
        NGINX["nginx<br/>reverse proxy + wildcard TLS termination"]
        CERTBOT["certbot (DNS-01)<br/>updates TXT via duckdns-hook.sh"]
        NGINX -->|":8000"| A["engwrite (Django)"]
        NGINX -->|":8100"| B["birthplanner (Vite SPA)"]
        NGINX -->|":8200"| C["cdocs (VitePress)"]
    end

    CERTBOT -->|"TXT add/clean"| DUCK
    CERTBOT -->|"issue wildcard cert<br/>*.mydomain.duckdns.org"| NGINX

    style USER fill:#e3f2fd,stroke:#1565c0
    style DUCK fill:#fff3e0,stroke:#e65100
    style IPTIME fill:#fce4ec,stroke:#c62828
    style NGINX fill:#e8f5e9,stroke:#2e7d32
    style CERTBOT fill:#ede7f6,stroke:#5e35b1
    style LE fill:#f3e5f5,stroke:#8e24aa
    style OVERSEAS fill:#ffebee,stroke:#b71c1c,stroke-dasharray: 5 5
</pre>

The key idea: keep **inbound from abroad blocked (dashed lines)** while handling cert validation through **DNS-01 (TXT lookup)**, which never needs to reach your server.

---

# [00] Why the Common Guide Fails Here

The common approach is **Let's Encrypt HTTP-01**: certbot drops a file under `/.well-known/acme-challenge/`, and Let's Encrypt **reads that file over port 80 from the outside** to prove domain ownership (the method in [STEP 06 of the previous post](/en/Network/iptime-duckdns-https-guide/)).

But if a Korean residential line (especially KT) or an iptime security setting **blocks inbound from abroad**, Let's Encrypt's validation servers (all overseas) cannot reach your port 80, and issuance fails.

```
Certbot failed to authenticate some domains (authenticator: webroot).
  Detail: <public IP>: Fetching http://<domain>/.well-known/acme-challenge/...:
          Timeout during connect (likely firewall problem)
```

:warning: This error usually leads people to suspect port forwarding, but often port forwarding is fine and only **overseas IPs are blocked**. Diagnose the root cause first.
{: .notice--warning}

---

# [01] Diagnosis — "Is It Really Unreachable From Outside?"

## 1-1. Do DNS and the public IP match?

```bash
curl -s ifconfig.me; echo            # my public IP
dig +short mydomain.duckdns.org          # should match the above
dig +short engwrite.mydomain.duckdns.org # DuckDNS returns the same IP for subdomains
```

## 1-2. Is the Port Open From Abroad? — The Key Check

A `nc` test from inside Korea **may succeed** (domestic is allowed). You must check from **overseas nodes**. [check-host.net](https://check-host.net){:target="_blank"} checks from many countries at once.

```bash
# Check port 80 from 8 overseas nodes
RID=$(curl -s -H 'Accept: application/json' \
  "https://check-host.net/check-tcp?host=mydomain.duckdns.org:80&max_nodes=8" \
  | grep -oE '"request_id":"[^"]+"' | cut -d'"' -f4)
sleep 12
curl -s -H 'Accept: application/json' "https://check-host.net/check-result/$RID"
```

If overseas nodes **all show `Connection timed out`** but domestic works → **region-based (overseas IP) inbound blocking**. It is not a port-forwarding or CGNAT problem.

:memo: **Tip**: If not just 80/443 but an **arbitrary high port** (one you already forwarded) also times out from abroad, it is "region blocking," not "specific-port blocking."
{: .notice--info}

## 1-3. Confirm the Culprit — iptime Country-Based Access Restriction

Open the iptime admin page → **Security → Country-based access restriction**. If only **South Korea is in the "allow" list** as below, all other inbound from the entire world is blocked (84,856 entries blocked in this example).

![iptime country-based access restriction — Korea only](/assets/images/iptime-country-block.png)

This setting is **useful for security**, so keep it on. Change the cert issuance method instead.

---

# [02] Choosing a Solution — Do You Need Overseas Access?

| Situation | Solution |
|-----------|----------|
| **Domestic use only** (most personal home servers) | **Keep country restriction + DNS-01** ← this post |
| Overseas access needed | Lift the country restriction then use HTTP-01, or Cloudflare Tunnel / Tailscale |

DNS-01 has Let's Encrypt read **only a DNS TXT record without connecting to your server**, so issuance and auto-renewal work even when inbound is blocked. Serving (443) only needs domestic users, so it coexists with the country restriction.

:bulb: DuckDNS allows only **one TXT slot per domain**, so if you have several subdomains, do not issue them one by one — issue a single **wildcard `*.mydomain.duckdns.org`**. A wildcard is validated by one `_acme-challenge.mydomain.duckdns.org` TXT record.
{: .notice--info}

---

# [03] Prerequisites

1. **DuckDNS domain + token**: see [STEP 02 of the previous post](/en/Network/iptime-duckdns-https-guide/) (add domain `mydomain` → copy the **token** at the top).
2. **iptime port forwarding**: external `443` → `192.168.0.22:443`. **DNS-01 does not need 80**, but 443 is required for domestic users' HTTPS access.
   - Even with the country restriction on, **domestic IPs** can still reach this 443.
3. `docker` + `docker compose` (v2), `curl`, `dig` on the server.

---

# [04] Issuing the Cert — certbot DNS-01 + DuckDNS hook

The core is attaching a **hook that sets/clears the DuckDNS TXT record** to certbot's `--manual` mode.

## 4-1. DuckDNS Hook Script

`~/myserver/scripts/duckdns-hook.sh` (make it executable):

```sh
#!/bin/sh
set -eu
action="${1:-}"
: "${DUCKDNS_DOMAIN:?}"; : "${DUCKDNS_TOKEN:?}"
base="https://www.duckdns.org/update?domains=${DUCKDNS_DOMAIN}&token=${DUCKDNS_TOKEN}"
case "$action" in
  add)   url="${base}&txt=${CERTBOT_VALIDATION}" ;;
  clean) url="${base}&txt=removed&clear=true" ;;
  *) echo "usage: duckdns-hook.sh add|clean" >&2; exit 2 ;;
esac
resp="$(curl -fsS "$url" || wget -qO- "$url")"
echo "duckdns-hook($action) -> $resp" >&2
[ "$action" = add ] && [ "$resp" != OK ] && exit 1
[ "$action" = add ] && sleep "${DUCKDNS_PROPAGATION:-30}"   # wait for TXT propagation
exit 0
```

:memo: `CERTBOT_DOMAIN`/`CERTBOT_VALIDATION` are environment variables certbot injects automatically when running the hook.
{: .notice--info}

## 4-2. docker compose (certbot service)

Inject the hook script and token into the certbot service of [the previous post's docker-compose.yml](/en/Network/iptime-duckdns-https-guide/).

```yaml
  certbot:
    image: certbot/certbot
    container_name: certbot
    restart: unless-stopped
    env_file:
      - ./duckdns.env          # DUCKDNS_DOMAIN / DUCKDNS_TOKEN / DUCKDNS_PROPAGATION
    volumes:
      - ./data/certbot/conf:/etc/letsencrypt
      - ./data/certbot/www:/var/www/certbot
      - ./scripts:/scripts:ro
    # auto-renew every 12h (reuses the stored manual hook)
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

`~/myserver/duckdns.env` (permission 600):

```ini
DUCKDNS_DOMAIN=mydomain
DUCKDNS_TOKEN=your-token-here
DUCKDNS_PROPAGATION=30
```

## 4-3. Issue (Rehearse With staging First)

Let's Encrypt production certs have a limit of **5 per week**, so validate with `--dry-run` (staging) first.

```bash
cd ~/myserver
docker compose run --rm --entrypoint certbot certbot certonly \
  --manual --preferred-challenges dns \
  --manual-auth-hook   "/scripts/duckdns-hook.sh add" \
  --manual-cleanup-hook "/scripts/duckdns-hook.sh clean" \
  --cert-name mydomain.duckdns.org \
  -d '*.mydomain.duckdns.org' \
  --email you@example.com --agree-tos --no-eff-email --non-interactive \
  --dry-run
```

When you see `The dry run was successful.`, rerun without `--dry-run` → real issuance.

```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/mydomain.duckdns.org/fullchain.pem
```

:warning: **Pitfall 1 — entrypoint**: If certbot has an auto-renew `entrypoint` (infinite renew loop) as above, `docker compose run certbot certonly ...` lets the entrypoint swallow the arguments, so `certonly` never runs (it stalls after `No renewals were attempted`). Always override with **`--entrypoint certbot`**.<br><br>**Pitfall 2 — wildcard cert path**: Pinning the lineage name with `--cert-name mydomain.duckdns.org` stores it under `live/mydomain.duckdns.org/`, making it easy to match the nginx config path.
{: .notice--danger}

---

# [05] nginx — Per-Subdomain 443 + Wildcard Cert

`~/myserver/nginx/nginx.conf` (essentials):

```nginx
events {}
http {
  map $http_upgrade $connection_upgrade { default upgrade; '' close; }
  client_max_body_size 50m;
  ssl_protocols TLSv1.2 TLSv1.3;     # certonly does not create options-ssl-nginx.conf, so inline it

  # 80 → 443 redirect (for domestic users)
  server {
    listen 80;
    server_name mydomain.duckdns.org *.mydomain.duckdns.org;
    location / { return 301 https://$host$request_uri; }
  }

  # one 443 server per subdomain — all use the same wildcard cert
  server {
    listen 443 ssl;
    server_name engwrite.mydomain.duckdns.org;
    ssl_certificate     /etc/letsencrypt/live/mydomain.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mydomain.duckdns.org/privkey.pem;
    location / {
      proxy_pass http://192.168.0.22:8000;     # no trailing '/' = pass root as-is
      proxy_set_header Host $host;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
  }
  # add the same kind of server block for birthplanner(:8100), cdocs(:8200)
}
```

```bash
cd ~/myserver && docker compose down && docker compose up -d
```

:memo: Unlike HTTP-01, `certonly` does not generate `options-ssl-nginx.conf` or `ssl-dhparams.pem`. Put `ssl_protocols` etc. **inline** in nginx to avoid startup failure.
{: .notice--info}

---

# [06] Serve Each App at Root ('/') — Advantage of Subdomains

The subdomain approach runs each app at **its own root**, so you never touch base paths. (Path-based routing like `/engwrite/` changes the base and easily breaks static files and redirects.) If you previously tried path-based routing, **revert it to root**.

- **Django (engwrite)**: `.env`
  - `DJANGO_ALLOWED_HOSTS=engwrite.mydomain.duckdns.org,127.0.0.1,localhost`
  - `CSRF_TRUSTED_ORIGINS=https://engwrite.mydomain.duckdns.org`
  - `USE_HTTPS=true`, `FORCE_SCRIPT_NAME=` (empty — serve at root)
  - settings: `SECURE_SSL_REDIRECT=False` (external nginx terminates HTTPS)
- **Vite SPA (birthplanner)**: remove `base` in `vite.config.ts` (default `/`), remove React Router `basename`, rebuild.
- **VitePress (cdocs)**: remove `base: '/cdocs/'` in config (default `/`), and serve a **prod static build, not the dev server** (don't expose the dev server externally — routing breaks).

---

# [07] Verification

```bash
# Each subdomain from the domestic network (200/301 = OK)
for s in engwrite birthplanner cdocs; do
  curl -Iks "https://$s.mydomain.duckdns.org/" | head -1
done

# Confirm the cert is a wildcard
echo | openssl s_client -servername engwrite.mydomain.duckdns.org \
  -connect mydomain.duckdns.org:443 2>/dev/null | openssl x509 -noout -subject -enddate
# subject= CN = *.mydomain.duckdns.org

# Auto-renew rehearsal (with the stored hook)
cd ~/myserver && docker compose run --rm --entrypoint certbot certbot renew --dry-run
# Congratulations, all simulated renewals succeeded
```

Open `https://engwrite.mydomain.duckdns.org/` in a browser → padlock + normal page means you're done.

---

# [08] Troubleshooting

| Symptom | Cause / Fix |
|---------|-------------|
| `Timeout during connect (likely firewall problem)` | Inbound from abroad blocked (country restriction / ISP). Use **DNS-01** instead of HTTP-01 (this post) |
| Stalls after `No renewals were attempted` | The certbot service entrypoint swallows `certonly` → add `--entrypoint certbot` |
| nginx fails to start: `options-ssl-nginx.conf missing` | `certonly` does not create this file → set `ssl_protocols` etc. **inline** in nginx |
| Host denied access to `live/...` | certbot creates it as root 0700. Run the `[ -f ]` check inside the container (`docker compose run --entrypoint test ...`) or use sudo |
| DNS-01 issued but no external access | Check whether 443 is also blocked. OK for domestic-only; for overseas, lift the country restriction or use a tunnel |
| rate limit (5/week) | Always debug failures with `--dry-run` (staging) |

---

# [09] Summary

- The common real cause of HTTPS not working on a Korean home server is often **not a port-forwarding mistake but "inbound from abroad being blocked"** (ISP or iptime country restriction).
- In that case, **DNS-01 + a DuckDNS wildcard** lets you add HTTPS without opening more ports and while keeping the country restriction (security) on.
- The subdomain approach keeps apps at root, avoiding base-path pitfalls.

:bulb: For a normal environment where overseas access is not blocked, start with the simpler **HTTP-01 (port-80 webroot)** approach in [DuckDNS + HTTPS Setup on an iptime Router](/en/Network/iptime-duckdns-https-guide/).
{: .notice--info}
