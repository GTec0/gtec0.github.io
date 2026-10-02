---
layout: post
title: "tmux for beginners: multiplex your terminal"
subtitle: "Learn how to use tmux to split terminal windows, keep remote tasks running in the background, and manage multiple shell sessions like a pro."
date: 2026-10-02
categories: []
tags: ["Linux", "Terminal", "Developer Tips"]
thumbnail-img: /assets/images/banners/tmux-for-beginners-multiplex-your-terminal-banner.png
share-img: /assets/images/banners/tmux-for-beginners-multiplex-your-terminal-banner.png
author: Asahluma Tyika
---
## Why You Need tmux in Your Terminal Toolkit

Have you ever run a long database migration or a build script over SSH, only for your Wi-Fi to flicker and kill the entire process? Or maybe you find yourself opening six different terminal tabs just to run a server, watch application logs, edit files, and check git status.

This is where **tmux** (short for **T**erminal **Mu**ltiple**x**er) changes your workflow. 

Think of tmux as a window manager running directly inside your terminal. It gives you two superpowers:

1. **Persistent sessions:** You can start a job on a server, detach from the session, close your laptop, commute home, and reattach right where you left off. The process keeps running.
2. **Workspaces in a single window:** You can slice one terminal screen into multiple panes and tabs without reaching for your mouse or opening separate terminal emulator windows.

Whether you run Ubuntu, macOS, WSL on Windows, or manage remote cloud instances, tmux is a must-have tool. Let's walk through how it works, how to control it, and how to build a complete workflow with it.

---

## Part 1: The tmux Hierarchy

To use tmux without getting lost, you only need to understand three core layers:

```text
[ Session: "api-dev" ]
  ├── [ Window 1: "editor" ]
  │     └── Pane 1 (Neovim)
  └── [ Window 2: "runtime" ]
        ├── Pane 1 (Node.js server)
        └── Pane 2 (tailing logs)
```

* **Sessions:** An isolated workspace dedicated to a specific project. You can have multiple sessions running simultaneously (e.g., `work`, `dotfiles`, `learning`).
* **Windows:** Tabs inside a session. Each window occupies the full terminal screen until you switch to another.
* **Panes:** Sub-divisions inside a single window. You can split a window horizontally and vertically into multiple active command lines.

---

## Part 2: The Magic Prefix Key

Every tmux command begins with a shortcut called the **Prefix**. By default, the prefix is:

`Ctrl` + `b`

To run a tmux shortcut:
1. Press `Ctrl` and `b` together.
2. Release both keys.
3. Press the command key (for example, `d` to detach or `%` to split).

If you hold down `Ctrl` and `b` while pressing the next key, tmux will usually ignore it. Tap `Ctrl+b`, release, then tap your action key.

### Essential Session Commands (CLI)

You run these commands directly from your standard shell prompt to manage sessions:

| Command | What it does |
| :--- | :--- |
| `tmux` | Start a new unnamed session |
| `tmux new -s work` | Start a new session named `work` |
| `tmux ls` | List all running sessions |
| `tmux attach -t work` | Attach (re-enter) the session named `work` |
| `tmux kill-session -t work` | Destroy the session named `work` |

### In-Session Shortcuts (Prefix = `Ctrl+b`)

Once you are inside a tmux session, use these key combinations:

| Action | Shortcut |
| :--- | :--- |
| **Detach** from session (leaves it running) | `Ctrl+b` then `d` |
| **Split pane vertically** (side-by-side) | `Ctrl+b` then `%` |
| **Split pane horizontally** (top-and-bottom) | `Ctrl+b` then `"` |
| **Switch active pane** | `Ctrl+b` then `Arrow Key` |
| **Zoom current pane** (toggle full-screen) | `Ctrl+b` then `z` |
| **Close current pane** | `Ctrl+b` then `x` (confirms with `y/n`) |
| **Create new window** (tab) | `Ctrl+b` then `c` |
| **Switch to next/previous window** | `Ctrl+b` then `n` / `p` |
| **Rename current window** | `Ctrl+b` then `,` |

---

## Part 3: Enabling Mouse Support

By default, tmux disables your mouse. That means you cannot click between panes or scroll up through terminal output with your trackpad.

You can fix this with a single configuration line. Create or edit the tmux config file located at `~/.tmux.conf`:

```bash
nano ~/.tmux.conf
```

Add the following configuration:

```tmux
# Enable mouse mode (tmux 2.1 and above)
set -g mouse on
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X` in nano). To apply the changes immediately without restarting tmux, run this command inside your terminal:

```bash
tmux source-file ~/.tmux.conf
```

Now you can click inside panes to focus them, drag pane borders to resize them, and scroll through output with your mouse wheel.

---

## Hands-on Example: Building a Developer Dashboard

