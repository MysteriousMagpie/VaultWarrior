import click

@click.command()
@click.argument('text')
@click.option('--write', is_flag=True)
def capture(text, write):
    click.echo('Note captured')