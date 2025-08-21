# Desktop (Tauri) Prototype

Experimental Tauri wrapper for the Vault web backend and UI.

## Objectives
- Native folder picker for selecting a vault.
- Launch Python FastAPI backend as sidecar (uvicorn serving `webapp.api:app`).
- Display HTML UI (adapted from `webapp/static.html`).

## Prerequisites
Install locally (macOS):
```bash
# Rust toolchain
curl https://sh.rustup.rs -sSf | sh
# Node (LTS) - using nvm or other manager
# Python 3.11+ with project editable install
pip install -e .[web]
```

## Structure
```
desktop/
  package.json        # (added if you run a JS frontend build later)
  src-tauri/
    tauri.conf.json
    Cargo.toml
    src/main.rs
  ui/
    index.html        # simple frontend (no build step yet)
```

## Running Dev
In one terminal (ensure virtualenv active):
```bash
# from repo root OR desktop/
cd desktop
# start Tauri dev (will build Rust + open window)
cargo tauri dev
```
Tauri will spawn the Python sidecar to serve the backend at `http://127.0.0.1:37999`.

### IMPORTANT: Tauri CLI Version Mismatch
This project is currently a Tauri v1 layout (`tauri = "1"` in `Cargo.toml`). If you have Tauri CLI 2.x globally you will see config errors (unknown keys like `package`, `devPath`). Use the v1 CLI for now:

```bash
# (optional) remove v2 cli
cargo uninstall tauri-cli || true
# install latest v1 cli
cargo install tauri-cli --version ^1.5 --locked

# verify (should show 1.x.x)
cargo tauri --version

# run dev
cargo tauri dev
```

Migration to Tauri v2 (later): bump `tauri` crate to `2`, replace `tauri.conf.json` with new schema (`identifier`, `productName`, `version`, `app`, `bundle`), move allowlist to capability files, and rename `devPath/distDir` to `app.frontendDist` / use `app.devUrl`. Deferred intentionally.

## Selecting a Vault
Use the "Select Vault" button in the window; it opens a native directory dialog and POSTs to the backend `/api/vault` endpoint.

## Reindex
Click Reindex to POST `/api/index`.

## Sidecar Logic
The Python process is launched with arguments roughly equivalent to:
```
python -m uvicorn webapp.api:app --host 127.0.0.1 --port 37999
```

## Next Steps Ideas
- Replace HTTP calls with direct Tauri commands (bypassing FastAPI for some operations).
- Add incremental index watch.
- Add global hotkey capture.
- Package & notarize for macOS.

## Cleanup
On exit Tauri will kill the sidecar; if not, manually kill leftover uvicorn processes.
