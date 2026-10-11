---
layout: post
title: "SSH like a pro: config file, jump hosts and tunnels"
subtitle: "Stop typing messy IP addresses and port flags. Learn how to master ~/.ssh/config, traverse jump hosts, and create local port tunnels like a pro."
date: 2026-10-11
categories: []
tags: ["Linux", "Networking", "Developer Tips"]
thumbnail-img: /assets/images/banners/ssh-like-a-pro-config-file-jump-hosts-and-tunnels-banner.png
share-img: /assets/images/banners/ssh-like-a-pro-config-file-jump-hosts-and-tunnels-banner.png
author: Asahluma Tyika
---
## Stop typing long SSH commands

If you work with remote servers, your terminal history probably looks something like this:

```bash
ssh -i ~/.ssh/production-key.pem -p 2222 ubuntu@198.51.100.42
```

Typing that out once is annoying. Typing it ten times a day is a waste of time. It gets worse when servers sit inside private subnets behind a bastion host, or when you need to view an internal dashboard running on `localhost:8080` of a remote box.

SSH has built-in tools to solve these exact headaches:
* **The SSH config file** turns complex connection strings into short aliases.
* **Jump hosts** let you hop through a gateway server to reach private machines seamlessly.
* **Local port forwarding (`-L`)** tunnels remote services securely onto your laptop so you can view them in your local browser or database GUI.

This guide is for any developer who knows the basics of SSH (`ssh user@host`) and wants to move from clunky one-liners to a clean, automated workflow.

---

## Part 1: Taming your connections with ~/.ssh/config

Instead of remembering IP addresses, usernames, custom ports, and specific key files, you can store those details in a plain-text configuration file located at `~/.ssh/config`.

If the file doesn't exist yet, create it and secure its permissions:

```bash
touch ~/.ssh/config
chmod 600 ~/.ssh/config
```

### Basic config syntax

Open `~/.ssh/config` in your favorite editor. The file uses simple `Key Value` pairs grouped under a `Host` nickname:

```text
Host dev
    HostName 198.51.100.42
    User ubuntu
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
```

With this entry saved, you no longer run that long command. You just run:

```bash
ssh dev
```

The SSH client looks up `dev`, finds the IP address, user, port, and key, and connects automatically.

### Useful config directives

| Directive | What it does | Example |
| :--- | :--- | :--- |
| `Host` | The nickname you type after `ssh` | `Host staging` |
| `HostName` | The real IP address or domain | `HostName api.example.internal` |
| `User` | The remote login account | `User ec2-user` |
| `IdentityFile` | Path to your private key | `IdentityFile ~/.ssh/my_key` |
| `Port` | Custom SSH port (default is 22) | `Port 2200` |
| `ServerAliveInterval` | Sends a keep-alive ping every X seconds to avoid timeouts | `ServerAliveInterval 60` |

### Using wildcards for global settings

You can apply settings across all servers by placing a wildcard block at the bottom of the file:

```text
Host *
    ServerAliveInterval 30
    ServerAliveCountMax 3
    AddKeysToAgent yes
```

Now, every connection you make automatically pings the server every 30 seconds to keep inactive sessions alive.

---

## Part 2: Reaching private servers with Jump Hosts

In real production environments, database servers and internal APIs rarely have public IP addresses. Instead, they sit in a private Virtual Private Cloud (VPC) behind a single, hardened gateway known as a **bastion** or **jump host**.

Historically, people used agent forwarding or awkward `ProxyCommand` netcat pipes to hop through these bastions. Modern OpenSSH has a much cleaner solution: the `ProxyJump` directive (or the `-J` flag on the CLI).

### How ProxyJump works

Instead of you logging into the bastion, opening a shell, and running `ssh` again from inside the bastion, OpenSSH automatically tunnels your connection through the bastion directly to the private target. Your private key stays on your local machine.

Here is how you write that in `~/.ssh/config`:

```text
# The public-facing gateway
Host bastion
    HostName 203.0.113.10
    User admin
    IdentityFile ~/.ssh/bastion_key

# The hidden internal server
Host internal-db
    HostName 10.0.1.50
    User postgres
    IdentityFile ~/.ssh/internal_key
    ProxyJump bastion
```

Now, run:

```bash
ssh internal-db
```

SSH talks to `bastion`, creates an encrypted tunnel to `10.0.1.50`, and logs you in as `postgres`—all in one smooth step.

---

## Part 3: Local port forwarding (-L) explained

Have you ever had an internal dashboard, a Redis instance, or a Postgres database running on a remote server that binds only to `127.0.0.1`?

You cannot reach it in your local browser because it is not exposed to the public internet. This is where **local port forwarding** comes in.

The `-L` flag maps a port on your local machine (`localhost`) to an address and port accessible from the remote server.

