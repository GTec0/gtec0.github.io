---
layout: post
title: "SSH keys and config: stop typing passwords"
subtitle: "Learn how to generate SSH keys, add them to GitHub, and configure ~/.ssh/config so you never type a password again."
date: 2026-09-30
categories: []
tags: ["Linux", "GitHub", "Developer Tips"]
thumbnail-img: /assets/images/banners/ssh-keys-and-config-stop-typing-passwords-banner.png
share-img: /assets/images/banners/ssh-keys-and-config-stop-typing-passwords-banner.png
author: Asahluma Tyika
---
## Introduction – why SSH keys matter

When you clone, pull, or push a Git repository over SSH you’re asked for a password **every** time. That extra keystroke is harmless, but it slows you down and forces you to keep a password in memory.  

SSH keys solve the problem by proving your identity with a cryptographic key pair instead of a password. Once the public key lives on the remote server (GitHub, GitLab, your own VPS) and the private key stays on your workstation, the SSH daemon can verify you instantly.

**Who should read this?**  
* Beginners who have used `git clone https://…` and are tired of typing passwords.  
* Intermediate developers who want a reproducible, secure login method for any SSH‑enabled service.

By the end of this tutorial you will:

1. Create an RSA or Ed25519 key pair.  
2. Register the public key with GitHub.  
3. Write a simple `~/.ssh/config` entry so `git` and `ssh` know which key to use.  
4. Verify the setup with `ssh -T git@github.com`.

---

## Part 1 – Generate an SSH key pair

### 1.1 Choose a key type

| Type      | Security (2026) | Key size | Recommended for | Notes |
|-----------|----------------|----------|----------------|-------|
| RSA       | Good (2048‑4096) | 4096 bits | Legacy systems | Larger files, slower |
| Ed25519   | Excellent      | Fixed (256‑bit) | Modern Linux/macOS | Small, fast, default on most distros |

**Recommendation:** Use **Ed25519** unless you need RSA for an old server.

### 1.2 Create the key

```bash
# Replace "myemail@example.com" with your real email – it helps you identify the key later
ssh-keygen -t ed25519 -C "myemail@example.com" -f ~/.ssh/id_ed25519 -N ""
```

* `-t ed25519` – key type.  
* `-C` – comment stored in the public key.  
* `-f` – output file (private key).  
* `-N ""` – empty passphrase (you can add one later with `ssh-add`).

If you prefer RSA:

```bash
ssh-keygen -t rsa -b 4096 -C "myemail@example.com" -f ~/.ssh/id_rsa -N ""
```

### 1.3 Verify permissions

SSH refuses to use keys that are readable by others.

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519   # or id_rsa
chmod 644 ~/.ssh/id_ed25519.pub
```

You can double‑check with:

```bash
ls -l ~/.ssh
```

Output should look like:

```
drwx------ 2 user user 4096 Sep 30 12:34 .
-rw------- 1 user user  534 Sep 30 12:34 id_ed25519
-rw-r--r-- 1 user user  146 Sep 30 12:34 id_ed25519.pub
```

---

## Part 2 – Add the public key to GitHub

### 2.1 Copy the public key

```bash
cat ~/.ssh/id_ed25519.pub | xclip -selection clipboard   # Linux with X11
# or
pbcopy < ~/.ssh/id_ed25519.pub                         # macOS
# or, if you have no clipboard tool:
cat ~/.ssh/id_ed25519.pub
```

### 2.2 Paste it on GitHub

1. Log in to GitHub.  
2. Click your avatar → **Settings** → **SSH and GPG keys** → **New SSH key**.  
3. Give it a title like “My‑Laptop‑2026”.  
4. Paste the key into the *Key* field and click **Add SSH key**.

GitHub will now trust any connection that proves possession of the matching private key.

---

## Part 3 – Configure `~/.ssh/config` for painless use

A `config` file lets you:

* Give a short alias to a host (`github.com` → `gh`).  
* Force a particular key for a host.  
* Set options like `AddKeysToAgent` and `UseKeychain` (macOS).

Create or edit the file:

```bash
nano ~/.ssh/config
```

Add the following block:

```config
# GitHub shortcut
Host gh
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    AddKeysToAgent yes
    IdentitiesOnly yes
