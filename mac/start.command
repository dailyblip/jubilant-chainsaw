#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo
  echo "Python 3 is not installed."
  echo "Install it from https://www.python.org/downloads/macos/ then run this command again."
  echo
  exit 1
fi

if [ ! -d "backend/.venv" ]; then
  echo "Preparing PorchLight controller..."
  python3 -m venv backend/.venv
  backend/.venv/bin/python -m pip install --upgrade pip
  backend/.venv/bin/pip install -r backend/requirements.txt
fi

if [ ! -f "backend/.env" ]; then
  cp backend/.env.example backend/.env
  backend/.venv/bin/python mac/setup_lights.py
fi

echo
echo "Starting PorchLight..."
cd backend
../backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8787 &
PID=$!

sleep 2

LAN_IP="$(ipconfig getifaddr en0 2>/dev/null || true)"
if [ -z "$LAN_IP" ]; then
  LAN_IP="$(ipconfig getifaddr en1 2>/dev/null || true)"
fi

open "http://127.0.0.1:8787"

echo
echo "PorchLight is running."
echo "Mac:    http://127.0.0.1:8787"
if [ -n "$LAN_IP" ]; then
  echo "iPhone: http://$LAN_IP:8787"
fi
echo
echo "Keep this Terminal window open while using PorchLight."
echo "Press Control-C to stop it."

trap 'kill $PID 2>/dev/null || true' INT TERM EXIT
wait $PID
