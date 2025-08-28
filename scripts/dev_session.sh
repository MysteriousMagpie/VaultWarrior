#!/usr/bin/env bash
# Quick dev session launcher: ensure venv + deps, (re)build icons, run tests, launch Tauri.
# Usage: ./scripts/dev_session.sh [--skip-tests] [--no-icons] [--release] [--fast] [--help]
# --fast skips dependency reinstall (trust existing), tests, and icons.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(pwd)
VENV_DIR="$ROOT/.venv"
PY=${PYTHON:-python3}
DO_TESTS=1
DO_ICONS=1
RELEASE=0
FAST=0
ALL_TESTS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-tests) DO_TESTS=0; shift;;
    --no-icons) DO_ICONS=0; shift;;
    --release) RELEASE=1; shift;;
  --fast) FAST=1; DO_TESTS=0; DO_ICONS=0; shift;;
  --all-tests) ALL_TESTS=1; shift;;
    -h|--help)
      grep '^# ' "$0" | sed 's/^# //'; exit 0;;
    *) echo "Unknown arg $1"; exit 1;;
  esac
done

log(){ printf "[dev] %s\n" "$*"; }

ensure_venv(){
  if [[ ! -d "$VENV_DIR" ]]; then
    log "Creating venv in .venv"; $PY -m venv "$VENV_DIR"
  fi
}

ensure_deps(){
  if [[ $FAST -eq 1 ]]; then return; fi
  local PYBIN="$VENV_DIR/bin/python"
  local PIP="$VENV_DIR/bin/pip"
  "$PYBIN" -m pip install -U pip >/dev/null 2>&1 || true
  local needed=0
  # Check core web deps
  if ! "$PYBIN" - <<'EOF' 2>/dev/null
import fastapi,uvicorn
EOF
  then needed=1; fi
  # Check dev test dep
  if [[ $DO_TESTS -eq 1 ]] && ! "$PYBIN" - <<'EOF' 2>/dev/null
import pytest
EOF
  then needed=1; fi
  # Check icon deps if needed
  if [[ $DO_ICONS -eq 1 ]] && ! "$PYBIN" - <<'EOF' 2>/dev/null
import cairosvg, PIL
EOF
  then needed=1; fi
  if [[ $needed -eq 1 ]]; then
    log "Installing/refreshing project deps (web+dev)"
    "$PIP" install -e '.[web,dev]'
  fi
  # Install subprojects (planning CLI variants) editable so their tests import
  if [[ $ALL_TESTS -eq 1 ]]; then
    for sub in ai-vault-planning-cli ai-vault-planning-cli-1; do
      if [[ -f "$sub/setup.cfg" || -f "$sub/pyproject.toml" ]]; then
        log "Ensuring editable install of $sub"
        (cd "$sub" && "$PIP" install -e '.[dev]' >/dev/null 2>&1 || true)
      fi
    done
  else
    log "Python deps present"
  fi
}

run_tests(){
  if [[ $DO_TESTS -eq 0 ]]; then return; fi
  local target="tests"
  if [[ $ALL_TESTS -eq 1 ]]; then
    log "Running ALL tests (monorepo: root + subprojects)"
    # Root tests
    if ! "$VENV_DIR/bin/pytest" -q tests; then log "Root tests failed"; exit 1; fi
    # Subprojects (each has its own test settings)
    for sub in ai-vault-planning-cli ai-vault-planning-cli-1; do
      if [[ -d "$sub/tests" ]]; then
        log "Running tests in $sub"
        ( cd "$sub" && "$VENV_DIR/bin/pytest" -q ) || { log "Tests failed in $sub"; exit 1; }
      fi
    done
    return
  fi
  if [[ ! -d "$target" ]]; then log "No root tests dir; skipping"; return; fi
  log "Running root tests only (add --all-tests to include subprojects)"
  if ! "$VENV_DIR/bin/pytest" -q "$target"; then
    log "Tests failed"; exit 1
  fi
}

build_icons(){
  if [[ $DO_ICONS -eq 0 ]]; then return; fi
  if [[ ! -f scripts/gen_icons.py ]]; then return; fi
  log "Generating icons"
  if "$VENV_DIR/bin/python" - <<'EOF' 2>/dev/null
import cairosvg, PIL
EOF
  then
    ( "$VENV_DIR/bin/python" scripts/gen_icons.py >/dev/null 2>&1 && log "Icons generated" ) || log "Icon script error"
  else
    log "Icon deps missing (cairosvg/pillow); skipping"
  fi
}

launch_tauri(){
  log "Launching Tauri ($([[ $RELEASE -eq 1 ]] && echo release || echo dev))"
  pushd desktop/src-tauri >/dev/null
  if [[ $RELEASE -eq 1 ]]; then
    PATH="$VENV_DIR/bin:$PATH" cargo tauri build
  else
    PATH="$VENV_DIR/bin:$PATH" cargo tauri dev
  fi
  popd >/dev/null
}

log "Starting dev session"
ensure_venv
source "$VENV_DIR/bin/activate"
ensure_deps
build_icons
run_tests
launch_tauri
