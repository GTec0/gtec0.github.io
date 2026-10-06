---
layout: post
title: "Git branches without fear: branch, merge, resolve conflicts"
subtitle: "Learn to create, merge, and resolve conflicts in Git with a tiny repo you can run in a terminal."
date: 2026-10-06
categories: []
tags: ["Git", "GitHub", "Beginner"]
thumbnail-img: /assets/images/banners/git-branches-without-fear-branch-merge-resolve-conflicts-banner.png
share-img: /assets/images/banners/git-branches-without-fear-branch-merge-resolve-conflicts-banner.png
author: Asahluma Tyika
---
## Introduction – what, why, who

Git lets you work on several lines of development at once.  
A *branch* is just a lightweight pointer to a commit, so you can try new ideas without breaking the main codebase.  

This tutorial is for anyone who has run `git clone` before but still feels shaky about:

* creating a branch,
* merging it back,
* fixing the inevitable merge conflict.

We’ll walk through a tiny repository, end with a clean merge, and keep the commands short enough to type on the spot.

---

## Part 1 – Core concept: a branch is a pointer

| Object | What it stores | How Git shows it |
|--------|----------------|------------------|
| **Commit** | Snapshot of all files + metadata | `git log` |
| **Branch** | Name → latest commit on that line | `git branch` |
| **HEAD**   | Pointer to *your* current branch | `git status` |

When you create a branch, Git just adds a new name that points at the current commit. No copy of files is made; the repository stays tiny.

---

## Part 2 – Creating and switching branches

| Command | Effect |
|---------|--------|
| `git branch feature-x` | Creates a new branch called `feature-x` that points at HEAD |
| `git checkout feature-x` | Moves HEAD to that branch, updates your working tree |
| `git switch -c feature-x` | Shortcut: create **and** check out in one step |

**Why switch?**  
Only the branch you’re *checked out* can be edited. Anything you commit goes onto that branch.

---

## Part 3 – Merging: fast‑forward vs three‑way

When you finish a feature, you bring it back to `main` (or `master`). Git decides between two strategies:

| Situation | Merge type | What happens |
|-----------|------------|--------------|
| `main` has not moved since you branched | **Fast‑forward** | `main` pointer simply jumps to the tip of the feature branch. No extra commit. |
| `main` has new commits | **Three‑way** | Git creates a *merge commit* that records both parents. This is where conflicts can appear. |

You trigger a merge from the target branch:

```bash
git checkout main
git merge feature-x
```

If there are no overlapping changes, Git merges automatically. If the same line was edited in both branches, you’ll get a conflict.

---

## Part 4 – Resolving a conflict

When Git can’t decide which line wins, it stops the merge and marks the file:

```text
<<<<<<< HEAD
code from main
=======
code from feature-x
>>>>>>> feature-x
```

Steps to resolve:

1. Open the file, decide the final content, and delete the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
2. Stage the fixed file: `git add <file>`.
3. Complete the merge: `git commit` (Git pre‑populates the message).

After the commit, the merge is recorded and the repository is clean again.

---

## Hands‑on example – a complete, runnable walk‑through

Open a terminal and copy‑paste each block. The whole thing works on any OS with Git installed.

```bash
# 1️⃣ Initialise a fresh repo in a temporary folder
mkdir git-branch-demo && cd git-branch-demo
git init
```

```bash
# 2️⃣ Create an initial file and commit it on the default branch (main)
echo "Hello, world!" > app.txt
git add app.txt
git commit -m "Initial commit"
```

```bash
# 3️⃣ Create and switch to a feature branch
git switch -c add-greeting
```

```bash
# 4️⃣ Edit the file on the feature branch
echo "Feature branch says: Hi there!" >> app.txt
git add app.txt
git commit -m "Add friendly greeting"
```

```bash
# 5️⃣ Switch back to main and make a conflicting edit
git checkout main
echo "Main branch says: Welcome!" > app.txt   # overwrite instead of append
git add app.txt
git commit -m "Change greeting on main"
```

```bash
# 6️⃣ Try to merge the feature branch – conflict expected
git merge add-greeting
```

You’ll see output similar to:

```
Auto-merging app.txt
CONFLICT (content): Merge conflict in app.txt
Automatic merge failed; fix conflicts and then commit the result.
```

```bash
# 7️⃣ Resolve the conflict
cat app.txt   # shows the markers
# Edit the file (any editor) to look like this:
# Hello, world!
# Feature branch says: Hi there!
# Main branch says: Welcome!
git add app.txt
git commit -m "Merge add-greeting into main, resolve greeting conflict"
```

```bash
# 8️⃣ Verify a clean history
git log --oneline --graph --decorate
```

You should see a merge commit with two parents, and the final `app.txt` contains all three lines.

```bash
# 9️⃣ Clean up (optional)
cd ..
rm -rf git-branch-demo
```

That’s the entire lifecycle: branch → work → conflict → resolve → clean merge.

---

## Common mistakes / troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `fatal: not a git repository` | Running a Git command outside a repo | `cd` into the folder that contains `.git` or run `git init` first |
| `error: Your local changes to the following files would be overwritten by merge` | Uncommitted changes on the current branch | Stash them (`git stash`), merge, then `git stash pop` |
| Merge conflict markers remain after `git commit` | Forgot to `git add` the resolved file | Run `git add <file>` again, then `git commit` |
| `Already up to date` when you expect a merge | The target branch already contains the feature (fast‑forward) | No action needed; the merge succeeded silently |
| `git switch -c <branch>` says branch already exists | Branch was created earlier | Use `git switch <branch>` to just check it out |

---

## Try it yourself

Create a second feature branch called `add-farewell`. Add a line `Goodbye!` to `app.txt`, commit, then merge it into `main` without causing a conflict (the file already has a clean state). Verify the final file contains all three greetings and the farewell.

---

## What’s next

* **Branch naming conventions** – keep your repo tidy as it grows.  
* **Rebasing vs merging** – learn when to rewrite history safely.  
* **Pull requests on GitHub** – turn the command‑line workflow into a collaborative review process.  
* **Automated conflict detection** – use CI tools to spot trouble early.

---

*Bookmark this guide for your next Git experiment.*
