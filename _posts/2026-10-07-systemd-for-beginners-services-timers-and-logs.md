---
layout: post
title: "systemd for beginners: services, timers and logs"
subtitle: "Master Linux background tasks with systemd. Learn how to write custom unit files, schedule runs with timers, and inspect logs using journalctl."
date: 2026-10-07
categories: []
tags: ["Linux", "DevOps"]
thumbnail-img: /assets/images/banners/systemd-for-beginners-services-timers-and-logs-banner.png
share-img: /assets/images/banners/systemd-for-beginners-services-timers-and-logs-banner.png
author: Asahluma Tyika
---
# systemd for beginners: services, timers and logs

## What is systemd and why should you care?

If you have ever deployed a web app, a Discord bot, or a Python script to a Linux server, you have probably run into the classic problem: *How do I keep this running after I close my SSH terminal?*

You might have reached for `screen`, `tmux`, or `nohup`. While those work in a pinch during development, they fall apart in production. If your server reboots for a kernel update or your app crashes due to an unhandled exception, your process simply dies. Nobody restarts it.

That is where **systemd** comes in.

On almost every modern Linux distribution (Ubuntu, Debian, Fedora, Arch, CentOS/RHEL), systemd is the **init system**—the very first process that boots (Process ID 1, or PID 1). Its job is to bring the system to life, spin up hardware interfaces, and manage services throughout their entire lifecycle.

When you manage your applications with systemd, you get three massive benefits out of the box:
1. **Reliability:** Your app starts automatically when the server boots and restarts automatically if it crashes.
2. **Unified logging:** Everything your app prints to standard output (`stdout`) and standard error (`stderr`) is captured into a structured log database.
3. **Clean task scheduling:** You can replace messy `cron` jobs with robust, monitored timers.

This guide is for any developer or junior sysadmin who wants to stop fighting Linux processes and start running production-ready background services.

---

## Part 1: The anatomy of a systemd service

systemd manages resources using text configuration files called **unit files**. A unit file that manages a running process has the `.service` extension.

System-wide unit files typically live in `/etc/systemd/system/`. Files in this directory override any defaults provided by the operating system.

A standard service file is split into three main sections: `[Unit]`, `[Service]`, and `[Install]`.

```ini
[Unit]
Description=My Background Worker
After=network.target

[Service]
Type=simple
User=sammy
WorkingDirectory=/opt/myworker
ExecStart=/usr/bin/python3 /opt/myworker/worker.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Let's break down what each line actually does:

| Directive | Section | Purpose |
| :--- | :--- | :--- |
| `Description` | `[Unit]` | A human-readable name shown in status outputs and logs. |
| `After` | `[Unit]` | Tells systemd to wait until specific milestones (like network connectivity) are ready before launching. |
| `Type` | `[Service]` | Usually `simple` (process runs in the foreground) or `exec` (starts immediately and considers the unit up once executed). |
| `User` | `[Service]` | Drops root privileges and runs the process as an unprivileged user for security. |
| `WorkingDirectory`| `[Service]` | Sets the current working directory before executing the command. |
| `ExecStart` | `[Service]` | The full, absolute path to the binary and its arguments. |
| `Restart` | `[Service]` | Defines when to restart the app. `on-failure` restarts on non-zero exit codes; `always` restarts regardless of exit code. |
| `RestartSec` | `[Service]` | Time to wait before attempting a restart (prevents crash loops from pinning your CPU). |
| `WantedBy` | `[Install]` | Tells systemd when to enable this service. `multi-user.target` roughly means "standard boot with networking and multi-user support." |

---

## Part 2: Managing services with systemctl

The primary tool you use to inspect and control systemd is `systemctl`. 

Here are the essential commands you will use daily:

| Command | What it does |
| :--- | :--- |
| `sudo systemctl start <name>` | Starts the service immediately. |
| `sudo systemctl stop <name>` | Stops the running service cleanly (sends `SIGTERM`, then `SIGKILL`). |
| `sudo systemctl restart <name>` | Stops and then starts the service. |
| `sudo systemctl reload <name>` | Tells the app to reload its configuration without dropping connections (if supported). |
| `systemctl status <name>` | Shows if the service is running, its PID, memory usage, and recent log entries. |
| `sudo systemctl enable <name>` | Configures the service to launch automatically at system boot. |
| `sudo systemctl disable <name>` | Prevents the service from starting at system boot. |
| `sudo systemctl daemon-reload` | Reloads systemd's internal cache after you create or edit a unit file. |

> **Pro Tip:** Whenever you edit or create a file in `/etc/systemd/system/`, systemd will not see the changes until you run `sudo systemctl daemon-reload`.

---

## Part 3: Reading logs with journalctl

Before systemd, logs were scattered across text files in `/var/log/` (`syslog`, `auth.log`, `messages`), and every app had to manage its own file rotation.

systemd routes all standard output (`stdout`) and standard error (`stderr`) streams directly into a centralized binary log engine called the **journal**. You read these logs using `journalctl`.

Because the logs are indexed, querying them is fast and precise. Here are the most useful command combinations:

```bash
# View all logs for a specific service
journalctl -u myworker.service

