---
layout: post
title: "Python f-strings and formatting: 12 patterns you will reuse"
subtitle: "Learn 12 copy‑paste‑ready Python f‑string patterns, see before/after output, and get a runnable example you can drop into any project."
date: 2026-10-09
categories: []
tags: ["Python", "Programming", "Beginner"]
thumbnail-img: /assets/images/banners/python-f-strings-and-formatting-12-patterns-you-will-reuse-banner.png
share-img: /assets/images/banners/python-f-strings-and-formatting-12-patterns-you-will-reuse-banner.png
author: Asahluma Tyika
---
# Python f-strings and formatting: 12 patterns you will reuse  

**Tags:** Python, Programming, Beginner  

## Introduction – what, why, and who this is for  

Python’s *f‑strings* (formatted string literals) were introduced in Python 3.6 and quickly became the go‑to way to build readable, efficient strings. They let you embed variables, run expressions, and apply formatting **inside** a string literal, all without the clutter of `%` or `str.format()`.  

If you’re a beginner who’s tired of concatenating with `+` or calling `format()`, or an intermediate coder looking for clean, repeatable patterns, this tutorial is for you. We’ll walk through 12 practical f‑string recipes, show the exact output before and after applying the pattern, and give you a ready‑to‑copy code block for each. No fluff—just runnable examples you can paste into your own projects.

---  

## Part 1 – Basic interpolation  

| # | Pattern | Before (plain concatenation) | After (f‑string) |
|---|---------|-----------------------------|-----------------|
| 1 | Insert a variable | `greeting = "Hello, " + name + "!"` | `greeting = f"Hello, {name}!"` |

```python
# before
name = "Alice"
greeting = "Hello, " + name + "!"
print(greeting)   # Hello, Alice!

# after
greeting = f"Hello, {name}!"
print(greeting)   # Hello, Alice!
```

*Why it matters:* No more `+` juggling, and the variable name is visible right where it appears.

---  

## Part 2 – Numeric formatting  

### 2️⃣ Fixed‑point numbers (2 decimal places)

```python
price = 9.5
# before
print("Price: $" + format(price, ".2f"))
# after
print(f"Price: ${price:.2f}")
```

**Output**

```
Price: $9.50
```

### 3️⃣ Thousands separator  

```python
population = 12345678
print(f"Population: {population:,}")
```

**Output**

```
Population: 12,345,678
```

### 4️⃣ Binary / hex / octal  

```python
value = 42
print(f"binary: {value:b}, hex: {value:#x}, oct: {value:#o}")
```

**Output**

```
binary: 101010, hex: 0x2a, oct: 0o52
```

---  

## Part 3 – Dates and times  

### 5️⃣ ISO‑8601 date  

```python
from datetime import date
today = date.today()
print(f"Today is {today:%Y-%m-%d}")
```

**Output**

```
Today is 2026-10-09
```

### 6️⃣ 12‑hour clock with AM/PM  

```python
from datetime import datetime
now = datetime.now()
print(f"Current time: {now:%I:%M %p}")
```

**Output**

```
Current time: 03:27 PM
```

### 7️⃣ Custom weekday name  

```python
print(f"Weekday: {now:%A}")
```

**Output**

```
Weekday: Monday
```

---  

## Part 4 – Alignment and padding  

| # | Pattern | Before | After |
|---|---------|--------|-------|
| 8 | Left‑align text in a 20‑char field | `print("{:<20}".format(name))` | `print(f"{name:<20}")` |
| 9 | Right‑align numbers with zero‑fill | `print("{:0>5}".format(num))` | `print(f"{num:0>5}")` |
|10 | Center with a custom fill char | `print("{:*^10}".format(word))` | `print(f"{word:*^10}")` |

```python
name = "Bob"
num = 7
word = "hi"

print(f"{name:<20}")   # Bob                 
print(f"{num:0>5}")    # 00007
print(f"{word:*^10}")  # ****hi****
```

---  

## Part 5 – Expressions inside f‑strings  

### 11️⃣ Inline calculations  

```python
a, b = 5, 3
print(f"{a} + {b} = {a + b}")
```

