---
title: "DuckDNS + HTTPS Setup on an iptime Router"
description: "How to configure external HTTPS access using DuckDNS and Let's Encrypt on an iptime router with a Linux server backend"
excerpt: "Full walkthrough: DuckDNS domain registration, iptime port forwarding, Nginx reverse proxy, Let's Encrypt cert issuance, including iptime models that don't support external DDNS"
date: 2026-04-07
categories: Network
tags: [iptime, DuckDNS, HTTPS, "Let's Encrypt", Certbot, Nginx, Docker, port-forwarding, reverse-proxy, SSL, WOL]
ref: iptime-duckdns-https-guide
---

:bulb: How to make a Linux server behind an iptime router accessible from the outside via HTTPS using a DuckDNS domain.
Environment: iptime router + Linux server (Ubuntu) + Docker
{: .notice--info}

# [00] Overall Architecture

```
External PC
  │
  │  https://mydomain.duckdns.org:443
  ▼
DuckDNS DNS server
  │  (domain → router external IP)
  ▼
iptime router (external IP)
  │  Port forwarding (80, 443 → internal server)
  ▼
Linux server
  │
  ├── Nginx (reverse proxy + SSL termination)
  │     │
  │     ├── service_a container
  │     ├── service_b container
  │     └── service_c container
  │
  └── Certbot (Let's Encrypt cert issue/renew)
```

# [01] Why DuckDNS Instead of iptime DDNS?

The `iptime.org` domain has CAA (Certification Authority Authorization) records that block Let's Encrypt from issuing certs:

```
0 issuewild ;
0 issue ;
```

DuckDNS allows CAA, so Let's Encrypt cert issuance works. DuckDNS is also free and has been running stably since 2013.

:memo: **Note**: You can use iptime DDNS and DuckDNS together. External HTTPS → `mydomain.duckdns.org`, internal LAN → `mydomain.iptime.org`.
{: .notice--warning}

# [02] Register a DuckDNS Domain

**Location: external PC (browser)**

