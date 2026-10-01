---
layout: post
title: "Python list comprehensions vs loops: when to use which"
subtitle: "Compare Python list comprehensions and loops with real benchmarks and readability tips, then decide which to use in your code."
date: 2026-10-01
categories: []
tags: ["Python", "Programming"]
thumbnail-img: /assets/images/banners/python-list-comprehensions-vs-loops-when-to-use-which-banner.png
share-img: /assets/images/banners/python-list-comprehensions-vs-loops-when-to-use-which-banner.png
author: Asahluma Tyika
---
# Python list comprehensions vs loops: when to use which  
**Tags:** Python, Programming  

## Intro – what, why, and who it’s for  
If you’ve written a few Python scripts, you’ve probably seen two ways to build a new list:

```python
# loop version
result = []
for x in data:
    result.append(f(x))
```

```python
# list‑comprehension version
result = [f(x) for x in data]
```

Both produce the same output, but they differ in speed, memory usage, and how easy they are to read. This tutorial shows you **when a comprehension is the right choice and when a plain loop is clearer**, using concrete benchmarks and readability guidelines. It’s aimed at beginners who understand basic Python syntax and want to write code that is both fast *and* maintainable.

---

## Part 1 – Core concepts of list comprehensions  

| Feature | Loop | List comprehension |
|---------|------|---------------------|
| Syntax | Multiple lines, explicit `append` | Single expression inside `[]` |
| Return value | Usually `None` (mutates a list) | New list is created automatically |
| Early exit | `break` works naturally | No built‑in break; need extra logic |
| Nesting | Can nest loops easily | Nested comprehensions are possible but can become hard to read |

### 1.1 Basic form  
```python
# Loop
squares = []
for n in range(5):
    squares.append(n * n)

# List comprehension
squares = [n * n for n in range(5)]
```

Both yield `[0, 1, 4, 9, 16]`. The comprehension packs the loop header, body, and `append` into one line.

### 1.2 Adding a filter (`if` clause)  
```python
# Loop with filter
evens = []
for n in range(10):
    if n % 2 == 0:
        evens.append(n)

# List comprehension with filter
evens = [n for n in range(10) if n % 2 == 0]
```

### 1.3 Multiple `for` clauses (nested loops)  
```python
# Loop version – Cartesian product
pairs = []
for i in range(3):
    for j in range(2):
        pairs.append((i, j))

# List comprehension version
pairs = [(i, j) for i in range(3) for j in range(2)]
```

When the nesting depth exceeds two, the comprehension line can become hard to scan, which is a readability red flag.

---

## Part 2 – Benchmarks: speed and memory  

### 2.1 Timing with `timeit`  
The following script measures the time to build a list of 1 000 000 squares using a loop vs. a comprehension.

```python
# benchmark.py
import timeit

setup = "data = range(1_000_000)"

loop_stmt = """
result = []
for n in data:
    result.append(n * n)
"""

comp_stmt = "result = [n * n for n in data]"

loop_time = timeit.timeit(loop_stmt, setup=setup, number=5)
comp_time = timeit.timeit(comp_stmt, setup=setup, number=5)

print(f"Loop time   : {loop_time:.4f} s")
print(f"Comprehension time: {comp_time:.4f} s")
```

Running it:

```
$ python benchmark.py
Loop time   : 0.5621 s
Comprehension time: 0.3428 s
```

**Result:** The comprehension is roughly **40 % faster** for this simple arithmetic case because the interpreter avoids the method call overhead of `list.append`.

### 2.2 Memory profile with `tracemalloc`  

```python
# mem_profile.py
import tracemalloc

def build_loop():
    result = []
    for n in range(1_000_000):
        result.append(n * n)
    return result

def build_comp():
    return [n * n for n in range(1_000_000)]

for func in (build_loop, build_comp):
    tracemalloc.start()
    func()
    current, peak = tracemalloc.get_traced_memory()
    print(f"{func.__name__:10} – peak memory: {peak / 1024 / 1024:.2f} MB")
    tracemalloc.stop()
```

Typical output on a modest laptop:

```
build_loop  – peak memory: 76.29 MB
build_comp  – peak memory: 76.29 MB
```

Both approaches allocate the same amount of memory because the final list size is identical. The only memory difference appears during the loop when the list grows incrementally; Python’s list implementation over‑allocates to avoid frequent resizing, so the impact is negligible for most workloads.

### 2.3 When the comprehension loses its edge  

