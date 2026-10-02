---
layout: post
title: "How DNS works: from domain to IP with dig"
subtitle: "A step‑by‑step guide that shows how a domain name becomes an IP address, using dig to watch every DNS hop."
date: 2026-10-02
categories: []
tags: ["Networking", "Linux"]
thumbnail-img: /assets/images/banners/how-dns-works-from-domain-to-ip-with-dig-banner.png
share-img: /assets/images/banners/how-dns-works-from-domain-to-ip-with-dig-banner.png
author: Asahluma Tyika
---
## How DNS works: from domain to IP with **dig**
**Tags:** Networking, Linux  

### Intro – what you’ll learn and who this is for
Domain Name System (DNS) is the phone‑book of the internet. When you type `example.com` into a browser, a series of hidden look‑ups turn that human‑readable name into a numeric IP address that computers can route.  

This tutorial explains **what** happens behind the scenes, **why** each step matters, and **how** you can watch the process in real time with the `dig` command. It’s written for:

* **Beginners** who have never touched DNS beyond “type a URL and it works”.
* **Intermediate developers** who want to debug resolution problems or understand caching.

No prior networking theory is required—just a Linux terminal and an internet connection.

---

## Part 1: Core DNS concepts

| Concept | Plain‑English definition | Typical value |
|---------|--------------------------|---------------|
| **Domain name** | Human‑readable label (e.g., `www.example.com`) | `example.com` |
| **Resource Record (RR)** | A single piece of DNS data (A, AAAA, NS, CNAME, etc.) | `A 93.184.216.34` |
| **Resolver** | Software on your computer that asks the DNS hierarchy for an answer | `systemd‑resolved`, `dnsmasq` |
| **Authoritative server** | The server that holds the definitive records for a zone | `ns1.example.com` |
| **Cache** | Temporary storage of recent answers to speed up future queries | 5 min – 48 h TTL |

### Record types you’ll see most often

| Type | Meaning | Example |
|------|---------|---------|
| **A** | IPv4 address | `A 93.184.216.34` |
| **AAAA** | IPv6 address | `AAAA 2606:2800:220:1:248:1893:25c8:1946` |
| **CNAME** | Alias to another name | `CNAME www.example.org` |
| **NS** | Nameserver for a zone | `NS ns1.example.com` |
| **MX** | Mail exchanger | `MX 10 mail.example.com` |

---

## Part 2: The resolution chain – from your PC to the root

When you ask for `www.example.com`, the resolver walks a **tree** from the root down to the authoritative server. The steps are:

```
+----------------+      +----------------+      +----------------+      +--------------------+
| Your Resolver  | ---> | Root server   | ---> | TLD server     | ---> | Authoritative server|
| (cache)        |      | (. )           |      | (.com)         |      | (example.com)      |
+----------------+      +----------------+      +----------------+      +--------------------+
```

1. **Cache check** – If the resolver already knows the answer (or a delegation), it returns it immediately.  
2. **Root query** – If the cache misses, the resolver asks a root server (`a.root-servers.net`). The root replies with the list of **.com** nameservers.  
3. **TLD query** – The resolver now asks one of the `.com` servers for `example.com`. The TLD server returns the NS records for `example.com` (e.g., `ns1.example.com`).  
4. **Authoritative query** – Finally the resolver asks `ns1.example.com` for the **A** record of `www.example.com`. The authoritative server returns the IP address.

Each hop is cached according to the **TTL** (time‑to‑live) field in the record, so subsequent look‑ups skip steps that are still fresh.

---

## Part 3: Using **dig** to watch each hop

`dig` (Domain Information Groper) is a powerful, low‑level DNS client. It lets you:

* Query a specific server (`@server`).
* Request a particular record type (`-t A`).
* Follow the entire chain (`+trace`).

### 3.1 Basic lookup

```bash
dig www.example.com
```

Output (trimmed):

```
;; ANSWER SECTION:
www.example.com.   3600 IN A 93.184.216.34
```

If the answer comes from cache, you’ll see `;; Query time: 1 msec`. To force a fresh lookup, add `+nocache`.

### 3.2 Query a specific server

```bash
dig @8.8.8.8 www.example.com
```

This forces the query to Google’s public DNS, bypassing your local resolver.

### 3.3 Inspect NS delegation

```bash
dig +noall +answer -t NS example.com
```

Result:

```
example.com.      172800 IN NS ns1.example.com.
example.com.      172800 IN NS ns2.example.com.
```

### 3.4 Follow the chain with **+trace**

```bash
dig +trace www.example.com
```

Sample output (abbreviated):

