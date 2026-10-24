#!/bin/sh
# Render scripts/showcase/showcase.html to images/showcase.png at 2x with headless Chrome.
set -e
cd "$(dirname "$0")/.."
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size=1280,940 \
  --virtual-time-budget=8000 \
  --screenshot="$PWD/images/showcase.png" \
  "file://$PWD/scripts/showcase/showcase.html"
