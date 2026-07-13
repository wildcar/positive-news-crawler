#!/usr/bin/env sh
set -eu
PYTHON="${PYTHON:-python3}"
"$PYTHON" -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m playwright install --with-deps chromium
.venv/bin/python manage.py migrate
printf '%s\n' 'Installation complete. Create the operator with:'
printf '%s\n' '.venv/bin/python manage.py createoperator operator'

