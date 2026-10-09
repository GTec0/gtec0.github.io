---
layout: post
title: "Python pip and requirements: stop breaking your system Python"
subtitle: "Learn how to protect your system Python with venv, pip freeze, and the --break-system-packages flag."
date: 2026-10-09
categories: []
tags: ["Python", "Beginner"]
thumbnail-img: /assets/images/banners/python-pip-and-requirements-stop-breaking-your-system-python-banner.png
share-img: /assets/images/banners/python-pip-and-requirements-stop-breaking-your-system-python-banner.png
author: Asahluma Tyika
---
## Introduction – what, why, and who this is for  
If you’ve ever run `pip install` and later found that a system tool (like `apt` or `yum`) stopped working, you know the pain of “breaking the system Python.” This tutorial shows you a safe workflow:

* **Create an isolated virtual environment** (`venv`) for every project.  
* **Use `pip freeze`** to lock exact package versions in a `requirements.txt`.  
* **Understand the `--break-system-packages` flag** and why you should avoid it.

You don’t need any prior virtual‑environment experience—just a working Python installation (2 years or newer). By the end you’ll have a repeatable, reproducible setup that never messes with the Python that your OS relies on.

---

## Part 1 – System Python vs. Project Python  

| Aspect                | System Python (e.g., `/usr/bin/python3`) | Virtual Environment (`venv`) |
|-----------------------|-------------------------------------------|-------------------------------|
| Location              | Managed by the OS package manager         | A folder inside your project   |
| Permissions           | Usually requires `sudo` to modify        | User‑writable, no `sudo` needed |
| Impact on other tools | Changing it can break `apt`, `dnf`, etc. | Isolated – other tools stay untouched |
| Upgrade path          | Tied to OS release cycles                 | Controlled per‑project via `pip` |

**Why it matters:**  
When you install a library globally (`sudo pip install pandas`), you replace the version the OS expects. Some OS utilities import `urllib3` or `six` from the global site‑packages; a mismatched version can cause cryptic errors. Keeping the system interpreter pristine is the first step to a stable workstation.

---

## Part 2 – Creating and activating a virtual environment  

1. **Choose a project folder**  
   ```bash
   mkdir my_project && cd my_project
   ```

2. **Create the environment** (Python 3.8+ ships with `venv` built‑in)  
   ```bash
   python3 -m venv .venv
   ```
   *`.venv`* is just a convention; you can name it anything.

3. **Activate it**  

   * **Linux/macOS**  
     ```bash
     source .venv/bin/activate
     ```
   * **Windows (PowerShell)**  
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   After activation your prompt changes (e.g., `( .venv ) $`), and `which python` now points inside `.venv`.

4. **Verify isolation**  
   ```bash
   python -c "import sys, pprint; pprint.pprint(sys.path)"
   ```
   The first entries should be something like `.../.venv/lib/python3.x/site-packages`.

When you’re done, leave the environment with `deactivate`. Nothing you install while it’s active touches the system Python.

---

## Part 3 – pip basics, `requirements.txt`, and `pip freeze`  

| Command                               | What it does                                   |
|---------------------------------------|------------------------------------------------|
| `pip install package`                 | Installs the latest version from PyPI.         |
| `pip install package==1.2.3`          | Installs a specific version.                   |
| `pip uninstall package`               | Removes a package from the current env.        |
| `pip list`                            | Shows all installed packages and versions.     |
| `pip freeze > requirements.txt`       | Writes exact versions to a file.               |
| `pip install -r requirements.txt`     | Recreates the exact environment elsewhere.     |

### Why `pip freeze` matters  
Imagine you share a project with a teammate. If you only list “`requests`” in your README, they might get version 2.28 while you are on 2.31, leading to subtle bugs. `pip freeze` captures the **exact** build numbers (including transitive dependencies), guaranteeing that `pip install -r requirements.txt` reproduces the same environment.

### Updating a dependency safely  

```bash
# 1. Upgrade inside the venv
pip install --upgrade numpy

# 2. Refresh the lock file
pip freeze > requirements.txt
```

Now anyone who runs `pip install -r requirements.txt` gets the same upgraded NumPy.

---

## Part 4 – The `--break-system-packages` flag  

