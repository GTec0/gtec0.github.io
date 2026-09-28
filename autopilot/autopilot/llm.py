"""Free text generation with graceful fallback chain.

Order: Gemini (free tier) -> Groq (free tier) -> Ollama (local, free) -> built-in template.
The template path needs ZERO keys, so `main.py --dry-run` and CI always produce
a solid tutorial even with no secrets configured.
"""
from __future__ import annotations
import json
import re
import urllib.request
import urllib.error


SYSTEM_STYLE = (
    "You write for 'Code easier! | GTec' — a programming/tech tutorials blog by Asahluma Tyika. "
    "Audience: beginners to intermediate developers. Tone: friendly, plain-English, practical, "
    "South-African-dev-blog voice. No fluff, no 'as an AI'. Every claim must be runnable/verifiable. "
    "Use ## headings, fenced code blocks with language tags, tables where they help."
)

POST_PROMPT = """Write a {min_words}-{max_words} word markdown tutorial titled: "{topic}"
Angle: {angle}. Tags: {tags}.
Required structure:
## (intro: what/why, who it's for)
## Part 1/2/3... (core concepts, small steps, tables where useful)
## Hands-on example (full runnable code/commands)
## Common mistakes / troubleshooting (3-5 bullets with fixes)
## Try it yourself (1 short exercise)
## What's next (2-4 bullets, tease a follow-up post)
Rules: plain English, beginner friendly, all code fenced with language, no lorem ipsum,
no 'in conclusion'. End with a 1-sentence bookmark line.
Also output 2 diagram ideas as HTML comments: <!-- DIAGRAM: <matplotlib-friendly description> -->
Also output a 1-line excerpt (<=160 chars) as: <!-- EXCERPT: ... -->
Body only, no front matter.
"""