```

### What each line does

| Directive | Meaning |
|-----------|---------|
| `Host gh` | Alias you will type (`ssh gh`). |
| `HostName github.com` | Real hostname. |
| `User git` | GitHub expects the SSH user `git`. |
| `IdentityFile` | Path to the private key to use. |
| `AddKeysToAgent yes` | Loads the key into `ssh-agent` automatically. |
| `IdentitiesOnly yes` | Prevents SSH from offering other keys that might cause “Too many authentication failures”. |

You can add more blocks for other services (e.g., a personal VPS) using the same pattern.

After saving, reload the config (optional):

```bash
ssh-add -l   # list keys already in the agent
ssh-add ~/.ssh/id_ed25519   # add if not present
```

---

## Hands‑on example – from zero to push without a password

Run the whole sequence in a fresh terminal. Replace `myemail@example.com` with your own.

```bash
# 1️⃣ Generate an Ed25519 key (no passphrase)
ssh-keygen -t ed25519 -C "myemail@example.com" -f ~/.ssh/id_ed25519 -N ""

# 2️⃣ Fix permissions (just in case)
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# 3️⃣ Copy the public key to clipboard (Linux)
cat ~/.ssh/id_ed25519.pub | xclip -selection clipboard

# 4️⃣ (Manual) Paste into GitHub → Settings → SSH and GPG keys → New SSH key

# 5️⃣ Create a config entry for GitHub
cat >> ~/.ssh/config <<'EOF'
Host gh
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    AddKeysToAgent yes
    IdentitiesOnly yes
EOF

# 6️⃣ Ensure the key is loaded in the agent
ssh-add -l >/dev/null 2>&1 || eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 7️⃣ Test the connection
ssh -T git@gh
```

**Expected output** (first time you connect, you’ll see a fingerprint prompt; type `yes`):

```
Hi <username>! You've successfully authenticated, but GitHub does not provide shell access.
```

If you see the message above, the key works and you can now clone using the short alias:

```bash
git clone git@gh:your‑username/your‑repo.git
```

No password prompt appears.

---

## Common mistakes / troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `Permission denied (publickey).` | Private key file is readable by others (`chmod 644`). | `chmod 600 ~/.ssh/id_ed25519` and `chmod 700 ~/.ssh`. |
| `ssh: Could not resolve hostname gh: Name or service not known` | No `Host gh` entry or typo in `~/.ssh/config`. | Open `~/.ssh/config` and verify the alias line. |
| `Too many authentication failures` | SSH offers many keys before the right one. | Ensure `IdentitiesOnly yes` is set in the host block. |
| First connection asks “Are you sure you want to continue connecting (yes/no)?” repeatedly | The host key is not added to `known_hosts`. | Accept the prompt once; it will be stored automatically. |
| `ssh-add: Could not open a connection to your authentication agent` | `ssh-agent` not running. | Start it: `eval "$(ssh-agent -s)"` then `ssh-add ~/.ssh/id_ed25519`. |

---

## Try it yourself

1. **Create a second key pair** named `id_ed25519_work` for a different GitHub account or a private server.  
2. Add a new block to `~/.ssh/config` with alias `gh-work` that points to the same `HostName github.com` but uses `IdentityFile ~/.ssh/id_ed25519_work`.  
3. Verify with `ssh -T git@gh-work` that the correct account is authenticated.

---

## What’s next

- **SSH agent forwarding** – use your local key on remote servers without copying it.  
- **Deploy keys vs personal keys** – best practices for CI/CD pipelines.  
- **Multiple Git hosts** – configure separate entries for GitLab, Bitbucket, and self‑hosted Git.  
- **Key rotation** – automate revoking old keys and adding new ones on GitHub.

Bookmark this page and run the hands‑on steps; you’ll never type a Git password again.
