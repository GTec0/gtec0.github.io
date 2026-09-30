# GTec Autopilot — free AI blog generator for gtec0.github.io (post-ONLY edition)

Generates tutorials, **you share them yourself**. Zero paid APIs, zero social tokens.

```
pick topic (trending HN/dev.to/GitHub + evergreen backlog, deduped)
  → write tutorial (Gemini free tier → Groq free → Ollama → offline template)
  → banner image (HuggingFace FLUX free tier → Pollinations → offline Pillow)
  → QA gates (length, code blocks, banned phrases, similarity)
  → beautiful-jekyll _posts/*.md + assets/images/banners/*
  → SHARE.txt: ready-to-paste FB/IG/Threads captions (you post them manually)
  → commit & push (GitHub Actions or your PC cron)
```

## Extra features

- **Trending radar**: HN top stories, dev.to rising, GitHub trending → rewritten as tutorials.
- **Evergreen backlog** (`topics.yaml`) round-robin — add ideas any time, never repeats (tracked in `state.json` + diffed against `_posts/`).
- **Fail-fast, never filler**: if Gemini/Groq/Ollama all fail, the run aborts (exit 4, red ✗ in Actions) and publishes nothing. The offline template exists only for local `--dry-run`/`--allow-template` testing.
- **QA firewall**: blocks short / codeless / off-voice / near-duplicate posts even in fully-auto mode (exit 2, nothing committed).
- **Share kit**: every run prints + saves `SHARE.txt` — FB caption (link attaches preview), IG caption (link-in-bio wording, since IG captions aren't clickable), ≤500-char Threads caption, plus the banner path to upload.
- **Dry-run preview**: `python main.py --dry-run` → `preview/` folder, zero side effects.

## Install (blog repo)

```bash
cd /path/to/gtec0.github.io   # your beautiful-jekyll checkout
cp -r /path/to/gtec-autopilot autopilot
cp autopilot/.github/workflows/autopilot.yml .github/workflows/autopilot.yml
# optional secrets: GEMINI_API_KEY (free from https://aistudio.google.com) for text,
# HF_TOKEN (free from https://huggingface.co/settings/tokens) for best banners —
# skip either and the chain falls back (template is NEVER used for real posts)
git add autopilot .github/workflows/autopilot.yml && git commit -m "add autopilot" && git push
```

Local test:
```bash
cd autopilot && pip install -r requirements.txt && python main.py --dry-run
```

Schedule: twice daily, 06:00 + 18:00 UTC via Actions (or your PC cron:
`0 6,18 * * * /path/to/blog/autopilot/run_autopilot.sh`). After each run, open
`autopilot/SHARE.txt` and paste the captions to Facebook / Instagram / Threads yourself.

## Files

| Path | What |
|---|---|
| `main.py` | CLI orchestrator |
| `config.yaml` | niches, lengths, images, QA, hashtags |
| `topics.yaml` | evergreen backlog |
| `autopilot/topics.py` | trending + dedup picker |
| `autopilot/llm.py` | Gemini/Groq/Ollama/template chain |
| `autopilot/images.py` | HuggingFace→Pollinations→Pillow banner chain |
| `autopilot/post.py` | beautiful-jekyll front matter writer |
| `autopilot/captions.py` | FB/IG/Threads caption builders (for SHARE.txt) |
| `autopilot/qa.py`, `state.py` | quality gates, dedup state |
