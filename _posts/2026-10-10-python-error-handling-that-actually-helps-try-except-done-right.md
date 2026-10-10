---
layout: post
title: "Python error handling that actually helps: try/except done right"
subtitle: "Stop using bare except and hiding crashes. Learn how to catch specific Python errors and build a clean logging pattern that makes debugging easy."
date: 2026-10-10
categories: []
tags: ["Python", "Programming"]
thumbnail-img: /assets/images/banners/python-error-handling-that-actually-helps-try-except-done-right-banner.png
share-img: /assets/images/banners/python-error-handling-that-actually-helps-try-except-done-right-banner.png
author: Asahluma Tyika
---
## Stop hiding your bugs: Why error handling matters

Every developer writes bugs. That is not a personal failure; it is just programming. What separates a smooth production deployment from a late-night debugging nightmare is how your code handles those bugs when they appear.

Too often, tutorials teach error handling like this:

```python
try:
    do_something()
except:
    pass
```

If you have this snippet anywhere in your project, you have buried a ticking time bomb. It looks peaceful because your program never crashes, but your data ends up corrupted, files end up half-written, and you have zero clues about what failed.

This guide is for beginner to intermediate Python developers who want their applications to fail gracefully, report the exact root cause, and keep running when safe to do so. We will look at why bare `except` blocks destroy systems, how to catch errors specifically, and how to set up an effortless logging pattern that turns hours of guesswork into a two-minute fix.

---

## Part 1: The "bare except" horror story

A bare `except:` catches **everything**. In Python, that does not just mean standard errors like `ValueError` or `FileNotFoundError`. It also catches system-level interrupts inherited from `BaseException`.

Consider this innocent-looking script:

```python
# dangerous_loop.py
import time

while True:
    try:
        print("Working...")
        time.sleep(1)
        # Pretend there's a typo here:
        pritn("Typo!")
    except:
        pass
```

Run that script and try to stop it by pressing `Ctrl + C`. 

It will not stop.

`Ctrl + C` raises a `KeyboardInterrupt`. Because `except:` catches every single exception, the loop swallows your manual stop command, hides the `NameError` on `pritn`, and spins endlessly until you kill the process from your task manager or terminal.

Even worse is catching `Exception` and silently printing nothing:

```python
try:
    user = database.get_user(user_id)
    send_welcome_email(user.email)
except Exception:
    print("Could not send email.")
```

If `database.get_user()` fails due to a network timeout, the message says `"Could not send email."` If `user.email` triggers an `AttributeError` because the user object is `None`, the message still says `"Could not send email."` You have thrown away the stack trace—the single most valuable piece of diagnostic data Python gives you.

---

## Part 2: Catching the right exceptions

Python provides a deep hierarchy of built-in exceptions. Instead of casting a giant net, catch only the errors you know how to recover from.

Here is a quick reference of errors you will encounter constantly:

| Exception | When it occurs | Common recovery tactic |
| :--- | :--- | :--- |
| `FileNotFoundError` | Missing file path during an `open()` call | Fall back to default config or create file |
| `KeyError` | Accessing a missing dictionary key | Use `.get()`, or set default fallback data |
| `ValueError` | Correct data type, invalid value (e.g., `int("abc")`) | Re-prompt the user or reject bad input |
| `TypeError` | Operation applied to mismatched types (e.g., `len(5)`) | Fix data transformation logic |
| `requests.RequestException` | Third-party network/HTTP call failed | Retry with backoff or notify client |

### The complete structure: `try`, `except`, `else`, `finally`

Python gives you two extra keywords that make code significantly cleaner: `else` and `finally`.

```python
def read_user_age(raw_input: str) -> int:
    try:
        age = int(raw_input)
    except ValueError as err:
        # Runs ONLY if int() raised a ValueError
        print(f"Invalid number supplied: {err}")
        return 0
    else:
        # Runs ONLY if the try block succeeded without errors
        print(f"Parsed valid age: {age}")
        return age
    finally:
        # ALWAYS runs, regardless of success or exceptions
        print("Parsing attempt finished.")
```

* **`try`**: Keep this block as small as possible. Only include lines that might actually raise the error you want to handle.
* **`except SpecificError as err`**: Intercepts the specific failure and binds the error details to the variable `err`.
* **`else`**: Runs code that relies on the `try` block succeeding, keeping that code out of the `try` block itself so you don't accidentally catch unexpected errors.
* **`finally`**: Perfect for clean-up routines—like closing network sockets, releasing database locks, or resetting temporary states.

---

## Part 3: The professional logging pattern

Instead of scattering `print()` statements across your code, use Python’s built-in `logging` module. 

A `print()` call writes raw text to standard output. It does not write timestamps, it does not assign severity levels (`INFO`, `WARNING`, `ERROR`), and it does not capture the traceback unless you manually format it.

Here is the pattern you should use in production scripts:

```python
import logging

# Configure logger (usually done once at your application entrypoint)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

def parse_price(raw_price: str) -> float:
    try:
        return float(raw_price.strip("$"))
    except ValueError:
        # logger.exception automatically appends the entire traceback
        logger.exception("Failed to parse price value '%s'", raw_price)
        return 0.0
```