# Follow logs in real time (like tail -f)
journalctl -u myworker.service -f

# Jump straight to the end of the log output
journalctl -u myworker.service -e

# View the last 50 log lines
journalctl -u myworker.service -n 50

# View logs generated since the current system boot
journalctl -u myworker.service -b

# Filter logs by time window
journalctl -u myworker.service --since "1 hour ago"
journalctl -u myworker.service --since "2024-03-01 09:00:00" --until "2024-03-01 10:00:00"
```

No log rotation configuration, no disk-filling plain text files without limits, and no guesswork about where an unhandled exception went.

---

## Part 4: Replacing cron with systemd timers

For decades, `cron` was the default way to run scheduled tasks on Unix. While simple, `cron` is silent when tasks fail, has awkward syntax for non-standard schedules, and makes logging difficult.

systemd provides an alternative: **timers**.

A systemd timer is composed of two companion files that share the same base name:
1. A `.service` file: Defines *what* command to run.
2. A `.timer` file: Defines *when* to run it.

For example, a timer file (`/etc/systemd/system/cleanup.timer`) looks like this:

```ini
[Unit]
Description=Run cleanup script nightly

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

* `OnCalendar=*-*-* 02:00:00`: Runs every day at 2:00 AM.
* `Persistent=true`: If the server was turned off at 2:00 AM, systemd will run the missed job immediately once the machine boots back up.

You enable and start the timer (not the service):

```bash
sudo systemctl enable --now cleanup.timer
```

To see all active timers across your system and when they will fire next, run:

```bash
systemctl list-timers
```

---

## Hands-on example: Deploying a real background logger

Let's build a working service from scratch. We will write a small Python status logger, wire it up as a systemd service, and inspect its runtime health.

### Step 1: Create the application script

First, create a folder for our application and a non-root system user to run it:

```bash
sudo useradd -r -s /bin/false appuser
sudo mkdir -p /opt/status-checker
```

Create a script named `/opt/status-checker/checker.py`:

```bash
sudo nano /opt/status-checker/checker.py
```

Paste the following code into the file:

```python
import time
import sys
import os

print("Status checker service starting up...", flush=True)

while True:
    load1, load5, load15 = os.getloadavg()
    print(f"System Load: {load1:.2f}, {load5:.2f}, {load15:.2f}", flush=True)
    time.sleep(10)
```

Make the script executable and set file permissions:

```bash
sudo chmod +x /opt/status-checker/checker.py
sudo chown -R appuser:appuser /opt/status-checker
```

### Step 2: Create the systemd service file

Create a new service definition file:

```bash
sudo nano /etc/systemd/system/status-checker.service
```

Add the following unit configuration:

```ini
[Unit]
Description=System Load Status Checker
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/status-checker
ExecStart=/usr/bin/python3 /opt/status-checker/checker.py
Restart=on-failure
RestartSec=3s

[Install]
WantedBy=multi-user.target
```

