from __future__ import annotations
from pathlib import Path
from typing import Iterable
from git import Repo, InvalidGitRepositoryError  # type: ignore
from .config import Config


def is_git_repo(path: Path) -> bool:
    try:
        _ = Repo(path, search_parent_directories=True)
        return True
    except InvalidGitRepositoryError:
        return False


def auto_commit(cfg: Config, paths: Iterable[Path], command: str, target: str, k: int):
    if not cfg.data.get('git', {}).get('auto_commit', True):
        return
    repo_path = cfg.vault_path
    if not is_git_repo(repo_path):
        return
    repo = Repo(repo_path)
    rels = []
    for p in paths:
        try:
            rels.append(str(p.relative_to(repo_path)))
        except ValueError:
            continue
    if not rels:
        return
    repo.index.add(rels)
    msg_tpl = cfg.data.get('git', {}).get('message_template', 'ai:{command} {target} (k={k})')
    repo.index.commit(msg_tpl.format(command=command, target=target, k=k))
