#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then python3 -m venv .venv; fi
if [ ! -f .venv/forge-installed.txt ]; then
  .venv/bin/python -m pip install -r requirements.txt
  touch .venv/forge-installed.txt
fi
exec .venv/bin/python -m streamlit run app.py --server.address 127.0.0.1