### Step 3: Load, start, and verify the service

Tell systemd to read your new file:

```bash
sudo systemctl daemon-reload
```

Start the service and configure it to boot automatically:

```bash
sudo systemctl enable --now status-checker.service
```

Check the active state of your service:

```bash
systemctl status status-checker.service
```

You should see output similar to this:

```text
● status-checker.service - System Load Status Checker
     Loaded: loaded (/etc/systemd/system/status-checker.service; enabled; vendor preset: enabled)
     Active: active (running) since Fri 2024-03-15 14:22:01 UTC; 4s ago
   Main PID: 18452 (python3)
      Tasks: 1 (limit: 2257)
     Memory: 6.8M
        CPU: 18ms
     CGroup: /system.slice/status-checker.service
             └─18452 /usr/bin/python3 /opt/status-checker/checker.py
```

### Step 4: Stream the logs

Watch your script log output in real time:

```bash
journalctl -u status-checker.service -f
```

Output:
```text
Mar 15 14:22:01 server python3[18452]: Status checker service starting up...
Mar 15 14:22:01 server python3[18452]: System Load: 0.12, 0.08, 0.02
Mar 15 14:22:11 server python3[18452]: System Load: 0.11, 0.08, 0.02
```

Press `Ctrl + C` to stop viewing the logs. The service continues running in the background.

---

## Common mistakes / troubleshooting

Even experienced developers make minor slip-ups when working with unit files. Keep an eye out for these four common tripwires:

* **Using relative binary paths in `ExecStart`:** systemd does not inherit your personal shell's `$PATH`. Running `ExecStart=python3 app.py` will fail with an error like `code=exited, status=203/EXEC`. Always use absolute paths: `ExecStart=/usr/bin/python3 /opt/app/app.py`. Find paths using `which python3` or `which node`.
* **Forgetting to run `daemon-reload`:** If you edit an existing `.service` file and immediately run `systemctl restart`, systemd will execute the old configuration cached in memory. Always run `sudo systemctl daemon-reload` right after saving unit edits.
* **Buffer delays hiding Python logs:** By default, Python buffers stdout when it is not connected to an interactive terminal. If your Python script seems to produce no journal logs, add `-u` to your Python command (`ExecStart=/usr/bin/python3 -u ...`) or set `flush=True` in your print calls.
* **Missing `[Install]` block when trying to enable:** If you run `sudo systemctl enable myservice` and see an error saying the unit does not have an install section, ensure your unit file includes `[Install]` with `WantedBy=multi-user.target`. Without this, systemd does not know into which boot target the unit should be linked.

---

## Try it yourself

Put your new knowledge to the test with this quick exercise:

1. Write a shell script at `/usr/local/bin/daily-backup.sh` that prints `Backup started at $(date)` and touches a temporary file `/tmp/backup-complete.txt`.
2. Create `/etc/systemd/system/daily-backup.service` (configured with `Type=oneshot`) to execute the script.
3. Create `/etc/systemd/system/daily-backup.timer` configured to run every minute using `OnCalendar=*-*-* *:*:00`.
4. Enable and start the timer with `systemctl enable --now daily-backup.timer`.
5. Run `systemctl list-timers` to verify when it will trigger, then verify the log output in `journalctl -u daily-backup.service`.

---

## What's next

Now that you can run background daemons and review their logs, you have unlocked the fundamentals of Linux service orchestration. From here, you can explore deeper features:

* **Securing services with sandboxing:** Restrict what your unit can touch using flags like `ProtectSystem=strict`, `ProtectHome=true`, and `NoNewPrivileges=true`.
* **Managing environment variables:** Securely pass secrets and configuration flags using the `EnvironmentFile=` directive.
* **User-level systemd units:** Run custom services without needing `sudo` privileges using `systemctl --user`.

Bookmark this page so you don't have to Google the syntax for `journalctl` flags or unit file sections the next time a server reboot stops your script.
