---
layout: post
title: "Vim survival guide: the 20 keys you actually need"
subtitle: "A quick cheat‑sheet of the 20 Vim keys you really need, plus a 5‑minute drill to turn you into a comfortable editor."
date: 2026-10-08
categories: []
tags: ["Linux", "Terminal", "Developer Tips"]
thumbnail-img: /assets/images/banners/vim-survival-guide-the-20-keys-you-actually-need-banner.png
share-img: /assets/images/banners/vim-survival-guide-the-20-keys-you-actually-need-banner.png
author: Asahluma Tyika
---
# Vim survival guide: the 20 keys you actually need  
*Tags: Linux, Terminal, Developer Tips*

## Introduction – what, why, and who this is for  

Vim is everywhere on Linux servers, in Docker containers, and even inside many IDEs. It’s powerful, but the default learning curve feels like climbing a mountain of obscure commands. This guide cuts the noise down to **20 keys** that let you navigate, edit, and save files without ever leaving the keyboard.  

If you:  

* are new to Vim or only use it for quick edits,  
* want to feel confident after a five‑minute practice session,  

then this cheat‑sheet plus a short drill will get you editing like a pro in under ten minutes.

---

## Part 1 – The absolute essentials  

| Mode | Key | Action | Quick tip |
|------|-----|--------|-----------|
| Normal | `h` `j` `k` `l` | Move left/down/up/right (arrow keys work too) | Keep hands on home row. |
| Normal | `w` `e` `b` | Jump to start of next word / end of word / start of previous word | Use for fast word‑wise navigation. |
| Normal | `0` `^` `$` | First column / first non‑blank / end of line | Handy for aligning code. |
| Normal | `gg` `G` | First line / last line (or line number) | `G` alone = bottom; `42G` = line 42. |
| Normal | `Ctrl‑d` `Ctrl‑u` | Scroll half‑page down / up | Keeps cursor in view while scrolling. |
| Normal | `:` | Enter command‑line mode | All `:` commands end with `<Enter>`. |
| Normal | `/` `?` | Search forward / backward | Press `n` for next, `N` for previous. |
| Normal | `.` | Repeat last change | Saves typing repetitive edits. |
| Insert | `i` `a` `I` `A` | Insert before cursor / after cursor / at line start / at line end | Choose the one that keeps your hands on the home row. |
| Insert | `Esc` | Return to Normal mode | Never press `Ctrl‑[`. |
| Normal | `x` `X` | Delete character under / before cursor | Faster than `dl` or `dh`. |
| Normal | `dd` `yy` `p` | Delete line / yank (copy) line / paste after cursor | Combine with a count: `5dd` deletes five lines. |
| Normal | `u` `Ctrl‑r` | Undo / redo | Undo works across whole file, not just last command. |
| Normal | `.` (dot) | Repeat last change | Works for deletes, inserts, etc. |
| Normal | `:` `w` `q` `wq` `qa!` | Write (save) / quit / write & quit / quit all without saving | `:w` writes, `:q!` forces quit. |
| Normal | `v` `V` `Ctrl‑v` | Start characterwise, linewise, or blockwise visual mode | Use `y` or `d` after selection. |
| Normal | `>` `<` | Indent / dedent selected lines (in visual mode) | `>>` indents current line. |
| Normal | `~` | Toggle case of character under cursor | Useful for quick typo fixes. |
| Normal | `.` (dot) | Repeat last edit command | Works after any change, even a visual block. |
| Normal | `Ctrl‑[` | Same as `Esc` (alternative) | Handy if your keyboard has a dedicated `Esc`. |

These 20 keys cover **movement, editing, saving, and undo/redo**—the core workflow for any file.

---

## Part 2 – Putting the keys together: a 5‑minute editing drill  

1. **Open a test file**  
   ```bash
   echo -e "function hello(){\n    console.log('hi');\n}\n" > demo.js
   vim demo.js
   ```

