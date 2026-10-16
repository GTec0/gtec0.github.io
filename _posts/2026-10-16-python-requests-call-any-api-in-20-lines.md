---
layout: post
title: "Python requests: call any API in 20 lines"
subtitle: "Learn how to use Python's requests library to call any public API with GET, POST, timeouts, and error handling in under 20 lines of code."
date: 2026-10-16
categories: []
tags: ["Python", "API", "Beginner"]
thumbnail-img: /assets/images/banners/python-requests-call-any-api-in-20-lines-banner.png
share-img: /assets/images/banners/python-requests-call-any-api-in-20-lines-banner.png
author: Asahluma Tyika
---
## Introduction – What, Why, and Who

Calling a web API is one of the most common tasks for a modern developer. Whether you need to fetch weather data, post a comment, or automate a workflow, the **requests** library makes HTTP communication in Python feel like a conversation with a friendly neighbor.

* **What** you’ll learn:  
  * Installing `requests`  
  * Performing a **GET** request  
  * Sending JSON with a **POST** request  
  * Adding **timeouts** to avoid hanging programs  
  * Handling common **errors** (network failures, non‑2xx responses)

* **Why** it matters: A reliable API call is the backbone of data‑driven apps, bots, and scripts. Mastering the basics now saves you debugging time later.

* **Who** this is for: Beginners who have written a few Python scripts and want to start talking to web services, and intermediate developers who need a quick refresher on best practices.

---

## Part 1 – Installing and Importing `requests`

| Step | Command / Code | Purpose |
|------|----------------|---------|
| 1 | `pip install requests` | Install the library from PyPI |
| 2 | `import requests` | Bring the module into your script |

> **Tip:** Use a virtual environment (`python -m venv venv`) to keep dependencies isolated.

---

## Part 2 – GET Requests in a Nutshell

A **GET** request asks the server for data. For a public test API we’ll use **httpbin.org**, which simply returns whatever you sent it.

```python
response = requests.get('https://httpbin.org/get', params={'name': 'Alice'})
print(response.status_code)   # 200 means success
print(response.json())        # Parsed JSON dictionary
```

* `params` are automatically URL‑encoded.
* `response.json()` raises a `ValueError` if the body isn’t valid JSON, so it’s safe to wrap in `try/except` when you’re unsure.

---

## Part 3 – POST Requests with JSON Payloads

A **POST** request sends data to the server, often to create a new resource. `requests` can serialize a Python dictionary to JSON for you.

```python
payload = {'title': 'Hello world', 'body': 'My first post', 'userId': 1}
resp = requests.post('https://jsonplaceholder.typicode.com/posts', json=payload)
print(resp.status_code)   # 201 Created
print(resp.json())        # The server echoes back the new object
```

* The `json=` argument sets the `Content‑Type: application/json` header automatically.
* Use `data=` if you need to send form‑encoded data (`application/x-www-form-urlencoded`).

---

## Part 4 – Timeouts and Error Handling

Network calls can stall forever if the remote host is slow or unreachable. A **timeout** tells `requests` to abort after a given number of seconds.

```python
try:
    r = requests.get('https://httpbin.org/delay/3', timeout=2)  # endpoint delays 3 s
except requests.Timeout:
    print('The request timed out!')
else:
    print('Success:', r.status_code)
```

### Catching HTTP errors

`requests` does not raise an exception for non‑2xx status codes by default. Call `raise_for_status()` to turn them into `HTTPError`s.

```python
try:
    r = requests.get('https://httpbin.org/status/404')
    r.raise_for_status()          # raises requests.HTTPError for 404, 500, …
except requests.HTTPError as err:
    print('Server returned an error:', err)
```

### Full error‑handling checklist

| Situation | Exception class | How to handle |
|-----------|----------------|---------------|
| Connection problems (DNS, refused) | `requests.ConnectionError` | Retry after a short sleep or alert the user |
| Timeout | `requests.Timeout` | Log and maybe fall back to cached data |
| Invalid HTTP response (e.g., 404, 500) | `requests.HTTPError` | Show a friendly message, optionally inspect `response.text` |
| Bad JSON body | `ValueError` (or `json.JSONDecodeError` in Python 3.5+) | Return `None` or an empty dict, and continue |

---

## Hands‑on Example – A Complete Script in ≤ 20 Lines

Below is a ready‑to‑run script that demonstrates everything above. Save it as `api_demo.py` and run `python api_demo.py`.

```python
#!/usr/bin/env python3
import sys
import requests

API_GET = 'https://httpbin.org/get'
API_POST = 'https://jsonplaceholder.typicode.com/posts'

def main():
    # ---- GET -------------------------------------------------
    try:
        r = requests.get(API_GET, params={'demo': 'true'}, timeout=5)
        r.raise_for_status()
        print('GET success →', r.json()['args'])
    except (requests.RequestException, ValueError) as e:
        sys.exit(f'GET failed: {e}')

    # ---- POST ------------------------------------------------
    payload = {'title': 'Demo', 'body': 'Testing POST', 'userId': 42}
    try:
        r = requests.post(API_POST, json=payload, timeout=5)
        r.raise_for_status()
        print('POST created ID →', r.json().get('id'))
    except (requests.RequestException, ValueError) as e:
        sys.exit(f'POST failed: {e}')

if __name__ == '__main__':
    main()
```

**Why it stays under 20 lines**

* One import block, two constant URLs, a `main()` function, and a guard (`if __name__ …`).  
* Each request block is compact yet includes timeout, error handling, and a useful printout.

Run the script and you should see something like:

```
GET success → {'demo': 'true'}
POST created ID → 101
```

The `jsonplaceholder` API always returns `id: 101` for new posts in its sandbox environment.

---

## Common Mistakes & Troubleshooting

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Forgetting `timeout=` | Script hangs forever when the server is down | Always pass a reasonable timeout (e.g., `timeout=5`) |
| Using `data=` for JSON without setting headers | Server receives plain text, returns 400 Bad Request | Use `json=` or add `headers={'Content-Type': 'application/json'}` |
| Ignoring `raise_for_status()` | You think the request succeeded but get a 404 later in the code | Call `response.raise_for_status()` right after the request |
| Assuming `response.json()` always works | `ValueError: No JSON object could be decoded` | Wrap in `try/except ValueError` or check `response.headers['Content-Type']` |
| Hard‑coding URLs with trailing slashes inconsistently | 301 redirects that add latency | Keep a consistent style (`https://example.com/resource`) and let `requests` follow redirects (default) |

---

## Try It Yourself

**Exercise:** Modify the script to call the **httpbin.org/post** endpoint instead of `jsonplaceholder`. Send a payload that includes a nested dictionary (e.g., `{'user': {'name': 'Bob', 'age': 30}}`). Print the **`json`** field that the server echoes back.

*Hint:* The echoed JSON will be under `response.json()['json']`.*

---

## What’s Next?

* **Authentication basics** – learn to add API keys, Bearer tokens, and OAuth headers.  
* **Streaming large responses** – use `iter_content()` for downloading files without loading them entirely into memory.  
* **Session objects** – keep cookies and connection pools alive across multiple calls.  
* **Async requests** – explore `httpx` or `aiohttp` for non‑blocking API calls.

---

Bookmark this guide and come back whenever you need a quick, reliable way to call an API with Python.
