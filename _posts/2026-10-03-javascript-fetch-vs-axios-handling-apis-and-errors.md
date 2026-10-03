---
layout: post
title: "JavaScript fetch vs axios: handling APIs and errors"
subtitle: "Learn how JavaScript fetch and Axios handle API calls and errors differently with practical, side-by-side code examples you can test right away."
date: 2026-10-03
categories: []
tags: ["JavaScript", "API", "Programming"]
thumbnail-img: /assets/images/banners/javascript-fetch-vs-axios-handling-apis-and-errors-banner.png
share-img: /assets/images/banners/javascript-fetch-vs-axios-handling-apis-and-errors-banner.png
author: Asahluma Tyika
---
## JavaScript fetch vs Axios: Handling APIs and Errors

Every modern web application talks to an external server sooner or later. Whether you are loading a user profile, submitting an order form, or fetching weather updates, you need a reliable way to make HTTP requests in JavaScript.

For years, developers have debated between two main options: the browser's built-in **Fetch API** and the popular third-party library **Axios**. 

Both handle HTTP calls using JavaScript Promises, but they handle data transformation, default configurations, and—most importantly—**errors** very differently.

If you are a beginner or intermediate developer trying to decide which tool fits your project, or if you have ever been bitten by a `fetch()` call that silently succeeded on a `404 Not Found` response, this guide is for you. We will compare them side by side with real, runnable code.

---

## Part 1: Installation and Basic GET Requests

The most obvious difference starts right at the setup stage.

- **`fetch()`** is built directly into modern browsers and Node.js (version 18 and newer). You do not need to install anything or add build dependencies.
- **Axios** is an external package. You must install it via npm or include it through a script tag.

To install Axios in a project:

```bash
npm install axios
```

### Fetching Data: Side-by-Side

Let's fetch a list of posts from the free JSONPlaceholder testing API.

#### Using `fetch()`

```javascript
async function getPostsWithFetch() {
  const response = await fetch('https://jsonplaceholder.typicode.com/posts/1');
  const data = await response.json();
  console.log('Fetch result:', data.title);
}

getPostsWithFetch();
```

#### Using Axios

```javascript
import axios from 'axios';

async function getPostsWithAxios() {
  const response = await axios.get('https://jsonplaceholder.typicode.com/posts/1');
  console.log('Axios result:', response.data.title);
}

getPostsWithAxios();
```

### Key Differences in GET Requests

1. **Two-step resolution in `fetch`:** When using `fetch()`, the first Promise resolves to a `Response` stream object. To access the JSON body, you must explicitly call and await `response.json()`.
2. **Automatic transformation in Axios:** Axios automatically checks the response header and parses JSON into a plain JavaScript object, placing it directly under `response.data`.

---

## Part 2: Sending Data with POST Requests

When sending payloads to an API, you usually convert your data into a JSON string and specify the `Content-Type: application/json` header.

Let's look at how both tools handle creating a new resource.

### The Side-by-Side POST Comparison

#### Using `fetch()`

```javascript
async function createPostWithFetch() {
  const newPost = {
    title: 'Learning Fetch',
    body: 'Native APIs are powerful!',
    userId: 1,
  };

  const response = await fetch('https://jsonplaceholder.typicode.com/posts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(newPost),
  });

  const data = await response.json();
  console.log('Created via Fetch:', data);
}

createPostWithFetch();
```

#### Using Axios

```javascript
import axios from 'axios';

async function createPostWithAxios() {
  const newPost = {
    title: 'Learning Axios',
    body: 'Axios keeps syntax concise!',
    userId: 1,
  };

  const response = await axios.post(
    'https://jsonplaceholder.typicode.com/posts',
    newPost
  );

  console.log('Created via Axios:', response.data);
}

createPostWithAxios();
```

With `fetch()`, you have to explicitly call `JSON.stringify(newPost)` and set the `'Content-Type': 'application/json'` header manually. If you forget either step, your backend server might receive an empty body or reject the payload with an `HTTP 400 Bad Request`.

Axios detects that you passed a standard JavaScript object as the payload, sets the `Content-Type` header to `application/json` automatically, and serializes the object for you behind the scenes.

---

## Part 3: The Big Difference: Error Handling

This is the single most common source of bugs for developers transitioning between `fetch` and Axios.

### How `fetch()` Treats Errors

The `fetch()` Promise **does not reject on HTTP error status codes** like `404 Not Found` or `500 Internal Server Error`. 

A `fetch()` promise only rejects if there is a fundamental network breakdown—such as being offline, hitting an invalid domain name, or encountering a blocked CORS preflight request.

If the server responds with a `404`, `fetch()` still treats the request as successful. You must manually verify the `response.ok` boolean property (which is `true` only for status codes `200-299`):

```javascript
async function fetchWithErrorHandling() {
  try {
    const response = await fetch('https://jsonplaceholder.typicode.com/invalid-route');

    if (!response.ok) {
      // Must manually throw to trigger the catch block
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.error('Fetch caught an error:', error.message);
  }
}

fetchWithErrorHandling();
```

### How Axios Treats Errors

Axios follows standard Promise conventions: **any HTTP status code outside the 2xx range automatically rejects the Promise**.

That means a `404` or `500` response skips the rest of the `try` block and lands immediately in your `catch` block. Furthermore, Axios attaches useful debugging information—including the status code, request configuration, and any payload the server returned—directly onto the error object:

```javascript
import axios from 'axios';

async function axiosWithErrorHandling() {
  try {
    const response = await axios.get('https://jsonplaceholder.typicode.com/invalid-route');
    console.log(response.data);
  } catch (error) {
    if (error.response) {
      // The server responded with a status code outside the 2xx range
      console.error(`Server error: ${error.response.status}`);
      console.error('Server error data:', error.response.data);
    } else if (error.request) {
      // The request was sent but no response was received (e.g., network drop)
      console.error('Network error: No response received');
    } else {
      // Something happened while setting up the request
      console.error('Request setup error:', error.message);
    }
  }
}

axiosWithErrorHandling();
```

### Quick Comparison Matrix

| Feature | `fetch()` | Axios |
| :--- | :--- | :--- |
| **Installation** | Built-in (no install needed) | `npm install axios` |
| **JSON Data Parsing** | Manual (`await res.json()`) | Automatic (`res.data`) |
| **JSON Serialization** | Manual (`JSON.stringify()`) | Automatic |
| **Rejects on 4xx/5xx?** | No (Check `res.ok` manually) | Yes (Automatically throws) |
| **Request Timeout** | Via `AbortSignal.timeout(ms)` | Built-in (`timeout: 5000`) |
| **Interceptors** | No native support | Native (`request` & `response`) |

---

## Part 4: Handling Timeouts

If an API hangs or takes thirty seconds to respond, you should fail gracefully rather than keep your user waiting forever.

### Native `fetch()` with `AbortSignal`

In modern JavaScript, you can cancel a hung `fetch()` call using `AbortSignal.timeout()`:

```javascript
async function fetchWithTimeout() {
  try {
    // Abort if request takes longer than 3000ms (3 seconds)
    const response = await fetch('https://jsonplaceholder.typicode.com/posts/1', {
      signal: AbortSignal.timeout(3000),
    });
    const data = await response.json();
    console.log(data);
  } catch (error) {
    if (error.name === 'TimeoutError') {
      console.error('Fetch request timed out!');
    } else {
      console.error('Fetch error:', error.message);
    }
  }
}
```

### Axios Timeout Configuration

Axios lets you pass a `timeout` property in milliseconds directly inside the request options:

```javascript
import axios from 'axios';

async function axiosWithTimeout() {
  try {
    const response = await axios.get('https://jsonplaceholder.typicode.com/posts/1', {
      timeout: 3000, // 3 seconds
    });
    console.log(response.data);
  } catch (error) {
    if (error.code === 'ECONNABORTED') {
      console.error('Axios request timed out!');
    } else {
      console.error('Axios error:', error.message);
    }
  }
}
```

---

## Hands-on Example

Here is a complete, runnable Node.js script comparing both methods against real endpoints.

To run this file, initialize a temporary Node directory:

```bash
mkdir api-demo && cd api-demo
npm init -y
npm pkg set type="module"
npm install axios
```

Save the following code as `test-requests.js`:

```javascript
import axios from 'axios';

const VALID_URL = 'https://jsonplaceholder.typicode.com/todos/1';
const BROKEN_URL = 'https://jsonplaceholder.typicode.com/todos/999999';

async function testFetch() {
  console.log('--- Testing Native Fetch ---');

  // 1. Successful request
  try {
    const res = await fetch(VALID_URL);
    if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
    const data = await res.json();
    console.log('Fetch Success:', data.title);
  } catch (err) {
    console.error('Fetch Failed:', err.message);
  }

  // 2. 404 Request
  try {
    const res = await fetch(BROKEN_URL);
    if (!res.ok) {
      throw new Error(`Fetch caught HTTP status ${res.status}`);
    }
    const data = await res.json();
    console.log(data);
  } catch (err) {
    console.log('Fetch caught expected error:', err.message);
  }
}

async function testAxios() {
  console.log('\n--- Testing Axios ---');

  // 1. Successful request
  try {
    const res = await axios.get(VALID_URL);
    console.log('Axios Success:', res.data.title);
  } catch (err) {
    console.error('Axios Failed:', err.message);
  }

  // 2. 404 Request
  try {
    await axios.get(BROKEN_URL);
  } catch (err) {
    console.log('Axios caught expected error: Status', err.response?.status);
  }
}

async function run() {
  await testFetch();
  await testAxios();
}

run();
```

Execute it in your terminal:

```bash
node test-requests.js
```

---

## Common Mistakes / Troubleshooting

- **Assuming `fetch()` rejects on 404 or 500 errors:** This is the most common bug in junior codebases. Always check `if (!response.ok)` right after awaiting `fetch()`, before you attempt to call `response.json()`.
- **Forgetting `await response.json()` in fetch:** Calling `const data = response.json()` without `await` returns an unresolved `Promise<pending>` instead of your actual data.
- **Reading `error.message` alone in Axios:** When an Axios request fails due to an HTTP error, the backend's error message (like `"Email already in use"`) is inside `error.response.data`, not in `error.message`.
- **Forgetting JSON stringification in fetch POST calls:** If you pass a plain object to `body: myObject` in `fetch()`, your browser will serialize it as `"[object Object]"`. Always pass `JSON.stringify(myObject)`.

---

## Try It Yourself

Open your editor and modify `test-requests.js`:

1. Write a function named `fetchUserPosts(userId)` using **either** `fetch()` or `Axios`.
2. Have it query `https://jsonplaceholder.typicode.com/posts?userId=${userId}`.
3. If an invalid ID (like `userId = 0`) returns an empty array `[]`, throw a custom error stating: `"No posts found for this user."`
4. Log the count of returned posts if successful.

---

## What's Next

- **Axios Interceptors:** Discover how to automatically attach JWT authorization tokens to every outgoing request.
- **AbortController Patterns:** Learn how to cancel active search requests when a user types a new character in an autocomplete bar.
- **Creating a Base API Client:** See how to create a pre-configured Axios instance with custom base URLs and retry logic.

Bookmark this guide to quickly look up error-handling patterns whenever you start a new JavaScript project.
