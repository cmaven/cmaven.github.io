---
title: "Self-Hosting a Django Web App: From Development to Deployment"
description: "End-to-end guide to running a Django project in production with Gunicorn + systemd, exposed to the public internet via DDNS and port forwarding"
excerpt: "A Django home-server deployment guide covering Gunicorn instead of runserver, systemd auto-start, and DDNS/port-forwarding setup"
date: 2026-03-25
categories: Python
tags: [Django, Gunicorn, Nginx, systemd, DDNS, port-forwarding, home-server, deployment, ufw, firewall, WSGI]
ref: django-home-server-deployment
---

:bulb: This post walks through the full process of taking a finished Django project and making it accessible from the public internet, served from a PC you already own.
{: .notice--info}

# [01] Overall Architecture: Development vs. Production

Development and production environments are fundamentally different.

<pre class="mermaid">
graph LR
    subgraph Development
        DEV_USER[Developer Browser] --> DEV_SERVER[runserver :8000]
        DEV_SERVER --> DEV_DB[(SQLite)]
    end

    subgraph Production
        EXT_USER[External User] --> ROUTER[Router<br/>Port Forwarding]
        ROUTER --> GUNICORN[Gunicorn<br/>WSGI Server]
        GUNICORN --> DJANGO[Django App]
        DJANGO --> PROD_DB[(SQLite)]
    end

    style DEV_SERVER fill:#ffcccc
    style GUNICORN fill:#ccffcc
</pre>

| Item | Development | Production |
|------|------|------|
| Server | `runserver` (single thread) | Gunicorn (multi-worker) |
| DEBUG | True (exposes error detail) | False (hides errors) |
| SECRET_KEY | Hardcoding OK | Must come from env var |
| Access scope | localhost only | Public internet |
| Process management | Manual | systemd (auto-restart) |

---

# [02] Introducing the Key Tools

Here are the main tools used in this post.

## 2-1. Gunicorn (Green Unicorn)

A **WSGI HTTP server** for Python. Used to run Python web frameworks like Django or Flask in production.

- **WSGI** (Web Server Gateway Interface): the standard interface between a Python web app and a web server
- Handles concurrent requests with **multiple workers** (runserver is single-threaded)
- Automatically respawns workers if a process dies

```shell
# Install
pip install gunicorn

# Run (3 workers, port 2929)
gunicorn myproject.wsgi:application --bind 0.0.0.0:2929 --workers 3
```

## 2-2. Nginx

A **high-performance web server and reverse proxy**. Handles static file serving, SSL termination, load balancing, and more.

- Sits in front of Gunicorn as a **reverse proxy**
- Serves static files (CSS, JS, images) directly without going through Gunicorn, improving performance
- Provides security features such as SSL (HTTPS) certificates and basic DDoS protection

```
External request -> Nginx (serves static files directly, forwards dynamic requests to Gunicorn) -> Gunicorn -> Django
```

:bulb: For small services, Gunicorn alone is enough — no Nginx needed. This post focuses on the Gunicorn-only setup and covers the Nginx extension in [10].
{: .notice--info}

## 2-3. systemd

Linux's **system and service manager**. Handles service (daemon) registration, auto-start, and process supervision.

- Automatically starts the service when the PC boots
- Automatically restarts the process if it terminates abnormally
- Service logs are accessible via `journalctl`

```shell
# Start / stop / restart a service
sudo systemctl start myservice
sudo systemctl stop myservice
sudo systemctl restart myservice

# Enable on boot
sudo systemctl enable myservice

# Tail logs
sudo journalctl -u myservice -f
```

## 2-4. ufw (Uncomplicated Firewall)

Ubuntu's **firewall management tool**. A simple front-end for iptables.

```shell
# Enable the firewall
sudo ufw enable

# Allow a specific port
sudo ufw allow 2929/tcp

# View current rules
sudo ufw status
```

---

# [03] Why You Shouldn't Serve with runserver

Django's `runserver` is for development only.

<pre class="mermaid">
graph TD
    A[Limits of runserver] --> B[Single thread<br/>no concurrent access]
    A --> C[No security hardening<br/>assumes DEBUG mode]
    A --> D[Inefficient static<br/>file serving]
    A --> E[No auto-recovery<br/>on failure]

    F[Advantages of Gunicorn] --> G[Multi-worker<br/>handles concurrency]
    F --> H[WSGI standard<br/>production-tuned]
    F --> I[Process management<br/>auto-respawn workers]
    F --> J[systemd integration<br/>auto-start on boot]
</pre>

**Bottom line**: `runserver` is a "demo", Gunicorn is "the real thing".

---

# [04] Network Topology for External Access

To access your home PC from outside, you need **DDNS + port forwarding**.

