---
layout: post
title: "Check disk space like a detective: df, du and ncdu"
subtitle: "Learn how to track down rogue logs, hidden caches, and bloated folders on Linux using df, du, and ncdu in five simple, practical steps."
date: 2026-10-13
categories: []
tags: ["Linux", "Terminal", "Beginner"]
thumbnail-img: /assets/images/banners/check-disk-space-like-a-detective-df-du-and-ncdu-banner.png
share-img: /assets/images/banners/check-disk-space-like-a-detective-df-du-and-ncdu-banner.png
author: Asahluma Tyika
---
# Check disk space like a detective: df, du and ncdu

You fire up a Docker build, pull a large Git repository, or try to save a critical database backup, and your terminal abruptly slams the brakes:

```text
No space left on device
```

Running out of disk space is a rite of passage for every developer and sysadmin. When it happens, your first instinct might be to randomly delete files in your home directory or reboot the machine. That rarely works, and deleting the wrong directory can break your entire environment.

To solve disk crunches quickly, you need to approach your filesystem like an investigator. You do not guess where the bloat lives; you follow the evidence.

This tutorial gives you a systematic 5-command playbook using three built-in and open-source command-line tools: `df`, `du`, and `ncdu`. Whether you run a tiny Ubuntu VPS, manage a Raspberry Pi, or work on a local Linux desktop, this workflow helps you locate and eliminate disk hogs in minutes.

---

## Part 1: Get the bird's-eye view with `df`

Before looking for individual fat files, you must answer two fundamental questions: *Which physical drive is full?* and *Are we actually out of storage bytes or out of index slots?* 

The `df` utility stands for **disk free**. It queries your filesystems and reports how much capacity remains.

### Command 1: Check storage volume usage

Run this command first:

```bash
df -h
```

The `-h` flag converts machine block counts into human-readable units (megabytes, gigabytes, and terabytes).

Your terminal prints a table that looks like this:

```text
Filesystem      Size  Used Avail Use% Mounted on
udev            1.9G     0  1.9G   0% /dev
tmpfs           392M  1.1M  391M   1% /run
/dev/sda1        40G   38G  420M  99% /
/dev/sda15      124M   11M  114M   9% /boot/efi
```

Scan the **Use%** and **Mounted on** columns:
* Look for partitions sitting at `90%` to `100%`.
* Identify the mount point. In the output above, `/dev/sda1` is mounted on `/` (the root directory) and consumes 99% of its 40 GB capacity. That tells you the problem lives somewhere inside the main system root, not on an external drive or a separate `/boot` partition.

### Command 2: Check inode exhaustion

Sometimes `df -h` shows plenty of free space—say, 15 GB available—yet Linux still throws `No space left on device`. 

Filesystems allocate a finite number of **inodes** (index nodes) when formatted. An inode stores metadata about a single file or directory. If an application (such as an unmonitored mail queue or a runaway session generator) creates millions of tiny, empty files, you will exhaust your inodes before you run out of actual gigabytes.

Check inode usage with:

```bash
df -ih
```

The `-i` flag shifts the report from byte capacity to inode counts:

| Flag | Meaning | Use When... |
| :--- | :--- | :--- |
| `df -h` | Human-readable byte capacity | You need to see total GB used vs. remaining. |
| `df -ih` | Human-readable inode capacity | You suspect millions of tiny files are choking the filesystem. |
| `df -T` | Print filesystem type | You need to verify if a mount is `ext4`, `xfs`, or `btrfs`. |

If `IUse%` on your root mount shows 100%, your drive is not out of raw gigabytes; it has run out of pointers to hold new files.

---

## Part 2: Hunt specific directories with `du`

Now that `df` has pointed you to the offending partition (for example, `/`), you need to zoom in. The `du` command stands for **disk usage**. It traverses directories and calculates the exact footprint of folders and their contents.

### Command 3: Summarize top-level folders

If you run plain `du`, it spits out a line for every subfolder on your drive—flooding your terminal with thousands of lines of unreadable noise. 

Instead, ask for a **summary** of immediate folders:

```bash
sudo du -sh /* 2>/dev/null
```

Here is what those flags do:
* `-s`: Summary mode. Shows only the total for the specified target, rather than every child folder inside it.
* `-h`: Human-readable format (MB, GB).
* `/*`: Expands across every folder at the root level (`/var`, `/home`, `/etc`, `/usr`, etc.).
* `sudo`: Ensures restricted system folders (like `/root` or `/var/log`) can be calculated.
* `2>/dev/null`: Silences permission warnings and virtual filesystem errors.

Example output:

```text
14M     /etc
4.2G    /home
0       /proc
28G     /var
1.2G    /usr
```

The culprit is immediately obvious: `/var` is taking up 28 GB of a 40 GB drive.

### Command 4: Find the top 10 space hogs in that path

Once you spot the bloated folder, drill down into it and sort the biggest offenders straight to the bottom (or top) of your screen. 

Run:

```bash
sudo du -ah --max-depth=1 /var 2>/dev/null | sort -rh | head -n 10
```

Breaking down this pipeline:
* `-a`: Include individual files, not just folders.
* `--max-depth=1`: Inspect only one level deeper so the output stays readable.
* `sort -rh`: Sorts numbers using human-readable numeric values (`-h`) in reverse order (`-r`), placing the biggest items at the top.
* `head -n 10`: Limits the screen output to the top 10 offenders.

Example output:

```text
28G     /var
22G     /var/log
4.1G    /var/lib
1.2G    /var/cache
```

