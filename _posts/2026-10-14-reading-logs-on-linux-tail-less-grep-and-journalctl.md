---
layout: post
title: "Reading logs on Linux: tail, less, grep and journalctl"
subtitle: "Learn six essential Linux commands—tail, less, grep, and journalctl—to watch live logs, filter errors, and troubleshoot fast."
date: 2026-10-14
categories: []
tags: ["Linux", "Beginner", "Developer Tips"]
thumbnail-img: /assets/images/banners/reading-logs-on-linux-tail-less-grep-and-journalctl-banner.png
share-img: /assets/images/banners/reading-logs-on-linux-tail-less-grep-and-journalctl-banner.png
author: Asahluma Tyika
---
## Introduction: why reading logs matters  
Every program you run on Linux writes messages to a log file or the system journal. Those messages tell you what the software is doing, when it fails, and how to fix it. If you can read and filter those logs quickly, you’ll spend far less time guessing and more time solving problems.

**Who this is for**  
* Beginners who have never opened a log file before.  
* Intermediate developers who want a reliable, repeatable workflow for debugging services.  

By the end of this tutorial you’ll have six go‑to commands that let you:

1. Follow a log as it grows (`tail -f`).  
2. Scroll back and search inside a log (`less`).  
3. Pull out only the lines you care about (`grep`).  
4. Work with the systemd journal (`journalctl`).  

---

## Part 1 – The basics of text‑based logs  

| Command | What it does | Typical use case |
|---------|--------------|------------------|
| `tail`  | Shows the last *n* lines of a file. | Quick glance at recent activity. |
| `less`  | Pager that lets you scroll forward and backward. | Browse a large log without loading it all into memory. |
| `grep`  | Filters lines that match a pattern. | Find errors, warnings, or specific IDs. |
| `journalctl` | Reads the binary systemd journal. | View logs from services that use `systemd` (most modern daemons). |

All four tools work on plain‑text files, but `journalctl` reads a binary store, so its syntax differs a little.

### 1.1 `tail` – the fastest way to see the newest entries  
```bash
# Show the last 10 lines (default)
tail /var/log/syslog

# Show the last 20 lines
tail -n 20 /var/log/syslog
```

**Follow mode** (`-f`) keeps the file open and prints new lines as they appear—perfect for watching a live process.

```bash
tail -f /var/log/syslog
```

Press `Ctrl‑C` to stop.

### 1.2 `less` – scroll, search, and filter on the fly  
```bash
less /var/log/syslog
```

Inside `less` you can:

* `Space` – page down  
* `b` – page up  
* `/pattern` – search forward for *pattern*  
* `?pattern` – search backward  
* `&pattern` – **filter view**: only show lines that match *pattern* (press `&` again to clear).  

When you’re done, type `q`.

### 1.3 `grep` – cut out the noise  
```bash
# Show only lines that contain the word "error"
grep -i error /var/log/syslog
```

* `-i` – case‑insensitive  
* `-n` – prefix each line with its line number  
* `-C 2` – show 2 lines of context before and after each match  

```bash
grep -i -n -C 2 "failed login" /var/log/auth.log
```

### 1.4 `journalctl` – the modern log daemon  

Systemd stores logs in a binary format under `/run/log/journal/`. Use `journalctl` to query them.

```bash
# Show the most recent 20 journal entries
journalctl -n 20

# Follow the journal like `tail -f`
journalctl -f

# Show only entries from a specific service
journalctl -u nginx.service

# Filter by priority (0=emerg, 3=err, 6=info)
journalctl -p err
```

`journalctl` also understands time ranges:

```bash
journalctl --since "2024-10-01 09:00" --until "2024-10-01 10:00"
```

---

## Part 2 – Combining the tools  

The real power comes when you pipe output from one command into another.

| Combination | What you get |
|-------------|--------------|
| `tail -f file | grep pattern` | Live view of only matching lines. |
| `journalctl -f | grep -i timeout` | Follow the system journal and watch for timeouts. |
| `less file` → `&pattern` | Interactive filter without leaving the pager. |
| `grep -i error file | less` | Paginated error list, searchable with `/`. |

