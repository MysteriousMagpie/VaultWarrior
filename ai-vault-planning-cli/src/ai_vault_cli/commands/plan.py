import click
from ai_vault_cli.planning.planner import create_plan
from ai_vault_cli.threads.manager import get_thread
from ai_vault_cli.utils.logging import log_info

@click.command()
@click.argument('slug')
@click.option('--weekly', is_flag=True, help='Create a weekly plan.')
@click.option('--write', is_flag=True, help='Write the plan to the thread.')
def plan(slug, weekly, write):
    """Create a plan based on the specified thread slug."""
    log_info(f"Planning for thread: {slug}, Weekly: {weekly}, Write: {write}")
    
    thread = get_thread(slug)
    if not thread:
        click.echo(f"Thread '{slug}' not found.")
        return

    plan = create_plan(thread, weekly)
    
    if write:
        # Logic to append the plan to the thread would go here
        click.echo(f"Plan for '{slug}' has been written.")
    else:
        click.echo(plan)

if __name__ == "__main__":
    plan()