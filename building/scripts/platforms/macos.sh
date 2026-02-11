#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../_common.sh"

log "macOS build"

cd "$PROJECT_ROOT/building/apple"

exec "$VENV_PYTHON" build_macos.py "$@"