### 2.1 Live filtering with `tail` and `grep`  

```bash
tail -f /var/log/nginx/error.log | grep -i "client sent malformed request"
```

This command will **only** print new lines that contain the phrase, letting you focus on the problem as it happens.

### 2.2 Using `journalctl` with `grep` for service‑specific debugging  

```bash
journalctl -u postgresql.service -f | grep -i "deadlock"
```

You now see every new PostgreSQL log entry that mentions “deadlock”.

### 2.3 Interactive filtering inside `less`  

```bash
less /var/log/apache2/access.log
```

Press `&` then type `200` to view only successful HTTP responses. Press `&` again (empty input) to clear the filter.

---

## Part 3 – Practical tips for clean log handling  

| Tip | Command | Why it helps |
|-----|---------|--------------|
| Limit output size | `journalctl -n 100` | Prevents scrolling through thousands of lines. |
| Save filtered output | `grep -i error file > errors.txt` | Keeps a permanent copy for later analysis. |
| Colorize matches | `grep --color=auto pattern file` | Highlights the matched text, easier to scan. |
| Show timestamps in `tail` | `tail -f file | ts` (install `moreutils`) | Adds a readable timestamp to each line. |
| Rotate logs safely | `logrotate` (system service) | Prevents logs from growing indefinitely. |

---

## Hands‑on example: track a failing web request  

Assume you have an Nginx server and you want to watch for 500‑status responses in real time.

```bash
# 1. Follow the Nginx access log
tail -f /var/log/nginx/access.log \
| # 2. Keep only lines with status code 500
  grep -E " 500 " \
| # 3. Show the line number and highlight the match
  grep --color=auto -n "500"
```

**Explanation**

1. `tail -f` streams new log lines as they arrive.  
2. `grep -E " 500 "` uses a regular expression to match the exact status code (the spaces avoid matching `5000`).  
3. The second `grep` adds line numbers (`-n`) and colors the `500` text for quick visual scanning.

You can pipe the result into `less` if you prefer a scrollable view:

```bash
tail -f /var/log/nginx/access.log | grep -E " 500 " | less
```

To keep a record for later review:

```bash
tail -f /var/log/nginx/access.log | grep -E " 500 " > /tmp/500-errors.log
```

Now you have a file that contains only the problematic requests.

---

## Common mistakes & troubleshooting  

* **Mistake:** Using `tail -f` on a rotated log file (the file disappears after rotation).  
  **Fix:** Use `tail -F` (capital F). It follows the file name across rotations.

* **Mistake:** Forgetting to escape special characters in `grep` patterns.  
  **Fix:** Quote the pattern or use `-F` for fixed‑string matching: `grep -F "error: 404"`.

* **Mistake:** Running `journalctl` without sufficient permissions, getting “Permission denied”.  
  **Fix:** Prefix with `sudo` or add your user to the `systemd-journal` group:  
  ```bash
  sudo usermod -aG systemd-journal $USER
  ```

* **Mistake:** Overwhelming the terminal with too much output, causing lag.  
  **Fix:** Limit the number of lines (`-n 100`) or add a time filter (`--since "5 min ago"`).

* **Mistake:** Using `grep` on a binary journal file (`/var/log/journal/...`).  
  **Fix:** Always query the journal with `journalctl`; do not feed the binary file to `grep`.

---

## Try it yourself  

1. Open a terminal.  
2. Run `journalctl -f` in one pane (or a separate tab).  
3. In another pane, intentionally trigger a failed `ssh` login (e.g., `ssh invalid@localhost`).  
4. Use `grep` to filter the journal for the string “Failed password” while the login attempt is happening:  

```bash
journalctl -f | grep -i "failed password"
```

You should see the new log line appear instantly.

---

## What’s next  

* **Log rotation deep dive** – how `logrotate` works and custom configuration.  
* **Structured logging** – parsing JSON logs with `jq`.  
* **Alerting basics** – piping log output to `mail` or `notify-send`.  
* **Performance profiling** – using `strace` and `lsof` alongside log analysis.

Bookmark this page and keep the six commands handy; they’ll become your daily debugging companions.
