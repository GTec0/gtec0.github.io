---
layout: post
title: "rsync: back up and sync files without the fear"
subtitle: "Learn how to use rsync safely with dry‑runs, five everyday recipes, and SSH remote sync—perfect for developers who want reliable backups."
date: 2026-10-05
categories: []
tags: ["Linux", "Backup", "Developer Tips"]
thumbnail-img: /assets/images/banners/rsync-back-up-and-sync-files-without-the-fear-banner.png
share-img: /assets/images/banners/rsync-back-up-and-sync-files-without-the-fear-banner.png
author: Asahluma Tyika
---
# rsync: back up and sync files without the fear  

## Intro – What rsync is and why you’ll love it  

`rsync` is a command‑line utility that copies files and directories while minimizing data transfer. It does this by comparing source and destination, sending only the differences.  

* **Why use rsync?**  
  * Fast incremental backups  
  * Works over SSH, so you can sync to another machine without extra tools  
  * Precise inclusion/exclusion rules – you decide exactly what gets copied  

* **Who is this tutorial for?**  
  * Beginners who have never run `rsync` before  
  * Intermediate developers who need a repeatable backup script  
  * Anyone who prefers to see what will happen before any file is touched  

The key to a fearless workflow is the *dry‑run* (`-n` / `--dry-run`) flag. It shows you the exact actions `rsync` would take, without moving a single byte.

---

## Part 1 – Core concepts (the building blocks)

| Option | Short | Meaning | Example |
|--------|-------|---------|---------|
| `-a`   | `--archive` | Recursively copy and preserve permissions, timestamps, symlinks, etc. | `rsync -a src/ dest/` |
| `-v`   | `--verbose` | Print what’s happening | `rsync -av src/ dest/` |
| `-n`   | `--dry-run` | Show actions without changing anything | `rsync -avn src/ dest/` |
| `--delete` | – | Remove files in the destination that no longer exist in the source | `rsync -av --delete src/ dest/` |
| `-e`   | `--rsh` | Specify remote shell (usually SSH) | `rsync -av -e ssh src/ user@host:/path/` |
| `--exclude` | – | Skip files matching a pattern | `rsync -av --exclude '*.log' src/ dest/` |
| `--progress` | – | Show a progress bar for large transfers | `rsync -av --progress src/ dest/` |

**How rsync decides what to copy**  
1. It builds a file list for the source.  
2. It builds a file list for the destination (or pretends to, if `--dry-run`).  
3. It compares size and modification time (unless you add `-c` to compare checksums).  
4. Only the mismatched files are sent.

---

## Part 2 – Five everyday recipes  

### 1️⃣ One‑off backup of a project folder (local)

```bash
# Dry‑run first – see what would be copied
rsync -avn --progress ~/projects/myapp/ ~/backups/myapp/

# If it looks good, run the real command
rsync -av --progress ~/projects/myapp/ ~/backups/myapp/
```

*Why the trailing slash?*  
`myapp/` (with slash) copies the *contents* of the folder. `myapp` (no slash) copies the folder itself, creating `~/backups/myapp/myapp/`.

---

### 2️⃣ Incremental backup with deletion (keep mirror)

```bash
rsync -avn --delete ~/documents/ ~/backups/documents/
```

When you’re satisfied:

```bash
rsync -av --delete ~/documents/ ~/backups/documents/
```

Now `~/backups/documents/` is an exact mirror of the source – any file removed locally disappears from the backup as well.

---

### 3️⃣ Excluding unwanted files (e.g., node_modules, logs)

```bash
rsync -avn \
  --exclude 'node_modules/' \
  --exclude '*.log' \
  --exclude '.git/' \
  ~/projects/webapp/ ~/backups/webapp/
```

Run without `-n` after confirming the list.

---

### 4️⃣ Syncing a large media library to an external drive

```bash
rsync -avn --progress \
  --exclude 'Thumbs.db' \
  /mnt/media/ /media/usb-drive/media/
```

The `--progress` flag is handy when copying gigabytes of video files.

---

### 5️⃣ Using a file‑list to back up selected items only

Create `list.txt`:

```text
Documents/report.pdf
Pictures/vacation/
src/main.py
```

Then:

```bash
rsync -avn --files-from=list.txt ~/ ~/backups/selected/
```

Only the paths listed (relative to `$HOME`) are processed.

---

## Part 3 – Sync over SSH (remote backup)

### 3.1 Why SSH?  
SSH encrypts traffic, authenticates the remote host, and requires no extra ports. `rsync` can invoke SSH automatically with the `-e ssh` option (default on most systems).

