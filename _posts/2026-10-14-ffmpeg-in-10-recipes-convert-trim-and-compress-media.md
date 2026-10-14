---
layout: post
title: "ffmpeg in 10 recipes: convert, trim and compress media"
subtitle: "Learn 10 practical ffmpeg one‑liners to convert, trim, and shrink videos on Linux without digging into codec theory."
date: 2026-10-14
categories: []
tags: ["Linux", "Developer Tips"]
thumbnail-img: /assets/images/banners/ffmpeg-in-10-recipes-convert-trim-and-compress-media-banner.png
share-img: /assets/images/banners/ffmpeg-in-10-recipes-convert-trim-and-compress-media-banner.png
author: Asahluma Tyika
---
# ffmpeg in 10 recipes: convert, trim and compress media  
**Tags:** Linux, Developer Tips  

## Intro – why ffmpeg and who should use these recipes  

`ffmpeg` is the Swiss‑army knife for audio‑video work on Linux. It can read almost any media format, apply filters, and write out a new file—all from a single command line. If you ever needed to:

* change a `.mov` to a web‑friendly `.mp4`  
* cut the first 30 seconds off a clip  
* shrink a 4 GB lecture video to under 500 MB  

…you’re in the right place. These 10 recipes assume you have `ffmpeg` installed (e.g., `sudo apt install ffmpeg`) and a basic command‑line comfort level. No deep codec theory, just copy‑paste commands that work out of the box.

---

## Part 1 – Simple format conversion  

| # | Goal | Command (copy‑paste) | Notes |
|---|------|----------------------|-------|
| 1 | Convert any video to MP4 (H.264 video, AAC audio) | ```bash\nffmpeg -i input.mov -c:v libx264 -c:a aac -movflags +faststart output.mp4\n``` | `-movflags +faststart` moves the index to the front for progressive streaming. |
| 2 | Convert a video to WebM (VP9 + Opus) | ```bash\nffmpeg -i input.mp4 -c:v libvpx-vp9 -b:v 2M -c:a libopus output.webm\n``` | Adjust `-b:v` (bitrate) to control quality vs. size. |
| 3 | Extract audio as MP3 | ```bash\nffmpeg -i input.mp4 -q:a 2 -map a output.mp3\n``` | `-q:a 2` gives near‑transparent VBR MP3; lower numbers = higher quality. |
| 4 | Extract audio as OGG Vorbis | ```bash\nffmpeg -i input.mp4 -c:a libvorbis -q:a 4 output.ogg\n``` | `-q:a 4` is a good balance for spoken content. |

**Why these flags?**  
* `-c:v` / `-c:a` pick the encoder.  
* `-b:v` sets a target video bitrate (optional).  
* `-q:a` is a quality‑based VBR setting for audio.  

---

## Part 2 – Trimming and stitching  

| # | Goal | Command (copy‑paste) | Explanation |
|---|------|----------------------|-------------|
| 5 | Cut the first 30 seconds (no re‑encoding) | ```bash\nffmpeg -ss 00:00:30 -i input.mp4 -c copy -avoid_negative_ts 1 cut-start.mp4\n``` | `-ss` before `-i` seeks quickly; `-c copy` avoids quality loss. |
| 6 | Cut a 10‑second segment from 01:02 to 01:12 (re‑encode) | ```bash\nffmpeg -i input.mp4 -ss 00:01:02 -t 00:00:10 -c:v libx264 -c:a aac segment.mp4\n``` | Placing `-ss` after `-i` gives frame‑accurate cuts at the cost of re‑encoding. |
| 7 | Concatenate two MP4 files (same codec) | ```bash\n# 1️⃣ create a list file\nprintf "file 'part1.mp4'\nfile 'part2.mp4'\n" > list.txt\n# 2️⃣ run concat demuxer\nffmpeg -f concat -safe 0 -i list.txt -c copy joined.mp4\n``` | All inputs must share codec, resolution, and frame rate. |
| 8 | Add a 5‑second fade‑in to the start | ```bash\nffmpeg -i input.mp4 -vf \"fade=t=in:st=0:d=5\" -c:a copy faded.mp4\n``` | `-vf` applies a video filter; audio is passed through unchanged. |

---

## Part 3 – Compression without sacrificing too much quality  