<pre class="mermaid">
sequenceDiagram
    participant User as External User
    participant DNS as DDNS Server<br/>(iptime, etc.)
    participant Router as Router
    participant PC as Home PC

    User->>DNS: Request xxx.xxx.com
    DNS-->>User: Return router public IP
    User->>Router: Connect to public-IP:2929
    Router->>PC: Forward to internal-IP:2929<br/>(port forwarding)
    PC-->>Router: Django response
    Router-->>User: Forward response
</pre>

## 4-1. What is DDNS?

Home internet connections have IPs that change frequently (dynamic IPs). DDNS (Dynamic DNS) automatically maps the changing IP to a fixed domain name.

```
Router IP: 221.148.xxx.xxx (changes often)
    | DDNS keeps it in sync
Domain: xxx.xxx.com (fixed)
```

Most iptime routers have DDNS built in and offer it for free.

## 4-2. What is port forwarding?

There are usually multiple devices behind your router. Port forwarding is the rule that decides which internal device a particular incoming port should be sent to.

<pre class="mermaid">
graph LR
    EXT[Public Internet] -->|:2929| ROUTER[Router]
    EXT -->|:3131| ROUTER

    ROUTER -->|:2929| PC1[PC - engwrite]
    ROUTER -->|:3131| PC2[PC - other service]

    style ROUTER fill:#ffffcc
</pre>

When running **multiple services on a single PC**, distinguish them by port number:
- `xxx.xxx.com:2929` -> engwrite (Django)
- `xxx.xxx.com:3131` -> another service

---

# [05] Components of the Production Setup

<pre class="mermaid">
graph TB
    subgraph "Production Stack"
        direction TB
        A[systemd] -->|process management| B[Gunicorn]
        B -->|WSGI protocol| C[Django]
        C -->|ORM| D[(SQLite DB)]
        E[.env environment file] -.->|SECRET_KEY<br/>DEBUG<br/>ALLOWED_HOSTS| C
        F[ufw firewall] -.->|allow port 2929| B
    end
</pre>

| Component | Role | Without it? |
|-----------|------|---------|
| **Gunicorn** | Python WSGI server, forwards requests to Django | No concurrency, slow |
| **systemd** | Process supervision, auto-start on boot | Manual startup after every reboot |
| **Env vars** | Manage secrets and settings outside the code | Leaked secrets, hardcoded config |
| **Firewall** | Allows only permitted ports from outside | Security exposure |

---

# [06] Django Settings: Switching from Development to Production

Django settings should change for production.

<pre class="mermaid">
graph LR
    subgraph "Development mode"
        D1[DEBUG = True]
        D2[SECRET_KEY = hardcoded]
        D3["ALLOWED_HOSTS = ['*']"]
    end

    subgraph "Production mode"
        P1[DEBUG = False]
        P2[SECRET_KEY = env var]
        P3["ALLOWED_HOSTS = ['xxx.xxx.com']"]
    end

    D1 -->|change| P1
    D2 -->|change| P2
    D3 -->|change| P3

    style D1 fill:#ffcccc
    style D2 fill:#ffcccc
    style D3 fill:#ffcccc
    style P1 fill:#ccffcc
    style P2 fill:#ccffcc
    style P3 fill:#ccffcc
</pre>

## 6-1. DEBUG = False

```
Development: errors expose code, variables, and SQL queries
Production:  a single "Server Error (500)" line
```

## 6-2. SECRET_KEY

```
Development: any value is fine
Production:  50+ random characters, never expose
             -> Otherwise session forgery, CSRF bypass, and other critical exploits become possible
```

## 6-3. ALLOWED_HOSTS

```
Development: ['*'] (allow all hosts)
Production:  ['xxx.xxx.com', 'localhost'] (explicit domains only)
             -> Prevents Host Header attacks
```

---

# [07] Deployment Flow

<pre class="mermaid">
flowchart TD
    START([Start Deployment]) --> VENV[1. Create virtual env<br/>python3 -m venv venv]
    VENV --> DEPS[2. Install dependencies<br/>pip install -r requirements.txt<br/>pip install gunicorn]
    DEPS --> ENV[3. Configure env vars<br/>write .env<br/>generate SECRET_KEY]
    ENV --> MIGRATE[4. DB migration<br/>python manage.py migrate]
    MIGRATE --> SYSTEMD[5. Register systemd service<br/>configure auto-start]
    SYSTEMD --> FIREWALL[6. Open firewall port<br/>ufw allow 2929/tcp]
    FIREWALL --> ROUTER[7. Configure router<br/>port forwarding + DDNS]
    ROUTER --> TEST[8. External access test<br/>xxx.xxx.com:2929]
    TEST --> DONE([Deployment Done])

    style START fill:#e6f3ff
    style DONE fill:#e6ffe6
</pre>

---

# [08] systemd: Keep the Service "Always On"

systemd is Linux's process manager. Register a service file and you get:

