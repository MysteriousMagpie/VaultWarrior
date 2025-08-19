from pathlib import Path
from ai.core.config import init_config, load_config
from typer.testing import CliRunner
from ai.cli import app

runner = CliRunner()

def write(p: Path, content: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')


def test_enrich_adds_frontmatter(tmp_path: Path):
    init_config(str(tmp_path))
    # note without frontmatter in nested folder
    nested = tmp_path / 'Projects' / 'Alpha' / 'note_one.md'
    write(nested, "Some body text")
    # dry-run first
    r = runner.invoke(app, ["enrich", "--vault-path", str(tmp_path)])
    assert r.exit_code == 0
    assert "would update" in r.stdout
    # apply
    r2 = runner.invoke(app, ["enrich", "--vault-path", str(tmp_path), "--apply"])  # apply changes
    assert r2.exit_code == 0
    txt = nested.read_text(encoding='utf-8')
    assert txt.startswith('---')
    assert 'title:' in txt
    assert 'created:' in txt
    # tags inferred from path segments (projects, alpha)
    assert 'projects' in txt.lower()
    assert 'alpha' in txt.lower()


def test_enrich_preserves_existing(tmp_path: Path):
    init_config(str(tmp_path))
    existing = tmp_path / 'x.md'
    write(existing, "---\ntitle: Custom\ncustom_key: 123\n---\n\nBody")
    r = runner.invoke(app, ["enrich", "--vault-path", str(tmp_path), "--apply"])
    assert r.exit_code == 0
    txt = existing.read_text(encoding='utf-8')
    assert 'custom_key:' in txt  # preserved
    assert 'title: Custom' in txt  # unchanged
