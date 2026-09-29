---
layout: post
title: "Bash scripting crash course: loops, ifs and functions in one post"
subtitle: "Build a single Bash script step‑by‑step that teaches loops, conditionals, and functions, then run it to back up .txt files."
date: 2026-09-29
categories: []
tags: ["Bash", "Linux", "automation"]
thumbnail-img: /assets/images/banners/bash-scripting-crash-course-loops-ifs-and-functions-in-one-post-banner.png
share-img: /assets/images/banners/bash-scripting-crash-course-loops-ifs-and-functions-in-one-post-banner.png
author: Asahluma Tyika
---
## Bash scripting crash course: loops, ifs and functions in one post  
**Tags:** Bash, Linux, automation  

### Introduction – what, why, and who this is for  

Bash (the Bourne‑Again SHell) is the default command interpreter on most Linux distributions and macOS. Writing a short Bash script lets you chain commands, make decisions, repeat work, and package logic that would otherwise require manual typing.  

* **What you’ll get:** a single, fully‑runnable script that grows step‑by‑step, demonstrating loops, conditional statements, and functions.  
* **Why it matters:** automation saves time, reduces human error, and is the first step toward DevOps‑style workflows.  
* **Who should read this:** beginners who know how to run commands in a terminal and want to start automating, and intermediate users who need a quick refresher on Bash control structures.  

---

## Part 1 – Loops: repeat work without re‑typing  

### 1.1 `for` loop over a list  

```bash
#!/usr/bin/env bash
# Simple for‑loop: print each word in a list
for word in apple banana cherry; do
    echo "Fruit: $word"
done
```

*`for word in …; do … done`* iterates over each element separated by spaces.  

### 1.2 `for` loop over files  

| Pattern | Meaning |
|---------|---------|
| `*`     | every file in the current directory |
| `*.txt` | every file ending with `.txt` |
| `?.sh`  | any one‑character name ending with `.sh` |

```bash
# Count lines in every .sh file
for file in *.sh; do
    lines=$(wc -l < "$file")
    echo "$file has $lines lines"
done
```

### 1.3 `while` loop with a condition  

```bash
# Count down from 5
counter=5
while (( counter > 0 )); do
    echo "Countdown: $counter"
    ((counter--))
done
echo "Liftoff!"
```

*The double‑parentheses `(( … ))` let Bash evaluate arithmetic expressions directly.*  

---

## Part 2 – Conditional statements (`if`, `elif`, `else`)  

### 2.1 Basic file‑existence test  

```bash
if [[ -f "$1" ]]; then
    echo "File '$1' exists."
else
    echo "File '$1' does NOT exist."
fi
```

| Test | Description |
|------|-------------|
| `-f` | true if path exists **and** is a regular file |
| `-d` | true if path exists **and** is a directory |
| `-z` | true if string is empty |
| `-n` | true if string is non‑empty |
| `==`| string equality (inside `[[ … ]]`) |
| `>`, `<` | numeric comparison (inside `(( … ))`) |

### 2.2 Combining tests with `&&` and `||`  

```bash
if [[ -d "$HOME" && -w "$HOME" ]]; then
    echo "Your home directory is writable."
fi
```

### 2.3 `case` for multiple branches (alternative to many `elif`s)  

```bash
read -p "Enter a day (Mon‑Sun): " day
case "$day" in
    Mon|Tue|Wed|Thu|Fri) echo "Weekday";;
    Sat|Sun)               echo "Weekend";;
    *)                     echo "Unknown day";;
esac
```

---

## Part 3 – Functions: reusable blocks of logic  

### 3.1 Defining and calling a function  

```bash
greet() {
    local name=$1
    echo "Hello, $name!"
}
greet "Bash learner"
```

*`local` limits the variable’s scope to the function, preventing accidental overwrites.*  

### 3.2 Returning a status code  

```bash
is_even() {
    (( $1 % 2 )) && return 1   # odd → non‑zero exit status
    return 0                    # even → zero exit status
}
if is_even 42; then
    echo "42 is even"
else
    echo "42 is odd"
fi
```

### 3.3 Function with output capture  

```bash
current_time() {
    date +"%Y-%m-%d %H:%M:%S"
}
timestamp=$(current_time)
echo "Script started at $timestamp"
```

---

## Hands‑on example – a single script that uses all three concepts  

Below is the final script you can copy to `backup.sh`, make executable (`chmod +x backup.sh`), and run. It backs up all `.txt` files from a source directory into a timestamped archive, but only if the source exists and contains files.

