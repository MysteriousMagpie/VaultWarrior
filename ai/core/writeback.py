from __future__ import annotations
from pathlib import Path
from datetime import datetime
from .config import Config


def can_write(cfg: Config, target: Path) -> bool:
    allow = cfg.data.get('writeback', {}).get('allow_globs', [])
    rel = target.relative_to(cfg.vault_path).as_posix()
    import fnmatch
    return any(fnmatch.fnmatch(rel, g) for g in allow)


def capture(cfg: Config, thought: str) -> Path:
    day_dir = cfg.vault_path / 'daily'
    day_dir.mkdir(parents=True, exist_ok=True)
    fname = datetime.utcnow().strftime('%Y-%m-%d') + '.md'
    fpath = day_dir / fname
    heading = '⚡ Captures'
    content = fpath.read_text(encoding='utf-8') if fpath.exists() else ''
    if heading not in content:
        content += f"\n## {heading}\n"
    content += f"- {datetime.utcnow().strftime('%H:%M')} {thought}\n"
    fpath.write_text(content, encoding='utf-8')
    return fpath
