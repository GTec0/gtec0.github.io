---
layout: post
title: "JSON vs YAML vs TOML: which config format when"
subtitle: "A side‑by‑side look at JSON, YAML, and TOML lets you pick the right config format for your next project."
date: 2026-10-15
categories: []
tags: ["Programming", "DevOps", "Beginner"]
thumbnail-img: /assets/images/banners/json-vs-yaml-vs-toml-which-config-format-when-banner.png
share-img: /assets/images/banners/json-vs-yaml-vs-toml-which-config-format-when-banner.png
author: Asahluma Tyika
---
# JSON vs YAML vs TOML: which config format when

## Introduction – what, why, and who this is for  

Configuration files tell software how to behave without recompiling. Three formats dominate the open‑source world:

| Format | Typical use‑case | Human‑readability | Comments support | Official spec |
|--------|------------------|-------------------|------------------|---------------|
| **JSON** | APIs, web front‑ends, data interchange | Good, but noisy (quotes, commas) | No (only via “//” in some parsers) | ECMA‑404 |
| **YAML** | DevOps tools (Docker Compose, Ansible), Kubernetes | Very friendly, indentation‑based | Yes (`#`) | YAML 1.2 |
| **TOML** | Rust projects, static site generators, modern CLIs | Clean, key‑value focused | Yes (`#`) | TOML 1.0 |

If you’re a beginner‑to‑intermediate developer setting up a small service, you’ll probably wonder which one to pick. This guide shows the exact same configuration expressed in each format, points out the common pitfalls, and gives you a ready‑to‑run Python example that reads all three.

---

## Part 1 – JSON basics  

JSON (JavaScript Object Notation) is the lingua‑franca of web data. Its grammar is strict:

* Keys **must** be double‑quoted strings.
* Values can be strings, numbers, booleans, `null`, arrays, or objects.
* No trailing commas.
* No native comment syntax (some parsers allow `//` or `/*…*/`, but it’s non‑standard).

### Minimal example  

```json
{
  "app": {
    "name": "DemoApp",
    "debug": true,
    "port": 8080,
    "allowed_hosts": ["localhost", "127.0.0.1"]
  }
}
```

### Pitfalls to watch  

| Issue | Symptom | Fix |
|-------|---------|-----|
| Missing quotes around a key | `SyntaxError: Unexpected token` | Always wrap keys in `" "` |
| Trailing comma after the last array element | `JSONDecodeError: Expecting value` | Remove the comma |
| Using single quotes for strings | `JSONDecodeError: Expecting property name` | Switch to double quotes |

---

## Part 2 – YAML basics  

YAML (YAML Ain’t Markup Language) is designed for humans. It relies on indentation, similar to Python, and supports comments out of the box.

### Minimal example  

```yaml
app:
  name: DemoApp
  debug: true
  port: 8080
  allowed_hosts:
    - localhost
    - 127.0.0.1
```

### Common gotchas  

| Issue | Symptom | Fix |
|-------|---------|-----|
| Mixing tabs and spaces | `found a tab character where an indentation space is expected` | Use spaces only (2 or 4 is typical) |
| Implicit type conversion (e.g., `yes` → `true`) | Unexpected boolean values | Quote ambiguous scalars: `"yes"` |
| Duplicate keys | `yaml.parser.ParserError: while parsing a block mapping` | Ensure each key appears only once |

---

## Part 3 – TOML basics  

TOML (Tom’s Obvious Minimal Language) aims for a balance: easy to read, easy to parse, and explicit about data types. It groups related keys into tables using `[table]` syntax.

### Minimal example  

```toml
[app]
name = "DemoApp"
debug = true
port = 8080
allowed_hosts = ["localhost", "127.0.0.1"]
```

### Pitfalls to avoid  

| Issue | Symptom | Fix |
|-------|---------|-----|
| Forgetting brackets for a table | Keys appear at the top level | Add `[section]` before the keys |
| Using single quotes for strings with escape sequences | Literal string, no escapes processed | Use double quotes for escaped content |
| Mixing array types | `TOMLDecodeError: Mixed array types` | Keep array elements of the same type |

---

## Hands‑on example – read the same config in three ways  

Below is a tiny Python script that loads the configuration from `config.json`, `config.yaml`, and `config.toml`. It prints the `app.name` and the port number, proving that the three files are interchangeable for the same data.

### 1. Install the parsers  

```bash
pip install pyyaml toml
```

`json` is part of the Python standard library, so no extra package is needed.

### 2. File layout  

```
project/
├─ config.json
├─ config.yaml
├─ config.toml
└─ read_config.py
```

### 3. The three config files (copy‑paste exactly)

**config.json**

```json
{
  "app": {
    "name": "DemoApp",
    "debug": true,
    "port": 8080,
    "allowed_hosts": ["localhost", "127.0.0.1"]
  }
}
```

**config.yaml**

```yaml
app:
  name: DemoApp
  debug: true
  port: 8080
  allowed_hosts:
    - localhost
    - 127.0.0.1
```

**config.toml**

```toml
[app]
name = "DemoApp"
debug = true
port = 8080
allowed_hosts = ["localhost", "127.0.0.1"]
```

### 4. `read_config.py`

```python
import json
import yaml
import toml
from pathlib import Path

def load_json(path: Path):
    with path.open() as f:
        return json.load(f)

def load_yaml(path: Path):
    with path.open() as f:
        return yaml.safe_load(f)

def load_toml(path: Path):
    with path.open() as f:
        return toml.load(f)

def show(cfg, source):
    app = cfg["app"]
    print(f"[{source}] {app['name']} runs on port {app['port']} (debug={app['debug']})")

if __name__ == "__main__":
    base = Path(__file__).parent
    show(load_json(base / "config.json"), "JSON")
    show(load_yaml(base / "config.yaml"), "YAML")
    show(load_toml(base / "config.toml"), "TOML")
```

### 5. Run it  

```bash
python read_config.py
```

**Expected output**

```
[JSON] DemoApp runs on port 8080 (debug=True)
[YAML] DemoApp runs on port 8080 (debug=True)
[TOML] DemoApp runs on port 8080 (debug=True)
```

If you see any errors, the troubleshooting section below will help.

---

## Common mistakes / troubleshooting  

* **File not found** – `FileNotFoundError`  
  *Fix*: Run the script from the directory that contains the config files, or use an absolute path (`Path("/full/path/config.json")`).  

* **Invalid JSON syntax** – `json.JSONDecodeError`  
  *Fix*: Run `python -m json.tool config.json` to pretty‑print and locate the offending line.  

* **YAML parser complains about tabs** – `yaml.scanner.ScannerError`  
  *Fix*: Replace all tabs with two spaces (`expandtabs(2)`) or configure your editor to insert spaces.  

* **TOML mixed‑type array error** – `toml.decoder.TomlDecodeError`  
  *Fix*: Ensure every element of an array shares the same type (all strings, all ints, etc.).  

* **Unicode or escape‑sequence mismatch** – characters appear garbled  
  *Fix*: Keep files UTF‑8 encoded (most editors default to this) and use double quotes for strings that need escape sequences (`\n`, `\"`).  

---

## Try it yourself  

1. Add a new key `log_level` with the value `"info"` to each config file.  
2. Extend `read_config.py` to print `app['log_level']`.  
3. Run the script and verify the output matches across all three formats.

---

## What’s next  

* **Advanced data structures** – nested tables in TOML, multi‑document YAML, and JSON references.  
* **Schema validation** – using JSON Schema, `cerberus` for YAML, and `tomlkit` validators.  
* **Streaming large configs** – when to use `ijson` for JSON or `ruamel.yaml` for incremental parsing.  
* **Performance comparison** – benchmark loading times for 10 KB, 100 KB, and 1 MB files.

Bookmark this guide for your next configuration decision.
