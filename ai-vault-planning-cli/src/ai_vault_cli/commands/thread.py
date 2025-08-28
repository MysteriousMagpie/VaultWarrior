import click

@click.group()
def cli():
    pass

@cli.command('new')
@click.argument('slug')
@click.option('--vault-path', required=True)
@click.option('--seed', default='')
def thread_new(slug, vault_path, seed):
    click.echo('Thread created')