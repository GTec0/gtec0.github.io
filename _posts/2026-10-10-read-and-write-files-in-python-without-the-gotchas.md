---
layout: post
title: "Read and write files in Python without the gotchas"
subtitle: "Learn how to read and write plain text, CSV, and JSON files in Python using safe with‑blocks, proper path handling, and practical recipes that avoid common pitf"
date: 2026-10-10
categories: []
tags: ["Python", "Beginner"]
thumbnail-img: /assets/images/banners/read-and-write-files-in-python-without-the-gotchas-banner.png
share-img: /assets/images/banners/read-and-write-files-in-python-without-the-gotchas-banner.png
author: Asahluma Tyika
---
## Intro – What, Why, and Who This Is For  

Reading from or writing to files is one of the first things you’ll do in a Python project—whether you’re logging results, loading configuration, or exporting data for a spreadsheet. The built‑in `open`, `csv`, and `json` modules are powerful, but a tiny mistake (forgetting to close a file, mixing path separators, or using the wrong newline mode) can cause hard‑to‑track bugs.

This tutorial is for **beginners to intermediate developers** who want a clear, step‑by‑step guide that works on Windows, macOS, and Linux without surprising “gotchas”. We’ll stick to the **`with` statement** for automatic cleanup, use **`pathlib`** for cross‑platform paths, and give you ready‑to‑run recipes for **plain text**, **CSV**, and **JSON** files.

---

## Part 1 – Safe File Access with `with`

| Mode | Meaning | Typical Use |
|------|---------|-------------|
| `'r'` | read (default) | Load a text file |
| `'w'` | write, truncates existing file | Create a new file or overwrite |
| `'a'` | append | Add new lines without deleting old data |
| `'x'` | exclusive creation, fails if file exists | Guard against accidental overwrite |
| `'b'` | binary (add to any of the above) | Work with images, PDFs, etc |
| `'t'` | text (default) | Human‑readable files |

The `with` statement guarantees that the file is closed **even if an exception occurs**:

```python
# plain_text_read.py
with open('example.txt', 'r', encoding='utf-8') as f:
    content = f.read()
print(content)
```

```python
# plain_text_write.py
lines = ['First line\n', 'Second line\n', 'Third line\n']
with open('example.txt', 'w', encoding='utf-8') as f:
    f.writelines(lines)          # writes each string as‑is
```

*Why `with`?*  
- No manual `f.close()`.  
- Cleaner indentation makes the scope obvious.  
- Works the same for `csv` and `json` objects that also support the context manager protocol.

---

## Part 2 – Cross‑Platform Paths with `pathlib`

Hard‑coding `"C:\\folder\\file.txt"` or `"folder/file.txt"` breaks when you switch OSes. `pathlib.Path` builds paths that automatically use the correct separator.

```python
from pathlib import Path

# Create a Path object relative to the script location
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'          # same as os.path.join(BASE_DIR, 'data')
DATA_DIR.mkdir(exist_ok=True)         # create folder if missing

txt_file = DATA_DIR / 'notes.txt'
csv_file = DATA_DIR / 'sales.csv'
json_file = DATA_DIR / 'config.json'
```

### Useful `Path` methods (quick reference)

| Method | Returns | Example |
|--------|---------|---------|
| `exists()` | `bool` | `txt_file.exists()` |
| `is_file()` | `bool` | `csv_file.is_file()` |
| `read_text(encoding='utf-8')` | `str` | `txt_file.read_text()` |
| `write_text(data, encoding='utf-8')` | `None` | `txt_file.write_text('Hello')` |
| `open(mode, encoding)` | file object | `txt_file.open('r', encoding='utf-8')` |

Using `Path` means you can drop the explicit `open` call for simple text files:

```python
# Write a short note in one line
(DATA_DIR / 'quick.txt').write_text('Saved with pathlib!\n')
```

---

## Part 3 – CSV Recipes

The `csv` module works with any iterable of rows. The most common mistake is forgetting the `newline=''` argument on Windows, which otherwise adds a blank line between rows.

### Writing a CSV

```python
import csv
from pathlib import Path

records = [
    ['id', 'name', 'score'],
    [1, 'Alice', 92],
    [2, 'Bob', 85],
    [3, 'Charlie', 78],
]

csv_path = Path('data') / 'students.csv'
csv_path.parent.mkdir(exist_ok=True)

with csv_path.open('w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(records)      # one call writes all rows
```

### Reading a CSV into a list of dictionaries

```python
import csv
from pathlib import Path

csv_path = Path('data') / 'students.csv'

with csv_path.open('r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)    # uses first row as keys
    rows = list(reader)

print(rows)   # [{'id': '1', 'name': 'Alice', 'score': '92'}, ...]
```

If you need numbers instead of strings, convert them on the fly:

```python
rows = [{k: int(v) if k != 'name' else v for k, v in row.items()} for row in rows]
```

