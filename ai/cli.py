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
):
    """One-off RAG question with citations."""
    cfg = config_mod.load_config(vault_path)
    results = retrieve_mod.retrieve(cfg, question, k=k)
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

if __name__ == "__main__":  # pragma: no cover
    app()
