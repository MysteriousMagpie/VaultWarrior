import click

@click.group()
def cli():
    pass

@cli.command('capture')
@click.argument('text')
@click.option('--write', is_flag=True)
def capture_cmd(text, write):
    click.echo('Note captured')