2. **Navigate**  
   * Press `gg` to go to the top.  
   * Use `w` to land on `hello`.  

3. **Rename the function**  
   * Type `ciw` (change inner word) → `greet` → `<Esc>`.  

4. **Add a missing semicolon**  
   * Move to the `console.log` line with `j`.  
   * Jump to the end of the line with `$`.  
   * Press `i;` then `<Esc>`.  

5. **Duplicate the `console.log` line**  
   * `yy` (yank line).  
   * Move down with `j`.  
   * `p` (paste).  

6. **Indent the new line**  
   * `V` to select the line.  
   * `>` to indent.  

7. **Undo the duplication**  
   * Press `u`.  

8. **Save and quit**  
   * Type `:wq` and `<Enter>`.  

You’ve just used **movement (`gg`, `w`, `$`, `j`), editing (`ciw`, `i;`, `yy`, `p`, `>`), undo (`u`), and saving (`:wq`)**—all within 5 minutes.

---

## Hands‑on example – a runnable script that demonstrates Vim commands  

Below is a tiny Bash script you can copy, run, and then edit with Vim using only the 20 keys.

```bash
#!/usr/bin/env bash
# demo_vim.sh – prints a greeting and the current date

greet() {
    echo "Hello, world!"
    echo "Today is $(date +%A), $(date +%Y-%m-%d)"
}

greet
```

1. Save the script as `demo_vim.sh` and make it executable:

```bash
chmod +x demo_vim.sh
```

2. Open it in Vim:

```bash
vim demo_vim.sh
```

Now try the drill from Part 2, but with a twist:

* Change **“Hello, world!”** to **“Hi, Vim!”** (`ciw` → `Hi` → `<Esc>`).  
* Add a comment above the function (`O` → `# prints a friendly message` → `<Esc>`).  
* Delete the blank line after the function (`dd`).  
* Save (`:w`) and quit (`:q`).  

Run the script again:

```bash
./demo_vim.sh
```

You should see the updated greeting. Every change was made with the 20 keys only.

---

## Common mistakes / troubleshooting  

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Pressing `i` does nothing, cursor stays in Normal mode | Still in **Insert** mode but terminal doesn’t show the `-- INSERT --` status line (e.g., using `vim -u NONE`) | Verify you’re in a full Vim session (`vim --clean`) or check `set showmode` is enabled. |
| `:` commands give “E492: Not an editor command” | Accidentally in **Visual** mode (`v` left on) when typing `:` | Press `<Esc>` to return to Normal mode before `:`. |
| `dd` deletes the wrong line | Cursor was on the line *below* the intended one | Use `k` to move up one line before `dd`, or use a count (`2dd`) to delete multiple lines. |
| `u` doesn’t undo the last change | You are in **Insert** mode; `u` works only in Normal mode | Press `<Esc>` first, then `u`. |
| Search (`/`) finds nothing | The search pattern includes hidden characters (e.g., trailing spaces) | Use `\s*` to ignore spaces, or press `:set ignorecase` for case‑insensitive search. |

---

## Try it yourself – short exercise  

1. Open a new file `notes.txt` with Vim.  
2. Write three lines of any text.  
3. Using only the 20 keys, **reorder** the lines so the third line becomes the first.  
4. Save and quit.  

*Hint:* Use visual line mode (`V`), move the selected line with `:m` command, or yank (`yy`) and paste (`p`).  

---

## What’s next  

* **Mastering motions** – learn the power of `f`, `t`, `;`, and `,` for character‑wise jumps.  
* **Registers and macros** – record repetitive edits with `q` and replay with `@`.  
* **Plugins for beginners** – try `vim-sensible` and `nerdtree` to make Vim more approachable.  
* **From Vim to Neovim** – see why many developers switch and what new features to expect.

---

*Bookmark this cheat‑sheet and you’ll never be stuck at the Vim command prompt again.*
