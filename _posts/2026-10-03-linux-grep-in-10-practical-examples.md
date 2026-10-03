---
layout: post
title: "Linux grep in 10 practical examples"
subtitle: "Learn how to master Linux grep with 10 real‑world log and code search examples, covering -r, -i, -n and more."
date: 2026-10-03
categories: []
tags: ["Linux", "Terminal", "Beginner"]
thumbnail-img: /assets/images/banners/linux-grep-in-10-practical-examples-banner.png
share-img: /assets/images/banners/linux-grep-in-10-practical-examples-banner.png
author: Asahluma Tyika
---
## Introduction – What is `grep` and why you need it  
`grep` (global regular expression print) is the Swiss‑army knife for searching text on the command line. Whether you’re digging through system logs, hunting a deprecated function in a codebase, or just checking a configuration file, `grep` lets you find exactly what you need in seconds.

**Who is this tutorial for?**  
- Beginners who have never used `grep` before.  
- Intermediate users who know the basics but want practical, real‑world patterns.  

By the end you’ll be comfortable with the most useful flags (`-r`, `-i`, `-n`) and you’ll have a ready‑to‑copy set of one‑liners for everyday debugging.

---

## Part 1 – Core concepts in bite‑size steps  

| Flag | Meaning | Typical use case |
|------|---------|------------------|
| `-i` | Ignore case | Search error keywords regardless of capitalisation (`ERROR`, `error`, `Error`). |
| `-r` | Recursive | Scan every file under a directory tree (e.g., all logs in `/var/log`). |
| `-n` | Show line numbers | Quickly jump to the offending line in a source file. |
| `-E` | Extended regex | Use `+`, `?`, `|` without backslashes. |
| `--color=auto` | Highlight matches | Makes the output easier to read. |

### Step‑by‑step building blocks  

1. **Simple literal search**  
   ```bash
   grep "failed" /var/log/auth.log
   ```
2. **Add case‑insensitivity**  
   ```bash
   grep -i "failed" /var/log/auth.log
   ```
3. **Show line numbers**  
   ```bash
   grep -in "failed" /var/log/auth.log
   ```
4. **Search every file in a folder**  
   ```bash
   grep -rin "failed" /var/log/
   ```
5. **Limit to a file type (e.g., *.log)**  
   ```bash
   grep -rin --include="*.log" "failed" /var/log/
   ```

---

## Part 2 – 10 practical examples  

### 1. Find all *ERROR* lines in the current directory’s log files  
```bash
grep -iRn --include="*.log" "error" .
```
*Why?* System administrators often need to spot error spikes across many rotated logs.

### 2. Locate a deprecated function in a large C/C++ codebase  
```bash
grep -Rnw "old_function_name" src/
```
*`-w`* forces whole‑word matching so you don’t get `old_function_name_extra`.

### 3. Extract IP addresses that caused a 404 in an Apache access log  
```bash
grep -i "404" /var/log/apache2/access.log | \
grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | sort | uniq -c | sort -nr
```
*Explanation*:  
- First `grep` filters 404 lines.  
- `-oE` prints only the IP part.  
- `sort | uniq -c` counts occurrences.  

### 4. Search for a TODO comment across all source files, ignoring case  
```bash
grep -Rin --exclude-dir=".git" "TODO" .
```
*Useful when you want a quick inventory of unfinished work.*

### 5. Find lines that contain **either** “fatal” **or** “panic” in system logs  
```bash
grep -iRnwE "fatal|panic" /var/log/
```
*`-E`* enables the `|` alternation operator.

### 6. Show the exact line number of a failing unit test in a Python test suite  
```bash
grep -in "AssertionError" tests/test_my_module.py
```
Now you can open the file at that line with `vim +42 tests/test_my_module.py`.

### 7. Search for a specific configuration key in all `.conf` files, but skip binary files  
```bash
grep -Rin --binary-files=without-match --include="*.conf" "max_connections" /etc/
```

### 8. Find all occurrences of a CSS class name in a front‑end project (ignore minified files)  
```bash
grep -Rin --exclude="*.min.css" "\.my-special-class" assets/
```
The backslash escapes the leading dot so the regex treats it as a literal period.

