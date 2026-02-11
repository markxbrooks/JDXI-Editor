#!/usr/bin/env bash
set -Eeuo pipefail

# -------------------------------
# Resolve project root reliably
# -------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/building/linux"
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"

# -------------------------------
# Validation
# -------------------------------
if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "ERROR: Virtual environment not found:"
    echo "  $VENV_PYTHON"
    echo "Run: python -m venv venv && pip install -r requirements.txt"
    exit 1
fi

if [[ ! -f "$BUILD_DIR/build_linux.py" ]]; then
    echo "ERROR: build_linux.py missing in $BUILD_DIR"
    exit 1
fi

# -------------------------------
# Execute build
# -------------------------------
cd "$BUILD_DIR"

echo "== JDXI Editor Linux Build =="
echo "Python: $VENV_PYTHON"
echo "Working directory: $PWD"
echo

exec "$VENV_PYTHON" build_linux.py "$@"
