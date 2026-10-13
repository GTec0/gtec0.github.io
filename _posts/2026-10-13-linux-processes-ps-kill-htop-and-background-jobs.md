---
layout: post
title: "Linux processes: ps, kill, htop and background jobs"
subtitle: "Learn how to locate a stuck Linux process, inspect it with ps/htop, kill it safely, and manage background jobs with &, jobs, and fg."
date: 2026-10-13
categories: []
tags: ["Linux", "Beginner"]
thumbnail-img: /assets/images/banners/linux-processes-ps-kill-htop-and-background-jobs-banner.png
share-img: /assets/images/banners/linux-processes-ps-kill-htop-and-background-jobs-banner.png
author: Asahluma Tyika
---
## Introduction – What, Why, and Who This Is For  

If you ever run a command that never returns, a script that hangs, or a GUI app that refuses to close, you’re dealing with a **stuck process**. Knowing how to spot it, inspect its details, and terminate it cleanly is a core skill for any Linux user.  

This tutorial is written for **beginners to intermediate developers** who use a terminal daily (or want to start). We’ll cover the most common tools:

| Tool | Primary use |
|------|--------------|
| `ps` | List processes, filter by name, user, or state |
| `kill` | Send signals (e.g., SIGTERM, SIGKILL) to a process |
| `htop` | Interactive, color‑rich process viewer |
| `&`, `jobs`, `fg`, `bg` | Run commands in the background and manage them |

By the end you’ll be able to find a rogue process, stop it without harming the system, and run long‑running jobs without blocking your shell.

---

## Part 1 – Inspecting Processes with `ps`

### 1.1 The basic `ps` command  

```bash
ps aux
```

* `a` – show processes for all users with a terminal  
* `u` – display the user/owner column  
* `x` – include processes without a controlling terminal (daemons)

The output looks like this:

| USER | PID | %CPU | %MEM | VSZ | RSS | TTY | STAT | START | TIME | COMMAND |
|------|-----|------|------|-----|-----|-----|------|-------|------|----------|
| alice | 1245 | 0.0 | 0.1 | 3456 | 560 | pts/0 | S | 09:12 | 0:00 | bash |
| root  | 1    | 0.1 | 0.5 | 8320 | 1024 | ?   | Ss   | 09:00 | 0:03 | /sbin/init |

* `STAT` codes are important:  
  * `R` – running  
  * `S` – sleeping (waiting for I/O)  
  * `D` – uninterruptible sleep (usually I/O)  
  * `Z` – zombie (already dead, waiting for parent)  
  * `T` – stopped (by job control or a signal)

### 1.2 Filtering by name or PID  

```bash
ps -C python          # show all processes whose executable name is "python"
ps -p 1245,1289       # show only the listed PIDs
ps aux | grep myapp   # quick text search (beware of the grep process itself)
```

### 1.3 Using `ps` with `--forest` for a tree view  

```bash
ps -ef --forest | grep nginx
```

The tree view helps you see parent‑child relationships, which is useful when a child process is stuck but the parent is still alive.

---

## Part 2 – Killing Processes Safely with `kill`

### 2.1 Signals 101  

| Signal | Number | Typical use |
|--------|--------|-------------|
| `SIGTERM` | 15 | Graceful shutdown (default) |
| `SIGINT`  | 2  | Interrupt (Ctrl‑C) |
| `SIGKILL` | 9  | Forceful kill, cannot be caught |
| `SIGSTOP` | 19 | Pause a process (like Ctrl‑Z) |
| `SIGCONT` | 18 | Resume a stopped process |

### 2.2 The usual workflow  

1. **Identify** the PID with `ps` or `htop`.  
2. **Ask nicely**:  

   ```bash
   kill -TERM 1245   # or simply: kill 1245
   ```

3. **Verify** that the process disappeared:

   ```bash
   ps -p 1245 && echo "still alive" || echo "gone"
   ```

4. **Escalate** only if needed:

   ```bash
   kill -KILL 1245   # last resort
   ```

### 2.3 Killing by name with `pkill` and `killall`  

```bash
pkill -f "my long script.py"   # matches the full command line
killall -9 nginx               # kill all processes named nginx
```

`pkill` uses pattern matching, while `killall` matches the executable name exactly. Both accept signal options (`-SIGTERM`, `-9`, etc.).

### 2.4 Preventing accidental kills  

* Use `-i` (interactive) with `killall` to confirm each PID.  
* Double‑check the PID with `ps -p $PID -o pid,ppid,user,stat,command`.  

---

## Part 3 – Interactive Inspection with `htop`

`htop` is not required for the tutorial, but it speeds up the “find‑and‑kill” loop.

```bash
sudo apt-get install htop   # Debian/Ubuntu
htop
```

