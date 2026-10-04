---
layout: post
title: "curl in 10 examples: test any API from the terminal"
subtitle: "Learn 10 practical curl commands to test GET, POST, headers, and auth against httpbin.org – perfect for beginners who want to probe any API from the terminal."
date: 2026-10-04
categories: []
tags: ["Linux", "API", "Networking", "Beginner"]
thumbnail-img: /assets/images/banners/curl-in-10-examples-test-any-api-from-the-terminal-banner.png
share-img: /assets/images/banners/curl-in-10-examples-test-any-api-from-the-terminal-banner.png
author: Asahluma Tyika
---
# curl in 10 examples: test any API from the terminal  
**Tags:** Linux, API, Networking, Beginner  

## Introduction – what is curl and why you need it  

`curl` (Client URL) is a command‑line tool that talks HTTP, HTTPS, FTP, and many other protocols. It’s installed by default on most Linux distributions, macOS, and even Windows Subsystem for Linux.  

- **What it does:** send a request to a URL and print the raw response.  
- **Why it matters:** you can verify an API’s behaviour without writing code, debug authentication problems, or automate health checks in scripts.  

This tutorial is for anyone who can open a terminal and type a command – from a brand‑new developer to a seasoned sysadmin who wants a quick way to poke an API.

## Part 1 – Core curl concepts  

| Option | Meaning | Example |
|--------|---------|---------|
| `-X`   | Explicit HTTP method (GET, POST, PUT, DELETE…) | `curl -X POST https://example.com` |
| `-d`   | Data to send in the request body (automatically sets `Content-Type: application/x-www-form-urlencoded` unless you override) | `curl -d "name=Bob" https://httpbin.org/post` |
| `-H`   | Add a custom header | `curl -H "Accept: application/json" …` |
| `-u`   | Basic auth in the form `user:password` | `curl -u alice:secret https://httpbin.org/basic-auth/alice/secret` |
| `-i`   | Include response headers in the output | `curl -i https://httpbin.org/get` |
| `-s`   | Silent mode – hide progress meter | `curl -s https://httpbin.org/ip` |
| `-o`   | Write response body to a file | `curl -o result.json https://httpbin.org/json` |
| `-L`   | Follow redirects (HTTP 3xx) | `curl -L http://httpbin.org/redirect/1` |
| `-v`   | Verbose – show request/response details (great for debugging) | `curl -v https://httpbin.org/get` |

### How curl builds a request  

1. **URL parsing** – the scheme (`http`/`https`) determines the port and TLS usage.  
2. **Method selection** – default is `GET`. Adding `-X` or `-d` changes it.  
3. **Headers** – curl adds a few defaults (`User-Agent`, `Accept`). You can replace or add with `-H`.  
4. **Body** – only sent for methods that support it (`POST`, `PUT`, `PATCH`).  

Understanding these steps makes the examples below easier to follow.

## Part 2 – 10 practical examples with httpbin.org  

`httpbin.org` is a free service that echoes back whatever you send it. It’s perfect for learning curl because you can see the exact request curl generated.

| # | Goal | Command | What you’ll see |
|---|------|---------|-----------------|
| 1 | Simple GET | `curl https://httpbin.org/get` | JSON with `args`, `headers`, `origin`, `url`. |
| 2 | GET with query string | `curl "https://httpbin.org/get?city=Paris&unit=metric"` | `args` shows the two parameters. |
| 3 | GET with custom header | `curl -H "X-My-Header: hello" https://httpbin.org/headers` | `headers` includes `X-My-Header`. |
| 4 | POST form data | `curl -d "username=bob&age=30" https://httpbin.org/post` | `form` contains the two fields. |
| 5 | POST JSON payload | `curl -X POST -H "Content-Type: application/json" -d '{"title":"curl","views":100}' https://httpbin.org/post` | `json` mirrors the JSON object. |
| 6 | PUT request with file | `curl -X PUT -T ./sample.txt https://httpbin.org/put` | `data` shows the file’s raw content. |
| 7 | DELETE request | `curl -X DELETE https://httpbin.org/delete` | JSON with `url` and `args` (empty). |
| 8 | Basic authentication | `curl -u user:pass https://httpbin.org/basic-auth/user/pass` | `{ "authenticated": true, "user": "user" }` |
| 9 | Bearer token header | `curl -H "Authorization: Bearer abc123" https://httpbin.org/bearer` | `{ "authenticated": true, "token": "abc123" }` |
|10| Follow a redirect chain | `curl -L https://httpbin.org/redirect/3` | Final JSON shows the original URL after three hops. |

