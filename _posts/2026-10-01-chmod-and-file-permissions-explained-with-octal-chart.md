---
layout: post
title: "chmod and file permissions explained with octal chart"
subtitle: "Master Linux file permissions and chmod with an easy octal chart, clear math breakdowns, and 5 practical real-world terminal scenarios."
date: 2026-10-01
categories: []
tags: ["Linux", "Terminal", "Beginner"]
thumbnail-img: /assets/images/banners/chmod-and-file-permissions-explained-with-octal-chart-banner.png
share-img: /assets/images/banners/chmod-and-file-permissions-explained-with-octal-chart-banner.png
author: Asahluma Tyika
---
## Understanding File Permissions in Linux

Ever tried running a shell script or saving a configuration file, only to be stopped cold by `bash: ./script.sh: Permission denied`?

Every file and directory in Linux has an explicit list of rules deciding who can look at it, who can edit it, and who can run it. The tool you use to manage these rules is `chmod`, which stands for **ch**ange **mod**e.

If you are a web developer deploying code, a sysadmin locking down servers, or a beginner trying to get comfortable inside the terminal, mastering `chmod` is a rite of passage. Once you understand the simple math behind Linux permissions, you will never have to guess random numbers like `777` again.

---

## Part 1: The Three Permissions and the Three Audiences

To configure permissions, Linux answers two questions: **What can be done?** and **Who can do it?**

### The Three Actions (Read, Write, Execute)

There are three basic rights you can grant:

*   **Read (`r`)**: Open and view file contents, or list the files inside a directory.
*   **Write (`w`)**: Modify, overwrite, or delete a file, or create/delete files inside a directory.
*   **Execute (`x`)**: Run a file as a program or script, or enter (`cd` into) a directory.

### The Three Audiences (User, Group, Others)

Every file assigns those actions to three distinct roles:

1.  **User (`u`)**: The owner of the file (usually the person who created it).
2.  **Group (`g`)**: A collection of users who share access to the file.
3.  **Others (`o`)**: Everyone else on the system.

When you run `ls -l` in your terminal, Linux displays these rules as a 10-character string:

```text
-rwxr-xr--
```

Here is how to read that string from left to right:

| Position | Character | Meaning |
| :--- | :--- | :--- |
| `0` | `-` | File type (`-` for regular file, `d` for directory) |
| `1-3` | `rwx` | **User (Owner)** can read, write, and execute |
| `4-6` | `r-x` | **Group** can read and execute, but cannot write |
| `7-9` | `r--` | **Others** can only read |

A dash (`-`) means that specific permission is not granted.

---

## Part 2: The Octal Chart (The Easy Math Behind chmod)

While you can use letters to modify permissions (like `chmod u+x script.sh`), numeric mode—also called **octal notation**—is the industry standard because it lets you set permissions for User, Group, and Others all at once using three numbers.

Each permission has a fixed numerical value:

*   **Read (`r`)** = `4`
*   **Write (`w`)** = `2`
*   **Execute (`x`)** = `1`
*   **No permission (`-`)** = `0`

To build an octal digit, simply add the numbers together:

### The Complete Octal Chart

| Octal Value | Binary | Permissions String | Human Meaning |
| :--- | :--- | :--- | :--- |
| **0** | `000` | `---` | No access at all |
| **1** | `001` | `--x` | Execute only |
| **2** | `010` | `-w-` | Write only (rare) |
| **3** | `011` | `-wx` | Write and execute (rare) |
| **4** | `100` | `r--` | Read only |
| **5** | `101` | `r-x` | Read and execute |
| **6** | `110` | `rw-` | Read and write |
| **7** | `111` | `rwx` | Full control (read, write, execute) |

When you supply three digits to `chmod`, you are setting:
1.  **Digit 1**: User permissions
2.  **Digit 2**: Group permissions
3.  **Digit 3**: Others permissions

For example, `chmod 754 file.txt` means:
*   **7** (`4 + 2 + 1`): Owner can **read**, **write**, and **execute**.
*   **5** (`4 + 0 + 1`): Group can **read** and **execute**.
*   **4** (`4 + 0 + 0`): Others can only **read**.

---

## Part 3: 5 Real-World Scenarios

You do not need to memorize every possible combination. In day-to-day work, you will repeatedly use these five standard configurations:

### Scenario 1: Securing Your Private SSH Key (`600`)

SSH strictly refuses to connect if your private key is accessible to anyone else on the machine.

*   Owner: Read + Write (`4 + 2 = 6`)
*   Group: None (`0`)
*   Others: None (`0`)

```bash
chmod 600 ~/.ssh/id_rsa
```

### Scenario 2: Standard Static Web Files (`644`)

For HTML, CSS, images, and config files on a web server, the owner needs to edit them, but the web server process (running as another user or group) only needs to read them.

