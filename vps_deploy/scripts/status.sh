#!/usr/bin/env bash
set -euo pipefail

PORT="${DASHBOARD_PORT:-8787}"
BASE_URL="http://127.0.0.1:${PORT}"

echo "== systemd =="
systemctl --no-pager --lines=8 status pm-refine-follow-dashboard || true
echo
systemctl --no-pager --lines=8 status pm-refine-follow-auto-screen || true

echo
echo "== memory =="
free -h || true

echo
echo "== /api/process =="
curl -fsS "${BASE_URL}/api/process" | python3 -m json.tool || true

echo
echo "== /api/serverchan-key =="
curl -fsS "${BASE_URL}/api/serverchan-key" | python3 -m json.tool || true

echo
echo "== /api/watchlist-refresh/status =="
curl -fsS "${BASE_URL}/api/watchlist-refresh/status" | python3 -m json.tool || true

echo
echo "== watchlist timer =="
systemctl --no-pager --lines=8 status pm-refine-follow-watchlist-refresh.timer || true

echo
echo "== recent auto_screen log =="
tail -n 30 /var/log/pm-refine-follow/auto_screen.log 2>/dev/null || true
