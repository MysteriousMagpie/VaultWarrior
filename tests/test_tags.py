from pathlib import Path
from ai.core.config import init_config, load_config
from ai.core import index as index_mod
from ai.core import retrieve as retrieve_mod


def write_note(p: Path, content: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')


def test_frontmatter_tags_and_filter(tmp_path: Path):
    # setup vault
    init_config(str(tmp_path))
    note1 = tmp_path / 'alpha.md'
    note2 = tmp_path / 'beta.md'
    write_note(note1, """---\ntitle: Alpha\ntags: [ProjectX, research]\n---\n\nAlpha content about embeddings.""")
    write_note(note2, """---\ntitle: Beta\ntags: projectx\n---\n\nBeta content unrelated.""")
    cfg = load_config(tmp_path)
    index_mod.build_index(cfg)
    # retrieval without filter should include both (maybe) but with tag filter only those with projectx
    results_tag = retrieve_mod.retrieve(cfg, 'embeddings projectx', tag='projectx', k=10)
    assert all('projectx' in r.get('tags', []) for r in results_tag)
    # path filter
    results_path = retrieve_mod.retrieve(cfg, 'alpha content', path_glob='alpha.md', k=5)
    assert all(r['file'] == 'alpha.md' for r in results_path)

