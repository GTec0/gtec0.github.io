---
layout: post
title: "Fix any Git mess: detached HEAD, bad commits, wrong branch"
subtitle: "Panic‑free Git rescue recipes that use reflog to undo detached HEAD, bad commits, or wrong‑branch work."
date: 2026-10-06
categories: []
tags: ["Git", "Developer Tips"]
thumbnail-img: /assets/images/banners/fix-any-git-mess-detached-head-bad-commits-wrong-branch-banner.png
share-img: /assets/images/banners/fix-any-git-mess-detached-head-bad-commits-wrong-branch-banner.png
author: Asahluma Tyika
---
## Intro – Why you need a safety net and who this is for
You’ve just typed `git checkout <hash>` or `git commit --amend` and the terminal looks like a crime scene. The HEAD is detached, a commit landed on the wrong branch, or you accidentally rewrote history. Panic is natural, but Git has a built‑in black box called **reflog** that records every move of your HEAD and branch pointers.  

This tutorial is for developers who are comfortable with basic Git commands (`clone`, `add`, `commit`, `push`) but have never needed to dig into reflog. By the end you’ll have three repeatable rescue recipes that turn a “Git mess” into a clean state without losing work.

---

## Part 1 – Understanding the reflog safety net  

| What you see | Meaning | Typical scenario |
|--------------|---------|-------------------|
| `HEAD@{0}`   | Current position of HEAD | After any command |
| `HEAD@{n}`   | n‑th previous position of HEAD | “Where was I 3 moves ago?” |
| `branch@{0}` | Current tip of a branch | Normal branch tip |
| `branch@{n}`| n‑th previous tip of that branch | After a forced push or reset |

*Key point:* Every time you move HEAD (checkout, merge, rebase, reset, commit, amend) Git writes a line to the reflog. Even if you delete a branch, its reflog lives on until garbage collection runs (default 90 days).  

**How to read it**

```bash
git reflog --date=iso
```

The output shows a short SHA, the action, and a human‑readable message, e.g.:

```
c3f9a2b HEAD@{0}: commit: Fix typo in README
a7b1d4e HEAD@{1}: checkout: moving from master to feature/login
...
```

You can jump back to any entry with `git checkout <ref>` or `git reset --hard <ref>`.

---

## Part 2 – Rescue recipe #1: Detached HEAD → back to a branch  

### When it happens
You ran `git checkout <commit‑hash>` to inspect an old version, or a merge conflict left you on a detached HEAD. Any new commits you make now sit on an orphaned pointer.

### Step‑by‑step

| Step | Command | What it does |
|------|---------|--------------|
| 1️⃣ | `git status` | Confirms you’re in “detached HEAD” state. |
| 2️⃣ | `git reflog -1` | Shows the commit you were on before the detach. |
| 3️⃣ | `git branch temp-fix <commit‑hash>` | Creates a temporary branch at the current (detached) commit. |
| 4️⃣ | `git checkout master` *(or your target branch)* | Returns you to a proper branch. |
| 5️⃣ | `git merge temp-fix` | Moves the work you made while detached onto the real branch. |
| 6️⃣ | `git branch -d temp-fix` | Cleans up the helper branch. |

### One‑liner rescue

```bash
git checkout -b rescue-branch && git checkout master && git merge rescue-branch && git branch -d rescue-branch
```

If you *don’t* need the detached work, simply `git checkout master` and discard the dangling commits; they’ll disappear after reflog expiration.

---

## Part 3 – Rescue recipe #2: Bad commit on the wrong branch  

### Typical mistake
You thought you were on `feature/login` but you were still on `master`. You committed, pushed, and now the history looks wrong.

### Step‑by‑step

| Step | Command | Explanation |
|------|---------|-------------|
| 1️⃣ | `git branch` | Verify you’re on the wrong branch. |
| 2️⃣ | `git reflog` | Locate the SHA of the bad commit (call it `BAD`). |
| 3️⃣ | `git checkout feature/login` | Switch to the intended branch. |
| 4️⃣ | `git cherry-pick BAD` | Apply the bad commit on the right branch. |
| 5️⃣ | `git checkout master` |
| 6️⃣ | `git revert BAD` *(if already pushed)* | Creates a new commit that undoes the bad change. |
| 7️⃣ | `git push` | Propagate both the cherry‑pick and the revert. |

### When the bad commit is the *latest* on master and you haven’t pushed yet

```bash
git reset --hard HEAD~1      # move master back one commit
git checkout feature/login
git cherry-pick <BAD_SHA>
```

### Quick cheat sheet

