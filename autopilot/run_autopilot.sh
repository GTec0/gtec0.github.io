#!/usr/bin/env bash
# Cron wrapper for the GTec autopilot (runs on YOUR pc, post-ONLY edition).
# Install:  crontab -e  →  0 6,18 * * * /path/to/gtec0.github.io/autopilot/run_autopilot.sh
#
# What it does: pull latest blog → generate tutorial post + images → commit + push.
# Sharing is MANUAL: read autopilot/SHARE.txt (or autopilot.log) and paste the
# captions to FB/IG/Threads yourself.
set -u
AUTO_DIR="$(cd "$(dirname "$0")" && pwd)"
BLOG_REPO="$(dirname "$AUTO_DIR")"
LOG="$AUTO_DIR/autopilot.log"
LOCK="$AUTO_DIR/.autopilot.lock"

exec 9>"$LOCK"
if ! flock -n 9; then
  echo "$(date -u +%FT%TZ) SKIP: previous run still active" >> "$LOG"
  exit 0
fi

{
  echo "===== $(date -u +%FT%TZ) autopilot start ====="
  cd "$BLOG_REPO" || exit 1
  git pull --rebase --autostash 2>&1 | tail -2
  cd "$AUTO_DIR" || exit 1
  python3 main.py 2>&1 | tail -40
  cd "$BLOG_REPO" || exit 1
  git add _posts/ assets/images/banners/ autopilot/SHARE.txt autopilot-state.json 2>/dev/null || true
  if git diff --cached --quiet; then
    echo "nothing new to commit"
  else
    git -c user.name "gtec-autopilot" -c user.email "autopilot@gtec0.github.io" \
      commit -m "autopilot: new tutorial $(date +%F)" 2>&1 | tail -2
    git push 2>&1 | tail -3
  fi
  echo "===== $(date -u +%FT%TZ) autopilot end ====="
} >> "$LOG" 2>&1
