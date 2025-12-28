import click
from ai_vault_cli.commands.init import init
from ai_vault_cli.commands.index import index
from ai_vault_cli.commands.thread import thread
from ai_vault_cli.commands.ask import ask
from ai_vault_cli.commands.chat import chat
from ai_vault_cli.commands.capture import capture
from ai_vault_cli.commands.plan import plan
from ai_vault_cli.commands.doctor import doctor

@click.group()
def cli():
    """AI Vault Planning CLI"""
    pass

for cmd in (init, index, thread, ask, chat, capture, plan, doctor):
    cli.add_command(cmd)

if __name__ == '__main__':
    cli()