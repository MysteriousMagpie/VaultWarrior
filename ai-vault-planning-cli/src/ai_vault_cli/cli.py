import click
from ai_vault_cli.commands import init, index, thread, ask, chat, capture, plan, doctor

@click.group()
def cli():
    """AI Vault Planning CLI"""
    pass

cli.add_command(init.cli)
cli.add_command(index.cli)
cli.add_command(thread.cli)
cli.add_command(ask.cli)
cli.add_command(chat.cli)
cli.add_command(capture.cli)
cli.add_command(plan.cli)
cli.add_command(doctor.cli)

if __name__ == "__main__":
    cli()