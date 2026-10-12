---
layout: post
title: "scp and sftp: move files to your server the easy way"
subtitle: "Learn five practical scp and sftp recipes—progress bars, resumable transfers, and batch mode—plus a hands‑on example and troubleshooting tips."
date: 2026-10-12
categories: []
tags: ["Linux", "Beginner"]
thumbnail-img: /assets/images/banners/scp-and-sftp-move-files-to-your-server-the-easy-way-banner.png
share-img: /assets/images/banners/scp-and-sftp-move-files-to-your-server-the-easy-way-banner.png
author: Asahluma Tyika
---
# scp and sftp: move files to your server the easy way  

**Tags:** Linux, Beginner  

## Introduction – what, why, and who  

Transferring files between your workstation and a remote Linux server is a daily task for developers, sysadmins, and hobbyists. Two tools come pre‑installed on almost every Unix‑like system:

| Tool | Typical use | Strength |
|------|--------------|----------|
| `scp` | Quick one‑off copy | Simple syntax, works over SSH |
| `sftp` | Interactive or scripted file management | Built‑in progress, can resume partially transferred files |

If you’ve ever stared at a blinking cursor while a 2 GB archive drags on, you’ll appreciate the recipes in this guide. They show how to see real‑time progress, restart a broken transfer, and automate bulk moves—all without installing extra software.

The tutorial assumes you have:

* A local Linux/macOS terminal (or Windows WSL) with SSH access to the remote host.  
* A user account on the remote host that can log in with a password or SSH key.  

No prior knowledge of `scp` or `sftp` is required.

---

## Part 1 – Basic `scp` copy  

The classic syntax is:

```bash
scp /path/to/local/file user@remote.example.com:/path/to/remote/
```

* `user` – your remote username.  
* `remote.example.com` – the server’s address.  
* The colon separates the host from the remote path.

**Key options**

| Option | Meaning |
|--------|---------|
| `-r`   | Recursively copy directories. |
| `-C`   | Enable SSH compression (good for text files). |
| `-p`   | Preserve timestamps, mode, and ownership. |
| `-i /path/to/key` | Use a specific private key. |

A simple example:

```bash
scp -C ~/projects/report.pdf alice@10.0.0.5:/home/alice/docs/
```

The command blocks until the transfer finishes. No progress bar is shown, which is fine for tiny files but not for larger ones.

---

## Part 2 – `scp` with a progress bar  

Modern OpenSSH ships with the `-v` (verbose) flag, but the easiest way to get a progress indicator is to pipe through `pv` (pipe viewer). Install it once:

```bash
# Debian/Ubuntu
sudo apt-get install pv
# Fedora
sudo dnf install pv
# macOS (Homebrew)
brew install pv
```

Then run:

```bash
pv ~/large/video.mov | ssh alice@10.0.0.5 "cat > /home/alice/videos/video.mov"
```

`pv` prints a live progress line (bytes transferred, rate, ETA). Because we’re using plain `ssh` + `cat`, we avoid the built‑in `scp` progress, which is limited to a simple “percentage” that disappears on line‑wrap.

If you prefer to stay within `scp`, the `-l` flag limits bandwidth and indirectly gives you a sense of speed, but it does **not** show a bar. For most users, the `pv` approach is the most informative.

---

## Part 3 – Resumable copy with `rsync` over SSH (the scp fallback)  

`scp` cannot resume a partially transferred file. The usual workaround is to use `rsync`, which ships on almost every server and client:

```bash
rsync -avz --partial --progress -e ssh ~/backup.tar.gz alice@10.0.0.5:/home/alice/backups/
```

* `-a` – archive mode (preserves permissions, timestamps).  
* `-v` – verbose.  
* `-z` – compress data during transfer.  
* `--partial` – keep the partially transferred file so the next run can continue.  
* `--progress` – show a progress bar.  
* `-e ssh` – tell `rsync` to use SSH for transport.

If the connection drops, re‑run the same command; `rsync` will pick up where it left off.

---

## Part 4 – Interactive `sftp` with built‑in progress  

` sftp` opens an interactive shell that looks like `ftp`, but everything runs over SSH. Start it with:

```bash
sftp alice@10.0.0.5
```

Inside the prompt you can run:

```
sftp> put -r ~/myproject .
```

The `put` command shows a progress line automatically:

```
myproject/ 100%   12MB   1.2MB/s   00:10
```

**Useful shortcuts**

| Command | Description |
|---------|-------------|
| `lcd /local/dir` | Change local directory. |
| `cd /remote/dir` | Change remote directory. |
| `ls` / `lls` | List remote / local files. |
| `get file` | Download a file. |
| `reget file` | Resume a partially downloaded file. |
| `reput file` | Resume a partially uploaded file (requires server support). |

`reput` is the **resume** counterpart for uploads. Not all servers enable it, but most modern OpenSSH builds do.

---

## Part 5 – Batch `sftp` for scripted, resumable uploads  

When you need to move many files automatically (e.g., CI pipelines), create a batch file and feed it to `sftp` with the `-b` option.

**Step 1 – Write `upload.txt`**

```text
# upload.txt – one command per line
lcd /home/user/build
cd /var/www/html
put -r *
```

**Step 2 – Run the batch**

```bash
sftp -b upload.txt -oBatchMode=no alice@10.0.0.5
```

The `-oBatchMode=no` flag forces `sftp` to prompt for a password if you haven’t set up key authentication.

**Resume support**  
If the batch aborts, edit the file to replace `put -r *` with `reput -r *`. The `reput` command tells `sftp` to continue any files that already exist on the remote side.

---

## Hands‑on example – copy a 1 GB test file with progress and resume  

1. **Create a dummy file** (run on your local machine):

```bash
dd if=/dev/urandom of=bigfile.bin bs=1M count=1024
```

2. **Start a transfer with `rsync`** (you’ll see progress and can interrupt with `Ctrl+C`):

```bash
rsync -avz --partial --progress -e ssh bigfile.bin alice@10.0.0.5:/home/alice/
```

3. **Simulate a network hiccup** – after a few seconds, press `Ctrl+C`. The partial file stays on the remote host.

4. **Resume the transfer** by re‑running the same command:

```bash
rsync -avz --partial --progress -e ssh bigfile.bin alice@10.0.0.5:/home/alice/
```

`rsync` will report “file has changed” and only send the missing blocks.

5. **Verify integrity** (optional):

```bash
ssh alice@10.0.0.5 "sha256sum /home/alice/bigfile.bin"
sha256sum bigfile.bin
```

Both hashes should match, confirming a successful, resumable copy.

---

## Common mistakes & troubleshooting  

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| “ssh: connect to host … port 22: Connection timed out” | Wrong hostname or firewall blocking SSH | Ping the host, check `ssh` port, or ask the admin to open port 22. |
| “scp: ambiguous target” | Missing colon or space in the remote path | Ensure the remote part is `user@host:/path` (colon required). |
| “sftp> put: No such file or directory” | Local file path wrong or `lcd` not set correctly | Use `lcd /full/path` before `put`, or give an absolute path. |
| “rsync: connection unexpectedly closed” | Network drop mid‑transfer | Re‑run the same `rsync` command; `--partial` will resume. |
| “reput: command not found” | Remote server runs an older OpenSSH that lacks `reput` | Upgrade the remote OpenSSH or fall back to `rsync`. |

---

## Try it yourself  

1. Create a small directory (`testdir`) with a few text files.  
2. Use **Part 4** to open an `sftp` session and upload the directory with `put -r`.  
3. Interrupt the session (`Ctrl+C`), then reconnect and run `reput -r testdir` to finish the upload.  

Observe the progress lines and verify that the remote directory contains all files.

---

## What’s next  

* **Secure key‑based authentication** – eliminate password prompts for automated scripts.  
* **Using `sshfs`** – mount a remote filesystem locally and copy files with any GUI tool.  
* **Speed tuning** – experiment with `-C` (compression) vs. raw transfer for binary data.  
* **Automated backups** – combine `rsync` with `cron` to keep a remote snapshot of your project folder.

Bookmark this page and try the hands‑on example; you’ll never stare at a frozen terminal again.
