---
layout: post
title: "Environment variables in Python and Bash: configure like a pro"
subtitle: "Learn to use .env files, Bash, and Python's os.getenv to manage configuration and secrets safely, with real‑world examples."
date: 2026-10-11
categories: []
tags: ["Python", "Bash", "DevOps"]
thumbnail-img: /assets/images/banners/environment-variables-in-python-and-bash-configure-like-a-pro-banner.png
share-img: /assets/images/banners/environment-variables-in-python-and-bash-configure-like-a-pro-banner.png
author: Asahluma Tyika
---
# Environment variables in Python and Bash: configure like a pro

## Intro – what, why, and who this is for  

Configuration lives outside of source code. By storing values such as API keys, database URLs, or feature flags in **environment variables** you:

| Benefit | Why it matters |
|--------|----------------|
| **Portability** | Same code runs on dev, CI, and production without changes. |
| **Security** | Secrets never get committed to Git. |
| **Flexibility** | Switch behaviour with a single line change. |

If you’re a beginner who has been hard‑coding values, or an intermediate developer looking to tidy up a growing codebase, this guide will show you how to:

1. Create and load a `.env` file in Bash.  
2. Pull those variables into Python with sensible defaults.  
3. Keep secrets out of version control and logs.

All commands and scripts are ready to copy‑paste and run.

---

## Part 1 – .env files and Bash basics  

### 1.1 What a `.env` file looks like  

A `.env` file is a plain‑text list of `KEY=VALUE` pairs, one per line. Blank lines and lines that start with `#` are ignored.

```dotenv
# .env – example for a web app
APP_ENV=development
DEBUG=True
DB_HOST=localhost
DB_PORT=5432
DB_USER=app_user
DB_PASSWORD=super_secret_password
API_KEY=abcdef123456
```

| Rule | Example |
|------|---------|
| No spaces around `=` | `KEY=value` (good) vs `KEY = value` (bad) |
| Quote only when you need a literal `#` or leading/trailing space | `PATH="/usr/local/bin"` |
| Do **not** commit this file | Add `.env` to `.gitignore` |

### 1.2 Loading a `.env` file in Bash  

The simplest way is to source it:

```bash
# load-env.sh
set -o allexport   # automatically export every variable
source .env
set +o allexport
```

Run it once per session:

```bash
source load-env.sh
echo $APP_ENV   # → development
```

If you prefer a one‑liner, use `export $(cat .env | xargs)` – but be aware that it fails on values containing spaces or special characters. The `allexport` method is safer.

### 1.3 Making the variables permanent for a project  

Create a **wrapper script** that both loads the env file and runs your command:

```bash
#!/usr/bin/env bash
# run.sh – usage: ./run.sh python app.py

set -o allexport
source "$(dirname "$0")/.env"
set +o allexport

exec "$@"
```

Now `./run.sh python app.py` runs the Python script with the environment already populated.

---

## Part 2 – Accessing env vars in Python  

### 2.1 The `os.getenv` function  

```python
import os

debug = os.getenv("DEBUG", "False")   # default if not set
port = int(os.getenv("DB_PORT", "5432"))
```

`os.getenv(key, default)` returns **`None`** when the variable is missing and no default is supplied. Always provide a default for non‑critical settings.

### 2.2 Converting types safely  

Environment variables are strings. Convert them explicitly:

```python
def str_to_bool(value: str) -> bool:
    return value.lower() in ("true", "1", "yes")

DEBUG = str_to_bool(os.getenv("DEBUG", "false"))
```

### 2.3 Centralising configuration  

A tiny `config.py` keeps all look‑ups in one place:

```python
# config.py
import os

def _get(key: str, default: str = None) -> str:
    """Raise a clear error if a required key is missing."""
    value = os.getenv(key, default)
    if value is None:
        raise EnvironmentError(f"Missing required env var: {key}")
    return value

APP_ENV = _get("APP_ENV", "production")
DEBUG   = _get("DEBUG", "False").lower() == "true"
DB_HOST = _get("DB_HOST", "localhost")
DB_PORT = int(_get("DB_PORT", "5432"))
DB_USER = _get("DB_USER")
DB_PASSWORD = _get("DB_PASSWORD")
API_KEY = _get("API_KEY")
```

Now any module can simply `from config import DB_HOST, DB_PORT`.

### 2.4 Loading a `.env` file automatically (optional)  

For local development you may want Python to read `.env` without a wrapper script. The third‑party package **python‑dotenv** does that in one line:

```bash
pip install python-dotenv
```

```python
# config.py (alternative)
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent.parent / ".env")   # locate .env at project root

# … then use os.getenv as before
```

Only add this in development; production environments should provide real OS variables.

---

## Part 3 – Keeping secrets safe  

| Practice | How to do it |
|----------|--------------|
| **Never commit** `.env` | Add `.env` and any `*.env.*` files to `.gitignore`. |
| **Use a secret manager** | In cloud (AWS Secrets Manager, GCP Secret Manager) inject variables at runtime. |
| **Restrict file permissions** | `chmod 600 .env` – readable only by the owner. |
| **Avoid printing** | Never `print(os.getenv("DB_PASSWORD"))` in logs. |
| **Rotate keys** | Change the secret, update the `.env`, and redeploy without code changes. |

