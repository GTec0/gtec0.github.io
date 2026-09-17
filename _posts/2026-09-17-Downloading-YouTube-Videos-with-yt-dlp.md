---
layout: post
title: "How to download YouTube Videos with yt-dlp"
thumbnail-img: /assets/img/ytdlp_yt_download_KW6dh7x.jpeg
share-img: /assets/img/ytdlp_yt_download_KW6dh7x.jpeg
tags: ['Youtube', 'ytdlp', 'Linux', 'automation']
author: Asahluma Tyika
---

### ⚠️Educational Disclaimer

This tutorial is for learning purposes only. Please use these tools to download content you legally own or have permission to use. We do **not support piracy, illegal hacking, or violation of copyright laws.

Picture this: You're a content creator studying video editing techniques from your favorite YouTubers. You've found the perfect tutorial series, but you're heading to a remote location with spotty internet for the next month. Or maybe you're a researcher archiving educational content for offline reference. Perhaps you're simply tired of buffering issues during your commute.

Enter yt-dlp—the Swiss Army knife of video downloading. Born as a more actively maintained fork of the legendary youtube-dl, yt-dlp has become the go-to tool for anyone who needs reliable, feature-rich video downloading capabilities. It's not just about YouTube anymore; yt-dlp supports over 1,000 websites, making it the ultimate digital archiving companion.

This isn't about piracy—it's about taking control of your digital media consumption, creating offline archives for legitimate use, and ensuring you have access to content when you need it most.

## Why yt-dlp?

### The Power User's Choice

Unlike browser extensions or sketchy online converters, yt-dlp offers:
- **Complete control** over video quality, format, and metadata
- **Batch downloading** for entire playlists and channels
- **Active development** with frequent updates and bug fixes
- **Privacy-focused** with no tracking or data collection
- **Cross-platform** support (Windows, macOS, Linux, Android via Termux)
- **Powerful filtering** and automation capabilities
- **Support for premium content** (with your own credentials)

## Installation

### Linux/macOS

The easiest method using pip:

```bash
pip install yt-dlp
```

Or using your package manager:

```bash
# Ubuntu/Debian
sudo apt install yt-dlp

# Arch Linux
sudo pacman -S yt-dlp

# macOS (Homebrew)
brew install yt-dlp
```

### Windows

Download the executable from the official GitHub releases:

```powershell
# Using winget
winget install yt-dlp

# Or download directly
# Visit: https://github.com/yt-dlp/yt-dlp/releases
```

### Android (Termux)

```bash
pkg install python
pip install yt-dlp
```

### Verify Installation

```bash
yt-dlp --version
```

## Getting Started: Basic Usage

### Your First Download

The simplest command—just paste the URL:

```bash
yt-dlp https://www.youtube.com/watch?v=VIDEO_ID
```

This downloads the best quality video available by default.

### Choosing Video Quality

**Download best quality:**
```bash
yt-dlp -f bestvideo+bestaudio https://youtube.com/watch?v=VIDEO_ID
```

**Download specific resolution:**
```bash
# 1080p
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" URL

# 720p
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" URL

# 4K
yt-dlp -f "bestvideo[height<=2160]+bestaudio/best[height<=2160]" URL
```

**List available formats:**
```bash
yt-dlp -F URL
```

This shows all available formats with their IDs, resolutions, and codecs.

### Audio-Only Downloads

**Extract best audio:**
```bash
yt-dlp -x --audio-format mp3 URL
```

**Specific audio quality:**
```bash
yt-dlp -x --audio-format mp3 --audio-quality 0 URL
```
(0 is best, 9 is worst)

## Advanced Techniques

### Downloading Entire Playlists

**Download complete playlist:**
```bash
yt-dlp https://www.youtube.com/playlist?list=PLAYLIST_ID
```

**Download playlist in reverse order:**
```bash
yt-dlp --playlist-reverse URL
```

**Download specific items from playlist:**
```bash
# Items 1 to 10
yt-dlp --playlist-items 1-10 URL

# Items 5, 10, 15
yt-dlp --playlist-items 5,10,15 URL

# From item 20 onwards
yt-dlp --playlist-items 20- URL
```

### Downloading Entire Channels

**Download all videos from a channel:**
```bash
yt-dlp https://www.youtube.com/@ChannelName/videos
```

**Download only recent uploads:**
```bash
yt-dlp --dateafter 20240101 https://www.youtube.com/@ChannelName/videos
```

### Smart Filtering

**Download videos by date range:**
```bash
yt-dlp --dateafter 20240101 --datebefore 20241231 URL
```

**Filter by duration:**
```bash
# Only videos shorter than 10 minutes
yt-dlp --match-filter "duration < 600" URL

# Only videos longer than 30 minutes
yt-dlp --match-filter "duration > 1800" URL
```

