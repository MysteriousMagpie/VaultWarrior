from __future__ import annotations
"""OpenAI embeddings helper with graceful fallback to sentence-transformers.

Usage:
  from . import openai_embed
  vecs = openai_embed.embed_texts(cfg, ["hello world"])

If OPENAI_API_KEY not present or openai unavailable, falls back to sentence-transformers model in cfg.rag.embed_model.
"""
from typing import List
import os

try:  # lazy import openai client
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore

from .config import Config

_client_cache = None


def have_openai(cfg: Config) -> bool:
    key = os.environ.get(cfg.data['provider'].get('api_key_env', 'OPENAI_API_KEY'))
    return bool(key and OpenAI)


def _client(cfg: Config):
    global _client_cache
    if _client_cache is None and have_openai(cfg):
        key = os.environ.get(cfg.data['provider'].get('api_key_env', 'OPENAI_API_KEY'))
        _client_cache = OpenAI(api_key=key)  # type: ignore
    return _client_cache


def embed_texts(cfg: Config, texts: List[str]):
    rag = cfg.data['rag']
    if have_openai(cfg):  # use OpenAI embedding model
        model_name = rag.get('openai_embedding_model', 'text-embedding-3-small')
        cli = _client(cfg)
        # openai batching: send all texts; returns list of data objects
        resp = cli.embeddings.create(model=model_name, input=texts)  # type: ignore
        return [d.embedding for d in resp.data]
    # fallback to local sentence-transformers
    from sentence_transformers import SentenceTransformer  # type: ignore
    model = SentenceTransformer(rag['embed_model'])
    embs = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    # convert to python lists to keep similar API; FAISS still can accept numpy later.
    return embs

