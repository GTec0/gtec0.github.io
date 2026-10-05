---
layout: post
title: "jq crash course: slice JSON from the command line"
subtitle: "Learn to pipe curl into jq and master 8 reusable filters for quick JSON slicing on Linux."
date: 2026-10-05
categories: []
tags: ["Linux", "API", "Developer Tips"]
thumbnail-img: /assets/images/banners/jq-crash-course-slice-json-from-the-command-line-banner.png
share-img: /assets/images/banners/jq-crash-course-slice-json-from-the-command-line-banner.png
author: Asahluma Tyika
---
# jq crash course: slice JSON from the command line  

<!-- Tags: Linux, API, Developer Tips -->

## Intro – what, why, who it’s for  

You’ve probably called a REST API with `curl` and got a wall‑of‑JSON back.  
Reading that blob by eye is slow, error‑prone, and makes scripting a nightmare.  

**`jq`** is a lightweight, pure‑C command‑line processor that lets you *filter*, *transform*, and *slice* JSON with a tiny syntax.  

- **What**: A quick‑start guide to eight jq filters you’ll use every week.  
- **Why**: Turn massive JSON payloads into the exact bits you need—right in the terminal.  
- **Who**: Anyone who writes shell scripts, automates API calls, or just wants to explore JSON without leaving the command line.

No prior jq knowledge is required; a basic familiarity with `curl` and Bash is enough.

---

## Part 1 – Installing jq  

| OS | Command |
|----|---------|
| Ubuntu / Debian | `sudo apt-get install jq` |
| Fedora / CentOS | `sudo dnf install jq` |
| macOS (brew) | `brew install jq` |
| Windows (WSL) | use the Linux command above or download from https://stedolan.github.io/jq/download/ |

Verify the installation:

```bash
jq --version
```

You should see something like `jq-1.6`.

---

## Part 2 – Core concepts (the 8 reusable filters)  

Below is a cheat‑sheet of the filters we’ll cover. Each one works on any valid JSON document.

| # | Filter | Description | Typical use |
|---|--------|-------------|-------------|
| 1 | `.key` | Extract a top‑level field | `jq .name response.json` |
| 2 | `.[index]` | Get an array element by zero‑based index | `jq .[0] users.json` |
| 3 | `.[start:end]` | Slice a range (end exclusive) | `jq .[2:5] logs.json` |
| 4 | `map(.field)` | Transform each array element, keep only `field` | `jq 'map(.id)' tickets.json` |
| 5 | `select(.field == "value")` | Filter objects that match a condition | `jq '.[] | select(.status=="open")' prs.json` |
| 6 | `.| @json` | Serialize a value back to a JSON string (useful for embedding) | `jq -r '.message | @json'` |
| 7 | `keys` | List all keys of an object (or indices of an array) | `jq 'keys' config.json` |
| 8 | `reduce` | Aggregate values (sum, max, etc.) | `jq 'reduce .[] as $i (0; . + $i.amount)' orders.json` |

All filters can be combined with the pipe operator `|`. The following sections show them in action.

---

## Part 3 – Small steps: piping `curl` into `jq`  

### 3.1 Get a JSON payload  

```bash
curl -s https://api.github.com/repos/stedolan/jq/releases/latest
```

`-s` silences progress output, leaving only raw JSON.  

### 3.2 Pipe to jq  

```bash
curl -s https://api.github.com/repos/stedolan/jq/releases/latest | jq .
```

`jq .` pretty‑prints the whole document. From here you can start slicing.

### 3.3 Using filter #1 – top‑level fields  

```bash
curl -s https://api.github.com/repos/stedolan/jq/releases/latest | jq .tag_name
```

Output (example): `"jq-1.6"`  

### 3.4 Using filter #2 – array index  

GitHub’s release JSON contains an array `assets`. Grab the first asset:

```bash
curl -s https://api.github.com/repos/stedolan/jq/releases/latest \
| jq '.assets[0]'
```

### 3.5 Using filter #3 – range slice  

List the first three assets:

```bash
curl -s https://api.github.com/repos/stedolan/jq/releases/latest \
| jq '.assets[0:3]'
```

### 3.6 Using filter #4 – map to a single field  

Extract just the download URLs of all assets:

```bash
curl -s https://api.github.com/repos/stedolan/jq/releases/latest \
| jq 'map(.browser_download_url)'
```

### 3.7 Using filter #5 – select with condition  

Only assets for Linux (`.name` ends with `.linux64`):

