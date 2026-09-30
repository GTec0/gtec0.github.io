---
layout: post
title: "How HTTP status codes actually work (with curl demos)"
subtitle: "Learn how HTTP status codes work by using curl against httpbin.org, complete with diagrams, scripts, and troubleshooting tips."
date: 2026-09-29
categories: []
tags: ["Networking", "API", "Beginner"]
thumbnail-img: /assets/images/banners/how-http-status-codes-actually-work-with-curl-demos-banner.png
share-img: /assets/images/banners/how-http-status-codes-actually-work-with-curl-demos-banner.png
author: Asahluma Tyika
---
## Introduction: What HTTP Status Codes Are and Why You Should Care  

When you type a URL into a browser or call a REST API from code, the server answers with a **status line** like `HTTP/1.1 200 OK`. That line tells the client whether the request succeeded, failed, or needs more work. Understanding these codes lets you:

* Diagnose broken APIs without guessing.  
* Write scripts that react intelligently (retry on 5xx, prompt the user on 4xx, etc.).  
* Communicate clearly with teammates about what “went wrong”.

This tutorial is for **beginners to intermediate developers** who already know how to run a terminal command and have heard of `curl`. We’ll use the free service **httpbin.org** to generate every kind of status code on demand, so you can see the exact request/response exchange.

---

## Part 1 – The Anatomy of an HTTP Response  

An HTTP response consists of three parts:

1. **Status line** – protocol version, numeric code, and textual reason phrase.  
2. **Headers** – key/value pairs that give metadata (`Content-Type`, `Cache-Control`, …).  
3. **Body** – optional payload (HTML, JSON, etc.).

```
HTTP/1.1 404 Not Found
Content-Type: text/html; charset=utf-8
Content-Length: 345

<!DOCTYPE html>...
```

The **numeric code** is the part you’ll be working with most. It’s divided into five classes:

| Class | Range | Typical Meaning |
|-------|-------|-----------------|
| 1xx   | 100‑199 | Informational – request received, continuing process |
| 2xx   | 200‑299 | Success – the action was completed as expected |
| 3xx   | 300‑399 | Redirection – client must take further action (e.g., follow a new URL) |
| 4xx   | 400‑499 | Client error – the request is malformed or unauthorized |
| 5xx   | 500‑599 | Server error – the server failed to fulfill a valid request |

**Why the numbers matter:** A script can decide to retry only on 5xx, or to prompt a user only on 401 – 403, etc. The textual phrase (`Not Found`, `Internal Server Error`) is for humans; machines only look at the number.

---

## Part 2 – Getting Status Codes with `curl`  

`curl` is a command‑line tool that can show the full HTTP exchange. The flags we’ll use most often are:

| Flag | Purpose |
|------|---------|
| `-i` | Include response headers in the output |
| `-s` | Silent mode (no progress meter) |
| `-o /dev/null` | Discard the body, keep only headers |
| `-w "%{http_code}"` | Print only the numeric status code after the transfer |

### 2.1 2xx – Success  

```bash
curl -s -o /dev/null -w "%{http_code}" https://httpbin.org/status/200
```

Output:

```
200
```

You can ask for any 2xx code; httpbin.org will return exactly what you request:

```bash
curl -i https://httpbin.org/status/201
```

Result (truncated):

```
HTTP/1.1 201 CREATED
Date: Thu, 29 Sep 2026 12:00:00 GMT
Content-Type: text/html; charset=utf-8
...
```

### 2.2 3xx – Redirection  

```bash
curl -i -L https://httpbin.org/status/302
```

* `-L` tells curl to **follow redirects** automatically. Without it you’ll see the raw 302 response:

```bash
curl -i https://httpbin.org/status/302
```

```
HTTP/1.1 302 FOUND
Location: /redirect/1
...
```

The `Location` header tells the client where to go next.

### 2.3 4xx – Client Errors  

```bash
curl -i https://httpbin.org/status/404
```

```
HTTP/1.1 404 NOT FOUND
Content-Type: text/html; charset=utf-8
...
```

Try a 401 (Unauthorized) that also includes a `WWW-Authenticate` header:

```bash
curl -i https://httpbin.org/status/401
```

```
HTTP/1.1 401 UNAUTHORIZED
WWW-Authenticate: Basic realm="Fake Realm"
...
```

### 2.4 5xx – Server Errors  

```bash
curl -i https://httpbin.org/status/500
```

```
HTTP/1.1 500 INTERNAL SERVER ERROR
Content-Type: text/html; charset=utf-8
...
```

A 503 (Service Unavailable) often carries a `Retry-After` header:

```bash
curl -i https://httpbin.org/status/503
```

