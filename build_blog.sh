#!/usr/bin/env bash
# Rebuild the blog from notebooks/*.ipynb into blog/.
# First run creates a local venv with nbconvert; later runs reuse it.
#
# Usage:  ./build_blog.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="${ROOT}/.venv-blog"

if [ ! -x "${VENV}/bin/python" ]; then
  echo "→ Creating blog build venv (one-time)…"
  python3 -m venv "${VENV}"
  "${VENV}/bin/pip" install --quiet --upgrade pip
  "${VENV}/bin/pip" install --quiet -r "${ROOT}/scripts/requirements.txt"
fi

echo "→ Building blog…"
"${VENV}/bin/python" "${ROOT}/scripts/build_blog.py"
echo "→ Done. Preview with ./serve.sh and open http://localhost:8000/blog/"