### 3.1 Example: Docker + .env  

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Run the container with the host’s `.env`:

```bash
docker build -t myapp .
docker run --env-file .env myapp
```

Docker passes each line as an environment variable, keeping the secret out of the image layers.

### 3.2 Example: GitHub Actions secret injection  

```yaml
# .github/workflows/ci.yml
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    env:
      DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
    steps:
      - uses: actions/checkout@v3
      - name: Install
        run: pip install -r requirements.txt
      - name: Test
        run: pytest
```

GitHub stores `DB_PASSWORD` encrypted; the workflow receives it as an env var without ever writing it to disk.

---

## Hands‑on example – a tiny Flask app that reads a DB URL from the environment  

**File layout**

```
myproject/
├─ .env
├─ app.py
├─ config.py
├─ requirements.txt
└─ run.sh
```

### 1️⃣ `.env`

```dotenv
# .env
APP_ENV=development
DEBUG=True
DB_HOST=localhost
DB_PORT=5432
DB_USER=flask_user
DB_PASSWORD=flask_secret
```

### 2️⃣ `requirements.txt`

```
Flask==3.0.0
python-dotenv==1.0.1   # optional, only for dev
```

### 3️⃣ `config.py`

```python
# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env only when it exists (development)
dotenv_path = Path(__file__).parent / ".env"
if dotenv_path.is_file():
    load_dotenv(dotenv_path)

def _get(key: str, default: str = None) -> str:
    value = os.getenv(key, default)
    if value is None:
        raise EnvironmentError(f"Missing required env var: {key}")
    return value

APP_ENV = _get("APP_ENV", "production")
DEBUG   = _get("DEBUG", "False").lower() == "true"
DB_HOST = _get("DB_HOST", "localhost")
DB_PORT = int(_get("DB_PORT", "5432"))
DB_USER = _get("DB_USER")
DB_PASSWORD = _get("DB_PASSWORD")
```

### 4️⃣ `app.py`

```python
# app.py
from flask import Flask, jsonify
from config import APP_ENV, DEBUG, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD

app = Flask(__name__)
app.config["ENV"] = APP_ENV
app.config["DEBUG"] = DEBUG

@app.route("/info")
def info():
    return jsonify({
        "environment": APP_ENV,
        "debug": DEBUG,
        "db": {
            "host": DB_HOST,
            "port": DB_PORT,
            "user": DB_USER,
            # Never expose the password!
        }
    })

if __name__ == "__main__":
    # Use host/port from env or defaults
    app.run(host="0.0.0.0", port=5000)
```

### 5️⃣ `run.sh`

```bash
#!/usr/bin/env bash
# run.sh – start the Flask app with env vars loaded

set -o allexport
source "$(dirname "$0")/.env"
set +o allexport

exec python app.py
```

### Run it

```bash
chmod +x run.sh
./run.sh
# → Flask starts, listening on http://0.0.0.0:5000
curl http://localhost:5000/info | jq
```

You should see a JSON payload containing the environment, debug flag, and DB connection info (without the password). All values came from the `.env` file, but the same code works unchanged if a CI system injects real production variables.

---

## Common mistakes / troubleshooting  

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `KeyError: 'DB_PASSWORD'` on start‑up | Variable not set and no default supplied | Add the variable to `.env` **or** export it in the shell before running. |
| `python-dotenv` loads an old `.env` | `.env` was edited after the process started | Restart the Python process (or use `load_dotenv(override=True)`). |
| Bash prints `command not found` after `source .env` | The `.env` file contains spaces around `=` or unquoted values with spaces | Remove spaces (`KEY=value`) and quote values with spaces (`KEY="my value"`). |
| Docker image contains the secret in a layer | `ENV VAR=value` used in Dockerfile instead of `--env-file` at run time | Pass secrets with `docker run --env-file .env …` or use Docker secrets. |
| CI logs show the password | `echo $DB_PASSWORD` or a step that prints the whole environment | Remove `echo` statements; use masked secrets in CI settings. |

---

## Try it yourself  

1. Create a new folder `demo/`.  
2. Copy the five files from the hands‑on example, but change `APP_ENV` to `staging` and set a different `DB_PASSWORD`.  
3. Run `./run.sh` and verify that `/info` returns the new `staging` value while the password stays hidden.  

If the endpoint shows the updated environment, you’ve mastered loading and reading env vars.

---

## What’s next  

- **Docker Compose with multiple `.env` files** – learn per‑service configuration.  
- **Using `dotenv-cli` for one‑off commands** – no wrapper script needed.  
- **Secret rotation pipelines** – automate key updates without downtime.  
- **Typed settings with `pydantic` or `dynaconf`** – add validation on top of env vars.

Bookmark this guide for quick reference when you set up your next project.