1. Visit [https://www.duckdns.org](https://www.duckdns.org){:target="_blank"} and log in with Google/GitHub
2. Under `add domain`, enter your desired name (e.g., `mydomain`)
3. Your router's current external IP is auto-registered
4. Copy the **token** at the top of the page and save it

# [03] DuckDNS Auto-IP-Update

Home internet typically has a dynamic IP, so the router's external IP can change. You must auto-update DuckDNS so your domain always points to the current router IP.

:warning: **iptime model differences**: Some iptime models don't support the `User DDNS` (external DDNS) menu. In that case, **the Linux server itself must handle the update**.
{: .notice--danger}

## Method A — Router-Side DDNS (Supported Models)

**Location: iptime admin page (192.168.0.1)**

Under `Advanced Settings` → `Special Features` → `DDNS`, if `User DDNS` is available:

| Field | Value |
|-------|-------|
| DDNS Service | User DDNS (or Custom) |
| URL | `https://www.duckdns.org/update?domains=mydomain&token=YOUR_TOKEN&ip=` |
| Update interval | 5 minutes |

> This is ideal — even when the server is off, the router updates the IP.

## Method B — Server-Side Update (Unsupported Models)

**Location: Linux server**

On models without external DDNS, the server must update DuckDNS itself. Set up **crontab (periodic) + systemd (immediate on boot)** together.

### B-1. Update Script

```bash
mkdir ~/duckdns

cat > ~/duckdns/duck.sh << 'EOF'
echo url="https://www.duckdns.org/update?domains=mydomain&token=YOUR_TOKEN&ip=" | curl -k -o ~/duckdns/duck.log -K -
EOF

chmod +x ~/duckdns/duck.sh
```

### B-2. Register in crontab (every 5 minutes)

```bash
crontab -e
# Add:
# */5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
```

### B-3. Update Immediately on Boot (systemd)

If you use WOL (Wake on LAN), the ISP may change the IP while the server is off. Register a systemd service that updates DuckDNS right after boot.

```bash
sudo nano /etc/systemd/system/duckdns.service
```

```ini
[Unit]
Description=DuckDNS IP update on boot
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/bin/bash /home/USERNAME/duckdns/duck.sh

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable duckdns.service
sudo systemctl start duckdns.service

# Verify
cat ~/duckdns/duck.log   # "OK" means success
```

:memo: **Method B summary**: crontab updates every 5 minutes, systemd updates immediately on boot. As long as the server is up, the DuckDNS domain always points to the latest IP.
{: .notice--info}

# [04] iptime Router Port Forwarding

**Location: iptime admin page (192.168.0.1)**

`Advanced Settings` → `NAT/Router Management` → `Port Forwarding`

Add these rules:

| Rule | External port | Internal IP | Internal port | Purpose |
|------|---------------|-------------|---------------|---------|
| certbot | 80 | server internal IP | 80 | Cert issuance |
| https | 443 | server internal IP | 443 | HTTPS service |

:memo: **Server internal IP**: check on server with `ip addr` or `hostname -I` (usually `192.168.0.xxx`)
{: .notice--info}

:memo: **Port 80**: needed for cert renewal (every 90 days). Leaving it open and redirecting to 443 in Nginx has no real security impact.
{: .notice--info}

# [05] Linux Server — Docker Compose

**Location: Linux server**

## Directory Structure

```
~/myserver/
├── docker-compose.yml
├── nginx/
│   └── nginx.conf
└── data/
    └── certbot/
        ├── conf/    ← cert storage
        └── www/     ← certbot webroot
```

## docker-compose.yml

```yaml
services:
  nginx:
    image: nginx:alpine
    container_name: nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./data/certbot/conf:/etc/letsencrypt:ro
      - ./data/certbot/www:/var/www/certbot:ro

  certbot:
    image: certbot/certbot
    container_name: certbot
    restart: unless-stopped
    volumes:
      - ./data/certbot/conf:/etc/letsencrypt
      - ./data/certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

  service_a:
    image: your-image-a
    container_name: service_a
    # No external ports needed — nginx connects internally

  service_b:
    image: your-image-b
    container_name: service_b

  service_c:
    image: your-image-c
    container_name: service_c
```

## nginx/nginx.conf

```nginx
events {}

http {
  # HTTPS redirect + certbot challenge
  server {
    listen 80;
    server_name mydomain.duckdns.org;

    location /.well-known/acme-challenge/ {
      root /var/www/certbot;
    }

    location / {
      return 301 https://$host$request_uri;
    }
  }

  # service_a
  server {
    listen 443 ssl;
    server_name mydomain.duckdns.org;

    ssl_certificate /etc/letsencrypt/live/mydomain.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mydomain.duckdns.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
      proxy_pass http://service_a:3000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }

  # service_b (subdomain)
  server {
    listen 443 ssl;
    server_name b.mydomain.duckdns.org;

    ssl_certificate /etc/letsencrypt/live/mydomain.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mydomain.duckdns.org/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
      proxy_pass http://service_b:4000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
    }
  }
}
```

# [06] First-Time Cert Issuance

**Location: Linux server**

## 6-1. Start Container with Temporary nginx.conf

Without a cert, Nginx will fail to load SSL config. First run with a temporary port-80-only config.

```nginx
# nginx/nginx.conf (temporary)
events {}
http {
  server {
    listen 80;
    server_name mydomain.duckdns.org;

    location /.well-known/acme-challenge/ {
      root /var/www/certbot;
    }

    location / {
      return 200 'ok';
    }
  }
}
```

```bash
cd ~/myserver
docker compose up -d nginx
```

## 6-2. Issue Cert

```bash
docker compose run --rm certbot certonly \
  --webroot \
  -w /var/www/certbot \
  -d mydomain.duckdns.org \
  --email your@email.com \
  --agree-tos \
  --no-eff-email
```

On success, cert files appear under `data/certbot/conf/live/mydomain.duckdns.org/`.

## 6-3. Restore Final nginx.conf and Restart

After restoring the final nginx.conf from STEP 05:

```bash
docker compose down
docker compose up -d
```

# [07] Verify Auto-Renewal

**Location: Linux server**

The certbot container in docker-compose.yml attempts renewal every 12 hours. Manual test:

```bash
docker compose run --rm certbot renew --dry-run
```

# [08] Access Test

```bash
# From external PC
curl -I https://mydomain.duckdns.org

# Or in a browser
# Visit https://mydomain.duckdns.org → verify the padlock icon
```

# [09] Troubleshooting

## Nginx Won't Start

```bash
docker logs nginx
# Check for SSL cert path errors
# Before cert issuance, run with the temporary config first
```

## Certbot Issuance Fails

- Check router port-80 forwarding is set
- Verify `http://mydomain.duckdns.org/.well-known/acme-challenge/test` is reachable from outside
- Confirm DuckDNS domain currently points to your router's IP

## DuckDNS Points to Wrong IP

```bash
# Check current router external IP
curl ifconfig.me

# Manually update DuckDNS
curl "https://www.duckdns.org/update?domains=mydomain&token=YOUR_TOKEN&ip=$(curl -s ifconfig.me)"
```

## Can't Reach DuckDNS After WOL (Method B)

```bash
# Check systemd service status
sudo systemctl status duckdns.service

# Manual update
~/duckdns/duck.sh
cat ~/duckdns/duck.log   # confirm OK

# Re-register if needed
sudo systemctl daemon-reload
sudo systemctl enable duckdns.service
```

# [10] Summary

| Step | Location | Task |
|------|----------|------|
| STEP 02 | External PC browser | DuckDNS domain registration |
| STEP 03 | Router or server | DuckDNS auto-IP-update (Method A: router / Method B: server) |
| STEP 04 | Router admin page | Add port 80, 443 forwarding |
| STEP 05 | Linux server | Docker Compose + Nginx setup |
| STEP 06 | Linux server | Let's Encrypt cert issuance |
| STEP 07 | Linux server | Confirm auto-renewal works |