```bash
#!/usr/bin/env bash
# backup.sh – demo script combining loops, conditionals, and functions
# Usage: ./backup.sh /path/to/source /path/to/destination

set -euo pipefail   # strict mode: exit on error, undefined vars, and pipe failures

# ---------- Functions ----------
timestamp() {
    date +"%Y%m%d_%H%M%S"
}

create_archive() {
    local src=$1 dest=$2 ts=$3
    local archive="${dest}/backup_${ts}.tar.gz"
    tar -czf "$archive" -C "$src" .   # compress everything in src
    echo "$archive"
}

# ---------- Argument validation ----------
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <source_dir> <dest_dir>"
    exit 1
fi

src_dir=$1
dest_dir=$2

# ---------- Conditional checks ----------
if [[ ! -d "$src_dir" ]]; then
    echo "Error: source directory '$src_dir' does not exist."
    exit 2
fi

if [[ ! -d "$dest_dir" ]]; then
    echo "Destination directory '$dest_dir' does not exist – creating it."
    mkdir -p "$dest_dir"
fi

# ---------- Loop: process each .txt file ----------
txt_count=0
for file in "$src_dir"/*.txt; do
    [[ -e "$file" ]] || continue   # skip if no .txt files match
    ((txt_count++))
    echo "Will include: $(basename "$file")"
done

if (( txt_count == 0 )); then
    echo "No .txt files found in '$src_dir'. Nothing to back up."
    exit 0
fi

# ---------- Build archive ----------
ts=$(timestamp)
archive_path=$(create_archive "$src_dir" "$dest_dir" "$ts")
echo "Backup created: $archive_path"
```

**How it works, line by line**

| Section | What happens |
|---------|--------------|
| `set -euo pipefail` | Makes the script stop on the first error, undefined variable, or failed pipe – a safety net for beginners. |
| Functions (`timestamp`, `create_archive`) | Encapsulate reusable logic. `timestamp` returns a formatted date; `create_archive` builds a `.tar.gz`. |
| Argument validation (`if [[ $# -ne 2 ]]`) | Guarantees the script receives exactly two paths. |
| Directory checks (`-d`) | Ensures source exists; creates destination if missing. |
| `for file in "$src_dir"/*.txt` | Loops over every `.txt` file; `[[ -e "$file" ]] || continue` skips the loop when the glob expands to itself (no matches). |
| Counter `txt_count` | Demonstrates arithmetic inside `(( … ))`. |
| Final archive creation | Calls the functions, prints the resulting archive path. |

Run it like this (replace the paths with ones on your machine):

```bash
./backup.sh "$HOME/documents" "$HOME/backups"
```

You’ll see a list of the `.txt` files that will be archived, followed by the full path to the generated `backup_YYYYMMDD_HHMMSS.tar.gz` file.

---

## Common mistakes & troubleshooting  

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Script exits with **“unbound variable”** | `set -u` is on and a variable was never assigned. | Initialise variables (`var=${var:-default}`) or remove `set -u` while you’re learning. |
| Loop processes the literal string `*.txt` | No `.txt` files exist, and the glob didn’t expand. | Add `[[ -e "$file" ]] || continue` inside the loop (as shown) or test with `shopt -s nullglob`. |
| `tar: cannot open: No such file or directory` | Destination directory missing and `mkdir -p` failed. | Verify you have write permission, or run script with `sudo` if needed. |
| `if [[ -f "$1" ]]; then` always “does NOT exist” | `$1` is empty because you forgot to pass an argument. | Check the usage line, or add a guard `[[ -z "${1:-}" ]] && echo "Missing arg" && exit 1`. |
| Function returns wrong status | Using `return` with a string instead of a numeric code. | `return 0` for success, `return 1` for failure; use `echo` for textual output. |

---

## Try it yourself – short exercise  

Modify the script so that, **in addition to `.txt` files**, it also backs up any `.md` (Markdown) files found in the source directory. Hint: change the glob pattern and adjust the “no files found” test accordingly.  

---

## What’s next  

- **Parameter parsing with `getopts`** – give your script named flags like `-v` for verbose.  
- **Parallel execution** – use `&` and `wait` to compress multiple directories at once.  
- **Logging to a file** – redirect `echo` output with `exec > >(tee -a logfile) 2>&1`.  
- **Scheduling with `cron`** – turn your script into a daily backup job.  

Happy scripting!  
*Bookmark this page for a quick reference.*

---

## Diagrams

![Flowchart showing script execution: start → argument check → directory validation → file loop → archive creation → end](/assets/images/banners/bash-scripting-crash-course-loops-ifs-and-functions-in-one-post-diagram-1.png)

*Flowchart showing script execution: start → argument check → directory validation → file loop → archive creation → end*

![Timeline diagram of timestamp function output format (YYYYMMDD_HHMMSS) with arrows pointing to archive filename.](/assets/images/banners/bash-scripting-crash-course-loops-ifs-and-functions-in-one-post-diagram-2.png)

*Timeline diagram of timestamp function output format (YYYYMMDD_HHMMSS) with arrows pointing to archive filename.*


---

*This tutorial was drafted with AI assistance and verified with runnable examples. Found a mistake? Email the author — corrections are welcome.*