Let's put this into practice by building a practical 2-window, 3-pane developer environment from scratch.

### Step 1: Install tmux

First, make sure tmux is installed on your machine.

On Ubuntu/Debian:
```bash
sudo apt update && sudo apt install -y tmux
```

On macOS (using Homebrew):
```bash
brew install tmux
```

### Step 2: Create a named session

Start a new session called `dashboard`:

```bash
tmux new -s dashboard
```

You are now inside tmux. Look at the bottom of the screen: you will see a green status bar showing `[dashboard] 0:bash*`.

### Step 3: Set up Window 1 (Monitoring)

Let's turn this first window into a system dashboard with two panes.

Split the current terminal window vertically into two side-by-side panes:
* Press `Ctrl+b`, release, then press `%` (usually `Shift+5`).

In the right pane, run a command that outputs active data:
```bash
top
```

Now move back to the left pane:
* Press `Ctrl+b`, release, then press `Left Arrow`.

Run a disk space watcher:
```bash
df -h
```

Rename this window so it's easy to identify:
* Press `Ctrl+b`, release, then press `,`.
* Clear the text, type `system`, and press `Enter`.

```text
+-----------------------+-----------------------+
|                       |                       |
|   df -h               |   top                 |
|   (Disk stats)        |   (Live CPU/RAM)      |
|                       |                       |
+-----------------------+-----------------------+
| [dashboard] 0:system*                         |
+-----------------------------------------------+
```

### Step 4: Create Window 2 (Workspace)

Now let's add a second tab dedicated to active work.

Create a new window:
* Press `Ctrl+b`, release, then press `c`.

Notice the status bar updates to show `1:bash*`. Rename this window to `work`:
* Press `Ctrl+b`, release, then press `,`.
* Type `work` and hit `Enter`.

Split this window horizontally (top and bottom):
* Press `Ctrl+b`, release, then press `"`.

Now you have two separate working areas in your second window.

### Step 5: Detach and Reattach

Imagine your workday is done or your SSH connection drops. Let's safely detach:
* Press `Ctrl+b`, release, then press `d`.

You are returned to your regular shell prompt:
```text
[detached (from session dashboard)]
```

Check that your session is still running in the background:
```bash
tmux ls
```

Output:
```text
dashboard: 2 windows (created Sun May 18 10:30:00 2025)
```

Now, reattach to your workspace:
```bash
tmux attach -t dashboard
```

Everything is exactly as you left it. Use `Ctrl+b` then `p` to jump back to your `system` window, or `Ctrl+b` then `n` to return to `work`.

---

## Common Mistakes and How to Fix Them

* **Typing shortcuts too fast or holding the keys down:** If you press `Ctrl+b+d` at the exact same moment, tmux will likely ignore it. Hit `Ctrl+b`, let go, and then press `d`.
* **Nesting tmux by accident:** If you are inside tmux and type `tmux new`, you create a session inside a session. The prefix keys will conflict. If your screen gets confusing, run `exit` in the inner panes until you drop back to the parent session.
* **Panic when a pane freezes:** If a process locks up a pane, you don't need to kill the terminal. Press `Ctrl+b`, then `x`, then press `y` to terminate only that stuck pane.
* **Losing track of sessions:** If you start sessions with just `tmux`, they get generic numeric names like `0`, `1`, `2`. Always use `tmux new -s <descriptive-name>` so `tmux ls` remains meaningful.

---

## Try It Yourself: The 2-Minute Split Challenge

Open your terminal and complete this quick exercise without touching your mouse:

1. Launch a temporary session: `tmux new -s test-run`
2. Split the screen vertically: `Ctrl+b` then `%`
3. Split the right half horizontally: `Ctrl+b` then `"`
4. Move focus back to the leftmost pane: `Ctrl+b` then `Left Arrow`
5. Zoom the leftmost pane to full screen: `Ctrl+b` then `z`
6. Un-zoom it back to normal: `Ctrl+b` then `z`
7. Clean up and close the session entirely: type `exit` in each pane until you are back at your standard shell.

---

## What's Next

Once you are comfortable with splits and sessions, you can customize tmux to match your exact development style:

* **Remap the prefix:** Many developers remap `Ctrl+b` to `Ctrl+a` (closer to the home row, matching GNU Screen).
* **Vim-style pane navigation:** Map `h`, `j`, `k`, and `l` to move between panes seamlessly.
* **Automate layouts:** Use shell scripts or tools like `tmuxinator` to launch multi-service development environments with a single command.

In an upcoming tutorial, we will write a custom shell script that boots an entire project stack—frontend, backend, database, and log streams—into a pre-configured tmux workspace in seconds.

Bookmark this guide so you always have the essential tmux shortcuts within reach whenever you open a terminal.