- **Auto-start on boot** — Django server starts when the PC boots
- **Auto-restart on crash** — process restarts 5 seconds after termination
- **Structured log management**

<pre class="mermaid">
stateDiagram-v2
    [*] --> Start: PC boot / systemctl start
    Start --> Running: Gunicorn process spawned
    Running --> Running: Handling requests
    Running --> CrashStop: Process crash
    CrashStop --> Start: Auto-restart after 5s
    Running --> CleanStop: systemctl stop
    CleanStop --> [*]
</pre>

## 8-1. Service file structure

```ini
[Unit]
Description=Service description
After=network.target          # Start after the network is ready

[Service]
User=kcloud                   # Run-as user
WorkingDirectory=/path/to/app # Project path
EnvironmentFile=/path/.env    # Environment file
ExecStart=/path/gunicorn ...  # Start command
Restart=always                # Always restart
RestartSec=5                  # Restart after 5 seconds

[Install]
WantedBy=multi-user.target    # Auto-start on boot
```

---

# [09] Running Multiple Services on a Single PC

You can run several web services on one machine.

<pre class="mermaid">
graph TB
    EXT[Public Internet]

    EXT -->|:2929| S1
    EXT -->|:3131| S2
    EXT -->|:4040| S3

    subgraph "Home PC (single machine)"
        S1[engwrite<br/>Gunicorn :2929<br/>engwrite.service]
        S2[Service B<br/>Node.js :3131<br/>service-b.service]
        S3[Service C<br/>Flask :4040<br/>service-c.service]
    end

    style S1 fill:#ddeeff
    style S2 fill:#ddfedd
    style S3 fill:#ffddee
</pre>

**Rules:**
- Each service uses a **different port**
- Each service gets its **own systemd service file**
- Add a **separate port-forwarding rule per port** on the router

---

# [10] Security Checklist

:warning: Items you must verify before exposing a home server to the internet.
{: .notice--warning}

<pre class="mermaid">
graph TD
    SEC[Security Checklist] --> A[DEBUG = False<br/>hide error details]
    SEC --> B[SECRET_KEY<br/>via env var]
    SEC --> C[ALLOWED_HOSTS<br/>explicit domain]
    SEC --> D[Firewall<br/>only required ports open]
    SEC --> E[Password policy<br/>min length + block common passwords]
    SEC --> F[CSRF protection<br/>token check on form submit]

    A --> PASS{Pass?}
    B --> PASS
    C --> PASS
    D --> PASS
    E --> PASS
    F --> PASS

    PASS -->|All Yes| SAFE[Ready to deploy]
    PASS -->|Any No| DANGER[Risky - fix required]

    style SAFE fill:#ccffcc
    style DANGER fill:#ffcccc
</pre>

---

# [11] Optional Extension: Nginx Reverse Proxy

For a more robust setup, you can add Nginx in front of Gunicorn.

<pre class="mermaid">
graph LR
    USER[External User] --> NGINX[Nginx<br/>:2929]
    NGINX -->|proxy| GUNICORN[Gunicorn<br/>:8000 internal]
    GUNICORN --> DJANGO[Django]

    style NGINX fill:#ccffcc
    style GUNICORN fill:#ffffcc
</pre>

| Gunicorn only | Nginx + Gunicorn |
|------------|-----------------|
| Simpler setup | Efficient static file serving |
| Good for small scale | Can configure SSL (HTTPS) |
| Directly exposed externally | Basic DDoS mitigation |

:bulb: At this project's scale, Gunicorn alone is enough. Add Nginx later, once you have more users or need HTTPS.
{: .notice--info}

---

# [12] Full Architecture Summary

<pre class="mermaid">
graph TB
    subgraph "Internet"
        USER[External User<br/>Browser]
    end

    subgraph "Router"
        DDNS[DDNS: xxx.xxx.com]
        FWD[Port forwarding<br/>:2929 -> internal-IP:2929]
    end

    subgraph "Home PC (Ubuntu)"
        FW[ufw firewall<br/>allow 2929/tcp]
        SD[systemd<br/>process manager]
        GU[Gunicorn<br/>WSGI server<br/>3 workers]
        DJ[Django<br/>engwrite app]
        DB[(SQLite<br/>db.sqlite3)]
        ENV[.env<br/>SECRET_KEY<br/>settings]
    end

    USER -->|xxx.xxx.com:2929| DDNS
    DDNS --> FWD
    FWD --> FW
    FW --> SD
    SD -->|manages| GU
    GU -->|WSGI| DJ
    DJ --> DB
    ENV -.-> DJ

    style USER fill:#e6f3ff
    style GU fill:#ccffcc
    style DJ fill:#ddeeff
    style DB fill:#ffffcc
</pre>

Once you understand this structure, you can deploy any web framework (Flask, FastAPI, Express, etc.) to a home server using the same pattern.
