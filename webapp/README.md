# Lightweight Vault Web UI

Experimental minimal web layer over the CLI.

## Install extras

```bash
pip install -e .[web]
```

## Run API

```bash
uvicorn webapp.api:app --reload --port 8000
```

Open `webapp/static.html` in a browser (or serve it) and:

1. Enter absolute path to your vault.
2. Click Select Vault (initializes if missing).
3. Reindex if needed.
4. Create/select a thread.
5. Ask or Chat.

Endpoints:
- `POST /api/vault` {"path": "/abs/path"}
- `GET  /api/tree`
- `POST /api/index`
- `POST /api/ask` {question, k?, tag?, path_glob?}
- `POST /api/chat` {thread, message, write?}
- `GET  /api/threads`
- `GET  /api/health`

Security: No auth, CORS open, local use only. Add auth before exposing.