### Running the examples  

Open a terminal, copy a line, and press **Enter**. All commands are self‑contained – no extra setup required.

#### Example 5 explained step‑by‑step  

```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"title":"curl","views":100}' \
     https://httpbin.org/post
```

- `-X POST` forces the POST method.  
- `-H "Content-Type: application/json"` tells the server we’re sending JSON.  
- `-d '{...}'` supplies the JSON body.  
- The response’s `json` field will be exactly the payload we sent, confirming that the request arrived intact.

## Part 3 – Hands‑on example: a tiny API health‑check script  

Below is a ready‑to‑run Bash script that checks three common aspects of any REST endpoint:

1. **Reachability** (GET `/status` or fallback to `/get`).  
2. **JSON validity** (expects a JSON response).  
3. **Response time** (fails if > 2 seconds).

```bash
#!/usr/bin/env bash
# healthcheck.sh – test an API endpoint with curl
# Usage: ./healthcheck.sh https://httpbin.org/get

set -euo pipefail

URL="${1:-https://httpbin.org/get}"
MAX_MS=2000   # 2 seconds

echo "🔎 Checking $URL …"

# 1️⃣ Reachability & timing
TIME_MS=$(curl -s -o /dev/null -w "%{time_total_ms}" "$URL")
if (( $(echo "$TIME_MS > $MAX_MS" | bc -l) )); then
  echo "❌ Too slow: ${TIME_MS}ms (limit ${MAX_MS}ms)"
  exit 1
fi
echo "✅ Response time: ${TIME_MS}ms"

# 2️⃣ HTTP status code
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
if [[ "$STATUS" != 2* ]]; then
  echo "❌ Unexpected status: $STATUS"
  exit 1
fi
echo "✅ HTTP status: $STATUS"

# 3️⃣ JSON validation (optional)
if curl -s "$URL" | jq . >/dev/null 2>&1; then
  echo "✅ Valid JSON returned"
else
  echo "❌ Response is not valid JSON"
  exit 1
fi

echo "🎉 All checks passed!"
```

**How to run**

```bash
chmod +x healthcheck.sh
./healthcheck.sh https://httpbin.org/get
```

If everything is fine you’ll see:

```
🔎 Checking https://httpbin.org/get …
✅ Response time: 123ms
✅ HTTP status: 200
✅ Valid JSON returned
🎉 All checks passed!
```

Feel free to replace the URL with any of your own services.

## Common mistakes & troubleshooting  

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `curl: (6) Could not resolve host` | Missing quotes around a URL that contains `?` or `&` | Wrap the full URL in double quotes: `curl "https://example.com?x=1&y=2"` |
| Empty response body when using `-d` | Forgot to set `-X POST` (curl defaults to GET) | Add `-X POST` or use `--data` which automatically switches to POST. |
| Server returns 401 but you supplied `-u user:pass` | The server expects **Bearer** token, not Basic auth | Use `-H "Authorization: Bearer <token>"` instead of `-u`. |
| `curl: (22) The requested URL returned error: 404 Not Found` | Wrong endpoint path (typo) | Double‑check the path on the API docs; use `curl -v` to see the exact request line. |
| JSON parsing fails with `jq` | Response is not JSON (e.g., HTML error page) | Inspect the raw output (`curl -i …`) to see the real content type. |

## Try it yourself  

**Exercise:** Use curl to send a `PATCH` request that updates a JSON field on `https://httpbin.org/patch`. Include a custom header `X-Exercise: true` and verify that the response’s `json` contains your changes.

```bash
curl -X PATCH \
     -H "Content-Type: application/json" \
     -H "X-Exercise: true" \
     -d '{"status":"completed"}' \
     https://httpbin.org/patch
```

Check that the `json` object in the output matches the payload and that `headers` shows `X-Exercise: true`.

## What’s next  

- **Batch testing:** combine curl with `xargs` or GNU Parallel to hit many endpoints at once.  
- **OAuth 2.0 flows:** use `curl` to exchange client credentials for an access token.  
- **Saving and reusing cookies:** explore `-c` and `-b` options for session handling.  
- **Performance profiling:** integrate `curl` with `time` or `hyperfine` for benchmark scripts.  

Keep experimenting, and soon you’ll be comfortable debugging any HTTP API right from your terminal.  

*Bookmark this guide for quick reference.*