```bash
# Move a commit from the current branch to another
git checkout target-branch
git cherry-pick <bad-sha>
# Undo it on the source branch (if already pushed)
git checkout source-branch
git revert <bad-sha>
```

---

## Part 4 – Rescue recipe #3: Accidentally rewound history (forced push)  

### Scenario
You ran `git push -f` after a rebase and now the remote is missing several commits. Your local reflog still knows about them.

### Step‑by‑step

| Step | Command | Why |
|------|---------|-----|
| 1️⃣ | `git fetch --all` | Ensure you have the latest remote refs. |
| 2️⃣ | `git reflog show origin/main` | Look for the SHA of the remote tip before the force‑push. |
| 3️⃣ | `git checkout -b restore-branch <old‑remote‑sha>` | Recover the lost commits in a new branch. |
| 4️⃣ | `git push origin restore-branch:main` | Re‑publish the original history (needs force if you want to replace again). |
| 5️⃣ | `git branch -d restore-branch` | Clean up after verification. |

**Safety tip:** Before you push a forced update, create a backup branch:

```bash
git branch backup-before-force
git push origin backup-before-force
```

---

## Hands‑on example – From panic to clean repo in 8 commands  

Below is a complete, copy‑pasteable session that demonstrates all three recipes. Open a fresh terminal and run:

```bash
# 1️⃣ Set up a demo repo
git init demo-repo && cd demo-repo
echo "Hello" > file.txt
git add . && git commit -m "Initial commit"

# 2️⃣ Create a feature branch and make a good commit
git checkout -b feature/login
echo "Login page" >> file.txt
git commit -am "Add login page"

# 3️⃣ Oops – detach HEAD and add a bad commit
git checkout HEAD~1          # detached at Initial commit
echo "Buggy change" >> file.txt
git commit -am "Buggy commit on detached HEAD"

# 4️⃣ Rescue the detached work (Recipe #1)
git branch temp-fix HEAD      # create temp branch at buggy commit
git checkout feature/login    # go back to proper branch
git merge temp-fix            # bring buggy work onto feature
git branch -d temp-fix        # delete helper

# 5️⃣ Realize the buggy commit belongs on a different branch
git checkout -b bugfix
git cherry-pick HEAD~1        # move it to bugfix
git checkout feature/login
git revert HEAD~1             # undo it on feature

# 6️⃣ Simulate a forced push disaster
git checkout main
git reset --hard HEAD~1       # lose the initial commit locally
git push origin main --force   # (pretend remote had the old commit)

# 7️⃣ Recover the lost commit (Recipe #3)
git reflog show origin/main   # find old SHA, assume abc1234
git checkout -b restore abc1234
git push origin restore:main   # restore remote history
git branch -d restore
```

All commands are runnable on any system with Git installed. After step 7 you’ll see the repository back in a sane state, with the buggy change safely on its own `bugfix` branch.

---

## Common mistakes / troubleshooting  

- **Forgot to create a temporary branch before leaving detached HEAD**  
  *Fix:* Run `git branch tmp <detached‑sha>` immediately after the detach; otherwise the commit may become unreachable.

- **`git revert` fails because the commit is already reverted**  
  *Fix:* Use `git revert -m 1 <merge‑sha>` for merge commits, or simply delete the stray commit with `git reset --hard HEAD~1` if it hasn’t been pushed.

- **Reflog entry not found after `git gc`**  
  *Fix:* Run `git reflog expire --expire-unreachable=now --all && git gc --prune=now` only **after** you have recovered what you need. Until then, avoid manual garbage collection.

- **Force‑pushing the restored branch gets rejected**  
  *Fix:* Add `--force-with-lease` instead of plain `--force` to protect against overwriting newer remote work.

- **Cherry‑pick reports conflicts you don’t understand**  
  *Fix:* Open the conflicted files, resolve manually, then run `git cherry-pick --continue`. If the conflict is too messy, abort with `git cherry-pick --abort` and try `git format-patch` + `git am` as an alternative.

---

## Try it yourself  

1. Clone any small public repo (e.g., `git clone https://github.com/git/git.git`).  
2. Create a new branch, make a commit, then intentionally detach HEAD and add another commit.  
3. Use the **detached‑HEAD rescue** recipe to bring the stray commit back onto your branch without losing any work.

---

## What’s next  

- **Branch‑level backups** – automate creation of reflog‑based snapshots before risky operations.  
- **Interactive reflog explorer** – using `gitk --reflog` or third‑party GUIs to visualize history.  
- **Recovering deleted branches** – a deep dive into `git fsck --lost-found`.  
- **Safety‑first workflows** – how to set up protected branches and pre‑push hooks that prevent accidental force pushes.

---

*Bookmark this page for the next time Git throws you a curveball.*
