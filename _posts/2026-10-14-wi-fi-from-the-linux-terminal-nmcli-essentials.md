---
layout: post
title: "Wi-Fi from the Linux terminal: nmcli essentials"
subtitle: "Learn how to scan, connect, and create a Wi‑Fi hotspot from the Linux terminal using just five nmcli commands."
date: 2026-10-14
categories: []
tags: ["Linux", "Networking"]
thumbnail-img: /assets/images/banners/wi-fi-from-the-linux-terminal-nmcli-essentials-banner.png
share-img: /assets/images/banners/wi-fi-from-the-linux-terminal-nmcli-essentials-banner.png
author: Asahluma Tyika
---
## Wi‑Fi from the Linux terminal: nmcli essentials  
*Tags: Linux, Networking*

### Intro – what, why, and who this is for  

Linux ships with **NetworkManager**, and its command‑line client **nmcli** lets you manage Wi‑Fi without ever touching a GUI.  
- **What**: A step‑by‑step guide to scan for networks, connect to one, and spin up a hotspot—all from the terminal.  
- **Why**: Handy on headless servers, minimal desktop environments, or when you need a quick fix while troubleshooting.  
- **Who**: Beginners who have a working Linux install and a wireless interface (e.g., `wlan0`), and intermediate users who want a repeatable scriptable workflow.

You only need five commands, plus a couple of optional flags for passwords and device names. Grab a terminal, and let’s get the radio talking.

---

## Part 1 – Understanding the wireless device  

| nmcli command | What it shows | Typical output |
|---|---|---|
| `nmcli device status` | List all network devices and their state | `wlan0   wifi   connected  MyHome` |
| `nmcli -f GENERAL.DEVICE,GENERAL.TYPE,GENERAL.STATE device show wlan0` | Detailed state of a single device | `GENERAL.DEVICE: wlan0`<br>`GENERAL.TYPE: wifi`<br>`GENERAL.STATE: 100 (connected)` |

> **Tip**: If `nmcli device status` reports `unavailable` or `disconnected`, make sure the wireless card isn’t blocked (`rfkill list`) and that the driver is loaded (`lsmod | grep iwlwifi` for Intel, `lsmod | grep ath9k` for Atheros, etc.).

---

## Part 2 – Scanning for Wi‑Fi networks  

The scan command is a single line, but you’ll often want a tidy list of SSIDs, signal strength, and security type.

```bash
# Scan and show a compact table
nmcli -f SSID,SIGNAL,SECURITY device wifi list
```

| Column | Meaning |
|---|---|
| **SSID** | Network name (may appear blank for hidden networks) |
| **SIGNAL** | 0‑100, higher is stronger |
| **SECURITY** | `WPA2`, `WPA1`, `WEP`, or `--` for open |

You can filter the output with `grep` or `awk` if you’re looking for a specific network:

```bash
nmcli -f SSID,SIGNAL,SECURITY device wifi list | grep -i "cafe"
```

---

## Part 3 – Connecting to a Wi‑Fi network  

### 3.1 One‑liner for a known password  

```bash
nmcli device wifi connect "MyHome" password "superSecret123"
```

- `device wifi connect` tells NetworkManager to create a new connection profile (or reuse an existing one).  
- If the SSID is hidden, add `--hidden yes`:

```bash
nmcli device wifi connect "HiddenNet" password "p@ssw0rd" --hidden yes
```

### 3.2 Re‑using a saved profile  

If you’ve connected before, the profile already exists. To reconnect without re‑entering the password:

```bash
nmcli connection up "MyHome"
```

You can list saved Wi‑Fi profiles with:

```bash
nmcli connection show --active
nmcli connection show
```

The first shows what’s currently active, the second lists *all* saved connections.

---

## Part 4 – Creating a Wi‑Fi hotspot (AP mode)  

A hotspot turns your Linux box into a wireless router. The command below creates a temporary hotspot called `MyHotspot` with password `hotspot123`. It works on most modern Wi‑Fi chips that support AP mode.

```bash
nmcli device wifi hotspot ifname wlan0 ssid MyHotspot password hotspot123
```

- `ifname` forces the command to use a specific interface (useful when you have more than one wireless device).  
- The hotspot will stay up until you run `nmcli connection down MyHotspot` or reboot.

You can inspect the hotspot’s settings with:

```bash
nmcli connection show MyHotspot
```

---

## Part 5 – Summarizing the five essential commands  

