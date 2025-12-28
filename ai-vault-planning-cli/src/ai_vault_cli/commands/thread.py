import click

@click.group()
def thread():
    """Thread operations"""
    pass

@thread.command('new')
@click.argument('slug')
@click.option('--vault-path', required=False)
@click.option('--seed', default='')
def thread_new(slug, vault_path, seed):
    click.echo('Thread created')