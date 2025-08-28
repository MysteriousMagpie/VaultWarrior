from __future__ import annotations
from typing import List, Dict, Any, Sequence
import faiss  # type: ignore
from sentence_transformers import SentenceTransformer  # type: ignore
from . import openai_embed
from .config import Config
from . import index as index_mod
import fnmatch


def retrieve(
    cfg: Config,
    query: str,
    k: int | None = None,
    tag: str | None = None,
    path_glob: str | None = None,
    oversample: int | None = None,
) -> List[Dict[str, Any]]:
    """Retrieve chunks.

    tag: if provided, filter results to chunks whose tags contain this (case-insensitive, normalized).
    path_glob: if provided, filter results whose file matches glob.
    oversample: retrieve more initial candidates before filtering (defaults to 3*k if filters applied).
    """
    params = cfg.data['rag']
    k = int(k or params['top_k'] or 8)
    use_openai = openai_embed.have_openai(cfg)
    faiss_index, chunks = index_mod.load_index(cfg)
    if use_openai:
        import numpy as np  # type: ignore
        q_vec = openai_embed.embed_texts(cfg, [query])[0]
        q_emb = np.array([q_vec], dtype='float32')
        # normalize
        import numpy as _np
        q_emb = q_emb / (_np.linalg.norm(q_emb, axis=1, keepdims=True)+1e-12)
    else:
        model = SentenceTransformer(params['embed_model'])
        q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    initial_k = k
    if (tag or path_glob):
        initial_k = oversample or (k * 3)
    D, I = faiss_index.search(q_emb, initial_k)
    results: List[Dict[str, Any]] = []
    for rank_raw, (score, idx) in enumerate(zip(D[0], I[0]), start=1):
        if idx == -1:
            continue
        ch = chunks[idx]
        results.append({
            'rank': rank_raw,
            'score': float(score),
            **ch,
        })
    # filtering
    if tag:
        tag_norm = tag.lstrip('#').lower()
        results = [r for r in results if tag_norm in (r.get('tags') or [])]
    if path_glob:
        results = [r for r in results if fnmatch.fnmatch(r['file'], path_glob)]
    # re-rank post filter
    for i, r in enumerate(results[:k], start=1):
        r['rank'] = i
    return results[:k]


def format_citations(results: Sequence[Dict[str, Any]]) -> str:
    lines = []
    for r in results:
        heading = r.get('heading') or ''
        lines.append(f"[{r['rank']}] {r['file']} {heading} (chars {r['start']:,}–{r['end']:,})")
    return '\n'.join(lines)
