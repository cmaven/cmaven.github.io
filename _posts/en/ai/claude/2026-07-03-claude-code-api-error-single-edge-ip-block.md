---
title: "The Real Cause of Claude Code's 'API error · Retrying' — Tracking Down a Single Blocked Edge IP"
description: "When Claude Code kept showing API error · Retrying, a layer-by-layer elimination diagnosis (DNS → MTU → conntrack → tcpdump) revealed that just one edge IP of api.anthropic.com was blocked by the corporate firewall. How it was found and bypassed via /etc/hosts, with a reusable diagnostic checklist and automation scripts"
excerpt: "When Claude Code keeps showing API error · Retrying, it's tempting to blame the client. But peeling back the layers revealed the culprit: a single destination IP, surgically blocked by the firewall"
date: 2026-07-03
categories: Claude
tags: [Claude Code, API error, Retrying, network-diagnosis, tcpdump, conntrack, MTU, DNS, etc-hosts, SNI, firewall, curl, api.anthropic.com]
ref: claude-code-api-error-single-edge-ip-block
---

:bulb: Claude Code kept repeating `API error · Retrying in 0s · attempt 1/10` and slowed to a crawl. My first suspect was a client bug, but working through the layers — DNS → MTU → conntrack → path → destination policy — the culprit turned out to be **a single destination IP** that the corporate firewall had surgically blocked. This post walks through how each hypothesis was formed and broken, plus a checklist for narrowing down the same symptom quickly.
{: .notice--info}

The conclusion up front:

- **Symptom**: Claude Code repeats `API error · Retrying` and responses get noticeably slow
- **Real cause**: Of the multiple edge IPs behind `api.anthropic.com`, **just one** was blocked/unstable at the corporate firewall — and the internal DNS happened to return only that IP
- **Fix**: Pin a healthy IP from the same range in `/etc/hosts` to route around the blocked front door
- **Lesson**: "Only this one service is flaky" is almost always a sign of a **per-destination policy**. And one bad hardcoded test IP can send your diagnosis down the wrong path for hours

---

# [01] Symptom — It Works After Retries, But Painfully Slowly

One day, Claude Code — which had been working fine — started repeating this message:

```
✻ API error · Retrying in 0s · attempt 1/10
```

Responses got noticeably slower, though they eventually succeeded after retries. Environment: Ubuntu 22.04, two nodes. Interestingly, everything was fine until last week, and other environments on the same network seemed unaffected. "Is it a client problem?" I wondered — but that hypothesis fell apart quickly.

---

# [02] Diagnosis — Form Hypotheses, Break Them

## 2-1. First, Suspect the Connection Itself

I hit the API endpoint directly with `curl`.

```bash
curl -I https://api.anthropic.com
# At first: SSL_connect: connection reset by peer
# Moments later: HTTP/2 404  <- normal (the root path has no page, so 404 is expected)
```

A `404` means **both the connection and TLS succeeded** (the root path simply has no content). But hitting it repeatedly gave inconsistent results.

```bash
for i in $(seq 1 10); do
  curl -s -o /dev/null -w "%{http_code} %{time_total}s\n" https://api.anthropic.com
done
# 000 94s  (timeout)
# 404 63s
# 000 94s
# ...successes and failures intermixed
```

The consistent `94s` timeout value and repeated `000` (connection failure) point to **intermittent connection drops**. Since `curl` failed the same way on the same machine, Claude Code's code was ruled out. The problem was in a lower layer.

## 2-2. DNS / IPv6 Hypothesis → Partially Wrong

The resolver went through `systemd-resolved` (stub `127.0.0.53`), and `api.anthropic.com` returned both IPv4 and IPv6. For a while I suspected "IPv6 fallback delay," but forcing IPv4 (`curl -4`) — and even **bypassing DNS entirely by pinning the IP (`--resolve`)** — still failed.

```bash
curl -4 --resolve api.anthropic.com:443:160.79.104.10 -o /dev/null -s \
  -w "%{http_code}\n" https://api.anthropic.com
# Still intermittent timeouts (000)
```

DNS is not the culprit. IPv6 had no connectivity at all, so the fallback hypothesis was discarded too.

## 2-3. MTU / conntrack Hypotheses → Both Innocent

- **MTU black hole?** Large packets (`ping -M do -s 1472`) passed without loss → MTU fine
- **conntrack exhaustion?** The table was nearly empty (`nf_conntrack_count` under 1% of the limit), and the `insert_failed`/`drop` counters were all zero → conntrack innocent