| Goal | nmcli command | What you get |
|---|---|---|
| Show device status | `nmcli device status` | List of interfaces and their state |
| Scan for networks | `nmcli -f SSID,SIGNAL,SECURITY device wifi list` | Table of visible APs |
| Connect to a network | `nmcli device wifi connect "<SSID>" password "<PASS>"` | Immediate connection & saved profile |
| Re‑connect using saved profile | `nmcli connection up "<PROFILE>"` | Quick bring‑up without password |
| Start a hotspot | `nmcli device wifi hotspot ifname <IF> ssid <SSID> password <PASS>` | Turn the box into an AP |

Memorize these five lines, and you have a complete Wi‑Fi toolbox.

---

## Hands‑on example (full, copy‑and‑paste script)

```bash
#!/usr/bin/env bash
# wifi-demo.sh – demonstrates the 5‑command workflow
# Run as a normal user; sudo is not required if you belong to the "netdev" group.

# 1️⃣ Show device status
echo "=== Device status ==="
nmcli device status

# 2️⃣ Scan for networks (filter for "Office")
echo -e "\n=== Scan for 'Office' networks ==="
nmcli -f SSID,SIGNAL,SECURITY device wifi list | grep -i "Office"

# 3️⃣ Connect (replace with your own SSID/password)
SSID="OfficeNet"
PASS="officePass42"
echo -e "\n=== Connecting to $SSID ==="
nmcli device wifi connect "$SSID" password "$PASS"

# 4️⃣ Verify connection
echo -e "\n=== Active connections ==="
nmcli connection show --active

# 5️⃣ Create a hotspot named "DemoAP"
HOTSPOT_SSID="DemoAP"
HOTSPOT_PASS="demo12345"
IFACE=$(nmcli -t -f DEVICE,TYPE device status | grep ':wifi' | cut -d: -f1 | head -n1)

echo -e "\n=== Starting hotspot $HOTSPOT_SSID on $IFACE ==="
nmcli device wifi hotspot ifname "$IFACE" ssid "$HOTSPOT_SSID" password "$HOTSPOT_PASS"

# Show hotspot details
echo -e "\n=== Hotspot details ==="
nmcli connection show "$HOTSPOT_SSID"
```

**How to run**

```bash
chmod +x wifi-demo.sh
./wifi-demo.sh
```

The script prints each step, connects to the network you specify, and finally creates a hotspot. Adjust `SSID`, `PASS`, `HOTSPOT_SSID`, and `HOTSPOT_PASS` to match your environment.

---

## Common mistakes & troubleshooting  

| Symptom | Likely cause | Fix |
|---|---|---|
| `Error: No network with SSID 'MyHome' found` | Interface is still scanning or the network is hidden. | Run `nmcli device wifi rescan` then repeat the scan; add `--hidden yes` if the AP does not broadcast its SSID. |
| `Error: Connection activation failed: (53) No network` | Wrong password or MAC‑filter on the router. | Double‑check the password; if the router uses MAC filtering, add your MAC (`nmcli device show wlan0 | grep GENERAL.HWADDR`). |
| Hotspot never appears on other devices | Wi‑Fi chip lacks AP support or is already in client mode. | Verify AP capability: `iw list | grep -A5 "Supported interface modes"`; if missing, you need a different adapter. |
| `nmcli: command not found` | NetworkManager not installed. | Install it: `sudo apt-get install network-manager` (Debian/Ubuntu) or `sudo dnf install NetworkManager` (Fedora). |
| After connecting, internet still fails | DNS not set or default route missing. | Run `nmcli device show wlan0 | grep IP4` to see IP; if missing, restart NetworkManager: `sudo systemctl restart NetworkManager`. |

---

## Try it yourself  

1. Turn off any GUI network manager (if running) with `sudo systemctl stop NetworkManager` **only** if you want to test nmcli in isolation.  
2. Use `nmcli device wifi list` to locate a network you have never connected to before.  
3. Connect to it **without** storing the password (`--ask` flag) to see the interactive prompt:

```bash
nmcli device wifi connect "<NEW_SSID>" --ask
```

Did it work? If not, note the error and refer to the table above.

---

## What’s next  

- **Scripted auto‑reconnect**: Use a cron job or `systemd` service that runs `nmcli connection up <profile>` when the link drops.  
- **Advanced security**: Switch to WPA3 (`--wifi-sec wpa3`) and store passwords in the keyring instead of plain text.  
- **Multi‑SSID hotspot**: Create a bridge (`br0`) to share both Ethernet and Wi‑Fi while keeping the same SSID for roaming.  
- **NetworkManager D‑bus**: Control Wi‑Fi from Python or Go for custom dashboards.

---

*Bookmark this page for a quick terminal‑only Wi‑Fi cheat sheet.*
