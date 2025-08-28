import os, yaml, click

@click.group()
def cli():
    pass

@cli.command('init')
@click.argument('vault_path')
def init_cmd(vault_path):
    if not os.path.exists(vault_path):
        os.makedirs(vault_path)
    cfg_dir = os.path.join(vault_path, '_ai')
    os.makedirs(cfg_dir, exist_ok=True)
    cfg_file = os.path.join(cfg_dir, 'config.yaml')
    if not os.path.exists(cfg_file):
        with open(cfg_file, 'w') as f:
            yaml.dump({'vault_path': vault_path}, f)
    os.makedirs(os.path.join(vault_path, 'threads'), exist_ok=True)
    os.makedirs(os.path.join(vault_path, 'daily'), exist_ok=True)
    click.echo('Configuration created')