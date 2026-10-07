---
layout: post
title: "cron in 15 minutes: schedule anything on Linux"
subtitle: "Learn the crontab syntax, set up three useful scheduled jobs with logging, and avoid common pitfalls—all in under 15 minutes."
date: 2026-10-07
categories: []
tags: ["Linux", "automation", "Beginner"]
thumbnail-img: /assets/images/banners/cron-in-15-minutes-schedule-anything-on-linux-banner.png
share-img: /assets/images/banners/cron-in-15-minutes-schedule-anything-on-linux-banner.png
author: Asahluma Tyika
---
## Intro: What is cron and why you’ll love it  
Cron is the built‑in scheduler on every Linux distribution. It lets you run a command or script at exact minutes, hours, days, or months—without you having to remember to start it manually.  

* **What you’ll get:** a quick reference chart for the crontab fields, three ready‑to‑copy job examples that write to log files, and a step‑by‑step walk‑through you can try on your own machine.  
* **Who it’s for:** beginners who have never touched a crontab, plus intermediate users who want a tidy cheat‑sheet and reliable logging patterns.  

By the end of this tutorial you’ll be able to schedule anything from a nightly backup to a daily reminder, and you’ll know how to debug the most common cron hiccups.

---

## Part 1: Core concepts – the crontab syntax chart  

A crontab line has **five time fields** followed by the command to run:

| Field | Allowed values | Meaning |
|-------|----------------|---------|
| `minute` | `0‑59` | The minute of the hour |
| `hour`   | `0‑23` | The hour of the day (24‑hour clock) |
| `day of month` | `1‑31` | Which calendar day |
| `month` | `1‑12` (or names `jan`‑`dec`) | Which month |
| `day of week` | `0‑7` (0 or 7 = Sunday, 1 = Monday…) (or names `sun`‑`sat`) | Which weekday |

You can combine values with commas, ranges with hyphens, and step values with a slash. The asterisk `*` means “every possible value”.

### Quick‑reference cheat sheet  

| Expression | Runs… |
|------------|-------|
| `* * * * *` | Every minute |
| `0 * * * *` | At minute 0 of every hour (top of the hour) |
| `30 2 * * *` | At 02:30 am every day |
| `15 14 1 * *` | At 14:15 on the 1st of each month |
| `0 9 * * 1‑5` | At 09:00 on Monday‑Friday |
| `*/10 * * * *` | Every 10 minutes |
| `0 0 * * 0` | Midnight on Sunday (weekly) |
| `0 0 1 */2 *` | Midnight on the 1st day of every **odd** month |

Remember: the order is **minute → hour → day‑of‑month → month → day‑of‑week**. A common mistake is swapping hour and minute; the table above helps you keep them straight.

---

## Part 2: Editing crontab, environment, and logging  

### 2.1 Opening your crontab  

```bash
crontab -e
```

The first time you run this, you’ll be asked to pick an editor (nano is the safest default). The file you edit belongs to your user, so the jobs run with your permissions.

### 2.2 The environment matters  

Cron runs with a **minimal environment**. Variables like `PATH`, `HOME`, or `LANG` are not the same as in your interactive shell. To avoid “command not found” errors:

* Use absolute paths (`/usr/bin/rsync` instead of just `rsync`), **or**
* Set `PATH` at the top of the crontab:

```bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

You can also source your profile file inside the command, but that adds overhead.

### 2.3 Logging every job  

Cron already captures stdout and stderr and emails them to the user (if a local MTA is configured). For a portable, file‑based log you can redirect output yourself:

```bash
* * * * * /path/to/command >> /var/log/mycron.log 2>&1
```

* `>>` appends, `>` overwrites.
* `2>&1` merges stderr into the same file.

If you want a timestamp for each line, wrap the command with `logger` or a tiny shell snippet:

```bash
* * * * * { echo "$(date +\%Y-\%m-\%d\ %H:\%M:\%S) Starting job"; /path/to/command; echo "$(date +\%Y-\%m-\%d\ %H:\%M:\%S) Job finished"; } >> /var/log/mycron.log 2>&1
```

That pattern will be reused in the three real‑world examples below.

---

## Part 3: Three real jobs with logging  

### 3.1 Nightly home‑directory backup (rsync)  

```bash
# 02:30 am every day – backup $HOME to /backup/home
30 2 * * * { echo "$(date +\%F\ %T) Starting backup"; /usr/bin/rsync -a --delete $HOME/ /backup/home/; echo "$(date +\%F\ %T) Backup finished"; } >> /var/log/backup.log 2>&1
```

* `-a` preserves permissions, timestamps, etc.  
* `--delete` removes files that no longer exist in the source.  
* Log file grows slowly; rotate it with `logrotate` later.

### 3.2 Keep a website alive – HTTP ping every 15 minutes  

```bash
# Every 15 minutes – curl the site and log status code
*/15 * * * * { echo "$(date +\%F\ %T) Pinging example.com"; STATUS=$(/usr/bin/curl -o /dev/null -s -w "%{http_code}" https://example.com); echo "HTTP status: $STATUS"; } >> /var/log/ping.log 2>&1
```

If the status code isn’t `200`, you can add a notification step (e.g., `mail` or a Slack webhook). The log will show a line for each check.

### 3.3 Clean up old temporary files – weekly  

```bash
# Sunday at 04:00 am – delete files older than 7 days in /tmp/myapp
0 4 * * 0 { echo "$(date +\%F\ %T) Cleaning /tmp/myapp"; /usr/bin/find /tmp/myapp -type f -mtime +7 -print -delete; echo "Cleanup done"; } >> /var/log/cleanup.log 2>&1
```

* `-mtime +7` selects files modified more than 7 days ago.  
* `-print` logs each file that will be removed, which is handy for audit trails.

All three jobs are ready to copy‑paste into `crontab -e`. Adjust paths, usernames, and frequencies to match your own setup.

---

## Hands‑on example: Write a timestamp to a log every minute  

Let’s create the simplest possible cron job and see the log grow in real time.

1. **Create a log file (ensure write permission).**

```bash
sudo touch /var/log/minute.log
sudo chown $(whoami):$(whoami) /var/log/minute.log
```

2. **Open your crontab.**

```bash
crontab -e
```

3. **Add the following line at the bottom.**  
   (It appends a timestamp each minute.)

```bash
* * * * * echo "$(date +\%Y-\%m-\%d\ %H:\%M:\%S) – minute tick" >> /var/log/minute.log 2>&1
```

4. **Save and exit** (in nano: `Ctrl+O`, `Enter`, `Ctrl+X`).  

5. **Watch the log grow.** Open a second terminal and run:

```bash
tail -f /var/log/minute.log
```

You should see a new line appear at the start of each minute. If you don’t, move to the troubleshooting section.

---

## Common mistakes / troubleshooting  

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Job never runs | Wrong time fields (e.g., swapped hour/minute) | Double‑check the order against the syntax chart. |
| “command not found” in log | Cron’s PATH is missing the binary location | Use absolute paths or prepend `PATH=…` at the top of the crontab. |
| Log file empty | Output is being sent to email instead of file | Ensure you have `>> /path/to/log 2>&1` at the end of the line. |
| Duplicate entries in log | Cron runs the job multiple times (e.g., both user and system crontabs) | Run `crontab -l` and inspect `/etc/crontab` and `/etc/cron.d/*` for overlapping definitions. |
| Permissions denied on log file | Cron user cannot write to the log location | Change ownership (`chown`) or choose a directory the user can write to, e.g., `$HOME/cron.log`. |

Tip: After editing, you can verify the schedule with `crontab -l` and test the command manually (run it in a shell) to confirm it works before relying on cron.

---

## Try it yourself  

**Exercise:** Set up a job that backs up the file `~/notes.txt` to `~/notes-backup/` **every hour** and logs the result to `~/notes-backup/backup.log`.  

*Hint:* Use `cp -u` (copy only when the source is newer) and the timestamp wrapper from the examples. Verify by editing the file, waiting an hour, and checking the log.  

---

## What’s next  

- **Log rotation:** Learn how to configure `logrotate` so your cron logs don’t fill the disk.  
- **Email alerts:** Hook `mail` or `sendmail` into a cron job to get instant failure notifications.  
- **Complex schedules:** Explore the `@yearly`, `@monthly`, `@weekly`, `@daily`, and `@reboot` shortcuts.  
- **System‑wide cron:** Dive into `/etc/crontab` and the `/etc/cron.d/` directory for root‑level tasks.  

Give those a try, and you’ll have a fully automated Linux workstation in no time.

*Bookmark this page for a quick reference whenever you need to schedule something on Linux.*
