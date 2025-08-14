from pathlib import Path
from ai.core.config import init_config, load_config

def test_init_and_load(tmp_path: Path):
    cfg_path = init_config(str(tmp_path))
    assert cfg_path.exists()
    cfg = load_config(tmp_path)
    assert str(tmp_path.resolve()) in cfg.vault_path.as_posix()
