from __future__ import annotations
import typer
from rich.console import Console
from pathlib import Path
from typing import Optional, List

from ai.core import config as config_mod
from ai.core import index as index_mod
from ai.core import retrieve as retrieve_mod
from ai.core import threads as threads_mod
from ai.core import llm as llm_mod
from ai.core import writeback as writeback_mod
from ai.core import gitwrap as gitwrap_mod
import re
import shutil
import time
import yaml
import datetime

app = typer.Typer(help="Vault-aware RAG planning assistant.")
console = Console()

@app.command()
def init(vault_path: str = typer.Argument(..., help="Path to vault")):
    """Initialize AI config inside vault."""
    cfg_path = config_mod.init_config(vault_path)
    console.print(f"Initialized config at {cfg_path}")


@app.command()
def index(vault_path: str = typer.Argument(...), watch: bool = typer.Option(False, "--watch")):
    """Build (or rebuild) the embedding index. --watch for incremental (placeholder)."""
    cfg = config_mod.load_config(vault_path)
    manifest = index_mod.build_index(cfg)
    console.print(f"Indexed {manifest['total_chunks']} chunks.")
    if watch:
        console.print("Watch mode not yet implemented.")


@app.command("thread")
def thread_new(
    action: str = typer.Argument(..., help="Use: new"),
    slug: str = typer.Argument(...),
    seed: Optional[str] = typer.Option(None, "--seed"),
    vault_path: str = typer.Option('.', help="Vault path"),
):
    """Thread operations (currently only: new)."""
    if action != 'new':
        raise typer.BadParameter("Only 'new' supported right now")
    cfg = config_mod.load_config(vault_path)
    p = threads_mod.create_thread(cfg, slug, seed=seed)
    console.print(f"Thread created at {p}")


@app.command()
def ask(
    question: str = typer.Argument(...),
    vault_path: str = typer.Option('.', help="Vault path"),
    filters: List[str] = typer.Option([], "--filters", help="Path glob filters"),
    k: Optional[int] = typer.Option(None, "--k"),
    tag: Optional[str] = typer.Option(None, "--tag", help="Filter by tag"),
    path_glob: Optional[str] = typer.Option(None, "--path", help="Filter by file path glob"),
):
    """One-off RAG question with citations."""
    cfg = config_mod.load_config(vault_path)
    results = retrieve_mod.retrieve(cfg, question, k=k, tag=tag, path_glob=path_glob)
    console.print(f"Question: [bold]{question}[/bold]")
    console.print("Sources:\n" + retrieve_mod.format_citations(results))


@app.command()
def chat(
    slug: str = typer.Argument(...),
    message: str = typer.Argument(...),
    vault_path: str = typer.Option('.', help="Vault path"),
    write: bool = typer.Option(False, "--write"),
    filters: List[str] = typer.Option([], "--filters"),
):
    """Chat within a thread, retrieving context and streaming response."""
    cfg = config_mod.load_config(vault_path)
    history = threads_mod.load_thread_history(cfg, slug)
    results = retrieve_mod.retrieve(cfg, message)
    citations = retrieve_mod.format_citations(results)
    prompt = (
        "You are a planning assistant. Use the provided context to answer.\n"\
        f"Thread history (truncated):\n{history}\n\n"\
        f"User message: {message}\n\nSources:\n{citations}\n"
    )
    redactor = llm_mod.build_redactor(cfg)
    prompt = redactor(prompt)
    console.print("[bold]Assistant:[/bold]", end=" ")
    try:
        out_text = ""
        for token in llm_mod.stream_completion(cfg, prompt):
            out_text += token
            console.print(token, end="")
        console.print()  # newline
    except Exception as e:  # broad for streaming robustness
        console.print(f"[red]LLM error:[/red] {e}")
        return
    console.print("Sources:\n" + citations)
    if write:
        threads_mod.append_entry(cfg, slug, 'user', message)
        threads_mod.append_entry(cfg, slug, 'assistant', out_text)
        gitwrap_mod.auto_commit(cfg, [threads_mod.thread_path(cfg, slug)], 'chat', slug, len(results))