def _http_post_json(url: str, payload: dict, headers: dict, timeout=90) -> dict:
    data = json.dumps(payload).encode()
    # NOTE: Groq sits behind Cloudflare, which 403s (error 1010) clients with
    # no/recognizable User-Agent — e.g. Python-urllib. Always identify ourselves.
    headers = {"User-Agent": "gtec-autopilot/1.0 (+https://gtec0.github.io)",
               **headers, "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _warn(provider: str, e: Exception) -> None:
    """Log WHY a provider failed. Never prints credentials (key redacted)."""
    detail = ""
    try:
        if isinstance(e, urllib.error.HTTPError):
            try:
                detail = e.read().decode("utf-8", "replace")[:400]
            except Exception:
                pass
    except Exception:
        pass
    msg = f"{type(e).__name__}: {e} {detail}".strip()
    msg = re.sub(r"key=[A-Za-z0-9_\-]+", "key=***", msg)
    msg = re.sub(r"Bearer [A-Za-z0-9_.\-]+", "Bearer ***", msg)
    print(f"[llm:{provider}] FAILED: {msg[:400]}", flush=True)


def gemini_generate(key: str, model: str, topic: str, angle: str, tags: list, lo: int, hi: int) -> str | None:
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        body = {"system_instruction": {"parts": [{"text": SYSTEM_STYLE}]},
                "contents": [{"parts": [{"text": POST_PROMPT.format(topic=topic, angle=angle, tags=', '.join(tags), min_words=lo, max_words=hi)}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 6000}}
        res = _http_post_json(url, body, {})
        parts = res["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts).strip() or None
    except Exception as e:
        _warn("gemini", e)
        return None


def groq_generate(key: str, model: str, topic: str, angle: str, tags: list, lo: int, hi: int) -> str | None:
    try:
        body = {"model": model, "temperature": 0.7, "max_tokens": 6000,
                "messages": [{"role": "system", "content": SYSTEM_STYLE},
                             {"role": "user", "content": POST_PROMPT.format(topic=topic, angle=angle, tags=', '.join(tags), min_words=lo, max_words=hi)}]}
        res = _http_post_json("https://api.groq.com/openai/v1/chat/completions", body,
                              {"Authorization": f"Bearer {key}"})
        return res["choices"][0]["message"]["content"].strip() or None
    except Exception as e:
        _warn("groq", e)
        return None


def ollama_generate(host: str, model: str, topic: str, angle: str, tags: list, lo: int, hi: int) -> str | None:
    try:
        body = {"model": model, "stream": False, "system": SYSTEM_STYLE,
                "prompt": POST_PROMPT.format(topic=topic, angle=angle, tags=', '.join(tags), min_words=lo, max_words=hi)}
        res = _http_post_json(f"{host.rstrip('/')}/api/generate", body, {})
        return (res.get("response") or "").strip() or None
    except Exception as e:
        _warn("ollama", e)
        return None


def template_generate(topic: str, angle: str, tags: list) -> str:
    """Zero-key fallback: a genuinely useful tutorial skeleton filled around the topic."""
    slug_words = re.sub(r"[^A-Za-z0-9 ]", "", topic)
    return f"""<!-- EXCERPT: {topic} — a plain-English, hands-on tutorial with runnable examples. -->
If you've been meaning to learn **{topic}**, this post is for you. We keep it plain-English, hands-on, and beginner friendly — no assumed knowledge beyond basic terminal/Python use.

> **Who this is for:** beginners to intermediate devs. **What you'll get:** working examples you can run in under 15 minutes.

---

## What it is and why it matters

**{topic}** comes up constantly in real projects ({angle}). Instead of memorizing flags or syntax, you'll learn the *mental model* first, then lock it in with runnable examples.

Think of it like this: the tool has a small set of core ideas, and everything else is a combination of those ideas. Learn the core, and the docs suddenly make sense.

---

## Part 1: The core idea in 2 minutes

Every {topic} workflow boils down to three steps:

| Step | What you do | Example |
|---|---|---|
| 1. Inspect | Look at what you have | `ls -la`, `pwd`, `cat file` |
| 2. Try safely | Run the non-destructive version first | add `--dry-run`, copy before you edit |
| 3. Apply | Run the real command, verify output | re-run with `echo $?`, check results |

**Scenario:** you want to practice without breaking anything. Make a sandbox:

```bash
mkdir -p ~/sandbox && cd ~/sandbox
echo "hello gtec" > demo.txt
cat demo.txt
```

You now have a safe playground for everything below.

---

## Part 2: Hands-on walkthrough

### Example 1 — see what's happening

```bash
ls -la
cat demo.txt
```

Expected output: you see `demo.txt` listed, and its contents printed. If a command prints nothing, that's data too — it usually means "success, no news".

### Example 2 — do it with Python as well

```python
from pathlib import Path
p = Path("demo.txt")
print(p.read_text())
print(f"size={{p.stat().st_size}} bytes")
```

### Example 3 — make it repeatable (script it)

```bash
cat > run.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
echo "== {slug_words} =="
ls -la
cat demo.txt
EOF
chmod +x run.sh
./run.sh
```

<!-- DIAGRAM: bar chart comparing manual steps vs scripted steps (3 bars: time saved) -->
<!-- DIAGRAM: flowchart: Inspect -> Try safely -> Apply -> Verify -->

---

## Part 3: 10 quick recipes (copy-paste ready)

| # | Goal | Command |
|---|---|---|
| 1 | Show everything including hidden files | `ls -la` |
| 2 | Find a file by name | `find . -name "*.py" 2>/dev/null` |
| 3 | Search inside files | `grep -rn "TODO" . --include="*.py"` |
| 4 | Watch a log live | `tail -f /var/log/syslog` |
| 5 | Check disk space | `df -h` |
| 6 | Check what's listening on a port | `ss -tlnp` then filter for 8000 |
| 7 | Retry the last command with sudo | `sudo !!` |
| 8 | See your Python version | `python3 --version` |
| 9 | Make a script executable | `chmod +x run.sh` |
| 10 | Undo the last commit (keep changes) | `git reset --soft HEAD~1` |

Run each one in `~/sandbox` first. For every recipe, ask: what did it print, and what
would happen if you added `--dry-run` or pointed it at `/` instead? That one question
prevents most beginner disasters.

### Example 4 — chain tools with a pipe

```bash
ls -la | sort -k5 -n | tail -5
cat demo.txt | tr 'a-z' 'A-Z'
```

Pipes (`|`) send one command's output into the next. Here we sort files by size and
show the 5 biggest, then uppercase the demo file. Piping is the single highest-leverage
skill in this whole post — practice it until it feels boring.

---

## Common mistakes / troubleshooting

- **"Permission denied"** — you need `chmod +x run.sh` on scripts, or `sudo` only for system paths. Never `chmod 777` to "fix" it.
- **"No such file or directory"** — run `pwd` and `ls`; 90% of the time you're in the wrong folder.
- **Copy-paste mangling quotes** — retype quotes/dashes if a pasted command fails with a syntax error.
- **Destructive flags first** — always run the read-only version (`--dry-run`, `ls`, `echo`) before the write/delete version.

---

## Try it yourself

In `~/sandbox`, adapt the script above to your own files: list them, print one, and add a check (e.g. `test -f demo.txt && echo OK`). If it prints `OK`, you've got it.

---

## What's next

- Bookmark this page — the sandbox + script pattern works for almost every Linux/Python topic here.
- Next up on GTec: a deeper dive into automation (loops, functions, cron).
- Got stuck? Email the blog or comment on the Facebook post — include the exact command + error message.

Happy hacking — and remember: inspect first, script it, then automate. 🔧
"""


def generate_post(cfg: dict, topic: dict, allow_template: bool = False) -> tuple[str | None, str]:
    """Returns (markdown_body, provider_name).

    If every real provider fails and allow_template is False, returns (None,
    reason) — the caller must abort WITHOUT publishing. The offline template
    is only for local dry-runs, never for real posts.
    """
    lo = cfg["content"].get("min_words", 900)
    hi = cfg["content"].get("max_words", 1600)
    env = cfg["_env"]
    t, a, tg = topic["topic"], topic.get("angle", ""), topic.get("tags", [])
    print(f"[llm] keys: gemini={'set' if env['gemini_key'] else 'MISSING'} "
          f"groq={'set' if env['groq_key'] else 'missing'} "
          f"ollama={'set' if env['ollama_host'] else 'missing'}", flush=True)
    if env["gemini_key"]:
        txt = gemini_generate(env["gemini_key"], env["gemini_model"], t, a, tg, lo, hi)
        if txt and len(txt.split()) > 300:
            return txt, f"gemini:{env['gemini_model']}"
        print("[llm] gemini unusable, trying next provider...", flush=True)
    if env["groq_key"]:
        txt = groq_generate(env["groq_key"], env["groq_model"], t, a, tg, lo, hi)
        if txt and len(txt.split()) > 300:
            return txt, f"groq:{env['groq_model']}"
    if env["ollama_host"]:
        txt = ollama_generate(env["ollama_host"], env["ollama_model"], t, a, tg, lo, hi)
        if txt and len(txt.split()) > 300:
            return txt, f"ollama:{env['ollama_model']}"
        print("[llm] ollama unusable, no providers left.", flush=True)
    if allow_template:
        print("[llm] FALLBACK: using offline template (testing only — never for real posts).", flush=True)
        return template_generate(t, a, tg), "template(free,offline)"
    return None, "all-providers-failed"


def extract_excerpt_and_diagrams(body: str) -> tuple[str, list[str], str]:
    excerpts = re.findall(r"<!--\s*EXCERPT:\s*(.*?)\s*-->", body, re.S)
    raw_diagrams = re.findall(r"<!--\s*DIAGRAM:\s*(.*?)\s*-->", body, re.S)
    # dedupe: LLMs often repeat the same diagram idea twice — keep first occurrence
    seen, diagrams = set(), []
    for d in raw_diagrams:
        k = d.strip().lower()
        if k and k not in seen:
            seen.add(k)
            diagrams.append(d.strip())
    diagrams = diagrams[:2]
    clean = re.sub(r"<!--\s*(EXCERPT|DIAGRAM):.*?-->", "", body, flags=re.S)
    excerpt = excerpts[0].strip()[:160] if excerpts else ""
    if not excerpt:
        para = re.sub(r"[#>*`\-]", "", clean).split("\n\n")
        para = [p.strip().replace("\n", " ") for p in para if len(p.strip()) > 60]
        excerpt = (para[0][:157] + "...") if para else ""
    return excerpt, diagrams, re.sub(r"\n{3,}", "\n\n", clean).strip() + "\n"
