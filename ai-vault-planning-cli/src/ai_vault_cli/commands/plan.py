import click

@click.command()
@click.argument('slug')
@click.option('--weekly', is_flag=True)
@click.option('--write', is_flag=True)
def plan(slug, weekly, write):
    click.echo('Plan created')