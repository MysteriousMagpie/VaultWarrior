from __future__ import annotations
from pathlib import Path
from datetime import datetime
from typing import List
from .config import Config
import yaml

THREAD_HEADER_KEYS = ["thread_id", "status", "context_links", "review_cadence"]


def thread_path(cfg: Config, slug: str) -> Path:
    return cfg.vault_path / cfg.data['writeback']['thread_dir'] / f"{slug}.md"


def create_thread(cfg: Config, slug: str, seed: str | None = None) -> Path:
    p = thread_path(cfg, slug)
    if p.exists():
        return p
    p.parent.mkdir(parents=True, exist_ok=True)
    front = {
        'thread_id': slug,
        'status': 'active',
        'context_links': [],
        'review_cadence': 'weekly',
    }
    body = ['---', yaml.safe_dump(front, sort_keys=False).strip(), '---', '']
    if seed:
        body.append(format_entry('user', seed))
    p.write_text('\n'.join(body), encoding='utf-8')
    return p


def format_entry(role: str, content: str) -> str:
    ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
    return f"**{ts} — {role}**\n\n{content}\n"


def append_entry(cfg: Config, slug: str, role: str, content: str):
    p = thread_path(cfg, slug)
    if not p.exists():
        raise FileNotFoundError(f"Thread {slug} not found")
    with p.open('a', encoding='utf-8') as f:
        f.write('\n' + format_entry(role, content))


def load_thread_history(cfg: Config, slug: str, max_chars: int = 3000) -> str:
    p = thread_path(cfg, slug)
    if not p.exists():
        return ''
    text = p.read_text(encoding='utf-8')
    # strip frontmatter
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            text = parts[2]
    # take last max_chars window
    return text[-max_chars:]