@app.command()
def capture(
    text: str = typer.Argument(...),
    vault_path: str = typer.Option('.', help="Vault path"),
    write: bool = typer.Option(False, "--write"),
):
    """Capture a quick thought into daily note."""
    cfg = config_mod.load_config(vault_path)
    if not write:
        console.print("Use --write to persist capture.")
        return
    p = writeback_mod.capture(cfg, text)
    gitwrap_mod.auto_commit(cfg, [p], 'capture', 'daily', 0)
    console.print(f"Captured to {p}")


@app.command()
def plan(
    slug: str = typer.Argument(...),
    weekly: bool = typer.Option(False, "--weekly"),
    vault_path: str = typer.Option('.', help="Vault path"),
    write: bool = typer.Option(False, "--write"),
):
    """Produce a planning checkpoint for a thread."""
    cfg = config_mod.load_config(vault_path)
    history = threads_mod.load_thread_history(cfg, slug)
    prompt = (
        "Summarize recent progress and produce a weekly checkpoint with: wins, blockers, next 3 tasks.\n"\
        f"History:\n{history}\n"
    )
    redactor = llm_mod.build_redactor(cfg)
    prompt = redactor(prompt)
    out_text = ""
    try:
        for token in llm_mod.stream_completion(cfg, prompt):
            out_text += token
            console.print(token, end="")
        console.print()
    except Exception as e:
        console.print(f"[red]LLM error:[/red] {e}")
        return
    if write:
        threads_mod.append_entry(cfg, slug, 'assistant', out_text)
        gitwrap_mod.auto_commit(cfg, [threads_mod.thread_path(cfg, slug)], 'plan', slug, 0)


@app.command()
def doctor(vault_path: str = typer.Option('.', help="Vault path")):
    """Run sanity checks."""
    from ai.core import llm as llm_mod
    ok = True
    try:
        cfg = config_mod.load_config(vault_path)
    except Exception as e:
        console.print(f"[red]Config error:[/red] {e}")
        return
    console.print(f"Config loaded for vault {cfg.vault_path}")
    # index
    try:
        index_mod.load_index(cfg)
        console.print("Index: present")
    except Exception as e:
        console.print(f"Index: [yellow]missing[/yellow] ({e})")
        ok = False
    # api key
    provider = cfg.data['provider']
    if not provider.get('api_key_env') or not typer.get_app_dir(provider['api_key_env']):
        # cannot actually verify secret here; skip
        console.print("API key env configured: " + provider.get('api_key_env', ''))
    console.print("Doctor complete." if ok else "Doctor found issues.")


@app.command()
def daemon():  # placeholder
    console.print("Daemon not implemented yet.")


def _ensure_md_path(p: Path) -> Path:
    if p.suffix.lower() != '.md':
        return p.with_suffix('.md')
    return p


