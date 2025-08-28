import click

@click.group()
def cli():
    pass

@cli.command('plan')
@click.argument('slug')
@click.option('--weekly', is_flag=True)
@click.option('--write', is_flag=True)
def plan_cmd(slug, weekly, write):
    click.echo('Plan created')