### 3.2 One‑time remote copy (dry‑run)

```bash
rsync -avn -e ssh ~/projects/myapp/ user@backup.example.com:/srv/backups/myapp/
```

You’ll see something like:

```
sending incremental file list
./
src/
src/main.py
src/utils.py
```

If the list matches expectations, drop the `-n`.

### 3.3 Setting up key‑based authentication (optional but recommended)

```bash
# Generate a key pair if you don’t have one
ssh-keygen -t ed25519 -C "my laptop"

# Copy the public key to the remote host
ssh-copy-id user@backup.example.com
```

Now `rsync` won’t prompt for a password, making it perfect for cron jobs.

### 3.4 Cron job example (daily remote backup)

Add to `crontab -e`:

```cron
0 2 * * * rsync -az --delete -e ssh ~/projects/myapp/ user@backup.example.com:/srv/backups/myapp/ >> ~/logs/rsync.log 2>&1
```

* `-z` compresses data on the wire, saving bandwidth.  
* `>>` appends output to a log file for later review.

---

## Hands‑on example (full, runnable script)

Create a file called `backup_myapp.sh` in your home directory:

```bash
#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------------------------------------
# Config – edit these values for your environment
# ----------------------------------------------------------------------
SRC="${HOME}/projects/myapp/"
DEST="${HOME}/backups/myapp/"
REMOTE_USER="user"
REMOTE_HOST="backup.example.com"
REMOTE_PATH="/srv/backups/myapp/"

# ----------------------------------------------------------------------
# Step 1 – Dry run locally
# ----------------------------------------------------------------------
echo "=== Dry run: local copy ==="
rsync -avn --delete "${SRC}" "${DEST}"

# ----------------------------------------------------------------------
# Step 2 – Real local copy (uncomment to enable)
# ----------------------------------------------------------------------
# echo "=== Performing local backup ==="
# rsync -av --delete "${SRC}" "${DEST}"

# ----------------------------------------------------------------------
# Step 3 – Dry run to remote host
# ----------------------------------------------------------------------
echo "=== Dry run: remote copy ==="
rsync -avn -e ssh --delete "${SRC}" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}"

# ----------------------------------------------------------------------
# Step 4 – Real remote copy (uncomment to enable)
# ----------------------------------------------------------------------
# echo "=== Performing remote backup ==="
# rsync -avz -e ssh --delete "${SRC}" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}"
```

Make it executable and run:

```bash
chmod +x ~/backup_myapp.sh
./backup_myapp.sh
```

You’ll see two dry‑run reports (local and remote). When you’re happy, remove the `#` before the real copy sections and re‑run.

---

## Common mistakes / troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| “rsync: change directory ... failed: No such file or directory (2)” | Destination path missing or typo | Create the target folder first: `mkdir -p ~/backups/myapp/` |
| No files are copied, but output shows “sending incremental file list” with nothing else | Trailing slash misuse – source path ends with `/` when you meant the folder itself | Remove the trailing slash or add one, depending on desired behavior |
| “permission denied (publickey)” when using SSH | SSH key not installed on remote or wrong user | Run `ssh-copy-id user@host` and verify with `ssh user@host` |
| “rsync: link_stat ... failed: Permission denied (13)” | Source files not readable by the current user | Run the command with `sudo` (if appropriate) or adjust file permissions |
| Transfer is very slow over LAN | `-z` (compression) is enabled on a fast local network | Drop `-z` for LAN transfers; keep it for WAN/Internet |

---

## Try it yourself  

1. Pick a small folder (e.g., `~/tmp/test/`) and create a couple of files inside.  
2. Run a dry‑run to a new backup location:  

   ```bash
   rsync -avn ~/tmp/test/ ~/tmp/backup/
   ```  

3. Verify the output matches the files you created.  
4. Remove `-n` and run the real copy.  
5. Delete one file from `~/tmp/test/`, then run a dry‑run with `--delete` to see the removal listed.  

You’ve just performed a safe, incremental backup!

---

## What’s next  

* **Versioned backups** – use `--link-dest` to keep daily snapshots without duplicating unchanged files.  
* **Filtering with `--filter`** – more powerful include/exclude patterns for complex projects.  
* **Parallel rsync with `--jobs`** (available in newer rsync versions) to speed up multi‑disk backups.  
* **Automated integrity checks** – combine `rsync` with `sha256sum` to verify copies after a run.  

Stay tuned for the next post where we turn these ideas into a fully automated, self‑healing backup system.

*Bookmark this guide for your next backup adventure.*
