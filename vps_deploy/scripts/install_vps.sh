#!/usr/bin/env bash
set -Eeuo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "Please run as root: sudo bash vps_deploy/scripts/install_vps.sh vps_deploy/.env" >&2
  exit 1
fi

ENV_FILE="${1:-}"
if [ -n "$ENV_FILE" ]; then
  if [ ! -f "$ENV_FILE" ]; then
    echo "Env file not found: $ENV_FILE" >&2
    exit 1
  fi
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
fi

REPO_URL="${REPO_URL:-https://github.com/meta-xucong/PM_refine_follow.git}"
BRANCH="${BRANCH:-main}"
APP_DIR="${APP_DIR:-/opt/pm-refine-follow/current}"
CONFIG_DIR="${CONFIG_DIR:-/etc/pm-refine-follow}"
DATA_DIR="${DATA_DIR:-/var/lib/pm-refine-follow}"
LOG_DIR="${LOG_DIR:-/var/log/pm-refine-follow}"
RUN_USER="${RUN_USER:-pmfollow}"
RUN_GROUP="${RUN_GROUP:-$RUN_USER}"
DASHBOARD_PORT="${DASHBOARD_PORT:-8787}"
AUTOSTART_SCAN="${AUTOSTART_SCAN:-1}"
SERVER_NAME="${DOMAIN:-_}"
BASIC_AUTH_USER="${BASIC_AUTH_USER:-admin}"
BASIC_AUTH_PASSWORD="${BASIC_AUTH_PASSWORD:-}"
DISABLE_NGINX_DEFAULT="${DISABLE_NGINX_DEFAULT:-1}"
ENABLE_LETSENCRYPT="${ENABLE_LETSENCRYPT:-0}"
LETSENCRYPT_EMAIL="${LETSENCRYPT_EMAIL:-}"
SCT_SENDKEY="${SCT_SENDKEY:-}"

export APP_DIR CONFIG_DIR DATA_DIR LOG_DIR RUN_USER RUN_GROUP DASHBOARD_PORT AUTOSTART_SCAN SERVER_NAME

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  apache2-utils \
  ca-certificates \
  curl \
  git \
  nginx \
  openssl \
  python3 \
  python3-pip \
  python3-venv

if [ -z "$BASIC_AUTH_PASSWORD" ]; then
  BASIC_AUTH_PASSWORD="$(openssl rand -base64 18 | tr -d '\n')"
  GENERATED_BASIC_AUTH_PASSWORD=1
else
  GENERATED_BASIC_AUTH_PASSWORD=0
fi

if ! getent group "$RUN_GROUP" >/dev/null; then
  groupadd --system "$RUN_GROUP"
fi
if ! id "$RUN_USER" >/dev/null 2>&1; then
  useradd --system --home-dir /opt/pm-refine-follow --create-home --shell /usr/sbin/nologin --gid "$RUN_GROUP" "$RUN_USER"
fi

mkdir -p "$(dirname "$APP_DIR")" "$CONFIG_DIR/secrets" "$DATA_DIR/auto_screen_data" "$DATA_DIR/dashboard" "$LOG_DIR"

if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" fetch origin "$BRANCH"
  git -C "$APP_DIR" checkout "$BRANCH"
  git -C "$APP_DIR" pull --ff-only origin "$BRANCH"
else
  rm -rf "$APP_DIR"
  git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
fi

python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/python" -m pip install --upgrade pip wheel
"$APP_DIR/.venv/bin/python" -m pip install -r "$APP_DIR/vps_deploy/requirements.vps.txt"
"$APP_DIR/.venv/bin/python" -m compileall "$APP_DIR/auto_screen" "$APP_DIR/agent_core" "$APP_DIR/dashboard" -q

render_template() {
  local src="$1"
  local dest="$2"
  python3 - "$src" "$dest" <<'PY'
import os
import sys
from pathlib import Path

src = Path(sys.argv[1])
dest = Path(sys.argv[2])
text = src.read_text(encoding="utf-8")
for key in (
    "APP_DIR",
    "CONFIG_DIR",
    "DATA_DIR",
    "LOG_DIR",
    "RUN_USER",
    "RUN_GROUP",
    "DASHBOARD_PORT",
    "AUTOSTART_SCAN",
    "SERVER_NAME",
):
    text = text.replace(f"__{key}__", os.environ[key])
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(text, encoding="utf-8")
PY
}

