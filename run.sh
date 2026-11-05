#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [ ! -x .venv-wsl/bin/python ]; then
    python3 -m venv .venv-wsl
    .venv-wsl/bin/python -m pip install -r requirements.txt
fi
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
exec .venv-wsl/bin/python -m fortune "$@"
