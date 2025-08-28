import click

@click.group()
def cli():
    pass

@cli.command('chat')
@click.argument('slug')
@click.argument('message')
@click.option('--write', is_flag=True)
def chat_cmd(slug, message, write):
    click.echo('Chat response')