| # | Goal | Command (copy‑paste) | Tips |
|---|------|----------------------|------|
| 9 | Reduce file size to ~50 % using CRF (constant‑rate‑factor) | ```bash\nffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k compressed.mp4\n``` | CRF 18–28 is typical; lower = higher quality. `-preset` trades speed for compression. |
|10| Target a specific output size (e.g., 700 MB) | ```bash\n# 1️⃣ get source duration in seconds\nDUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4)\n# 2️⃣ compute video bitrate (bits per second)\nTARGET=700M   # desired size\nBITRATE=$(( (TARGET*8*1024*1024) / DUR - 128000 ))   # subtract 128 kbps audio\nffmpeg -i input.mp4 -c:v libx264 -b:v ${BITRATE} -c:a aac -b:a 128k sized.mp4\n``` | Replace `700M` with your own target. This method uses average bitrate, not CRF. |

**Quick reference table for CRF values**

| CRF | Approx. quality (subjective) | Typical file size (vs. source) |
|-----|-----------------------------|--------------------------------|
| 18  | Visually lossless          | ~90 % of source |
| 20  | High quality, minor loss   | ~80 % |
| 23  | Default, good for web      | ~60 % |
| 26  | Noticeable compression     | ~40 % |
| 28  | Low‑bitrate streaming       | ~30 % |

---

## Hands‑on example – turn a 4 GB lecture into a 500 MB web‑ready MP4  

```bash
# 1️⃣ Install ffmpeg (Ubuntu/Debian)
sudo apt update && sudo apt install -y ffmpeg

# 2️⃣ Inspect the source (optional but helpful)
ffprobe -v error -show_format -show_streams lecture.mov

# 3️⃣ Convert & compress in one step
ffmpeg -i lecture.mov \
       -c:v libx264 -crf 24 -preset slow \
       -c:a aac -b:a 128k \
       -movflags +faststart \
       lecture_compressed.mp4
```

*What the flags do*  

* `-crf 24` – a sweet spot for lecture slides (text + static graphics).  
* `-preset slow` – takes longer but squeezes out extra compression.  
* `-movflags +faststart` – makes the video start playing before the whole file downloads.  

After the command finishes, check the size:

```bash
ls -lh lecture_compressed.mp4
```

You should see something around 500 MB, ready for upload to a learning platform.

---

## Common mistakes & how to fix them  

* **“ffmpeg: command not found”** – Install it (`sudo apt install ffmpeg` or use your distro’s package manager).  
* **Audio out of sync after cutting** – Use `-avoid_negative_ts 1` with copy‑only cuts, or re‑encode the audio (`-c:a aac`).  
* **“Invalid argument” when using `-ss`** – Ensure the timestamp format is `hh:mm:ss` or seconds (`30` works too).  
* **Output file larger than expected** – Lower the CRF value or add `-b:v` to force a tighter bitrate.  
* **Concat fails with “different codecs”** – Re‑encode all parts to the same codec first, or use the concat filter:

  ```bash
  ffmpeg -i "concat:part1.mp4|part2.mp4" -c copy joined.mp4
  ```

---

## Try it yourself  

*Take a 2‑minute MP4 clip (`sample.mp4`). Trim the first 15 seconds, add a 3‑second fade‑in, and compress it to a 10 MB file.*  

```bash
ffmpeg -i sample.mp4 -ss 00:00:15 -t 00:01:45 \
       -vf "fade=t=in:st=0:d=3" \
       -c:v libx264 -crf 26 -preset fast \
       -c:a aac -b:a 96k \
       -movflags +faststart sample_final.mp4
```

Verify the result with `ffprobe` and `ls -lh`.

---

## What’s next  

* **Batch processing** – Write a short Bash loop to apply the same recipe to every file in a folder.  
* **Advanced filters** – Explore `scale`, `crop`, and `drawtext` for thumbnail generation.  
* **Streaming presets** – Use `-profile:v high -level 4.2` for HLS/DASH compatibility.  
* **Hardware acceleration** – Replace `libx264` with `h264_nvenc` (NVIDIA) or `h264_vaapi` (Intel) for faster encoding.

---

*Bookmark this page for a quick ffmpeg cheat sheet whenever you need to tinker with media.*