### The formula

```bash
ssh -L local_port:destination_host:destination_port user@remote_server
```

Think of it as reading left-to-right:
1. `local_port`: The port on your laptop you want to open.
2. `destination_host`: The host as seen *from the remote server's perspective* (often `localhost` or an internal IP).
3. `destination_port`: The port the service is actually listening on remotely.

### Example scenario

A remote server runs an administrative web panel on port `8080`. That port is blocked by the server firewall, but you have SSH access.

Run this:

```bash
ssh -N -L 9000:localhost:8080 dev
```

* `-N` tells SSH: "Do not execute a remote command or open a shell prompt. Just keep the connection open for tunneling."
* `-L 9000:localhost:8080` routes any traffic sent to your laptop's port `9000` through the SSH connection to `localhost:8080` on `dev`.

Open your browser, navigate to `http://localhost:9000`, and you are viewing the remote app safely over an encrypted channel.

---

## Hands-on example: Tunneling an internal web service

Let's run a complete, verifiable test. We will simulate an internal service on a remote machine using Python's built-in HTTP server, forward that port back to our laptop, and view it locally.

### Step 1: Add the host to your config

Add your remote machine to `~/.ssh/config`:

```text
Host lab
    HostName 192.0.2.15
    User debian
    IdentityFile ~/.ssh/id_ed25519
```

*(Replace the `HostName` and `User` with your real remote server details.)*

### Step 2: Start an isolated service on the remote server

SSH into the machine:

```bash
ssh lab
```

Once logged in, start Python's built-in web server bound **strictly** to the remote machine's loopback interface so it is invisible to the public internet:

```bash
python3 -m http.server 8888 --bind 127.0.0.1
```

You should see output like:
```text
Serving HTTP on 127.0.0.1 port 8888 (http://127.0.0.1:8888/) ...
```

Leave this terminal window open.

### Step 3: Create the tunnel from your local machine

Open a **new** terminal tab on your laptop and run:

```bash
ssh -N -L 3000:127.0.0.1:8888 lab
```

The command will look like it is hanging—that is expected because `-N` runs quietly in the background without giving you a shell prompt.

### Step 4: Verify the connection

Open a third terminal tab on your laptop (or open your local web browser) and test the tunnel:

```bash
curl http://localhost:3000
```

You will get back a directory listing HTML page from your remote server. Back in the terminal where Python is running, you will see a `200 OK` log entry showing that the request came from `127.0.0.1`.

To stop the tunnel, hit `Ctrl + C` in the terminal where you ran the `ssh -N -L` command.

---

## Common mistakes and troubleshooting

* **`Bad owner or permissions on ~/.ssh/config`**: OpenSSH strictly verifies file permissions. If other users can write to your config or keys, SSH rejects them. Run `chmod 600 ~/.ssh/config` and `chmod 700 ~/.ssh`.
* **`bind [127.0.0.1]:3000: Address already in use`**: The local port you picked is already taken by another application running on your laptop. Change the first number to an unused port, like `3001` or `8000`.
* **`channel 2: open failed: connect failed: Connection refused`**: The SSH tunnel was created successfully, but when you sent traffic to it, the remote machine could not find any app listening on the specified destination port. Make sure your target service (e.g., Python, PostgreSQL) is actively running on the remote side.
* **The tunnel dies silently when your laptop sleeps**: Add `ServerAliveInterval 15` and `ExitOnForwardFailure yes` to your `~/.ssh/config`. `ExitOnForwardFailure` ensures that if SSH fails to bind the port, it exits immediately with an error rather than hanging silently.

---

## Try it yourself

Create a shortcut for your port tunnel directly in your `~/.ssh/config` file so you don't even have to remember the `-L` syntax.

1. Open `~/.ssh/config` and add the `LocalForward` directive under a dedicated host block:

```text
Host lab-tunnel
    HostName 192.0.2.15
    User debian
    LocalForward 3000 127.0.0.1:8888
```

2. Run `ssh -N lab-tunnel`.
3. Check `curl http://localhost:3000` to confirm your config-based tunnel works identically to the manual flag!

---

## What's next

Now that your daily SSH workflow is faster and cleaner, here are a few techniques you can explore next:

* **Dynamic port forwarding (`-D`)**: Turn your remote server into a temporary, secure SOCKS5 proxy to route all your browser traffic through it.
* **Reverse tunnels (`-R`)**: Expose a port running on your local laptop to a remote server—handy for testing webhooks locally without services like ngrok.
* **SSH multiplexing (`ControlMaster`)**: Reuse existing SSH connections to make opening new sessions to the same host instantaneous.

We will cover reverse tunnels and SSH multiplexing in a follow-up post.

Bookmark this page so you have these recipes ready the next time you need to jump through a bastion or wire up a quick local tunnel.
