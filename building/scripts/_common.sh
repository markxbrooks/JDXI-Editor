#!/usr/bin/env bash

log() { echo "▶ $*"; }
die() { echo "✗ $*" >&2; exit 1; }

detect_project_root() {
    if [[ -n "${PROJECT_ROOT:-}" ]]; then
        return
    fi

    local dir="$(pwd)"

    while [[ "$dir" != "/" ]]; do
        if [[ -f "$dir/pyproject.toml" || -f "$dir/setup.py" ]]; then
            PROJECT_ROOT="$dir"
            export PROJECT_ROOT
            log "PROJECT_ROOT = $PROJECT_ROOT"
            return
        fi
        dir="$(dirname "$dir")"
    done

    die "Could not locate project root"
}

ensure_venv() {
    VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"
    export VENV_PYTHON

    [[ -x "$VENV_PYTHON" ]] || \
        die "Virtualenv missing. Run: python -m venv venv && pip install -r requirements.txt"
}