render_template "$APP_DIR/vps_deploy/templates/auto_screen_config.vps.json" "$CONFIG_DIR/auto_screen_config.json"
render_template "$APP_DIR/vps_deploy/templates/agent_core_config.vps.json" "$CONFIG_DIR/agent_core_config.json"
render_template "$APP_DIR/vps_deploy/templates/pm-refine-follow-dashboard.service" "/etc/systemd/system/pm-refine-follow-dashboard.service"
render_template "$APP_DIR/vps_deploy/templates/nginx.pm-refine-follow.conf" "/etc/nginx/sites-available/pm-refine-follow.conf"

if [ -n "$SCT_SENDKEY" ]; then
  printf '%s\n' "$SCT_SENDKEY" > "$CONFIG_DIR/secrets/serverchan_sendkey.txt"
elif [ ! -f "$CONFIG_DIR/secrets/serverchan_sendkey.txt" ]; then
  : > "$CONFIG_DIR/secrets/serverchan_sendkey.txt"
fi

htpasswd -bB -c /etc/nginx/.pm-refine-follow.htpasswd "$BASIC_AUTH_USER" "$BASIC_AUTH_PASSWORD" >/dev/null

ln -sfn /etc/nginx/sites-available/pm-refine-follow.conf /etc/nginx/sites-enabled/pm-refine-follow.conf
if [ "$DISABLE_NGINX_DEFAULT" = "1" ]; then
  rm -f /etc/nginx/sites-enabled/default
fi

chown -R "$RUN_USER:$RUN_GROUP" /opt/pm-refine-follow "$CONFIG_DIR" "$DATA_DIR" "$LOG_DIR"
chmod 750 "$CONFIG_DIR" "$CONFIG_DIR/secrets"
chmod 600 "$CONFIG_DIR/secrets/serverchan_sendkey.txt"
touch "$LOG_DIR/auto_screen.log"
chown "$RUN_USER:$RUN_GROUP" "$LOG_DIR/auto_screen.log"

nginx -t
systemctl enable --now nginx
systemctl reload nginx
systemctl daemon-reload
systemctl enable --now pm-refine-follow-dashboard

if [ "$ENABLE_LETSENCRYPT" = "1" ]; then
  if [ "$SERVER_NAME" = "_" ] || [ -z "$LETSENCRYPT_EMAIL" ]; then
    echo "Skip Let's Encrypt: DOMAIN must be a real DNS name and LETSENCRYPT_EMAIL must be set." >&2
  else
    DEBIAN_FRONTEND=noninteractive apt-get install -y certbot python3-certbot-nginx
    certbot --nginx -d "$SERVER_NAME" --non-interactive --agree-tos -m "$LETSENCRYPT_EMAIL" --redirect
  fi
fi

echo
echo "PM Refine Follow VPS deploy completed."
echo "Dashboard: http://${SERVER_NAME}/"
echo "Basic Auth user: ${BASIC_AUTH_USER}"
if [ "$GENERATED_BASIC_AUTH_PASSWORD" = "1" ]; then
  echo "Generated Basic Auth password: ${BASIC_AUTH_PASSWORD}"
else
  echo "Basic Auth password: configured in env file"
fi
echo "Config dir: ${CONFIG_DIR}"
echo "Data dir: ${DATA_DIR}"
echo "Log dir: ${LOG_DIR}"
echo "SendKey file: ${CONFIG_DIR}/secrets/serverchan_sendkey.txt"
echo
echo "Useful commands:"
echo "  systemctl status pm-refine-follow-dashboard"
echo "  journalctl -u pm-refine-follow-dashboard -f"
echo "  tail -f ${LOG_DIR}/auto_screen.log"
echo "  bash ${APP_DIR}/vps_deploy/scripts/status.sh"