**Output**

```
5 + 3 = 8
```

### 12️⃣ Debug‑friendly output (`=` specifier)  

Python 3.8 added the `=` conversion flag, which prints both the expression and its value.

```python
x = 12
print(f"{x=}, {x*2=}")
```

**Output**

```
x=12, x*2=24
```

---  

## Hands‑on example – a tiny report generator  

Below is a complete, runnable script that combines **all 12 patterns** into a single, readable report. Copy it, run `python report.py`, and you’ll see the formatted output immediately.

```python
# report.py
from datetime import datetime, date

# 1 – basic interpolation
user = "Eve"
greeting = f"Hello, {user}!"

# 2 – fixed‑point price
price = 49.99
price_line = f"Price: ${price:.2f}"

# 3 – thousands separator
visits = 1520345
visits_line = f"Total visits: {visits:,}"

# 4 – binary/hex/octal
mask = 0b101010
mask_line = f"Mask (bin/hex/oct): {mask:b}/{mask:#x}/{mask:#o}"

# 5‑7 – dates and times
today = date.today()
now = datetime.now()
date_line = f"Date (ISO): {today:%Y-%m-%d}"
time_line = f"Time (12‑hr): {now:%I:%M %p}"
weekday_line = f"Weekday: {now:%A}"

# 8‑10 – alignment & padding
left = f"{user:<15}"
right = f"{price:0>8}"
center = f"{'Report':*^30}"

# 11 – inline calculation
total = price * visits
calc_line = f"{price:.2f} × {visits:,} = ${total:,.2f}"

# 12 – debug output
debug_line = f"{visits=}, {price=}, {total=:,.2f}"

# Assemble report
report = f"""
{center}
{greeting}
{price_line}
{visits_line}
{mask_line}
{date_line}
{time_line}
{weekday_line}
Left‑align: {left}
Zero‑pad:   {right}
{calc_line}
{debug_line}
"""

print(report)
```

**Sample output**

```
*************Report*************
Hello, Eve!
Price: $49.99
Total visits: 1,520,345
Mask (bin/hex/oct): 101010/0x2a/0o52
Date (ISO): 2026-10-09
Time (12‑hr): 03:27 PM
Weekday: Monday
Left‑align: Eve             
Zero‑pad:   00049.99
49.99 × 1,520,345 = $75,997,185.55
visits=1520345, price=49.99, total=75,997,185.55
```

All 12 patterns are demonstrated, and you can edit any line to fit your own data.

---  

## Common mistakes / troubleshooting  

- **Forgot the leading `f`** – `"{name}"` won’t interpolate. Add `f` before the opening quote.  
- **Mismatched braces** – Every `{` must have a matching `}`. Python raises `SyntaxError: f-string: unmatched '{'`. Count them or use an editor’s bracket‑matching feature.  
- **Using a colon inside the expression** – Only the *format spec* after the first colon belongs to the f‑string. Write `{value:.2f}` not `{value : .2f}` (extra spaces break the spec).  
- **Mixing bytes and f‑strings** – `bf"..."` is not allowed. Convert to `str` first or use `.decode()`.  
- **Running on Python < 3.6** – f‑strings don’t exist. Upgrade or fall back to `str.format()`.

---  

## Try it yourself  

Create a list of product names and prices, then print a table where:

1. Names are left‑aligned in a 12‑character column.  
2. Prices show two decimals and a thousands separator.  
3. Each line ends with the expression `price * 1.07` (adding 7 % tax) shown using the `=` debug flag.

```python
products = [("Notebook", 1999.5), ("Pen", 2.3), ("Backpack", 49.99)]
# Write your f‑string loop below
```

---  

## What’s next  

- **Advanced formatting:** custom numeric formats, locale‑aware output.  
- **Multiline f‑strings:** using `textwrap.dedent` for clean templates.  
- **Performance tip:** f‑strings vs. `%`/`format()` in tight loops.  
- **Logging with f‑strings:** structured logs without extra libraries.

Happy formatting!  

*Bookmark this page for quick copy‑paste of the 12 patterns.*
