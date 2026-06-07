#!/usr/bin/env bash
# compare.sh — bash wrapper around compare.py
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python "$SCRIPT_DIR/compare.py" "$@"
