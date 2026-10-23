#!/usr/bin/env bash
# Render each diagram HTML file to a 2x PNG with a transparent background, next to the README's images.
# Run from the repo root: bash docs/diagrams/src/render.sh
set -euo pipefail
cd "$(dirname "$0")"
for f in *.html; do
  slug="${f%.html}"
  h=$(grep -o 'viewBox="0 0 960 [0-9]*"' "$f" | head -1 | grep -o '[0-9]*"$' | tr -d '"')
  google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=2 --default-background-color=00000000 \
    --virtual-time-budget=4000 --window-size=960,"$h" \
    --screenshot="../$slug.png" "file://$PWD/$f" 2>/dev/null
done
