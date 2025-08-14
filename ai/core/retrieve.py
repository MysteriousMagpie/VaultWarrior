from __future__ import annotations
from typing import List, Dict, Any, Sequence
import faiss  # type: ignore
from sentence_transformers import SentenceTransformer  # type: ignore
from .config import Config
from . import index as index_mod


def retrieve(cfg: Config, query: str, k: int | None = None) -> List[Dict[str, Any]]:
    params = cfg.data['rag']
    k = k or params['top_k']
    model = SentenceTransformer(params['embed_model'])
    faiss_index, chunks = index_mod.load_index(cfg)
    q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    D, I = faiss_index.search(q_emb, k)
    results: List[Dict[str, Any]] = []
    for rank, (score, idx) in enumerate(zip(D[0], I[0]), start=1):
        if idx == -1:
            continue
        ch = chunks[idx]
        results.append({
            'rank': rank,
            'score': float(score),
            **ch,
        })
    return results


def format_citations(results: Sequence[Dict[str, Any]]) -> str:
    lines = []
    for r in results:
        heading = r.get('heading') or ''
        lines.append(f"[{r['rank']}] {r['file']} {heading} (chars {r['start']:,}–{r['end']:,})")
    return '\n'.join(lines)