Key shortcuts:

| Key | Action |
|-----|--------|
| `F3` | Search (type part of the command) |
| `F4` | Filter (show only matching rows) |
| `F5` | Tree view (parent‑child) |
| `F9` | Kill – choose a signal from a menu |
| `Space` | Tag multiple processes for batch actions |
| `s` | Sort by column (CPU, MEM, TIME, etc.) |

You can also start `htop` with a filter:

```bash
htop -p $(pgrep -d',' python)
```

This opens `htop` showing only Python processes, making it easy to spot the one that’s stuck.

---

## Part 4 – Running and Managing Background Jobs

### 4.1 The `&` operator  

Appending `&` runs a command **asynchronously**, returning control to the shell immediately.

```bash
sleep 120 &    # runs for 2 minutes in the background
echo "I can type now"
```

The shell prints a job number and PID, e.g., `[1] 5678`.

### 4.2 Listing jobs  

```bash
jobs            # shows jobs started in the current shell
```

Output example:

```
[1]+  Running                 sleep 120 &
[2]-  Stopped                 vim
```

### 4.3 Bringing a job to the foreground  

```bash
fg %1           # bring job 1 back to the foreground
```

### 4.4 Sending a job to the background (after stopping)  

```bash
Ctrl+Z          # stop the current foreground job (SIGSTOP)
bg %2           # resume job 2 in the background
```

### 4.5 Disowning a job  

If you want a background job to survive after you close the terminal, use `disown`:

```bash
sleep 300 &     # start a long sleep
disown %1       # remove it from the shell's job table
```

Now `jobs` won’t list it, but the process keeps running (check with `ps`).

---

## Hands‑On Example – Find, Inspect, and Kill a Stuck Process

Below is a reproducible scenario you can try on any Linux box.

```bash
#!/usr/bin/env bash
# demo_stuck.sh – creates a process that loops forever
while true; do
    echo "Working..."   # writes to stdout every second
    sleep 1
done
```

1. **Run the script in the background**  

   ```bash
   chmod +x demo_stuck.sh
   ./demo_stuck.sh &
   ```

   You’ll see something like `[1] 12345`.

2. **Verify it’s running**  

   ```bash
   ps -p 12345 -o pid,stat,command
   ```

   Expected output:

   ```
   PID STAT COMMAND
   12345 S   ./demo_stuck.sh
   ```

3. **Inspect with `htop`** (optional)  

   ```bash
   htop -p 12345
   ```

   Look at the `%CPU` column – a tight loop often shows near‑100% CPU.

4. **Kill it gracefully**  

   ```bash
   kill 12345          # sends SIGTERM
   sleep 1
   ps -p 12345 && echo "still alive" || echo "gone"
   ```

   If the script ignored SIGTERM (unlikely here), force it:

   ```bash
   kill -9 12345
   ```

5. **Clean up the job table**  

   ```bash
   jobs               # should show no jobs, because the process is gone
   ```

You’ve now gone from “a runaway script” to “clean termination” using only terminal commands.

---

## Common Mistakes & Troubleshooting

- **Killing the wrong PID** – Always double‑check with `ps -p $PID -o pid,command`.  
- **Using `kill -9` first** – This bypasses any cleanup code. Prefer `SIGTERM` (default) and only fall back to `SIGKILL` if the process refuses to exit.  
- **Forgetting the `&` when you meant to background** – The shell will block, making you think the command hung. Add `&` and re‑run.  
- **`jobs` shows “Stopped” but the process still consumes CPU** – The process may have been resumed by another shell or a script. Use `ps -o pid,stat,command` to see the real state.  
- **`htop` not installed** – Install via your distro’s package manager (`sudo dnf install htop`, `sudo pacman -S htop`, etc.) or fall back to `top`.

---

## Try It Yourself

Create a background job that writes a large file, then stop it, move it to the background, and finally kill it:

```bash
dd if=/dev/zero of=bigfile bs=1M count=100 &
# 1. Press Ctrl+Z to stop it
# 2. Run `bg %1` to resume in background
# 3. Find its PID with `ps aux | grep bigfile`
# 4. Kill it with `kill -TERM <PID>`
```

Observe how the file size stops growing after the kill.

---

## What’s Next?

- **Signal handling in code** – Learn how programs can catch `SIGTERM` and clean up resources.  
- **Using `systemd` to manage long‑running services** – Replace manual `nohup`/`&` with proper unit files.  
- **Advanced `htop` customizations** – Columns, filters, and user‑defined meters.  
- **Process accounting with `pidstat` and `perf`** – Dive deeper into performance analysis.

---

Keep this page bookmarked; you’ll return to it whenever a process misbehaves.
