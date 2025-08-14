from __future__ import annotations
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict

DEFAULT_CONFIG = {
    "vault_path": "",
    "provider": {"type": "openai", "model": "gpt-4.1-mini", "api_key_env": "OPENAI_API_KEY"},
    "rag": {
        "embed_model": "sentence-transformers/all-MiniLM-L6-v2",
        "chunk_chars": 1200,
        "chunk_overlap": 200,
        "top_k": 8,
        "exclude_globs": ["_ai/**", ".obsidian/**"],
    },
    "writeback": {
        "thread_dir": "_ai/threads",
        "default_target": "daily",
        "allow_globs": ["daily/**", "_ai/threads/**", "projects/**"],
    },
    "privacy": {"redact": [r"(?i)passport\s*\d+", r"(?i)api[_-]?key\s*[:=]\s*\S+"]},
    "git": {"auto_commit": True, "message_template": "ai:{command} {target} (k={k})"},
}

CONFIG_REL_PATH = Path("_ai/config.yaml")

@dataclass
class Config:
    data: Dict[str, Any]

    @property
    def vault_path(self) -> Path:
        return Path(self.data.get("vault_path") or ".").expanduser().resolve()

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(self.data, f, sort_keys=False)


def init_config(vault_path: str) -> Path:
    vault = Path(vault_path).expanduser().resolve()
    cfg = Config(dict(DEFAULT_CONFIG))
    cfg.data["vault_path"] = str(vault)
    cfg_path = vault / CONFIG_REL_PATH
    if cfg_path.exists():
        # do not overwrite; load existing
        return cfg_path
    cfg.save(cfg_path)
    (vault / "_ai" / "threads").mkdir(parents=True, exist_ok=True)
    (vault / "daily").mkdir(parents=True, exist_ok=True)
    return cfg_path


def load_config(vault_path: str | Path) -> Config:
    vault = Path(vault_path)
    cfg_path = vault / CONFIG_REL_PATH
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config not found at {cfg_path}. Run 'ai init <vault_path>'.")
    with cfg_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return Config(data)