```bash
sysctl net.netfilter.nf_conntrack_count net.netfilter.nf_conntrack_max
conntrack -S | grep -E "insert_failed|drop"   # all zero
```

## 2-4. The Decisive Evidence — SYN Goes Out, SYN-ACK Never Comes Back

I caught the failure in the act with `tcpdump`.

```bash
sudo tcpdump -ni any host 160.79.104.10 and tcp port 443
# Failure case:
#  Out ... > 160.79.104.10.443: Flags [S]      <- SYN sent
#  Out ... > 160.79.104.10.443: Flags [S]      <- retransmitted 1s later
#  (no SYN-ACK response -> connect timeout)
# Success case:
#  Out ... [S]  ->  In ... [S.]  ->  normal handshake
```

Our SYN leaves the NIC just fine, but the response (SYN-ACK) never returns. So the drop point is **on the path or a device outside the client**. Quantified:

```
SYN sent: 48   ->   SYN-ACK received: 37   (~23% loss)
```

The OS was irrelevant too. Running `Test-NetConnection` 30 times from a Windows box on the same network failed at a similar rate (~13%). The impression that "Windows works fine" came from comparing against a measurement artifact and an environment that took a different path.

## 2-5. The Trap — A Bad Hardcoded Test IP

Comparing multiple destinations at once, I hit major confusion. I had pinned an arbitrary google IP with `--resolve`, but it wasn't a valid IP on that network — so **google appeared to fail 100%** of the time. I nearly reached the wrong conclusion of "everything is blocked."

:warning: When you hardcode an IP, first question whether it's actually valid. Re-measuring with the IPs that DNS returned showed google, amazon, and github at 100% success. One bad control sample can drag the whole diagnosis in the wrong direction.
{: .notice--warning}

## 2-6. The Real Cause — Per-Destination-IP Blocking

Running a script that measures multiple destinations **simultaneously in the same round** (Appendix A) made the picture crisp. Using the healthy IPs that DNS returns:

| Destination | Result |
|-------------|--------|
| google / amazon / github | 100% success |
| `api.anthropic.com` (`160.79.104.10`) | nearly 100% failure |

And the clincher: **the neighboring IPs in the same range were perfectly fine.**

```bash
for ip in 160.79.104.10 160.79.104.11 160.79.104.12 160.79.104.13; do
  # .10 -> 9/10 failed
  # .11 -> 10/10 success
  # .12 -> 10/10 success
  # .13 -> 10/10 success
done
```

Only `160.79.104.10` was blocked; `.11` through `.13` worked flawlessly. A random network fault could never split 0%/100% this cleanly along IP boundaries. This is a strong signal that **a firewall/IPS is blocking one specific destination IP**.

DNS made it worse. Both internal and external DNS returned **only the blocked `.10`** for `api.anthropic.com`. So the client always headed for the blocked front door, and the failure rate fluctuated over time because `.10` sat right on the "partially blocked/unstable" boundary.

:memo: **Why are there multiple IPs?** Behind a domain like `api.anthropic.com` sit multiple edge servers, each with its own IP — multiple "front doors" into the same service. Normally DNS picks one for you. Here, that pick was stuck on the one blocked door.
{: .notice--warning}

---

# [03] Fix — Pin a Healthy Edge IP in /etc/hosts

## 3-1. Why Changing the IP Is Safe (SNI)

HTTPS identifies the destination **by domain name (SNI), not by IP**. Whichever edge IP you connect to, the connection carries "I'm looking for `api.anthropic.com`," and the server responds with the certificate and content for that name. So connecting via `.11` instead of `.10` is just a different door into the same building — certificate validation is domain-based, so it passes unchanged.

## 3-2. Pin a Live IP in /etc/hosts

For name→IP resolution, `/etc/hosts` is consulted before DNS. Writing a healthy IP there skips the DNS query and goes straight to that IP. It applies only to this one server, without touching internal DNS or firewall config.

```bash
echo "160.79.104.11 api.anthropic.com" | sudo tee -a /etc/hosts
sudo resolvectl flush-caches
```

## 3-3. Automating Apply/Rollback

Since `/etc/hosts` is a sensitive file, I handled it with a script that does automatic backup before applying, duplicate prevention, pre-apply connectivity validation, and one-click rollback (full code in Appendix B).

