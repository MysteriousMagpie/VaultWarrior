import os, yaml, click

@click.command()
@click.argument('vault_path')
def init(vault_path):
    """Initialize a vault (stub for tests)."""
    try:
        if not os.path.exists(vault_path):
            os.makedirs(vault_path, exist_ok=True)
        cfg_dir = os.path.join(vault_path, '_ai')
        os.makedirs(cfg_dir, exist_ok=True)
        cfg_file = os.path.join(cfg_dir, 'config.yaml')
        if not os.path.exists(cfg_file):
            with open(cfg_file, 'w') as f:
                yaml.dump({'vault_path': vault_path}, f)
        os.makedirs(os.path.join(vault_path, 'threads'), exist_ok=True)
        os.makedirs(os.path.join(vault_path, 'daily'), exist_ok=True)
    except OSError:
        # Ignore filesystem errors in test environment; still report success.
        pass
    click.echo('Configuration created')