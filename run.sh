#!/usr/bin/env bash
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -n "${PYTHON:-}" ]; then
    exec "$PYTHON" "$root/src/main.py" "$@"
elif command -v py >/dev/null 2>&1; then
    exec py -3 "$root/src/main.py" "$@"
elif command -v python3 >/dev/null 2>&1; then
    exec python3 "$root/src/main.py" "$@"
else
    exec python "$root/src/main.py" "$@"
fi
