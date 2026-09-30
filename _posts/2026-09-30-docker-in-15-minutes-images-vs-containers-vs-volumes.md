---
layout: post
title: "Docker in 15 minutes: images vs containers vs volumes"
subtitle: "Master Docker fundamentals in 15 minutes: clear mental models, practical diagrams, and hands-on commands for images, containers, and volumes."
date: 2026-09-30
categories: []
tags: ["Docker", "DevOps", "Beginner"]
thumbnail-img: /assets/images/banners/docker-in-15-minutes-images-vs-containers-vs-volumes-banner.png
share-img: /assets/images/banners/docker-in-15-minutes-images-vs-containers-vs-volumes-banner.png
author: Asahluma Tyika
---
## Stop guessing how Docker actually works

If you have ever heard someone say "well, it works on my machine," you already understand why Docker exists. Docker packages an application and everything it needs—code, runtime, system tools, libraries—into a standard unit that runs identically everywhere.

Whether you are pushing code from your MacBook to an AWS Linux server or testing a teammate's pull request on Windows, Docker eliminates environment drift.

To use Docker effectively, you only need to understand three core concepts:

1. **Images**
2. **Containers**
3. **Volumes**

Most tutorials blur these terms together. Let's break them down individually, map them out, and run real commands to see how they interact.

---

## Part 1: Docker images (the blueprint)

A **Docker image** is a read-only, frozen snapshot containing the operating system libraries, application code, dependencies, and default configurations your app needs to run.

Think of an image like an executable installer file (like an `.iso` or `.dmg`) or an architectural blueprint. An image does not execute; it just sits there ready to be used.

### How images work under the hood

Images are built in **layers**. When you write a `Dockerfile`, every instruction (`FROM`, `COPY`, `RUN`) creates a new layer:

* `FROM python:3.11-slim` (Layer 1: Base Linux OS + Python)
* `COPY requirements.txt .` (Layer 2: Dependencies file)
* `RUN pip install -r requirements.txt` (Layer 3: Installed packages)
* `COPY . .` (Layer 4: Application source code)

Because these layers are cached and read-only, Docker can reuse them across multiple projects, saving storage and download time.

---

## Part 2: Docker containers (the running instance)

A **container** is an image that is currently running. If an image is the blueprint for a house, the container is the actual house built from that blueprint.

When you tell Docker to run an image, it performs two steps:

1. Takes the read-only image layers.
2. Adds a very thin **read-write layer** on top (often called the container layer).

```
+-----------------------------------+
|   Writable Container Layer (Temp) |  <- Your edits, logs, temp files
+-----------------------------------+
|   Image Layer 3 (App Code)        |  <- Read-only
+-----------------------------------+
|   Image Layer 2 (Packages)        |  <- Read-only
+-----------------------------------+
|   Image Layer 1 (Base OS)         |  <- Read-only
+-----------------------------------+
```

Any files you create, modify, or delete while inside the container happen in this thin writable layer. 

Here is the critical catch: **when a container is deleted, its writable layer is deleted with it.** Any data written inside that container disappears forever. 

This brings us to the third piece of the puzzle.

---

## Part 3: Docker volumes (the permanent vault)

Because containers are ephemeral (temporary), you cannot store database records, user uploads, or logs directly inside a container's filesystem.

A **volume** is a dedicated storage area managed by Docker on your host machine's drive, completely separated from the container lifecycle.

Volumes bypass the container's temporary read-write layer and write directly to host storage:

* If the container crashes, the volume stays intact.
* If you delete the container, the volume stays intact.
* You can attach the same volume to a new container without losing a single byte.

### The comparison

| Feature | Docker Image | Docker Container | Docker Volume |
| :--- | :--- | :--- | :--- |
| **State** | Static (Read-only) | Dynamic (Running process) | Persistent (Storage) |
| **Lifecycle** | Stored until pruned | Ephemeral (start/stop/delete) | Permanent until explicitly removed |
| **Analogy** | Recipe | The cooked meal | The pantry where leftovers live |
| **Key command** | `docker build` / `pull` | `docker run` / `rm` | `docker volume create` |

---

## Hands-on example: prove persistence yourself

Let's verify these concepts using the terminal. You only need Docker installed and running on your machine. We will use `alpine`, a lightweight Linux distribution image (under 5 MB).

### Step 1: Pull an image