```bash
curl -s https://api.github.com/repos/stedolan/jq/releases/latest \
| jq '.assets[] | select(.name | endswith(".linux64"))'
```

### 3.8 Using filter #6 – serialize a string  

If you need the URL as a plain string for another command:

```bash
url=$(curl -s https://api.github.com/repos/stedolan/jq/releases/latest \
      | jq -r '.assets[] | select(.name | endswith(".linux64")) | .browser_download_url')
echo "$url"
```

`-r` outputs raw strings (no quotes).  

### 3.9 Using filter #7 – list keys  

Show which fields the release object contains:

```bash
curl -s https://api.github.com/repos/stedolan/jq/releases/latest | jq 'keys'
```

### 3.10 Using filter #8 – reduce for aggregation  

Suppose an API returns a list of orders, each with an `amount`. Summing them:

```bash
curl -s https://example.com/api/orders | jq 'reduce .[] as $o (0; . + $o.amount)'
```

*(Replace the URL with a real endpoint that returns an array of objects with `amount`.)*

---

## Hands‑on example (full runnable code)  

Let’s build a tiny script that fetches the latest release of `jq`, prints the version, and downloads the Linux binary.

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1️⃣ Fetch the release JSON
release_json=$(curl -s https://api.github.com/repos/stedolan/jq/releases/latest)

# 2️⃣ Extract the tag (e.g., "jq-1.6")
tag=$(echo "$release_json" | jq -r .tag_name)
echo "Latest jq version: $tag"

# 3️⃣ Find the Linux 64‑bit asset URL
linux_url=$(echo "$release_json" \
  | jq -r '.assets[] | select(.name | endswith(".linux64")) | .browser_download_url')

echo "Downloading $linux_url ..."
curl -L -o "jq-${tag}.linux64" "$linux_url"

# 4️⃣ Make it executable
chmod +x "jq-${tag}.linux64"
echo "✅ Downloaded and ready: jq-${tag}.linux64"
```

Save as `download-jq.sh`, make it executable (`chmod +x download-jq.sh`), and run:

```bash
./download-jq.sh
```

You’ll see the version printed, the download progress, and a final success message. The script demonstrates **filters #1, #5, #6** in a real‑world workflow.

---

## Common mistakes / troubleshooting  

- **Mistake 1 – Forgetting `-r` for raw output**  
  *Symptom*: You get quoted strings (`"value"`).  
  *Fix*: Add `-r` (or `--raw-output`) to `jq` when you need a plain value, e.g., `jq -r .id`.

- **Mistake 2 – Using `select` on the wrong level**  
  *Symptom*: No output even though the condition matches.  
  *Fix*: Remember `select` works on each stream element. If your JSON is an object, first iterate with `.[]` or target the array: `.assets[] | select(...)`.

- **Mistake 3 – Index out of bounds**  
  *Symptom*: `jq: error (at <stdin>:...): Cannot index array with number`  
  *Fix*: Check array length first: `jq 'length' file.json` or guard with `if`.

- **Mistake 4 – Mixing Bash variable expansion and jq quoting**  
  *Symptom*: Unexpected characters or empty strings.  
  *Fix*: Use `printf '%s' "$var" | jq ...` or wrap the variable in single quotes inside jq: `jq --arg v "$var" '.field == $v'`.

- **Mistake 5 – Ignoring HTTP errors**  
  *Symptom*: `curl` returns HTML error page, jq then fails with “parse error”.  
  *Fix*: Add `-f` to `curl` (`curl -sf`) so it exits on non‑2xx codes, or test `$?` before piping.

---

## Try it yourself  

**Exercise**: The public API `https://api.spacexdata.com/v4/launches/latest` returns the most recent SpaceX launch.  

1. Use `curl` + `jq` to print the launch **name** and **date_utc**.  
2. List the **payload IDs** (`payloads` is an array of strings).  
3. Count how many **cores** were used (`cores` is an array of objects).

*Hint*: Combine `jq -r`, `map`, and `length` filters.

---

## What’s next  

- **Nested transformations** – learn `walk` and recursive filters for deeply nested data.  
- **Saving jq scripts** – store reusable filters in `.jq` files and invoke them with `-f`.  
- **Performance tricks** – streaming mode (`--stream`) for multi‑gigabyte JSON.  
- **Integrating with `xargs`** – batch‑process many URLs in parallel.

Stay tuned for a follow‑up post that turns these ideas into a full‑featured API client script.

*Bookmark this cheat‑sheet for your next terminal session.*