*   Owner: Read + Write (`4 + 2 = 6`)
*   Group: Read (`4`)
*   Others: Read (`4`)

```bash
chmod 644 index.html
```

### Scenario 3: Public Web Directories (`755`)

Directories require execute (`x`) permissions for users to navigate inside them (`cd`) and read permissions to list directory contents.

*   Owner: Read + Write + Execute (`4 + 2 + 1 = 7`)
*   Group: Read + Execute (`4 + 1 = 5`)
*   Others: Read + Execute (`4 + 1 = 5`)

```bash
chmod 755 /var/www/html
```

### Scenario 4: Private Shell Scripts for You Alone (`700`)

If you write a backup script containing database credentials or API keys, nobody else on the server should read or run it.

*   Owner: Read + Write + Execute (`4 + 2 + 1 = 7`)
*   Group: None (`0`)
*   Others: None (`0`)

```bash
chmod 700 backup_database.sh
```

### Scenario 5: Shared Team Automation Script (`775`)

When you collaborate with other developers in the same Linux group, both you and your group members need to edit and test scripts, while the rest of the world should only read and run them.

*   Owner: Read + Write + Execute (`7`)
*   Group: Read + Write + Execute (`7`)
*   Others: Read + Execute (`5`)

```bash
chmod 775 deploy_staging.sh
```

---

## Hands-on Example

Open your Linux or macOS terminal and run through this exercise to see permissions in action.

### Step 1: Create a test directory and a file

```bash
mkdir chmod_practice
cd chmod_practice
touch run_me.sh
```

### Step 2: Add code to your script

```bash
echo '#!/bin/bash' > run_me.sh
echo 'echo "Hello from Code easier!"' >> run_me.sh
```

### Step 3: Check current permissions

```bash
ls -l run_me.sh
```

You will see output similar to this:

```text
-rw-r--r-- 1 asahluma asahluma 46 May 15 10:00 run_me.sh
```

Notice the missing `x` characters. The owner only has read and write (`rw-`), which equals octal `644`.

### Step 4: Try executing the script

```bash
./run_me.sh
```

Terminal output:

```text
bash: ./run_me.sh: Permission denied
```

### Step 5: Fix it using octal permissions

Grant yourself read, write, and execute permissions (`7`), while letting others only read and execute (`5`):

```bash
chmod 755 run_me.sh
```

### Step 6: Verify and execute

```bash
ls -l run_me.sh
```

Output:

```text
-rwxr-xr-x 1 asahluma asahluma 46 May 15 10:00 run_me.sh
```

Now run the script:

```bash
./run_me.sh
```

Output:

```text
Hello from Code easier!
```

---

## Common Mistakes / Troubleshooting

*   **Setting files to `chmod 777` when stuck**: 
    `777` gives read, write, and execute access to literally every user on the system. It is a critical security vulnerability, and web servers like Nginx/Apache or tools like SSH will actively refuse to use files with `777` permissions. Use `644` for files or `755` for directories instead.
*   **Stripping the execute bit from a directory**:
    If you set a directory to `644`, you can no longer `cd` into it, even if you own it. Directories must have execute permissions (`+x` or `7`/`5`) for you to navigate into them or access files within them.
*   **Running recursive `chmod -R` without targeting file types**:
    Running `chmod -R 755 .` turns every plain text file and image into an executable. Running `chmod -R 644 .` breaks every folder by removing the execute bit. Instead, use `find`:
    ```bash
    # Set directories to 755
    find . -type d -exec chmod 755 {} +

    # Set regular files to 644
    find . -type f -exec chmod 644 {} +
    ```
*   **Confusing `chmod` with `chown`**:
    `chmod` alters *what actions* are allowed (read/write/execute). `chown` changes *who owns* the file or group (e.g., `chown www-data:www-data index.php`). If you do not own the file, you cannot use `chmod` on it unless you use `sudo`.

---

## Try It Yourself

Put your knowledge to work:

1. Create a file called `secret.txt`:
   ```bash
   echo "Top Secret Database Password" > secret.txt
   ```
2. Using the octal chart, calculate the code that gives:
   * **User**: Read and write access
   * **Group**: Read-only access
   * **Others**: Zero access
3. Apply that permission using `chmod`.
4. Run `ls -l secret.txt` to confirm your result matches `-rw-r-----`.

*(Hint: `4 + 2 = 6`, `4 = 4`, `0 = 0`)*

---

## What's Next

Now that you can calculate and set octal permissions with confidence, you are ready to tackle deeper system permissions:

*   Learn **`chown` and `chgrp`** to manage user and group file ownership across multi-user servers.
*   Explore **`umask`**, which decides the default permissions automatically assigned whenever you create new files or folders.
*   Dive into special bits (**SUID, SGID, and the Sticky Bit**) used for shared directories and administrative binaries.

Keep this guide bookmarked so you never have to guess the math behind file permissions again.