- `apply [IP]` — tests the given IP 5 times first and pins it in hosts only if alive (after backup)
- `rollback` — removes exactly the entry we added and flushes caches
- `status` — shows the currently resolved IP and connection results
- `probe` — auto-scans `.11`–`.20` for live alternative IPs

Our line carries an identifying marker, so repeated runs don't stack lines, and rollback removes only that line (other hosts entries are preserved).

## 3-4. Caveat — Existing Sessions Must Be Restarted

`/etc/hosts` is consulted **only once, when a new connection starts**. Connections already established to the blocked IP, or a program's internal DNS cache, can linger — so flush caches **and restart the program** to make sure it reconnects via the new IP.

---

# [04] Result — Verified in Four Steps

After pinning `.11`, I verified in four steps.

```bash
# 1) hosts entry
grep anthropic /etc/hosts
#  160.79.104.11 api.anthropic.com

# 2) name resolution
getent ahostsv4 api.anthropic.com
#  160.79.104.11  STREAM api.anthropic.com

# 3) actual connection (check remote_ip)
curl -4 -o /dev/null -s -w "%{remote_ip} -> %{http_code} (%{time_total}s)\n" https://api.anthropic.com
#  160.79.104.11 -> 404 (0.06s)   <- connects quickly via .11

# 4) live sessions — the most important
ss -tnp | grep 160.79.104
#  ESTAB ... 160.79.104.11:443  users:(("claude",pid=...))   (many connections, all .11)
#  -> not a single .10
```

Step 4 was decisive: every live Claude Code connection was established to `.11`, and `.10` had vanished completely. We had fully escaped the blocked front door. The `API error · Retrying` messages disappeared and response times returned to normal.

## Remaining Work

