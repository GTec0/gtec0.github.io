---
layout: post
title: "Regular expressions part 2: groups, alternation and real validation"
subtitle: "Level up your regex skills with capture groups, alternation, and practical phone and email validation in Python and JavaScript."
date: 2026-10-15
categories: []
tags: ["Python", "JavaScript", "Programming"]
thumbnail-img: /assets/images/banners/regular-expressions-part-2-groups-alternation-and-real-validation-banner.png
share-img: /assets/images/banners/regular-expressions-part-2-groups-alternation-and-real-validation-banner.png
author: Asahluma Tyika
---
# Regular expressions part 2: groups, alternation and real validation

In [Part 1 of our regex series](https://example.com/regex-part-1), we looked at basic characters, character sets, anchors, and quantifiers. You learned how to match fixed patterns like three digits or a string that starts with a capital letter.

That foundation gets you far, but real-world data is rarely neat. You will run into strings where you need to match either "cat" or "dog", isolate the domain name from an email address, or parse an optional country code from an incoming phone number.

This tutorial is for developers who know the basic syntax and want to write expressive, reliable patterns for user input. We will look at alternation, capturing groups, non-capturing groups, and named groups. Then, we will assemble practical patterns for phone numbers and email addresses in Python and JavaScript.

---

## Part 1: Alternation (`|`) — The Regex "OR"

The pipe character (`|`) represents alternation. It tells the regex engine to match either what is on the left side or what is on the right side.

```regex
apple|banana
```

This pattern matches the text "apple" or "banana". 

The most common trap with alternation is operator precedence. The pipe splits the *entire* expression around it unless you contain it.

| Pattern | Input | Match Result | Why? |
| :--- | :--- | :--- | :--- |
| `cat|dog food` | `cat` | **Match** (`cat`) | Matches either `cat` or `dog food` |
| `cat|dog food` | `cat food` | **Match** (`cat`) | Matches the `cat` at the beginning |
| `(cat|dog) food` | `cat food` | **Match** (`cat food`) | Parentheses group the alternation |
| `(cat|dog) food` | `food` | **No match** | Must match `cat` or `dog`, followed by ` food` |

To apply alternation to a specific part of a pattern, wrap the choices in parentheses: `(mon|tues|wednes)day`.

---

## Part 2: Groups — Capturing, Non-Capturing, and Named

Parentheses do two things at once: they group tokens together, and they *capture* the matched text so you can extract it later.

### 1. Capturing Groups: `(...)`

Whenever you use standard parentheses, the regex engine stores the substring matched inside them into a numbered slot, starting at 1. Slot 0 always holds the entire match.

Let us say you want to parse an HTTP header value like `Content-Type: text/html`:

```regex
Content-Type: (\w+)/(\w+)
```

- Group 0: `Content-Type: text/html`
- Group 1: `text`
- Group 2: `html`

### 2. Non-Capturing Groups: `(?:...)`

Sometimes you need grouping logic, but you do not care about extracting that specific piece. Storing captures consumes memory and clutters your results. 

Prefix the inside of the group with `?:` to disable capturing:

```regex
(?:https?|ftp)://([a-zA-Z0-9.-]+)
```

In this pattern:
- `(?:https?|ftp)` groups the protocols so the `|` works properly, but it does **not** create a capture slot.
- `([a-zA-Z0-9.-]+)` becomes Group 1, holding only the host domain.

### 3. Named Capturing Groups

Numbered groups get confusing quickly once a pattern has three or four sets of parentheses. Named groups let you assign meaningful identifiers to your extracts.

- **Python syntax:** `(?P<name>pattern)`
- **JavaScript syntax:** `(?<name>pattern)`

*(Note: JavaScript supports Python's syntax in modern engines, but the `(?<name>...)` syntax is the official ECMAScript standard).*

---

## Part 3: Practical Pattern 1 — North American Phone Numbers

Let us build a pattern for standard US/Canadian phone numbers. These numbers come in many formats:
- `555-0199`
- `(555) 019-2834`
- `555.019.2834`
- `1-555-019-2834`
- `+1 555 019 2834`

Let us break down the requirements:
1. Optional country code: a leading `+` or `1`, followed by a separator.
2. Area code: 3 digits, sometimes enclosed in `(...)`.
3. Separator: space, dash, dot, or nothing.
4. Prefix: 3 digits.
5. Line number: 4 digits.

Here is the combined pattern:

```regex
^(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$/
```

Let us dissect the pieces:

| Segment | Meaning |
| :--- | :--- |
| `^` and `$` | Match the start and end of the string to avoid partial hits. |
| `(?:\+?1[-.\s]?)?` | Optional non-capturing group: an optional `+`, a `1`, and an optional separator (`-`, `.`, or space). The trailing `?` makes the whole country code optional. |
| `\(?([0-9]{3})\)?` | Matches an optional `(`, captures exactly 3 digits (Area Code), and matches an optional `)`. |
| `[-.\s]?` | Optional separator between area code and central office code. |
| `([0-9]{3})` | Captures 3 digits (Exchange code). |
| `[-.\s]?` | Optional separator. |
| `([0-9]{4})` | Captures the final 4 digits (Subscriber number). |

---

## Part 4: Practical Pattern 2 — Web Form Email Validation

The official email specification ([RFC 5322](https://datatracker.ietf.org/doc/html/rfc5322)) allows bizarre formats like `"very.(),:;<>[]\".VERY.\"very@\\ \"very\".unusual"@strange.example.com`. Writing a regex for full RFC compliance results in an unmaintainable, multi-page expression.

For web applications, your goal is simpler: catch typos (missing `@`, spaces, missing TLD) and confirm the basic shape before sending a verification link.

Here is a balanced email validation pattern:

```regex
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

How it works:
1. `^[a-zA-Z0-9._%+-]+`: The username allows letters, digits, and common email punctuation (`.`, `_`, `%`, `+`, `-`).
2. `@`: A single, mandatory at-sign.
3. `[a-zA-Z0-9.-]+`: The domain name allows letters, numbers, hyphens, and subdomains separated by dots.
4. `\.`: A literal dot before the Top-Level Domain (TLD).
5. `[a-zA-Z]{2,}$`: The TLD must be at least two letters long (e.g., `com`, `org`, `tech`).

If you want to extract the username and domain separately, wrap them in named groups:

```regex
^(?P<user>[a-zA-Z0-9._%+-]+)@(?P<domain>[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$
```

---

## Hands-on example

Let us run these patterns in both Python and JavaScript to see how capture groups work in code.

### Python Example

Save this as `regex_demo.py` and run it with `python regex_demo.py`:

```python
import re

# 1. Phone parsing with named capture groups
phone_pattern = re.compile(
    r"^(?:\+?1[-.\s]?)?\(?(?P<area>\d{3})\)?[-.\s]?(?P<prefix>\d{3})[-.\s]?(?P<line>\d{4})$"
)

raw_phones = [
    "+1 (555) 234-5678",
    "555.867.5309",
    "1-800-555-0199",
    "invalid-number-123",
]

print("--- Phone Number Extraction ---")
for text in raw_phones:
    match = phone_pattern.match(text.strip())
    if match:
        data = match.groupdict()
        formatted = f"({data['area']}) {data['prefix']}-{data['line']}"
        print(f"Original: {text:<20} -> Standardized: {formatted}")
    else:
        print(f"Original: {text:<20} -> REJECTED")

# 2. Email validation and group extraction
email_pattern = re.compile(
    r"^(?P<account>[a-zA-Z0-9._%+-]+)@(?P<host>[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})$"
)

sample_email = "asahluma.dev@gtec.example.com"
email_match = email_pattern.match(sample_email)

print("\n--- Email Parsing ---")
if email_match:
    print(f"Full address : {email_match.group(0)}")
    print(f"Account name : {email_match.group('account')}")
    print(f"Domain host  : {email_match.group('host')}")
```

### JavaScript Example

Save this as `regex_demo.js` and run it with `node regex_demo.js`:

```javascript
const phonePattern = /^(?:\+?1[-.\s]?)?\(?(?<area>\d{3})\)?[-.\s]?(?<prefix>\d{3})[-.\s]?(?<line>\d{4})$/;

const testNumbers = [
  "(555) 444-3322",
  "555.222.1199",
  "9999-bad-input"
];

console.log("--- Phone Validation (Node.js) ---");
testNumbers.forEach((num) => {
  const match = num.match(phonePattern);
  if (match) {
    const { area, prefix, line } = match.groups;
    console.log(`Matched: ${num} -> (${area}) ${prefix}-${line}`);
  } else {
    console.log(`Failed:  ${num}`);
  }
});
```

---

## Common mistakes / troubleshooting

- **Unintended Captures with Alternation:** Writing `http|https://` creates an alternation between the entire string `http` and `https://`. Wrap your options in a non-capturing group: `(?:http|https)://` or write `https?://`.
- **Forgetting that `.` matches any character:** If you write `domain.com`, the unescaped dot matches `domain-com` or `domainxcom`. Always escape dots intended as literal punctuation: `domain\.com`.
- **Mismatched Group Indexing:** In JavaScript and Python, index `0` is the entire matched string. Your first capture group starts at index `1`. If you expect `match[0]` to be the first parenthesis, your indices will be off by one.
- **Accidental Greedy Subgroups:** Inside groups, quantifiers like `.*` will eat separators if you are not careful. Use character classes with negated sets or specific tokens instead of open-ended wildcards (e.g., use `[^@\s]+` instead of `.+` before an `@` symbol).

---

## Try it yourself

Write a regular expression that parses a standard date string in `YYYY-MM-DD` format (such as `2026-03-29`).

**Requirements:**
1. Match the full string from start to finish.
2. Group the year (4 digits), month (2 digits), and day (2 digits) using **named groups**: `year`, `month`, and `day`.
3. Support either hyphens (`-`) or forward slashes (`/`) as separators, but require the same separator for both positions (hint: you can either match both explicitly or use alternation).

*Test cases:*
- `2026-03-29` should pass (`year: 2026, month: 03, day: 29`).
- `1999/12/31` should pass (`year: 1999, month: 12, day: 31`).
- `2026-03/29` should fail (mismatched separators).

---

## What's next

You now have the tools to group tokens, handle multiple conditions, and extract meaningful sub-data out of strings.

Coming up in our next installment:
- **Lookahead and Lookbehind assertions** (`(?=...)`, `(?!...)`): how to check what comes next without including it in the match.
- **Enforcing password complexity**: requiring digits, symbols, and uppercase characters in a single regex.
- **Regex performance and catastrophic backtracking**: how to prevent poorly written patterns from freezing your server.

Bookmark this guide for the next time you need to extract clean values from messy user input.