---

## Part 4 – JSON Recipes

JSON is the lingua franca for configuration files and API payloads. The `json` module works with any Python object that can be represented as a combination of dicts, lists, strings, numbers, booleans, and `None`.

### Writing JSON (pretty‑printed)

```python
import json
from pathlib import Path

config = {
    "app_name": "FileWizard",
    "version": "1.0.0",
    "debug": True,
    "thresholds": {"low": 10, "high": 90}
}

json_path = Path('data') / 'config.json'
with json_path.open('w', encoding='utf-8') as f:
    json.dump(config, f, indent=4, ensure_ascii=False)
```

### Reading JSON

```python
import json
from pathlib import Path

json_path = Path('data') / 'config.json'
with json_path.open('r', encoding='utf-8') as f:
    config = json.load(f)

print(config['app_name'])   # FileWizard
```

**Tip:** Use `json.loads()` if you have a JSON string already in memory, and `json.dumps()` to turn a Python object back into a string.

---

## Hands‑On Example – A Tiny “Contact Book”

Below is a complete, runnable script that demonstrates every concept covered so far:

```python
# contact_book.py
import csv
import json
from pathlib import Path

# -------------------------------------------------
# 1️⃣  Set up paths
BASE = Path(__file__).parent
DATA = BASE / 'data'
DATA.mkdir(exist_ok=True)

TXT_FILE   = DATA / 'welcome.txt'
CSV_FILE   = DATA / 'contacts.csv'
JSON_FILE  = DATA / 'settings.json'

# -------------------------------------------------
# 2️⃣  Write a simple text file with `with`
welcome_msg = "Welcome to the Contact Book!\nAdd, view, or export contacts.\n"
with TXT_FILE.open('w', encoding='utf-8') as f:
    f.write(welcome_msg)

# -------------------------------------------------
# 3️⃣  Create a CSV of contacts
contacts = [
    ['id', 'first_name', 'last_name', 'email'],
    [1, 'Ada', 'Lovelace', 'ada@example.com'],
    [2, 'Grace', 'Hopper', 'grace@example.com'],
    [3, 'Alan', 'Turing', 'alan@example.com'],
]

with CSV_FILE.open('w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(contacts)

# -------------------------------------------------
# 4️⃣  Store some settings in JSON
settings = {
    "theme": "dark",
    "autosave": True,
    "max_contacts": 1000
}
with JSON_FILE.open('w', encoding='utf-8') as f:
    json.dump(settings, f, indent=2)

# -------------------------------------------------
# 5️⃣  Read everything back and print
print("--- Text file ---")
print(TXT_FILE.read_text(encoding='utf-8'))

print("--- CSV as dicts ---")
with CSV_FILE.open('r', newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
print(rows)

print("--- JSON settings ---")
print(json.load(JSON_FILE.open('r', encoding='utf-8')))
```

**Run it**

```bash
python contact_book.py
```

You’ll see the welcome message, a list of contacts (as dictionaries), and the JSON settings printed to the console, and three files will appear under `data/`.

---

## Common Mistakes / Troubleshooting

| Symptom | Typical Cause | Fix |
|---------|---------------|-----|
| Blank lines appear between CSV rows on Windows | Missing `newline=''` in `open` | Use `open(..., newline='')` (or `Path.open` with the same argument) |
| `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff` | File opened with wrong encoding (often a UTF‑16 or ISO‑8859‑1 file) | Specify the correct `encoding` argument, e.g., `encoding='utf-16'` |
| `FileNotFoundError` when reading a file that *does* exist | Relative path points to a different working directory | Use `Path(__file__).parent / 'filename'` to build an absolute path relative to the script |
| JSON file loads as a string, not a dict | Used `json.loads(f.read())` on a file opened in binary mode or forgot `json.load` | Call `json.load(f)` directly on a text‑mode file object |
| Data is overwritten unintentionally | Used mode `'w'` instead of `'a'` or `'x'` | Choose `'a'` to append, `'x'` to abort if the file already exists, or check `Path.exists()` before writing |

---

## Try It Yourself  

Create a new script called `inventory.py` that:

1. Stores a list of products (`id`, `name`, `price`) in a CSV file.  
2. Reads the CSV back into a list of dictionaries and prints only the products priced above **$20**.  
3. Saves a JSON file containing a summary: total number of products and average price.

Run the script and verify the output matches the data you entered.

---

## What’s Next  

- **Reading large files efficiently** – using generators and `itertools.islice`.  
- **Working with Excel files** – `openpyxl` vs `pandas`.  
- **File locking for concurrent writes** – `portalocker` or `fcntl`.  
- **Serializing custom objects** – `json` with `default=` or third‑party libraries like `orjson`.

---

*Bookmark this guide for quick reference whenever you need reliable file I/O in Python.*
