#!/usr/bin/env bash
# Lightweight launcher for the Vault web UI.
# Usage examples:
#   ./scripts/run_web.sh                 # defaults PORT=8765 HOST=0.0.0.0
#   PORT=9000 ./scripts/run_web.sh       # different port
#   VAULT_PATH=~/MyVault ./scripts/run_web.sh
#   INDEX_ON_START=1 VAULT_PATH=~/MyVault ./scripts/run_web.sh
#
# Optional env vars:
#   PORT (default 8765)
#   HOST (default 0.0.0.0)
#   APP  (default webapp.api:app)
#   RELOAD (1 to enable --reload; default 1)
#   VAULT_PATH (if set: ensure config exists; optionally index if INDEX_ON_START=1)
#   INDEX_ON_START=1 (force rebuild index before launch when VAULT_PATH set)
#
set -euo pipefail

PORT=${PORT:-8765}
HOST=${HOST:-0.0.0.0}
APP=${APP:-webapp.api:app}
RELOAD=${RELOAD:-1}
VAULT_PATH=${VAULT_PATH:-}
INDEX_ON_START=${INDEX_ON_START:-0}
PYTHON=${PYTHON:-python}

if [[ -n "$VAULT_PATH" ]]; then
  ABS_VAULT=$(python - <<'PY'
import sys, pathlib, json
p=pathlib.Path(sys.argv[1]).expanduser().resolve()
print(p)
PY
"$VAULT_PATH")
  if [[ ! -f "$ABS_VAULT/_ai/config.yaml" ]]; then
    echo "[run_web] Initializing config in $ABS_VAULT" >&2
    $PYTHON -c "from ai.core.config import init_config; init_config(r'$ABS_VAULT')" || { echo "Config init failed" >&2; exit 1; }
  fi
  if [[ "$INDEX_ON_START" == "1" ]]; then
    echo "[run_web] Building index..." >&2
    $PYTHON -c "from ai.core.config import load_config; from ai.core import index as idx; cfg=load_config(r'$ABS_VAULT'); idx.build_index(cfg)" || { echo "Index build failed" >&2; exit 1; }
  fi
fi

OPTS=("$APP" "--host" "$HOST" "--port" "$PORT")
if [[ "$RELOAD" == "1" ]]; then
  OPTS+=("--reload")
fi

echo "[run_web] Starting uvicorn on $HOST:$PORT (app=$APP, reload=$RELOAD)" >&2
if [[ -n "$VAULT_PATH" ]]; then
  echo "[run_web] VAULT_PATH=$ABS_VAULT" >&2
fi
exec uvicorn "${OPTS[@]}"
