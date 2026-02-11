#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/../_common.sh"

log "Linux build"

cd "$PROJECT_ROOT/building/linux"

exec "$VENV_PYTHON" build_linux.py "$@"
