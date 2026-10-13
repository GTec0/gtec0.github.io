---
layout: post
title: "Ports demystified: ss, lsof and talking to localhost"
subtitle: "Learn how to find and free “Address already in use” ports on Linux with ss, lsof, and simple localhost tests."
date: 2026-10-13
categories: []
tags: ["Linux", "Networking", "Beginner"]
thumbnail-img: /assets/images/banners/ports-demystified-ss-lsof-and-talking-to-localhost-banner.png
share-img: /assets/images/banners/ports-demystified-ss-lsof-and-talking-to-localhost-banner.png
author: Asahluma Tyika
---
## Intro: What’s the problem and who this is for  

When you start a web server, a database, or any networked service, you’ll often see an error like:

```
Error: address already in use
```

It means something else is already listening on the same **IP + port** combination you’re trying to bind.  
If you’re a beginner or a hobbyist, the error feels cryptic, and the tools to investigate it ( `ss`, `lsof` ) look intimidating.

This tutorial is for **Linux users who know a little shell** and want a practical, step‑by‑step way to:

1. Understand what a *port* is and why “localhost” matters.  
2. Locate the offending process with `ss` and `lsof`.  
3. Free the port or change your configuration.  

All commands are runnable on any recent distribution (Ubuntu, Fedora, Arch, etc.). No extra packages are required.

---

## Part 1: Core concepts – ports, localhost, and “address already in use”

| Concept | What it means | Typical value |
|---------|---------------|---------------|
| **IP address** | Numeric identifier of a network interface. | `127.0.0.1` (loopback), `192.168.1.42` (LAN) |
| **Port** | 16‑bit number that distinguishes many services on the same IP. | `80` (HTTP), `5432` (PostgreSQL) |
| **Socket** | Combination of IP + port + protocol (TCP/UDP). | `127.0.0.1:8080/TCP` |
| **localhost** | The loopback interface; traffic never leaves the host. | Always resolves to `127.0.0.1` (IPv4) or `::1` (IPv6) |
| **Address already in use** | Kernel refuses to bind because another socket already occupies the same IP + port + protocol. | Happens when you start a second copy of a server, or when a previous run didn’t exit cleanly. |

**Why “localhost” matters**  
When you test a service locally, you usually bind to `127.0.0.1` (or `0.0.0.0` to listen on all interfaces). Binding to the loopback address isolates the service from the outside world, which is great for development. However, the same “address already in use” rule applies: only **one** process can bind to `127.0.0.1:PORT/TCP` at a time.

---

## Part 2: Using `ss` to list listening sockets

`ss` (socket statistics) ships with the `iproute2` package and is faster than the older `netstat`. The most useful invocations are:

```bash
# Show all listening TCP sockets (IPv4 + IPv6)
ss -tlnp
```

Explanation of flags:

| Flag | Meaning |
|------|---------|
| `-t` | TCP only |
| `-l` | Listening sockets |
| `-n` | Show numeric addresses (no DNS look‑ups) |
| `-p` | Show the PID / program name that owns the socket |

Sample output:

```
State      Recv-Q Send-Q   Local Address:Port   Peer Address:Port
LISTEN     0      128      127.0.0.1:5432       *:*        users:(("postgres",pid=1245,fd=5))
LISTEN     0      511      0.0.0.0:22           *:*        users:(("sshd",pid=743,fd=3))
```

To focus on a single port, add a filter:

```bash
ss -tlnp 'sport = :8080'
```

If the output shows a process, you’ve found the culprit.

---

## Part 3: Using `lsof` as an alternative

`lsof` (“list open files”) can also reveal which process has a network socket open. It’s especially handy when you need to see *both* TCP and UDP or when you want to grep for a program name.

```bash
# List all network sockets that are listening
sudo lsof -i -P -n | grep LISTEN
```

Flags:

| Flag | Meaning |
|------|---------|
| `-i` | Show network files |
| `-P` | Show ports as numbers (no service name lookup) |
| `-n` | Skip host name resolution |
| `sudo` | Required because non‑root users can’t see other users’ sockets |

To look for a specific port:

```bash
sudo lsof -iTCP:8080 -sTCP:LISTEN
```

Typical output:

```
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3  3172 alice   4u  IPv4  12345      0t0  TCP 127.0.0.1:8080 (LISTEN)
```

Now you know *exactly* which PID is holding the port.

---

## Hands‑on example: Freeing port 8080 for a simple Flask app

We'll create a tiny Python Flask server that listens on `127.0.0.1:8080`. Then we'll simulate a conflict, locate the offender, and resolve it.

### 1. Install Flask (if you don’t have it)

```bash
python3 -m venv venv
source venv/bin/activate
pip install Flask
```

### 2. Minimal Flask app (`app.py`)

```python
# app.py
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from Flask!"

if __name__ == "__main__":
    # Bind explicitly to localhost:8080
    app.run(host="127.0.0.1", port=8080)
```

### 3. Run it in the background

```bash
nohup python3 app.py > flask.log 2>&1 &
echo $!   # prints the PID, e.g. 4521
```

You can test it:

```bash
curl http://127.0.0.1:8080/
# → Hello from Flask!
```

### 4. Simulate a conflict – start a second server on the same port

Open a new terminal and run:

```bash
python3 -c "import socket, time; s=socket.socket(); s.bind(('127.0.0.1',8080)); s.listen(); time.sleep(60)"
```

You’ll see:

```
OSError: [Errno 98] Address already in use
```

### 5. Find the offending process with `ss`

```bash
ss -tlnp 'sport = :8080'
```

Output (example):

```
State      Recv-Q Send-Q   Local Address:Port   Peer Address:Port
LISTEN     0      128      127.0.0.1:8080       *:*        users:(("python3",pid=4521,fd=3))
```

The PID is **4521** – that’s our Flask app.

### 6. Kill the process (or change its port)

```bash
kill 4521          # graceful SIGTERM
# If it doesn’t exit:
kill -9 4521       # forceful SIGKILL
```

Verify the port is free:

```bash
ss -tlnp 'sport = :8080'   # should return nothing
```

### 7. Restart the second server (the one we wrote with `socket`)

```bash
python3 -c "import socket, time; s=socket.socket(); s.bind(('127.0.0.1',8080)); s.listen(); print('Listening...'); time.sleep(60)"
```

Now the socket command works because the Flask process is gone.

---

## Common mistakes / troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ss -tlnp` shows **no** PID column (empty) | You ran the command without `sudo`. Non‑root users can’t see other users’ sockets. | Prefix with `sudo`. |
| `lsof` returns **Permission denied** | Same as above – you need root privileges to see all sockets. | Run `sudo lsof …`. |
| Killing the PID doesn’t free the port | The process has *multiple* threads each holding a socket, or it spawned a child that inherited the socket. | Use `pkill -f <program>` or check `ps -ef | grep <pid>` for children, then kill them. |
| Port still appears busy after `kill` | The process is in *TIME_WAIT* state (common for TCP). | Wait a few seconds, or enable `SO_REUSEADDR` in your code (advanced). |
| `ss` shows `0.0.0.0:PORT` but you expected `127.0.0.1:PORT` | The service bound to **all** interfaces, not just localhost. | Adjust the program’s bind address (e.g., `host="127.0.0.1"`). |

---

## Try it yourself

1. **Create a conflict**: Run any simple TCP server (Python, Netcat, etc.) on port 9090.  
2. **Locate it**: Use `ss -tlnp 'sport = :9090'` and `sudo lsof -iTCP:9090 -sTCP:LISTEN`.  
3. **Free it**: Kill the PID, then verify the port is empty.

If you can repeat the steps without errors, you’ve mastered the basics.

---

## What’s next

- **Understanding `SO_REUSEADDR` and `SO_REUSEPORT`** – how to design services that can restart without “address already in use”.  
- **Using `iptables` or `firewalld` to block external access while keeping localhost open**.  
- **Automating port cleanup with a small Bash helper script**.  
- **Diagnosing UDP port conflicts** – similar tools, slightly different flags.

Stay tuned for the follow‑up post that dives into those topics!

*Bookmark this page for the next time “address already in use” pops up.*