- **Apply to other nodes** — the second node on the same network was handled the same way
- **Check other anthropic domains** — if an auxiliary domain used by the client resolves to a blocked IP, the same symptom can recur; check the same way if anything looks off
- **The root fix belongs to the admin** — the `/etc/hosts` workaround is temporary. Edge IPs can change, so getting the firewall to unblock that IP (or allow the domain's range) frees you from maintaining hosts entries

---

# [05] Diagnostic Checklist (Reusable)

The order for quickly narrowing down a similar "intermittent API connection failure":

1. **Client vs system** — does `curl` reproduce it against the same destination? If so, the client is innocent
2. **DNS** — does it still fail with the IP pinned directly (`--resolve`)? If so, DNS is innocent
3. **MTU** — do large packets (`ping -M do -s 1472`) pass? If so, MTU is innocent
4. **conntrack** — is `nf_conntrack_count` near the limit? Are `insert_failed/drop` zero?
5. **Path** — does `tcpdump` show SYNs going out with no SYN-ACK returning? Then it's an external drop
6. **Per-destination** — measure multiple destinations **simultaneously**. If only specific IPs differ, it's a destination policy
7. **Neighboring IPs in the range** — do adjacent IPs (`.11`, `.12`) work? If so, individual-IP blocking is confirmed

:bulb: And above all: always question whether a hardcoded test IP is valid. One bad control sample can drag the entire diagnosis in the wrong direction.
{: .notice--info}

---

# Appendix A. Multi-Destination Simultaneous Diagnostic Script (conn_check.sh)

Measures multiple destinations simultaneously in the same round, to tell over time whether blocked/unblocked windows are common to all destinations (= full path/gateway issue) or specific to one destination. Running it 2–3 times makes the average failure rate and any periodicity clear.

```bash
#!/usr/bin/env bash
# conn_check.sh
# Simultaneously measures new TCP 443 connection success/failure to multiple
# destinations in the same round, to distinguish "intermittent full blocking"
# from "blocking of a specific destination" over time.
# Usage: ./conn_check.sh   |   ROUNDS=100 ./conn_check.sh   |   TIMEOUT=2 ./conn_check.sh
set -u

ROUNDS="${ROUNDS:-50}"        # number of measurement rounds
TIMEOUT="${TIMEOUT:-3}"       # connect timeout (seconds)
SLEEP="${SLEEP:-0.3}"         # interval between rounds (seconds)

# Targets: "name|host-header|IP". Pin IPs directly to remove the DNS variable
# (measures the pure TCP/TLS path only).
# NOTE: verify that each pinned IP is actually valid in YOUR environment.
#   A wrong IP makes that destination look 100% failed and poisons the diagnosis.
#   To be safe, measure via the bare domain (no --resolve), or check the real IP
#   first with: getent ahostsv4 <domain>
TARGETS=(
  "anthropic|api.anthropic.com|160.79.104.10"
  "google|www.google.com|142.250.207.110"
  "cloudflare|one.one.one.one|1.1.1.1"
  "github|github.com|140.82.112.3"
  "amazon|www.amazon.com|54.239.28.85"
)

TS="$(date +%Y%m%d_%H%M%S)"
CSV="./conn_check_${TS}.csv"

NAMES=()
for t in "${TARGETS[@]}"; do NAMES+=("${t%%|*}"); done

declare -A FAILS TOTAL
for n in "${NAMES[@]}"; do FAILS["$n"]=0; TOTAL["$n"]=0; done

{ printf "timestamp,round"
  for n in "${NAMES[@]}"; do printf ",%s_code,%s_time" "$n" "$n"; done
  printf "\n"; } > "$CSV"

echo "Starting: ROUNDS=$ROUNDS TIMEOUT=${TIMEOUT}s  log=$CSV"
printf "%-10s %-3s" "time" "#"
for n in "${NAMES[@]}"; do printf " %-12s" "$n"; done
printf "\n"

probe() {  # returns: "<http_code> <time_total>" (code=000 on failure)
  local host="$1" ip="$2"
  curl -4 -o /dev/null -s -w "%{http_code} %{time_total}" \
    --connect-timeout "$TIMEOUT" --resolve "${host}:443:${ip}" \
    "https://${host}" 2>/dev/null || echo "000 0"
}

for ((r=1; r<=ROUNDS; r++)); do
  now="$(date +%H:%M:%S)"; printf "%-10s %-3d" "$now" "$r"; csv_line="$now,$r"
  for t in "${TARGETS[@]}"; do
    name="${t%%|*}"; rest="${t#*|}"; host="${rest%%|*}"; ip="${rest##*|}"
    read -r code time <<< "$(probe "$host" "$ip")"
    TOTAL["$name"]=$(( TOTAL["$name"] + 1 ))
    if [[ "$code" == "000" ]]; then
      FAILS["$name"]=$(( FAILS["$name"] + 1 )); printf " %-12s" "FAIL"
    else
      printf " %-12s" "ok ${time}s"
    fi
    csv_line+=",${code},${time}"
  done
  printf "\n"; echo "$csv_line" >> "$CSV"; sleep "$SLEEP"
done

echo ""; echo "================== Summary (failure rate) =================="
for n in "${NAMES[@]}"; do
  tot="${TOTAL[$n]}"; f="${FAILS[$n]}"
  (( tot > 0 )) && rate=$(( f * 100 / tot )) || rate=0
  printf "  %-12s failed %2d/%-2d  (%d%%)\n" "$n" "$f" "$tot" "$rate"
done
echo "============================================================="
echo "CSV log: $CSV"
```

**Interpretation guide**

- All destinations FAIL/OK together in the same rounds → intermittent full blocking (path/gateway)
- FAILs stand out for one specific destination → destination-specific blocking
- FAILs come in clusters → periodic blocking (suspect session/NAT exhaustion)

---

# Appendix B. Apply/Rollback Script (anthropic_ip_fix.sh)

Since `/etc/hosts` is a sensitive file, the script includes automatic backup before applying, duplicate prevention, pre-apply connectivity validation, and one-click rollback. Our line carries an identifying marker so repeated runs don't stack lines, and rollback removes exactly that line (other hosts entries are preserved).

```bash
#!/usr/bin/env bash
# anthropic_ip_fix.sh
# Pins (apply) an /etc/hosts entry so api.anthropic.com connects via a live IP
# instead of a blocked edge IP, or restores it (rollback). Backs up before
# applying and verifies afterwards.
# Usage:
#   sudo ./anthropic_ip_fix.sh apply              (use default IP)
#   sudo ./anthropic_ip_fix.sh apply 160.79.104.12 (specify IP)
#   sudo ./anthropic_ip_fix.sh rollback
#   sudo ./anthropic_ip_fix.sh status
#   sudo ./anthropic_ip_fix.sh probe              (auto-scan alternative IPs)
set -euo pipefail

HOSTS="/etc/hosts"
DOMAIN="api.anthropic.com"
DEFAULT_IP="160.79.104.11"                   # replace with a live IP for your environment
MARK="# added-by-anthropic_ip_fix"
BACKUP_DIR="/var/backups/anthropic_ip_fix"

need_root() {
  [[ "$(id -u)" -eq 0 ]] || { echo "ERROR: root required. 'sudo $0 ...'" >&2; exit 1; }
}
flush_dns() { command -v resolvectl >/dev/null 2>&1 && resolvectl flush-caches 2>/dev/null || true; }

show_status() {
  echo "----- Current status -----"
  echo -n "Resolved IP : "; getent ahostsv4 "$DOMAIN" | awk '{print $1}' | sort -u | tr '\n' ' '; echo
  echo -n "Connection results (5x): "
  for i in $(seq 1 5); do
    curl -4 -o /dev/null -s -w "%{http_code} " --connect-timeout 3 "https://$DOMAIN" || echo -n "000 "
  done; echo
  echo -n "Entry in $HOSTS: "
  grep -q "$MARK" "$HOSTS" && grep "$MARK" "$HOSTS" || echo "(none - using DNS default)"
  echo "--------------------------"
}

probe_ips() {
  echo "Scanning alternative IP candidates (160.79.104.11 ~ .20):"
  local best=""
  for last in $(seq 11 20); do
    local ip="160.79.104.${last}" ok=0
    for i in $(seq 1 5); do
      code=$(curl -4 -o /dev/null -s -w "%{http_code}" --connect-timeout 3 \
              --resolve "${DOMAIN}:443:${ip}" "https://${DOMAIN}" 2>/dev/null || echo 000)
      [[ "$code" != "000" ]] && ok=$((ok+1))
    done
    printf "  %-16s %d/5 succeeded\n" "$ip" "$ok"
    [[ -z "$best" && "$ok" -eq 5 ]] && best="$ip"
  done
  [[ -n "$best" ]] && echo ">> Recommended IP: $best"
}

apply_fix() {
  need_root; local ip="${1:-$DEFAULT_IP}"
  [[ "$ip" =~ ^[0-9]{1,3}(\.[0-9]{1,3}){3}$ ]] || { echo "ERROR: invalid IP: $ip" >&2; exit 1; }

  echo "Pre-check: testing connectivity to $ip..."
  local pre_ok=0
  for i in $(seq 1 5); do
    code=$(curl -4 -o /dev/null -s -w "%{http_code}" --connect-timeout 3 \
            --resolve "${DOMAIN}:443:${ip}" "https://${DOMAIN}" 2>/dev/null || echo 000)
    [[ "$code" != "000" ]] && pre_ok=$((pre_ok+1))
  done
  echo "  $ip : $pre_ok/5 succeeded"
  (( pre_ok >= 3 )) || { echo "ERROR: $ip unstable. Run 'probe' to find a live IP first." >&2; exit 1; }

  mkdir -p "$BACKUP_DIR"
  local backup="${BACKUP_DIR}/hosts.$(date +%Y%m%d_%H%M%S)"
  cp -a "$HOSTS" "$backup"; echo "Backup: $backup"

  sed -i "/$MARK/d" "$HOSTS"                      # remove our previous entry (dedup)
  echo "${ip} ${DOMAIN} ${MARK}" >> "$HOSTS"; echo "Added: ${ip} ${DOMAIN}"
  flush_dns; echo; show_status
}

rollback_fix() {
  need_root
  if ! grep -q "$MARK" "$HOSTS"; then
    echo "Nothing to roll back (already at default)"; flush_dns; show_status; return 0
  fi
  mkdir -p "$BACKUP_DIR"
  cp -a "$HOSTS" "${BACKUP_DIR}/hosts.before_rollback.$(date +%Y%m%d_%H%M%S)"
  sed -i "/$MARK/d" "$HOSTS"
  echo "Removed: pinned entry for ${DOMAIN}"; flush_dns; echo; show_status
}

case "${1:-}" in
  apply)    shift; apply_fix "${1:-}";;
  rollback) shift; rollback_fix;;
  status)   show_status;;
  probe)    probe_ips;;
  *)        echo "usage: sudo $0 {apply [IP]|rollback|status|probe}";;
esac
```

**Recommended order**: `status` → `probe` → `apply` → (test with Claude Code) → `rollback` if anything goes wrong. After applying, flush caches and restart any running client so it reconnects via the new IP.

---

*Environment: Ubuntu 22.04 / Claude Code. Internal IPs, hostnames, and other identifying details in this post have been generalized; `160.79.104.x` is an example of publicly observable edge IPs. Blocking policies and IPs vary by environment and point in time.*