**Filter by views:**
```bash
# Only videos with more than 1M views
yt-dlp --match-filter "view_count > 1000000" URL
```

### Output Organization

**Custom filename template:**
```bash
yt-dlp -o "%(title)s-%(id)s.%(ext)s" URL
```

**Organize by uploader:**
```bash
yt-dlp -o "%(uploader)s/%(title)s.%(ext)s" URL
```

**Organize by date:**
```bash
yt-dlp -o "%(upload_date)s-%(title)s.%(ext)s" URL
```

**Complex organization:**
```bash
yt-dlp -o "%(uploader)s/%(playlist)s/%(playlist_index)s-%(title)s.%(ext)s" URL
```

### Subtitle Management

**Download with subtitles:**
```bash
yt-dlp --write-sub --sub-lang en URL
```

**Auto-generated subtitles:**
```bash
yt-dlp --write-auto-sub --sub-lang en URL
```

**Download all available subtitles:**
```bash
yt-dlp --write-sub --all-subs URL
```

**Embed subtitles in video:**
```bash
yt-dlp --embed-subs --sub-lang en URL
```

## Real-World Scenarios

### Scenario 1: The Student's Archive

You're taking an online course and want offline access:

```bash
yt-dlp \
  -f "bestvideo[height<=720]+bestaudio" \
  --write-sub --sub-lang en \
  --embed-subs \
  -o "Course Materials/%(playlist_index)s - %(title)s.%(ext)s" \
  https://www.youtube.com/playlist?list=COURSE_PLAYLIST_ID
```

This downloads 720p videos with embedded subtitles, organized by lesson number.

### Scenario 2: The Music Collector

Building an offline music library:

```bash
yt-dlp \
  -x --audio-format mp3 \
  --audio-quality 0 \
  --embed-thumbnail \
  --add-metadata \
  -o "Music/%(artist)s/%(album)s/%(track_number)s - %(title)s.%(ext)s" \
  URL
```

Extracts high-quality audio with thumbnails and metadata.

### Scenario 3: The Content Creator

Downloading reference material for video editing:

```bash
yt-dlp \
  -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]" \
  --merge-output-format mp4 \
  --write-thumbnail \
  -o "References/%(uploader)s - %(title)s.%(ext)s" \
  URL
```

Ensures MP4 format for compatibility with editing software.

### Scenario 4: The Archivist

Preserving educational content:

```bash
yt-dlp \
  --download-archive downloaded.txt \
  --write-description \
  --write-info-json \
  --write-thumbnail \
  --all-subs \
  -o "Archive/%(upload_date)s/%(title)s [%(id)s].%(ext)s" \
  https://www.youtube.com/@EducationalChannel/videos
```

Creates a comprehensive archive with all metadata and prevents re-downloading.

## Power User Features

### Using Configuration Files

Create a config file at `~/.config/yt-dlp/config` (Linux/macOS) or `%APPDATA%/yt-dlp/config.txt` (Windows):

```
# Default video quality
-f bestvideo[height<=1080]+bestaudio/best

# Output template
-o ~/Videos/%(uploader)s/%(title)s.%(ext)s

# Always write subtitles
--write-sub
--sub-lang en

# Archive to avoid re-downloads
--download-archive ~/Videos/archive.txt

# Rate limiting to be respectful
--limit-rate 5M
```

Now just run:
```bash
yt-dlp URL
```

### Batch Downloads from File

Create a text file with URLs (one per line):

```
https://youtube.com/watch?v=VIDEO1
https://youtube.com/watch?v=VIDEO2
https://youtube.com/watch?v=VIDEO3
```

Download all:
```bash
yt-dlp -a urls.txt
```

### Using Cookies for Premium Content

Export cookies from your browser (using a browser extension) and use them:

```bash
yt-dlp --cookies cookies.txt URL
```

This allows downloading member-only or age-restricted content you have access to.

### Sponsorblock Integration

Skip sponsored segments automatically:

```bash
yt-dlp --sponsorblock-remove all URL
```

### Live Stream Recording

**Record ongoing live stream:**
```bash
yt-dlp --live-from-start LIVE_STREAM_URL
```

**Wait for scheduled live stream:**
```bash
yt-dlp --wait-for-video 300 SCHEDULED_STREAM_URL
```

## Automation Scripts

### Daily Channel Monitor (Python)

```python
#!/usr/bin/env python3
import subprocess
from datetime import datetime, timedelta

def download_recent_videos(channel_url, days=7):
    """Download videos from the last N days"""
    date_after = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    
    command = [
        'yt-dlp',
        '--dateafter', date_after,
        '--download-archive', 'downloaded.txt',
        '-o', '%(uploader)s/%(upload_date)s - %(title)s.%(ext)s',
        channel_url
    ]
    
    subprocess.run(command)

# Usage
channels = [
    'https://www.youtube.com/@Channel1/videos',
    'https://www.youtube.com/@Channel2/videos',
]

for channel in channels:
    download_recent_videos(channel, days=7)
```

