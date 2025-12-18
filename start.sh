#!/usr/bin/env bash
set -euo pipefail

cd /app

echo "[BOOT] WORKER='${WORKER-}'" >&2
env | grep -E '^WORKER=' >&2 || true

case "${WORKER:-image}" in
  image)
    exec python3 -u /app/image_worker/handler.py
    ;;
  llm)
    exec python3 -u /app/llm_worker/handler.py
    ;;
  *)
    echo "ERROR: WORKER must be 'image' or 'llm' (got '${WORKER:-}')" >&2
    exit 2
    ;;
esac