@app.command()
def new(
    name: str = typer.Argument(..., help="Path or name for new note (relative to vault)"),
    vault_path: str = typer.Option('.', help="Vault path"),
    title: Optional[str] = typer.Option(None, "--title"),
    tags: List[str] = typer.Option([], "--tag"),
    no_frontmatter: bool = typer.Option(False, "--no-frontmatter", help="Do not add template frontmatter"),
):
    """Create a new note with optional frontmatter template and reindex."""
    cfg = config_mod.load_config(vault_path)
    vault = cfg.vault_path
    rel = Path(name)
    target = _ensure_md_path(vault / rel)
    if target.exists():
        raise typer.BadParameter(f"File exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    note_title = title or target.stem.replace('_', ' ').replace('-', ' ').title()
    fm = ''
    if not no_frontmatter:
        ts = time.strftime('%Y-%m-%dT%H:%M:%S')
        tag_list = [t.lstrip('#').lower() for t in tags]
        fm = ('---\n'
              f'title: {note_title}\n'
              f'created: {ts}\n'
              f'tags: {tag_list}\n'
              '---\n\n')
    target.write_text(fm, encoding='utf-8')
    console.print(f"Created {target.relative_to(vault)}")
    index_mod.update_index_incremental(cfg)
    gitwrap_mod.auto_commit(cfg, [target], 'new', target.name, 0)


def _update_links(vault: Path, old_rel: str, new_rel: str):
    """Update wiki-style and markdown links referencing old_rel to new_rel."""
    # Patterns: [[old_rel]] possibly with anchors or alias; markdown: ](old_rel)
    # We'll search every md file. Simple heuristic.
    for f in vault.rglob('*.md'):
        txt = f.read_text(encoding='utf-8', errors='ignore')
        changed = False
        # wiki links
        # Accept variants: [[old_rel]], [[old_rel#anchor]], [[old_rel|alias]]
        def repl_wiki(m):
            nonlocal changed
            changed = True
            inner = m.group(1)
            rest = m.group(2) or ''
            return f'[[{new_rel}{rest}]]'
        pattern_wiki = re.compile(rf"\[\[({re.escape(old_rel)})([^\]]*)\]\]")
        txt2 = pattern_wiki.sub(repl_wiki, txt)
        # markdown links: (old_rel) or (old_rel#anchor)
        def repl_md(m):
            nonlocal changed
            changed = True
            suffix = m.group(2) or ''
            return f'({new_rel}{suffix})'
        pattern_md = re.compile(rf"\((?:./)?({re.escape(old_rel)})(#[^)]+)?\)")
        txt3 = pattern_md.sub(repl_md, txt2)
        if changed:
            f.write_text(txt3, encoding='utf-8')


@app.command()
def mv(
    old: str = typer.Argument(..., help="Existing note path (relative)"),
    new: str = typer.Argument(..., help="New note path (relative)"),
    vault_path: str = typer.Option('.', help="Vault path"),
    update_links: bool = typer.Option(True, "--update-links/--no-update-links"),
):
    """Rename or move a note; updates links and reindexes."""
    cfg = config_mod.load_config(vault_path)
    vault = cfg.vault_path
    src = _ensure_md_path(vault / old)
    dst = _ensure_md_path(vault / new)
    if not src.exists():
        raise typer.BadParameter(f"Source not found: {src}")
    if dst.exists():
        raise typer.BadParameter(f"Destination exists: {dst}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    src_rel = src.relative_to(vault).as_posix()
    dst_rel = dst.relative_to(vault).as_posix()
    shutil.move(str(src), str(dst))
    if update_links:
        _update_links(vault, src_rel, dst_rel)
    # update frontmatter title if exists
    try:
        txt = dst.read_text(encoding='utf-8')
        if txt.startswith('---'):
            m = re.match(r"---\n(.*?)\n---\n", txt, re.DOTALL)
            if m:
                fm_raw = m.group(1)
                meta = yaml.safe_load(fm_raw) or {}
                if isinstance(meta, dict):
                    new_title = dst.stem.replace('_', ' ').replace('-', ' ').title()
                    if meta.get('title') != new_title:
                        meta['title'] = new_title
                        new_fm = '---\n' + yaml.safe_dump(meta, sort_keys=False).strip() + '\n---\n'
                        body = txt[m.end():]
                        dst.write_text(new_fm + body, encoding='utf-8')
    except Exception:
        pass
    index_mod.update_index_incremental(cfg)
    gitwrap_mod.auto_commit(cfg, [dst], 'mv', f"{src_rel}->{dst_rel}", 0)
    console.print(f"Moved {src_rel} -> {dst_rel}")


def _find_backlinks(vault: Path, target_rel: str) -> List[Path]:
    hits: List[Path] = []
    # Combine wiki-style and markdown link patterns referencing the target.
    pattern = re.compile(rf"\[\[({re.escape(target_rel)})([^\]]*)\]\]|\((?:./)?({re.escape(target_rel)})(#[^)]+)?\)")
    for f in vault.rglob('*.md'):
        try:
            txt = f.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        if pattern.search(txt):
            hits.append(f)
    return hits


@app.command()
def rm(
    path: str = typer.Argument(..., help="Note path to delete (relative)"),
    vault_path: str = typer.Option('.', help="Vault path"),
    force: bool = typer.Option(False, "--force", help="Skip backlink check"),
):
    """Delete a note after checking backlinks; reindex."""
    cfg = config_mod.load_config(vault_path)
    vault = cfg.vault_path
    target = _ensure_md_path(vault / path)
    if not target.exists():
        raise typer.BadParameter(f"Not found: {target}")
    rel = target.relative_to(vault).as_posix()
    if not force:
        backlinks = _find_backlinks(vault, rel)
        if backlinks:
            console.print(f"[yellow]Warning:[/yellow] {len(backlinks)} files link to {rel}:")
            for b in backlinks[:10]:
                console.print(f" - {b.relative_to(vault)}")
            if len(backlinks) > 10:
                console.print(" (more omitted)")
            confirm = typer.confirm("Proceed with deletion?", default=False)
            if not confirm:
                console.print("Aborted.")
                raise typer.Exit(1)
    target.unlink()
    index_mod.update_index_incremental(cfg)
    gitwrap_mod.auto_commit(cfg, [], 'rm', rel, 0)
    console.print(f"Deleted {rel}")


@app.command()
def enrich(
    vault_path: str = typer.Option('.', help="Vault path"),
    apply: bool = typer.Option(False, "--apply", help="Write changes (otherwise dry-run)"),
    add_tags: bool = typer.Option(True, "--add-tags/--no-add-tags", help="Infer tags from path folders if missing"),
):
    """Normalize / add frontmatter across existing notes.

    - Adds frontmatter if absent with: title, created timestamp, tags (optional)
    - If present, preserves existing keys; adds missing title / tags only.
    - Infers title from filename if absent.
    - Infers tags from folder path segments (excluding leading '.') if enabled and tags were missing.
    """
    cfg = config_mod.load_config(vault_path)
    vault = cfg.vault_path
    changed: List[Path] = []
    examined = 0
    now_iso = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    for p in vault.rglob('*.md'):
        rel = p.relative_to(vault).as_posix()
        # skip internal dirs
        if rel.startswith('_ai/') or rel.startswith('daily/'):
            continue
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        meta, body = index_mod.parse_frontmatter(text)
        had_frontmatter = bool(meta)
        updated = False
        if not had_frontmatter:
            meta = {}
        # title
        if 'title' not in meta or not meta.get('title'):
            meta['title'] = p.stem.replace('_', ' ').replace('-', ' ').title()
            updated = True
        # created
        if 'created' not in meta:
            meta['created'] = now_iso
            updated = True
        # tags inference only if missing
        if add_tags and ('tags' not in meta or not meta.get('tags')):
            # derive from path segments except filename
            parts = list(p.relative_to(vault).parts[:-1])
            tag_candidates = []
            for seg in parts:
                seg_clean = seg.strip().lower()
                if not seg_clean or seg_clean.startswith('.'):
                    continue
                # sanitize to simple word
                seg_clean = re.sub(r'[^a-z0-9_-]+', '', seg_clean)
                if seg_clean:
                    tag_candidates.append(seg_clean)
            if tag_candidates:
                meta['tags'] = tag_candidates
                updated = True
        if updated:
            new_fm = '---\n' + yaml.safe_dump(meta, sort_keys=False).strip() + '\n---\n\n'
            new_text = new_fm + body if body else new_fm
            if apply:
                p.write_text(new_text, encoding='utf-8')
            changed.append(p)
        examined += 1
    if changed:
        console.print(f"Enrich: {'updated' if apply else 'would update'} {len(changed)} / {examined} notes.")
    else:
        console.print(f"Enrich: no changes across {examined} notes.")
    if apply and changed:
        # reindex after metadata changes
        index_mod.update_index_incremental(cfg)
        gitwrap_mod.auto_commit(cfg, changed, 'enrich', 'frontmatter', 0)
        console.print("Reindexed after enrichment.")

if __name__ == "__main__":  # pragma: no cover
    app()