```
; <<>> DiG 9.18.12 <<>> +trace www.example.com
;; global options: +cmd
.                       518400 IN NS a.root-servers.net.
...
com.                    172800 IN NS a.gtld-servers.net.
...
example.com.            172800 IN NS ns1.example.com.
...
www.example.com.        3600   IN A 93.184.216.34
```

Each block shows a separate query: root → TLD → authoritative. This is the fastest way to verify that the delegation chain is intact.

### 3.5 Show the TTL values

```bash
dig +nocmd +noall +answer www.example.com
```

Result includes the TTL (the fourth column). Knowing the TTL helps you understand how long a result will stay in cache.

---

## Hands‑on example – reproducing the whole flow on your machine

Below is a **runnable script** you can paste into a terminal. It:

1. Clears the local DNS cache (systemd‑resolved only; adapt for other resolvers).  
2. Performs a `+trace` lookup for `www.example.com`.  
3. Extracts and prints each server’s IP address.  
4. Verifies the final A record.

```bash
#!/usr/bin/env bash
set -euo pipefail

DOMAIN="www.example.com"

# 1️⃣ Flush systemd-resolved cache (skip if you use another resolver)
if command -v resolvectl &>/dev/null; then
    echo "Flushing systemd-resolved cache..."
    sudo resolvectl flush-caches
fi

# 2️⃣ Run +trace and capture the raw output
echo "Running dig +trace for $DOMAIN ..."
TRACE_OUTPUT=$(dig +trace "$DOMAIN" 2>/dev/null)

# 3️⃣ Print each delegation step
echo "=== Delegation chain ==="
echo "$TRACE_OUTPUT" | awk '
/^;;/ {next}               # skip comment lines
/^$/ {next}                # skip blank lines
/^[^.]+\.?$/ {next}        # skip stray lines
{
    print $0
}
' | while read -r line; do
    # Show the server name and its IP (if present)
    if [[ $line =~ ^([^.]+\.)\s+([0-9]+)\s+IN\s+NS\s+([^.]+\.)$ ]]; then
        ns="${BASH_REMATCH[3]}"
        ip=$(dig +short "$ns")
        printf "NS: %-30s → %s\n" "$ns" "${ip:-no‑IP}"
    fi
done

# 4️⃣ Verify final A record
echo -e "\n=== Final A record ==="
dig +short "$DOMAIN"
```

**How to run**

```bash
chmod +x dns-demo.sh
./dns-demo.sh
```

You should see a list of NS servers with their IPs, followed by the final IPv4 address of `www.example.com`. If any step fails, the script will abort because of `set -e`.

---

## Common mistakes / troubleshooting

| Symptom | Likely cause | Quick fix |
|---------|--------------|-----------|
| `dig: connection timed out; no servers could be reached` | No network or firewall blocks DNS (UDP/53). | Verify internet connectivity (`ping 8.8.8.8`). Open UDP port 53 or switch to a different resolver (`dig @1.1.1.1 …`). |
| Answer shows **`SERVFAIL`** | Upstream server cannot reach authoritative zone (often DNSSEC validation failure). | Disable DNSSEC temporarily (`dig +dnssec=no …`) or use a resolver that doesn’t enforce DNSSEC (`dig @9.9.9.9 …`). |
| TTL appears **0** even though the zone sets a higher value | Your local resolver is configured to ignore TTL (common in corporate networks). | Check resolver config (`/etc/systemd/resolved.conf` → `Cache=yes`). |
| `dig +trace` stops at the TLD step | The TLD server returned a **referral** but the NS hostnames lack glue A records, and your resolver cannot resolve them. | Use `dig @<TLD‑server> ns1.example.com` to fetch glue, or query a public resolver that already knows the glue. |
| Unexpected **CNAME** chain (e.g., `www → cdn.example.net → …`) | The domain uses a CDN or load balancer. | Follow the chain with `dig +short CNAME www.example.com` repeatedly until you reach an A/AAAA record. |

---

## Try it yourself

1. Pick a domain you own (or any public site).  
2. Run `dig +trace` on it.  
3. Identify the **authoritative nameserver** and note its IP address.  
4. Verify that the IP you get from the final A record matches what you see when you `ping` the domain.

If the numbers differ, you’ve just discovered a caching or load‑balancing discrepancy!

---

## What’s next

* **DNSSEC deep dive** – how signatures protect the chain and how to verify them with `dig +dnssec`.  
* **Programmatic look‑ups** – using `libresolv` or Python’s `dnspython` to automate queries.  
* **Performance tuning** – configuring `systemd-resolved` or `unbound` for faster local caching.  
* **Troubleshooting real‑world outages** – case studies where DNS misconfiguration broke a service.

---

*Bookmark this page for a quick reference whenever you need to peek behind the curtain of a domain name.*
