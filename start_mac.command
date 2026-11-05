#!/bin/sh
cd "$(dirname "$0")" || exit 1
if command -v python3 >/dev/null 2>&1; then
  python3 server.py
else
  echo 'Python 3 is required. Install Python 3.9 or newer and run python3 server.py.'
  read -r a
fi