| Situation | Loop advantage | Why |
|-----------|----------------|-----|
| Early exit (`break`) | Loop can stop immediately | Comprehensions evaluate the entire iterable before returning |
| Complex side effects (e.g., logging) | Loop lets you intersperse statements | A comprehension must be a single expression |
| Very long or nested comprehensions | Loop keeps each step on its own line | Readability drops dramatically after two `for` clauses |

---

## Part 3 – Readability guidance  

1. **Keep it one line** – If the comprehension fits on a single line and stays under ~80 characters, it’s usually the clearer choice.  
2. **Avoid deep nesting** – More than two `for` clauses or an `if` that contains another comprehension should be rewritten as a loop.  
3. **Name intermediate results** – When the expression inside the comprehension is non‑trivial, give it a name first:

   ```python
   # Bad: long expression inside comprehension
   result = [process(item).value * factor for item in items if item.active]

   # Better: break it out
   active = (item for item in items if item.active)
   transformed = (process(item).value for item in active)
   result = [value * factor for value in transformed]
   ```

4. **Prefer explicit loops for side effects** – If you need to `print`, `log`, or mutate external state, a loop signals intent more clearly than a comprehension that silently does the same.

---

## Hands‑on example – a real‑world task  

**Task:** Load a CSV file, keep only rows where the *price* column is under $20, and compute a discounted price (10 % off). Then write the transformed rows to a new CSV.

```python
# discount_csv.py
import csv
from pathlib import Path

INPUT = Path("products.csv")
OUTPUT = Path("discounted.csv")
DISCOUNT = 0.10
MAX_PRICE = 20.0

def read_rows(path):
    """Yield each row as a dict."""
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

def apply_discount(rows):
    """Return a list of transformed rows using a comprehension."""
    return [
        {
            **row,
            "price": f"{float(row['price']) * (1 - DISCOUNT):.2f}",
            "discounted": "yes",
        }
        for row in rows
        if float(row["price"]) < MAX_PRICE
    ]

def write_rows(path, rows, fieldnames):
    """Write rows back to CSV."""
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    raw = list(read_rows(INPUT))               # materialise once for simplicity
    transformed = apply_discount(raw)
    if transformed:
        write_rows(OUTPUT, transformed, fieldnames=transformed[0].keys())
    print(f"✔️  {len(transformed)} rows written to {OUTPUT}")

if __name__ == "__main__":
    main()
```

**How to run**

```bash
$ python discount_csv.py
✔️  42 rows written to discounted.csv
```

*Why a comprehension?* The transformation is a pure mapping with a single filter; the whole operation fits on one line and is easy to scan. If you needed to log every skipped row, you’d switch to a loop.

---

## Common mistakes / troubleshooting  

- **Mistake:** Forgetting to convert strings to numbers before comparison.  
  **Fix:** Wrap the column in `float()` (as shown) or use `decimal.Decimal` for precise money handling.  

- **Mistake:** Using a comprehension for side effects only (e.g., `[_ for _ in data if print(_)]`).  
  **Fix:** Replace with a loop; side effects belong in statements, not expressions.  

- **Mistake:** Running out of memory when the source iterable is huge.  
  **Fix:** Keep the comprehension lazy by using generator expressions (`(expr for x in iterable)`) and write rows one‑by‑one instead of building a full list.  

- **Mistake:** Nested comprehensions become unreadable (`[ (a,b) for a in A for b in B if a+b > 10]`).  
  **Fix:** Break the logic into separate loops or helper functions.  

- **Mistake:** Assuming the comprehension is always faster.  
  **Fix:** Benchmark with `timeit` on your actual data; for tiny lists the difference is negligible, and readability may outweigh micro‑optimizations.

---

## Try it yourself  

**Exercise:** Write a function `prime_factors(n)` that returns a list of all prime factors of `n`. Implement it twice—once with a `for` loop and once with a list comprehension (you may need an auxiliary generator). Compare the runtime for `n = 1_000_003` using `timeit`.  

*Hint:* Use `range(2, int(n**0.5) + 1)` as the candidate divisor range.

---

## What’s next  

- **Generator expressions vs. list comprehensions** – when to stay lazy.  
- **Using `map` and `filter` together with comprehensions** – trade‑offs.  
- **Parallel list processing with `concurrent.futures`** – speed up CPU‑bound loops.  
- **Profiling real‑world scripts** – integrating `cProfile` and visual tools.

---

*Bookmark this guide for quick reference when you’re deciding between a loop and a list comprehension.*
