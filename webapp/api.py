from __future__ import annotations
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from typing import List, Optional

from ai.core import config as config_mod
from ai.core import index as index_mod
from ai.core import retrieve as retrieve_mod
from ai.core import threads as threads_mod

app = FastAPI(title="Vault Web")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VaultSelect(BaseModel):
    path: str

class AskRequest(BaseModel):
    question: str
    k: Optional[int] = None
    tag: Optional[str] = None
    path_glob: Optional[str] = None

class ChatRequest(BaseModel):
    thread: str
    message: str
    write: bool = False

class ThreadCreate(BaseModel):
    slug: str
    seed: str | None = None

class FileUpdate(BaseModel):
    path: str  # relative
    content: str

_cached_cfg: config_mod.Config | None = None

def get_cfg() -> config_mod.Config:
    if _cached_cfg is None:
        raise HTTPException(status_code=400, detail="Vault not set. Call POST /api/vault first.")
    return _cached_cfg  # type: ignore

@app.post('/api/vault')
def set_vault(v: VaultSelect):
    global _cached_cfg
    p = Path(v.path).expanduser().resolve()
    if not p.exists():
        raise HTTPException(404, f"Path not found: {p}")
    # load or init config
    try:
        cfg = config_mod.load_config(p)
    except FileNotFoundError:
        config_mod.init_config(str(p))
        cfg = config_mod.load_config(p)
    _cached_cfg = cfg
    return {"vault": str(cfg.vault_path)}

@app.get('/api/tree')
def tree():
    cfg = get_cfg()
    out: List[dict] = []
    for f in cfg.vault_path.rglob('*.md'):
        rel = f.relative_to(cfg.vault_path).as_posix()
        out.append({"file": rel, "size": f.stat().st_size})
    return {"files": out}

@app.post('/api/index')
def rebuild_index():
    cfg = get_cfg()
    manifest = index_mod.build_index(cfg)
    return manifest

@app.post('/api/ask')
def ask(req: AskRequest):
    cfg = get_cfg()
    results = retrieve_mod.retrieve(cfg, req.question, k=req.k, tag=req.tag, path_glob=req.path_glob)
    return {"question": req.question, "results": results}

@app.post('/api/chat')
def chat(req: ChatRequest):
    cfg = get_cfg()
    # ensure thread
    threads_mod.create_thread(cfg, req.thread)
    results = retrieve_mod.retrieve(cfg, req.message)
    citations = retrieve_mod.format_citations(results)
    # naive call to underlying CLI LLM stream (reuse llm.core) - for now reuse existing function
    from ai.core import llm as llm_mod
    history = threads_mod.load_thread_history(cfg, req.thread)
    prompt = (
        "You are a planning assistant. Use context.\n" f"History:\n{history}\nUser: {req.message}\nSources:\n{citations}\n"
    )
    redactor = llm_mod.build_redactor(cfg)
    prompt = redactor(prompt)
    try:
        full = ''.join(list(llm_mod.stream_completion(cfg, prompt)))
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")
    if req.write:
        threads_mod.append_entry(cfg, req.thread, 'user', req.message)
        threads_mod.append_entry(cfg, req.thread, 'assistant', full)
    return {"thread": req.thread, "answer": full, "citations": citations, "k": len(results)}

@app.get('/api/threads')
def list_threads():
    cfg = get_cfg()
    tdir = cfg.vault_path / cfg.data['writeback']['thread_dir']
    threads = []
    if tdir.exists():
        for f in tdir.glob('*.md'):
            threads.append(f.stem)
    return {"threads": threads}

@app.get('/api/health')
def health():
    return {"ok": True}

@app.get('/', response_class=HTMLResponse)
def root():  # simple redirect meta
    return """<!DOCTYPE html><html><head><meta http-equiv='refresh' content='0; url=/app/static.html'>
    <title>Vault Web</title></head><body>
    <p>Loading <a href='/app/static.html'>Vault Web UI</a>...</p></body></html>"""

@app.post('/api/thread')
def create_thread(req: ThreadCreate):
    cfg = get_cfg()
    p = threads_mod.create_thread(cfg, req.slug, seed=req.seed)
    return {"created": p.name}

def _assert_in_vault(rel: str, vault: Path) -> Path:
    p = (vault / rel).resolve()
    if not str(p).startswith(str(vault)):
        raise HTTPException(400, 'Path escapes vault')
    return p

@app.get('/api/file')
def read_file(path: str = Query(..., description="Relative markdown path")):
    cfg = get_cfg()
    p = _assert_in_vault(path, cfg.vault_path)
    if not p.exists():
        raise HTTPException(404, 'Not found')
    if p.suffix.lower() != '.md':
        raise HTTPException(400, 'Only .md allowed')
    content = p.read_text(encoding='utf-8', errors='ignore')
    return {"path": path, "content": content, "size": len(content)}

@app.put('/api/file')
def update_file(update: FileUpdate):
    cfg = get_cfg()
    p = _assert_in_vault(update.path, cfg.vault_path)
    if p.suffix.lower() != '.md':
        raise HTTPException(400, 'Only .md allowed')
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(update.content, encoding='utf-8')
    return {"updated": update.path, "bytes": len(update.content)}

# Mount static assets under /app
try:
    app.mount('/app', StaticFiles(directory=Path(__file__).parent), name='app')
except Exception:
    pass

# Run with: uvicorn webapp.api:app --reload