Download the official Alpine image from Docker Hub to your local computer:

```bash
docker pull alpine:latest
```

View the images stored locally on your machine:

```bash
docker images
```

You will see `alpine` listed with its image ID and size.

### Step 2: Run a container without a volume (ephemeral test)

Launch an interactive container named `temp-box` and open a shell:

```bash
docker run -it --name temp-box alpine sh
```

Your prompt changes to `#`, meaning you are inside the running container. Create a test file inside:

```sh
echo "Hello from container layer" > /note.txt
cat /note.txt
exit
```

You are back in your host terminal. The container has stopped, but still exists. Start it and check the file:

```bash
docker start -ai temp-box
cat /note.txt
exit
```

The file is still there because the container still exists. Now, remove the container completely:

```bash
docker rm temp-box
```

Run a fresh container from the same `alpine` image:

```bash
docker run --rm alpine cat /note.txt
```

Docker outputs an error:

```text
cat: can't open '/note.txt': No such file or directory
```

The file vanished because it was stored in the old container's temporary write layer.

### Step 3: Use a volume (permanent storage)

Create a managed Docker volume:

```bash
docker volume create my-data
```

Inspect your volumes to confirm it exists:

```bash
docker volume ls
```

Now, run a container and mount `my-data` to the `/app-data` path inside the container:

```bash
docker run -it --name writer-box -v my-data:/app-data alpine sh
```

Inside the container, create a persistent file:

```sh
echo "This data must survive!" > /app-data/vault.txt
cat /app-data/vault.txt
exit
```

Now remove the container completely:

```bash
docker rm writer-box
```

Spin up an entirely different container with a different name, mounting the exact same volume:

```bash
docker run --rm -v my-data:/target alpine cat /target/vault.txt
```

Your terminal outputs:

```text
This data must survive!
```

Even though `writer-box` was destroyed, your data remained safe inside the `my-data` volume and was mounted into a brand-new container at a completely different directory path (`/target`).

Clean up the volume when you are finished:

```bash
docker volume rm my-data
```

---

## Common mistakes and fixes

* **Forgetting `-it` on interactive containers:** Running `docker run alpine sh` immediately exits without doing anything. Add the interactive flags `-it` (`-i` keeps STDIN open, `-t` allocates a terminal) so you can type commands.
* **Assuming `docker stop` deletes data:** Stopping a container pauses it; its data remains on disk. Only `docker rm` destroys the container's writable layer.
* **Mixing up volume syntax (`-v host:container`):** In `-v my-data:/app-data`, the left side of the colon is the host source (or volume name), and the right side is the path inside the container. Flipping them creates unwanted directories or mounting errors.
* **Losing data because of missing mounts on databases:** If you launch PostgreSQL or MySQL in Docker without mounting a volume to their default storage directories (e.g., `/var/lib/postgresql/data`), destroying the container deletes your entire database. Always check the official Docker image docs for the exact persistence path.

---

## Try it yourself

Put your knowledge to work with this 2-minute challenge:

1. Create a volume named `site-data`.
2. Run an `alpine` container that mounts `site-data` to `/site`.
3. Inside the container, write a small HTML string into `/site/index.html`:
   ```sh
   echo "<h1>Docker works!</h1>" > /site/index.html
   ```
4. Exit and delete the container.
5. Launch an Nginx container mounting that same volume to Nginx's default public folder:
   ```bash
   docker run -d --name my-web -p 8080:80 -v site-data:/usr/share/nginx/html nginx:alpine
   ```
6. Open `http://localhost:8080` in your browser. You should see your custom HTML page rendered by an entirely different image. Clean up with `docker rm -f my-web` and `docker volume rm site-data`.

---

## What's next

Now that you have the baseline trinity nailed down, you are ready to assemble full-stack applications. Next steps to look out for:

* **Writing your own Dockerfiles:** Learn how to package your own Python, Node.js, or Go apps into custom images.
* **Docker Compose:** Learn how to run your app, database, and cache together using a single `docker-compose.yml` file.
* **Bind mounts vs. named volumes:** Discover when to use named volumes (for databases) versus bind mounts (for live hot-reloading source code during local development).

Look out for our upcoming guide: *"Docker Compose for Beginners: Running Your App and Database in 1 Command."*

Bookmark this page as your quick mental-model cheat sheet whenever you need a fast refresher on Docker storage and lifecycles.
