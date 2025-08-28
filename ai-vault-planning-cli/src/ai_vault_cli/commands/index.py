import click
from ai_vault_cli.indexing.crawler import crawl_vault
from ai_vault_cli.indexing.parser import parse_markdown
from ai_vault_cli.indexing.embeddings import create_embeddings

@click.group()
def cli():
    """Index related commands."""
    pass

@cli.command("index")
@click.argument("vault_path")
def index_cmd(vault_path: str):
    """Perform a lightweight indexing (demo)."""
    files = crawl_vault(vault_path)
    parsed = [parse_markdown(f) for f in files[:3]]  # dummy parse (paths)
    _ = [create_embeddings(p) for p in parsed]
    click.echo("Indexing complete")