Notice `logger.exception()`. When called inside an `except` block, it logs your custom message at the `ERROR` level **and** automatically attaches the full traceback. You do not need to import `sys` or manually inspect anything.

---

## Hands-on example: Resilient config parser

Let's put this into practice with a complete, runnable script. This program reads a JSON configuration file, parses server settings, validates ports, and uses proper exception handling paired with logging.

Save this code as `config_loader.py` and run it directly in your terminal:

```python
import json
import logging
from pathlib import Path

# Step 1: Set up our logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ConfigLoader")

DEFAULT_CONFIG = {
    "host": "127.0.0.1",
    "port": 8080,
    "debug": False
}

def load_server_config(file_path: Path) -> dict:
    """
    Safely loads and validates a server configuration JSON file.
    Falls back to safe defaults if the file is missing or invalid.
    """
    # Guard: Make sure the file exists before attempting complex reads
    if not file_path.exists():
        logger.warning("Config file '%s' not found. Using defaults.", file_path)
        return DEFAULT_CONFIG.copy()

    try:
        with file_path.open("r", encoding="utf-8") as f:
            raw_data = json.load(f)

    except json.JSONDecodeError:
        logger.exception("Malformed JSON in '%s'. Reverting to defaults.", file_path)
        return DEFAULT_CONFIG.copy()
    
    except OSError:
        logger.exception("Disk or permission error reading '%s'.", file_path)
        return DEFAULT_CONFIG.copy()

    # Validate individual fields safely
    config = DEFAULT_CONFIG.copy()

    try:
        raw_port = raw_data.get("port", 8080)
        port = int(raw_port)

        if not (1 <= port <= 65535):
            raise ValueError(f"Port {port} out of valid range (1-65535).")

        config["port"] = port
        config["host"] = str(raw_data.get("host", "127.0.0.1"))
        config["debug"] = bool(raw_data.get("debug", False))

    except (ValueError, TypeError) as err:
        logger.error("Configuration validation failed: %s. Using default port.", err)
        config["port"] = 8080

    return config

# Step 2: Demonstration
if __name__ == "__main__":
    demo_file = Path("bad_config.json")

    # Create a deliberately broken JSON file to see how it handles errors
    demo_file.write_text('{"host": "localhost", "port": "not-a-number"}', encoding="utf-8")

    logger.info("Attempting to load config...")
    final_config = load_server_config(demo_file)

    logger.info("Final config in use: %s", final_config)

    # Clean up the demo file
    if demo_file.exists():
        demo_file.unlink()
```

Run it:

```bash
python3 config_loader.py
```

### What happens here?
1. The script reads the broken file without crashing.
2. The JSON decodes correctly, but when it attempts to parse `"not-a-number"` into an integer, a `ValueError` is triggered.
3. Our `except (ValueError, TypeError)` catches that exact situation, logs a clean error message, and applies a safe fallback.
4. The program finishes cleanly.

---

## Common mistakes and troubleshooting

* **Placing entire functions inside a single `try` block:**
  * *The problem:* If you wrap 40 lines of code inside one `try`, an unexpected `KeyError` on line 35 might trigger an exception handler you intended for line 4.
  * *The fix:* Keep `try` blocks narrow. Isolate the single line or small block that performs the risky operation (I/O, network calls, type conversions).

* **Using `except Exception: pass`:**
  * *The problem:* Silent failures make maintenance impossible. Bugs will compound silently until corrupted data enters your database.
  * *The fix:* At bare minimum, log the exception using `logger.exception("Context message")`. If you truly intend to ignore an error, use `contextlib.suppress(SpecificError)`.

* **Overwriting original exceptions when re-raising:**
  * *The problem:* Catching an error and raising a new one without chaining destroys the original context.
  * *The fix:* Use `raise CustomError("message") from err`. The `from` keyword preserves Python’s traceback history so you can see both errors in the log.

* **Catching `Exception` instead of standard errors:**
  * *The problem:* Catching top-level `Exception` can accidentally mask logic bugs in your own code, such as `NameError` or `UnboundLocalError`.
  * *The fix:* Target specific classes (`IndexError`, `KeyError`, `ZeroDivisionError`). Reserve catching `Exception` for top-level entrypoints (like background job runners or API controllers) where crashing the entire process must be prevented.

---

## Try it yourself

Write a small script that asks a user for two numbers and divides them:

1. Prompt the user for a numerator and denominator using `input()`.
2. Wrap the conversion and division in a `try` block.
3. Handle two specific errors:
   * Non-numeric strings (raises `ValueError`).
   * Division by zero (raises `ZeroDivisionError`).
4. Use an `else` block to print the valid result.
5. Use a `finally` block to print `"Calculation attempt completed."`

Test your script by feeding it numbers, letters, and the number `0` to make sure each branch behaves as expected.

---

## What's next

* Build your own custom domain exceptions by subclassing `Exception` to represent distinct business logic failures.
* Clean up resource handling with Python's context managers (`with` statements and `contextlib`).
* In our next post, we will explore **custom exception hierarchies** for building maintainable internal SDKs and API wrappers.

Bookmark this page so you have a quick template ready the next time you need clean, production-grade error handling.
