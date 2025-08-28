from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Iterator, List, Dict, Any, Tuple, Optional
import fnmatch
import hashlib
import re
import yaml

import faiss  # type: ignore
from sentence_transformers import SentenceTransformer  # type: ignore
from . import openai_embed

from .config import Config

INDEX_DIR = "_ai/index"
CHUNKS_FILE = "chunks.jsonl"
INDEX_FILE = "faiss.index"
MANIFEST_FILE = "manifest.json"

class Chunk(Dict[str, Any]):
    pass

def _hash_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]


def chunk_markdown(text: str, chunk_chars: int, overlap: int) -> List[Tuple[int, int]]:
    spans: List[Tuple[int, int]] = []
    n = len(text)
    start = 0
    while start < n:
        end = min(n, start + chunk_chars)
        spans.append((start, end))
        if end == n:
            break
        start = max(0, end - overlap)
    return spans


def extract_headings(text: str) -> List[Tuple[int, str]]:
    lines = text.splitlines(keepends=True)
    headings: List[Tuple[int, str]] = []
    offset = 0
    for line in lines:
        if line.startswith('#'):
            lvl = len(line) - len(line.lstrip('#'))
            title = line.strip('#').strip()
            headings.append((offset, f"{'#'*lvl} {title}"))
        offset += len(line)
    return headings


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Return (metadata, body_without_frontmatter). If no frontmatter, metadata is {}."""
    if not text.startswith('---'):
        return {}, text
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw = m.group(1)
    try:
        meta = yaml.safe_load(raw) or {}
        if not isinstance(meta, dict):
            meta = {}
    except Exception:
        meta = {}
    remainder = text[m.end():]
    return meta, remainder


def normalize_tags(meta: Dict[str, Any]) -> List[str]:
    raw = meta.get('tags')
    if raw is None:
        return []
    if isinstance(raw, str):
        tags = [raw]
    else:
        try:
            tags = list(raw)
        except Exception:
            return []
    norm: List[str] = []
    for t in tags:
        if not isinstance(t, str):
            continue
        t = t.strip()
        if not t:
            continue
        if t.startswith('#'):
            t = t[1:]
        norm.append(t.lower())
    # de-duplicate preserving order
    seen = set()
    out: List[str] = []
    for t in norm:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def heading_for_offset(headings: List[Tuple[int, str]], pos: int) -> str:
    current = ""
    for off, h in headings:
        if off <= pos:
            current = h
        else:
            break
    return current


def scan_files(vault: Path, exclude_globs: List[str]) -> List[Path]:
    files: List[Path] = []
    for p in vault.rglob('*.md'):
        rel = p.relative_to(vault).as_posix()
        if any(fnmatch.fnmatch(rel, g) for g in exclude_globs):
            continue
        files.append(p)
    return files


def build_index(cfg: Config, model: SentenceTransformer | None = None) -> Dict[str, Any]:
    vault = cfg.vault_path
    params = cfg.data['rag']
    exclude = params.get('exclude_globs', [])
    files = scan_files(vault, exclude)
    # Only instantiate sentence-transformers if we won't use OpenAI
    use_openai = openai_embed.have_openai(cfg)
    if not use_openai:
        model = model or SentenceTransformer(params['embed_model'])
    all_chunks: List[Chunk] = []
    texts: List[str] = []
    for file in files:
        full_text = file.read_text(encoding='utf-8', errors='ignore')
        meta, body = parse_frontmatter(full_text)
        tags = normalize_tags(meta)
        headings = extract_headings(body)
        spans = chunk_markdown(body, params['chunk_chars'], params['chunk_overlap'])
        for i, (s, e) in enumerate(spans):
            chunk_text = body[s:e]
            heading = heading_for_offset(headings, s)
            chunk_id = f"{file.name}-{i}-{_hash_text(chunk_text)}"
            all_chunks.append(Chunk({
                'file': file.relative_to(vault).as_posix(),
                'chunk_id': chunk_id,
                'start': s,
                'end': e,
                'heading': heading,
                'tags': tags,
            }))
            texts.append(chunk_text)
    if not texts:
        if use_openai:
            # default OpenAI embedding dims: small=1536, adjust if model differs
            dim = 1536
        else:
            dim = model.get_sentence_embedding_dimension()  # type: ignore[arg-type]
        index = faiss.IndexFlatIP(dim)
    else:
        if use_openai:
            embs = openai_embed.embed_texts(cfg, texts)
            import numpy as np  # type: ignore
            embs = np.array(embs, dtype='float32')
            # OpenAI embeddings already L2 normalized? We ensure normalization for IP cosine.
            import numpy as _np
            norms = _np.linalg.norm(embs, axis=1, keepdims=True) + 1e-12
            embs = embs / norms
        else:
            embs = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)  # cosine via IP
        dim = embs.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embs)
    # persistence
    out_dir = vault / INDEX_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(out_dir / INDEX_FILE))
    with (out_dir / CHUNKS_FILE).open('w', encoding='utf-8') as f:
        for row in all_chunks:
            f.write(json.dumps(row) + '\n')
    manifest = {
        'model': (params['openai_embedding_model'] if use_openai else params['embed_model']),
        'provider': 'openai' if use_openai else 'local',
        'total_chunks': len(all_chunks),
        'created_at': time.time(),
    }
    (out_dir / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    return manifest


def load_index(cfg: Config):
    vault = cfg.vault_path
    out_dir = vault / INDEX_DIR
    if not (out_dir / INDEX_FILE).exists():
        raise FileNotFoundError("Index not found. Run 'ai index'.")
    index = faiss.read_index(str(out_dir / INDEX_FILE))
    chunks: List[Chunk] = []
    with (out_dir / CHUNKS_FILE).open('r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
    return index, chunks


def update_index_incremental(cfg: Config, model: SentenceTransformer | None = None) -> Dict[str, Any]:
    # Simplification: full rebuild for now.
    return build_index(cfg, model=model)