```
HTTP/1.1 503 SERVICE UNAVAILABLE
Retry-After: 120
...
```

---

## Part 3 – Putting It All Together: A Mini‑Status‑Checker Script  

Below is a **bash** function you can paste into your shell or a script file. It accepts a URL, performs a `GET`, and prints a friendly summary based on the status code.

```bash
#!/usr/bin/env bash
# status_check.sh – simple HTTP status inspector using curl

check_status() {
    local url=$1
    # -s silent, -o /dev/null discard body, -w prints code, -D - writes headers to a temp file
    local headers=$(mktemp)
    local code=$(curl -s -D "$headers" -o /dev/null -w "%{http_code}" "$url")
    
    echo "▶️  $url → $code"

    case $code in
        1[0-9][0-9]) echo "ℹ️  Informational – server is processing the request." ;;
        2[0-9][0-9]) echo "✅  Success – everything worked!" ;;
        3[0-9][0-9]) 
            local location=$(grep -i '^Location:' "$headers" | cut -d' ' -f2- | tr -d '\r')
            echo "🔀  Redirection – follow $location"
            ;;
        4[0-9][0-9]) echo "⚠️  Client error – check the request (auth, syntax, etc.)." ;;
        5[0-9][0-9]) echo "🚨  Server error – may be temporary, consider retrying." ;;
        *) echo "❓  Unexpected code." ;;
    esac

    rm "$headers"
}

# Example usage:
# check_status "https://httpbin.org/status/404"
```

**How it works**

1. `curl -D "$headers"` writes the response headers to a temporary file.  
2. `-w "%{http_code}"` captures the numeric code.  
3. A `case` statement maps the code to a human‑readable message.  
4. For 3xx responses we extract the `Location` header so you know where to go next.

Run it like:

```bash
bash status_check.sh https://httpbin.org/status/302
```

You’ll see something like:

```
▶️  https://httpbin.org/status/302 → 302
🔀  Redirection – follow /redirect/1
```

---

## Hands‑On Example: Querying All Major Classes in One Script  

The following one‑liner loops through a representative set of status codes, prints the full response headers, and stores the bodies in a `responses/` folder for later inspection.

```bash
#!/usr/bin/env bash
# demo_all_codes.sh – fetches several status codes from httpbin.org

mkdir -p responses
codes=(200 201 302 303 404 401 418 500 503)

for c in "${codes[@]}"; do
    echo "=== Requesting $c ==="
    curl -i -s "https://httpbin.org/status/$c" > "responses/$c.txt"
    # Show just the status line
    head -n 1 "responses/$c.txt"
done
```

After running:

```bash
bash demo_all_codes.sh
```

You’ll have seven files (`200.txt`, `201.txt`, …) each containing the exact raw HTTP exchange. Open any with `cat` or a text editor to see the headers and optional body.

---

## Common Mistakes & Troubleshooting  

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| `curl: (6) Could not resolve host` | Misspelled URL or DNS issue | Verify the domain (`httpbin.org`) and your internet connection. |
| No status code printed, only an empty line | Used `-w "%{http_code}"` without `-s` and the output got mixed with progress meter | Add `-s` (silent) or redirect stderr: `curl -s -w "%{http_code}" … 2>/dev/null`. |
| 3xx response never follows the redirect | Forgot `-L` flag | Use `curl -L …` to let curl automatically follow `Location` headers. |
| Body appears as binary gibberish | Server sent compressed data (`gzip`) but curl didn’t decompress | Add `--compressed` to let curl handle `Content-Encoding: gzip`. |
| `Retry-After` header ignored in script | Script only checks the code, not headers | Parse the header (as shown in the `check_status` function) and respect the delay. |

---

## Try It Yourself  

**Exercise:** Write a tiny Python script that uses `requests` to fetch `https://httpbin.org/status/418` and prints “I’m a teapot” only when the status code is **418**. Otherwise, print the received code.

```python
import requests

resp = requests.get('https://httpbin.org/status/418')
if resp.status_code == 418:
    print("I'm a teapot")
else:
    print(f"Got {resp.status_code}")
```

Run it with `python3 teapot.py` and verify the output.

---

## What’s Next?  

- **Automated retries**: Build a wrapper that backs off exponentially on 5xx codes.  
- **Content negotiation**: Use `Accept` and `Content-Type` headers to request JSON vs. HTML.  
- **Custom status pages**: Learn how servers generate friendly error pages (404, 500).  
- **Monitoring with curl**: Hook curl into cron or a CI pipeline to alert on unexpected status codes.

Each of these topics expands the practical power of the basics you just learned.

*Bookmark this guide for quick reference when debugging APIs.*
