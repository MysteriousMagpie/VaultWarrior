import click

@click.command()
@click.argument('slug')
@click.argument('message')
@click.option('--write', is_flag=True)
def chat(slug, message, write):
    click.echo('Chat response')