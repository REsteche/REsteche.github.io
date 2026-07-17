#!/usr/bin/env bash
# Local preview for resteche.github.io — no install step needed.
# Usage:  ./serve.sh          # default port 8000
#         ./serve.sh 4000     # custom port

set -euo pipefail

PORT="${1:-8000}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
URL="http://localhost:${PORT}"

# Prefer python3 (ships with macOS); fall back to python.
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Error: Python is required to serve the site locally." >&2
  echo "Install it from https://www.python.org/downloads/ or via: brew install python" >&2
  exit 1
fi

# Bail early if the port is already taken.
if command -v lsof >/dev/null 2>&1 && lsof -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port ${PORT} is already in use. Try:  ./serve.sh $((PORT + 1))" >&2
  exit 1
fi

echo ""
echo "  ┌──────────────────────────────────────────┐"
echo "  │  Ruben Esteche — local preview           │"
echo "  │  ${URL}                     │"
echo "  │  Press Ctrl+C to stop                    │"
echo "  └──────────────────────────────────────────┘"
echo ""

# Open the browser a moment after the server starts (best-effort).
(
  sleep 0.6
  if command -v open >/dev/null 2>&1; then
    open "${URL}"          # macOS
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "${URL}"      # Linux
  fi
) &

cd "${ROOT}"
exec "${PY}" -m http.server "${PORT}"
