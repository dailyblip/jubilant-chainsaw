#!/bin/bash
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "Run with: sudo bash install.sh"
  exit 1
fi

APP_DIR=/opt/porchlight
SOURCE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

apt-get update
apt-get install -y python3 python3-venv python3-pip avahi-daemon rsync

mkdir -p "$APP_DIR"
rsync -a --delete "$SOURCE_DIR/backend/" "$APP_DIR/backend/"
python3 -m venv "$APP_DIR/backend/.venv"
"$APP_DIR/backend/.venv/bin/pip" install --upgrade pip
"$APP_DIR/backend/.venv/bin/pip" install -r "$APP_DIR/backend/requirements.txt"

if [[ ! -f "$APP_DIR/backend/.env" ]]; then
  cp "$APP_DIR/backend/.env.example" "$APP_DIR/backend/.env"
fi

# The standard Raspberry Pi OS user may not be named 'pi'. Patch service user.
ACTUAL_USER="${SUDO_USER:-pi}"
sed "s/^User=pi$/User=${ACTUAL_USER}/" "$SOURCE_DIR/pi/porchlight.service" > /etc/systemd/system/porchlight.service
chown -R "$ACTUAL_USER":"$ACTUAL_USER" "$APP_DIR"

systemctl daemon-reload
systemctl enable porchlight.service
systemctl restart porchlight.service

echo
echo "PorchLight installed."
echo "Edit: $APP_DIR/backend/.env"
echo "Then run: sudo systemctl restart porchlight"
echo "Status:   sudo systemctl status porchlight"