### 9. List all files that contain a given secret token (use `-l` to show only filenames)  
```bash
grep -Ril "SECRET_TOKEN_12345" .
```
Great for security audits before committing code.

### 10. Count how many times a particular warning appears in the kernel ring buffer  
```bash
dmesg | grep -ci "warning"
```
`-c` returns only the count, no need to scroll through the whole output.

---

## Hands‑on example – A complete, copy‑and‑paste workflow  

Suppose you are troubleshooting a web service that writes JSON logs to `/var/log/myapp/`. Each log line looks like:

```json
{"time":"2026-09-30T12:34:56Z","level":"error","msg":"Database connection failed","host":"srv01"}
```

You want to:

1. Find **all** error entries (case‑insensitive).  
2. Show the line number within each file.  
3. Output only the `msg` field for quick reading.

```bash
# 1️⃣ Grab every error line, recursively, with line numbers
grep -iRn '"level":"error"' /var/log/myapp/ > errors_raw.txt

# 2️⃣ Extract only the message part (using a simple regex)
awk -F'"msg":"' '{print $2}' errors_raw.txt | \
sed -E 's/".*$//' > error_messages.txt

# 3️⃣ Display the result with a friendly header
echo "=== Database error messages ==="
cat error_messages.txt
```

**What each command does**

| Command | Purpose |
|---------|---------|
| `grep -iRn '"level":"error"' /var/log/myapp/` | Recursively search for the JSON key `"level":"error"` ignoring case, and prefix each match with `filename:line`. |
| `awk -F'"msg":"' '{print $2}'` | Split on the literal `"msg":"` and keep the second field (the message plus trailing characters). |
| `sed -E 's/".*$//'` | Remove everything after the closing quote, leaving only the message text. |
| `> errors_raw.txt` / `> error_messages.txt` | Store intermediate results so you can inspect or reuse them. |

Run the block in a terminal; you’ll end up with a tidy list of error messages ready for a ticket.

---

## Common mistakes & troubleshooting  

- **Forgot `-r` for a directory search**  
  *Symptom*: Only the top‑level file is scanned.  
  *Fix*: Add `-r` (or `-R`) to make the search recursive.  

- **Getting binary garbage in the output**  
  *Symptom*: `grep` prints unreadable characters.  
  *Fix*: Use `--binary-files=without-match` or limit the search to text files with `--include="*.log"`.  

- **Case‑sensitivity causing missed matches**  
  *Symptom*: Searching for “error” returns nothing, but the file contains “Error”.  
  *Fix*: Add `-i`.  

- **Accidentally matching substrings**  
  *Symptom*: Searching for “cat” also returns “concatenated”.  
  *Fix*: Use `-w` for whole‑word matching.  

- **Performance slowdown on huge directories**  
  *Symptom*: The command takes minutes.  
  *Fix*: Exclude heavy folders (e.g., `--exclude-dir=node_modules`) or limit to specific extensions with `--include`.  

---

## Try it yourself  

Create a small test directory and practice the flags:

```bash
mkdir -p ~/grep-demo/subdir
cat > ~/grep-demo/app.log <<'EOF'
INFO Starting service
WARN Low memory
ERROR Database connection failed
info Service stopped
EOF

cat > ~/grep-demo/subdir/notes.txt <<'EOF'
TODO: Refactor error handling
Remember to check ERROR logs daily.
EOF
```

Now run:

```bash
grep -in "error" ~/grep-demo/*
```

You should see two matches, one from `app.log` and one from `notes.txt`, each with its line number.

---

## What’s next  

- **Advanced regex** – Learn look‑ahead/look‑behind patterns for more precise matches.  
- **Combining `grep` with `xargs`** – Perform actions (e.g., delete, move) on files that contain a pattern.  
- **Using `awk` and `sed` together** – Turn `grep` results into structured reports.  
- **Performance tuning with `ripgrep` (`rg`)** – A modern, faster alternative for massive codebases.

Bookmark this page and keep experimenting – the more you search, the faster you’ll spot the needle in the haystack.