### Cron Job for Automatic Downloads

Add to crontab (`crontab -e`):

```bash
# Download new videos from favorite channels daily at 2 AM
0 2 * * * /usr/local/bin/yt-dlp --download-archive ~/archive.txt -o "~/Videos/%(uploader)s/%(title)s.%(ext)s" -a ~/channels.txt
```

### Bash Script for Selective Downloads

```bash
#!/bin/bash

# Interactive download script
echo "Enter video URL:"
read URL

echo "Select quality:"
echo "1) Best quality"
echo "2) 1080p"
echo "3) 720p"
echo "4) Audio only (MP3)"
read CHOICE

case $CHOICE in
    1)
        yt-dlp -f bestvideo+bestaudio "$URL"
        ;;
    2)
        yt-dlp -f "bestvideo[height<=1080]+bestaudio" "$URL"
        ;;
    3)
        yt-dlp -f "bestvideo[height<=720]+bestaudio" "$URL"
        ;;
    4)
        yt-dlp -x --audio-format mp3 "$URL"
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
```

## Tips and Best Practices

### 1. Be Respectful with Rate Limiting

```bash
yt-dlp --limit-rate 5M URL
```

This prevents overwhelming servers.

### 2. Use Archive Files

```bash
yt-dlp --download-archive archive.txt URL
```

Prevents re-downloading videos you already have.

### 3. Keep yt-dlp Updated

YouTube frequently changes their site, breaking downloaders:

```bash
pip install --upgrade yt-dlp
```

Or use the built-in updater:

```bash
yt-dlp -U
```

### 4. Verify Downloads

```bash
yt-dlp --no-overwrites --continue URL
```

Resumes interrupted downloads and skips completed ones.

### 5. Handle Geo-Restrictions

```bash
yt-dlp --geo-bypass URL
```

Or use a proxy:

```bash
yt-dlp --proxy socks5://127.0.0.1:9050 URL
```

### 6. Extract Metadata

```bash
yt-dlp --write-info-json --write-description --write-thumbnail URL
```

Saves complete metadata for archival purposes.

## Troubleshooting

### Common Issues

**"Unable to extract video data"**
- Solution: Update yt-dlp with `yt-dlp -U`

**"HTTP Error 429: Too Many Requests"**
- Solution: Add rate limiting: `--limit-rate 5M`

**"Requested format not available"**
- Solution: List formats with `-F` and choose an available one

**"Video unavailable"**
- Solution: Check if video is private, deleted, or geo-restricted

**Slow downloads**
- Solution: Use `--concurrent-fragments 4` for faster downloads

### Debug Mode

For troubleshooting:

```bash
yt-dlp --verbose URL
```

## Legal and Ethical Considerations

### Important Reminders

- **Respect copyright**: Download only content you have rights to or permission for
- **Follow Terms of Service**: Check platform terms before downloading
- **Personal use**: Keep downloads for personal, educational, or research purposes
- **Attribution**: Give credit to creators when using their content
- **Support creators**: Subscribe, like, and consider purchasing official content

### Legitimate Use Cases

- Creating offline educational archives
- Research and academic analysis
- Accessibility (downloading with subtitles for hearing-impaired users)
- Archiving your own content
- Backing up purchased or licensed content
- Preserving content that may be removed

## Beyond YouTube

yt-dlp supports 1000+ sites including:

```bash
# Vimeo
yt-dlp https://vimeo.com/VIDEO_ID

# Twitter/X
yt-dlp https://twitter.com/user/status/TWEET_ID

# TikTok
yt-dlp https://www.tiktok.com/@user/video/VIDEO_ID

# Instagram
yt-dlp https://www.instagram.com/p/POST_ID/

# Reddit
yt-dlp https://www.reddit.com/r/subreddit/comments/POST_ID/

# SoundCloud
yt-dlp https://soundcloud.com/user/track
```

## Conclusion: Your Digital Freedom

yt-dlp represents more than just a download tool—it's about digital autonomy. In an age where content can disappear overnight, streaming services change their libraries, and internet access isn't always guaranteed, having control over your media consumption is valuable.

Whether you're a student building an offline study library, a creator gathering reference material, a researcher archiving content, or simply someone who values reliable offline access to media, yt-dlp is an essential tool in your digital toolkit.

The key is using it responsibly, respecting creators' rights, and understanding that with great power comes great responsibility. Download wisely, respect copyright, support creators, and enjoy the freedom of offline media access.

Happy downloading! 🎥