Now you know `/var/log` contains 22 GB of data. Repeat the exact same command targeting `/var/log`:

```bash
sudo du -ah --max-depth=1 /var/log 2>/dev/null | sort -rh | head -n 10
```

If you see an unrotated `syslog` or an application log that grew to 18 GB, you have found your suspect.

---

## Part 3: Interactive visual navigation with `ncdu`

Drilling down through nested directories using repeated `du` commands works well, but it can feel tedious when files are buried deep inside project caches or hidden directories.

Enter `ncdu` (**NCurses Disk Usage**). It wraps the speed of `du` in a text-based, interactive menu inside your shell.

### Command 5: Launch the interactive detective

Install it via your package manager if it is not already present:

```bash
# On Debian / Ubuntu:
sudo apt update && sudo apt install -y ncdu

# On Fedora / RHEL:
sudo dnf install -y ncdu

# On Arch Linux:
sudo pacman -S ncdu
```

Once installed, launch it against the directory you want to inspect:

```bash
sudo ncdu /var/log
```

If you want to scan an entire partition from root without accidentally crossing into mounted network drives or external USBs, add the `-x` flag:

```bash
sudo ncdu -x /
```

`ncdu` scans the tree and displays an interactive view:

```text
ncdu 1.15.1 ~ Use the arrow keys to navigate, press ? for help
--- /var/log -------------------------------------------------------------
   18.4 GiB [##########]  app-error.log
    2.1 GiB [#         ]  syslog.1
    1.1 GiB [          ]  journal/
  320.0 MiB [          ]  nginx/
   48.0 KiB [          ]  dpkg.log
```

### Essential `ncdu` shortcuts

* **Up / Down arrows**: Move through the list.
* **Enter / Right arrow**: Step inside the highlighted folder.
* **Left arrow**: Go back to the parent folder.
* **n**: Sort items by name.
* **s**: Sort items by file size.
* **d**: Prompt to delete the highlighted file or folder right on the spot (use with caution!).
* **q**: Quit and return to your terminal prompt.

---

## Hands-on example

Let's simulate a disk-space incident inside a temporary workspace, investigate it using our 5-command workflow, and clean it up.

Run these commands in your terminal:

```bash
# 1. Create an isolated practice sandbox
mkdir -p ~/disk-detective-lab/nested/deep-cache
cd ~/disk-detective-lab

# 2. Generate two large dummy files using fallocate (100MB and 250MB)
fallocate -l 100M app_archive.tar
fallocate -l 250M nested/deep-cache/runaway_trace.log

# 3. Add a few smaller files
touch notes.txt config.yaml nested/seed.json
```

Now, act like the detective:

```bash
# Step 1: Check overall usage of your lab
du -sh ~/disk-detective-lab
```

You will see `351M` total used.

```bash
# Step 2: Sort the top items in this directory
du -ah --max-depth=1 ~/disk-detective-lab | sort -rh
```

You will see `nested` consumes `250M`, while `app_archive.tar` consumes `100M`.

```bash
# Step 3: Launch ncdu to investigate nested directories
ncdu ~/disk-detective-lab
```

Use your **Down arrow** to highlight `nested/`, press **Enter**, highlight `deep-cache/`, press **Enter**, and you will see `runaway_trace.log` sitting at 250 MiB.

When you are done testing, clean up the lab:

```bash
cd ~
rm -rf ~/disk-detective-lab
```

---

## Common mistakes / troubleshooting

* **The deleted file that will not free up space:** You ran `rm /var/log/app.log`, but `df -h` still reports that your drive is 100% full. Why? A running service still holds an open file handle to that deleted file. The Linux kernel will not free the storage blocks until that process exits or restarts. Check for open deleted files using:
  ```bash
  sudo lsof +L1
  ```
  Look for the process name and restart the service (e.g., `sudo systemctl restart nginx`).

* **Skipping `sudo` when checking disk usage:** Running `du` as a normal user causes silent skips on root-owned directories. If your disk is full due to Docker volumes in `/var/lib/docker`, a non-root `du` command skips that folder entirely, leading you to believe the disk is empty when it is not.

* **Crossing mount points by mistake:** Scanning root with `du` or `ncdu` without caution can cause your command to crawl through mounted remote NFS shares, attached backup drives, or thousands of container virtual layers. Always use `ncdu -x /` to lock the scan to the single physical filesystem.

* **Treating `df` and `du` numbers as identical:** `df` reports filesystem-level block allocation directly from the kernel, while `du` counts up files individually. Differences can occur due to uncommitted writes, open-deleted files, or filesystem reserved space (Linux typically reserves 5% of root space for the `root` user).

---

## Try it yourself

Run this one-liner on your machine right now to print your current user directory's 5 largest space-hogging directories or files:

```bash
du -ah --max-depth=2 ~ 2>/dev/null | sort -rh | head -n 5
```

Take a look at the results. Is your disk space being spent on ancient `.cache` folders, forgotten node modules, or old ISO images?

---

## What's next

Now that you can track down rogue files in under two minutes, the next step is making sure your disks never fill up unexpectedly in the first place:

* **Automate log cleanup:** Learn how `logrotate` keeps system logs from ballooning over time.
* **Tame systemd journals:** Trim stored journal logs using `journalctl --vacuum-time=7d`.
* **Prune container clutter:** Reclaim gigabytes by scrubbing stopped containers and dangling images with `docker system prune`.

Bookmark this quick guide so you never have to scramble during an emergency disk alert again.