Starting with **Python 3.11**, the `pip` command refuses to install or upgrade packages in a *global* (system) Python unless you explicitly allow it with `--break-system-packages`. Example:

```bash
sudo pip install pandas
# → ERROR: Cannot install into a system Python without --break-system-packages
```

### What the flag does  
`--break-system-packages` tells `pip`: *I understand that I might overwrite files the OS cares about.* It bypasses the safety check, but it **does not** magically fix incompatibilities—if the OS expects an older version of a library, you’ll still break it.

### When (if ever) to use it  
* You are on a personal machine, fully understand the risk, and need a quick hack.  
* You are building a container image where the “system Python” is the only Python you have.

**Best practice:** Never use it on a workstation that also runs the OS package manager. Instead, spin up a `venv` and install there. The flag exists for edge cases, not for everyday development.

---

## Hands‑on example – a reproducible Flask app  

Below is a tiny Flask web service that returns “Hello, world!” and a complete workflow from start to finish. All commands assume you are in an empty folder called `flask_demo`.

### 1. Set up the project folder  

```bash
mkdir flask_demo && cd flask_demo
python3 -m venv .venv
source .venv/bin/activate   # or .\.venv\Scripts\Activate.ps1 on Windows
```

### 2. Install Flask and pin the version  

```bash
pip install Flask==2.3.2
pip freeze > requirements.txt
```

`requirements.txt` now contains something like:

```text
click==8.1.7
Flask==2.3.2
itsdangerous==2.1.2
Jinja2==3.1.4
MarkupSafe==2.1.5
Werkzeug==3.0.2
```

### 3. Write the app (`app.py`)  

```python
# app.py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, world!"

if __name__ == "__main__":
    # Running on localhost:5000
    app.run(debug=True)
```

### 4. Run it  

```bash
python app.py
```

Open a browser to <http://127.0.0.1:5000/> – you should see **Hello, world!**. All dependencies live inside `.venv`; the system Python stayed untouched.

### 5. Share the project  

Commit `app.py` and `requirements.txt` to Git (ignore `.venv`). A teammate can clone the repo, create a venv, and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

They get the exact same Flask version without any risk to their OS.

---

## Common mistakes / troubleshooting  

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `pip install` says “You are using pip version X.Y, but this version of pip does not support Python 3.Z” | Using an old `pip` inside a newly created venv | Run `python -m pip install --upgrade pip` after activating the venv |
| `ImportError: cannot import name 'urlparse' from 'urllib'` after installing a package globally | A global package overwrote the standard library module | Delete the offending package from the system site‑packages (`sudo pip uninstall <pkg>`) **or** recreate the venv and reinstall only needed packages |
| `Command not found: activate` on Windows | Ran the wrong activation script (PowerShell vs. CMD) | Use `.\.venv\Scripts\activate.bat` for CMD, `.\.venv\Scripts\Activate.ps1` for PowerShell |
| `pip freeze` outputs nothing or only `pip==...` | You installed packages with `sudo pip` outside the venv | Deactivate any venv, activate the correct one, then reinstall needed packages inside it |
| `ERROR: Cannot install into a system Python without --break-system-packages` | Accidentally omitted `source .venv/bin/activate` before installing | Activate the venv first, or explicitly add `--break-system-packages` **only** if you truly intend to modify the system Python (not recommended) |

---

## Try it yourself  

1. Create a new folder `demo_pkg`.  
2. Inside, set up a venv and install **requests** (`pip install requests`).  
3. Write a short script (`fetch.py`) that GETs `https://api.github.com` and prints the JSON.  
4. Freeze the environment, delete the venv folder, then recreate it from the `requirements.txt`.  
5. Run `fetch.py` again – it should work exactly as before.

If any step fails, refer to the troubleshooting table above.

---

## What’s next  

* **Dependency security** – scanning `requirements.txt` with tools like `safety` or `pip-audit`.  
* **Multiple environments** – using `pipenv` or `poetry` for more automation.  
* **Docker + venv** – containerizing your isolated setup for deployment.  
* **Automated CI** – having GitHub Actions install from `requirements.txt` on every push.

---

Bookmark this page and keep it handy; a clean Python environment saves you hours of debugging.
